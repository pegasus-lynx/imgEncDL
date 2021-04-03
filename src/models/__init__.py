from typing import Tuple, Optional, List
from pathlib import Path

def load_conf

class PathFuncs(object):
    @classmethod
    def _path_to_test_score(cls, path):
        parts = str(path.name).replace('.pkl', '').split('_')
        test_score = float(parts[-1])
        return test_score

    @classmethod
    def _path_to_total_score(cls, path):
        parts = str(path.name).replace('.pkl', '').split('_')
        tot_score = float(parts[-2]) + float(parts[-1])
        return tot_score

    @classmethod
    def _path_to_step_no(cls, path):
        parts = str(path.name).replace('.pkl', '').split('_')
        step_no = int(parts[-3])
        return step_no

    @classmethod
    def sorted_models(cls, model_dir, sort:str = 'step', desc:bool = True) -> List[Path]:
        """
        Lists models in descending order of modification time
        :param sort: how to sort models ?
          - valid_score: sort based on score on validation set
          - total_score: sort based on validation_score + training_score
          - mtime: sort by modification time
          - step (default): sort by step number
        :param desc: True to sort in reverse (default); False to sort in ascending
        :return: list of model paths
        """
        paths = model_dir.glob('model_*.pkl')
        sorters = {
            'test_score': cls._path_to_test_score,
            'total_score': cls._path_to_total_score,
            'step': cls._path_to_step_no
        }
        if sort not in sorters:
            raise Exception(f'Sort {sort} not supported. valid options: {sorters.keys()}')
        return sorted(paths, key=sorters[sort], reverse=desc)

    @classmethod
    def _get_first_model(cls, model_dir, sort: str, desc: bool) -> Tuple[Optional[Path], int]:
        """
        Gets the first model that matches the given sort criteria
        :param sort: sort mechanism
        :param desc: True for descending, False for ascending
        :return: Tuple[Optional[Path], step_num:int]
        """
        models = cls.sorted_models(model_dir, sort=sort, desc=desc)
        if models:
            step, train_score, test_score = models[0].name.replace('.pkl', '').split('_')[-3:]
            return models[0], int(step)
        else:
            return None, 0

    @classmethod
    def get_best_known_model(cls, model_dir) -> Tuple[Optional[Path], int]:
        """
            Gets best Known model (best on lowest scores on training and validation sets)
        """
        return cls._get_first_model(model_dir, sort='total_score', desc=False)

    @classmethod
    def get_last_saved_model(cls, model_dir) -> Tuple[Optional[Path], int]:
        """
            Gets last saved model (based on steps)
        """
        return cls._get_first_model(model_dir, sort='step', desc=True)
