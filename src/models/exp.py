from pathlib import Path
from tqdm import tqdm
import copy

from src import yaml
from src.models import load_conf
from src.models.layers.shake_drop import ShakePyramidNet
from src.utils import ensure_dir, ensure_path
from src.utils.dataloader import DataLoader
from src.utils.load_cifar import load_cifar
from src.models import PathFuncs as Pf

class ImgRecExperiment(object):

    def __init__(self, work_dir:Path, config=None):
        
        self.work_dir = ensure_dir(path)
        self.model_dir = self.work_dir / 'models'

        self._conf_file = self.work_dir / 'conf.yml'
        self.score_file = self.model_dir / 'scores.tsv'


        if isinstance(config, str) or isinstance(config, Path):
            config = load_conf(config)
        self.config = config

        self._trained_file = self.work_dir / '_TRAINED'

    @property
    def model_args(self):
        return self.config.get('model_args')

    @property
    def optim_args(self):
        return self.config.get('optim_args')

    def has_trained(self):
        return self._trained_file.exists()

    def load(self):
        self.load_dataset()
        self.load_model()

    def load_dataset(self, dataset_name:str='cifar-10'):
        train_dataset, test_dataset = load_cifar(dataset_name)
        self.train_loader = DataLoader(train_dataset, 64)
        self.test_loader = DataLoader(test_dataset, 64)

    def load_model(self):
        model_args = self.config.get('model_args')
        self.model = ShakePyramidNet(
            depth=model_args.get('depth'),
            alpha=model_args.get('alpha'),
            labels=self.num_classes)
        
        optim_args = self.config.get('optim_args')
        self.optimizer = optim.SGD(self.model.parameters(),
                                    lr=optim_args.get('lr'),
                                    momentum=optim_args.get('momentum', 0.9),
                                    weight_decay=optim_args.get('wt_decay',0.0001),
                                    nesterov=optim_args.get('nesterov', True))
        train_args = self.config.get('train_args')
        steps = train_args.get('steps')
        self.scheduler = optim.lr_scheduler.MultiStepLR(self.optimizer,
                                    [steps // 2, (steps * 3) // 4])
        self.loss_func = nn.CrossEntropyLoss()
        self.last_step = 0

        self.load_last()

    def make_checkpt(self, train_loss, test_loss):
        step_num = self.last_step
        total_loss = train_loss + test_loss
        model = self.model
        state = {
            'model_state': model.state_dict(),
            'optim_state': self.optimizer.state_dict(),
            'step': step_num,
            'total_loss': total_loss,
            'test_loss': test_loss,
            'model_args': self.model_args,
            'optim_args': self.optim_args
        }

        name = f'model_{step_num:03d}_{total_loss:.6f}_{test_loss:.6f}.pkl'
        path = self.model_dir / name
        torch.save(state, str(path))

        with open(self.score_file, 'a') as fw:
            cols = [str(step_num), name, f'{total_loss:g}', 
                    f'{train_loss:g}', f'{test_loss:g}']
            text = '\t'.join(cols)
            fw.write(f'{text}\n')

    def get_best_model(self):
        return Pf.get_last_saved_model(self.model_dir)

    def get_last_model(self):
        return Pf.get_best_known_model(self.model_dir)

    def load_last(self):
        last_model, last_step = self.get_last_model()
        if last_model:
            state = torch.load(last_model, map_location=self.device)
            model_state = state['model_state'] if 'model_state' in state else state
            self.model.load_state_dict(model_state)
            self.model.to(self.device)

            optim_state = state['optim_state'] if 'optim_state' in state else None
            if optim_state:
                self.optimizer.load_state_dict(optim_state)

    def train(self, data_loader):
        self.train_mode(True)
        train_loss = 0
        with tqdm(data_loader, total=len(data_loader)) as data_bar:
            for p, batch in enumerate(data_bar):
                x, t = batch
                x, t = x.cuda(), t.cuda()
                y = self.model(x)
                loss = self.loss_func(y, t)
                loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()
                train_loss += loss.item()
                msg = f'Batch : {p+1}, Train Loss : {train_loss / (p+1)}'
                data_bar.set_postfix_str(msg, refresh=True)
        return train_loss / len(data_loader)

    def predict(self, data_loader, get_outs:bool=False):
        self.train_mode(False)
        test_loss= 0
        test_preds, test_trues = [], []
        with tqdm(data_loader, total=len(data_loader)) as data_bar:
            for p, batch in enumerate(data_bar):
                x, trues = batch
                x, trues = x.cuda(), trues.cuda()
                preds = self.model(x)
                loss = self.loss_func(preds, trues)
                test_loss += loss.item()
                msg = f'Batch : {p+1}, Test Loss : {test_loss / (p+1)}'
                data_bar.set_postfix_str(msg, refresh=True)
                test_trues.append(trues)
                test_preds.append(preds)
        if get_outs:
            preds = torch.cat(test_preds, dim=-1)
            return test_loss, preds
        return test_loss

    def run(self):
        train_args = self.config.get('train_args')

        total_steps = train_args.get('steps')
        _, last_step = Pf.get_last_saved_model(self.model_dir)

        if self.has_trained():
            try:
                last_step = max(last_step, yaml.load(self._trained_file.read_text())['steps'])
            except Exception:
                pass
        if last_step >= total_steps:
            return

        train_loss, test_loss = 0, 0
        for step in range(self.last_step+1, total_steps):
            train_loss = self.train(self.train_loader)
            self.last_step = step
            unsaved = True
            if step % checkpt_stage == 0:
                test_loss = self.predict(self.test_loader)
                self.make_checkpt(train_loss, test_loss)
                unsaved = False
                self.train_mode(True)
                self._write_trained(step)
        if unsaved:
            test_loss = self.predict(self.test_loader)
            self.make_checkpt(train_loss, test_loss)
            self._write_trained(total_steps)
        return

    def evaluate(self):
        preds = self.predict(self.test_loader, get_outs=True)
        labels = self.test_loader.dataset.labels
        

    def _write_trained(self, step):
        yaml.dump(dict(step=step, stream=self._trained_flag)        

    def train_mode(self, mode:bool=True):
        torch.set_grad_enable(mode)
        self.model.train(mode)