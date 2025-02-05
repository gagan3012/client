from argparse import Namespace

import pytorch_lightning
from pytorch_lightning.utilities import rank_zero_only

from ..logger import DAGsHubLogger as LoggerImpl


class DAGsHubLogger(pytorch_lightning.logging.LightningLoggerBase):

    def __init__(self,
                 metrics_path: str = 'metrics.csv',
                 should_log_metrics: bool = True,
                 hparams_path: str = 'params.yml',
                 should_log_hparams: bool = True,
                 should_make_dirs: bool = True,
                 status_hyperparam_name: str = 'status',
                 ):
        """
        :param metrics_path: Where to save the single metrics CSV file.
        :param should_log_metrics: Whether to log metrics at all. Should probably always be True.
        :param hparams_path: Where to save the single hyperparameter YAML file.
        :param should_log_hparams: Whether to log hyperparameters to a file.
            Should be False if you want to work with hyperparameters in a dependency file,
            rather than specifying them using command line arguments.
        :param should_make_dirs: If true, the directory structure required by metrics_path and hparams_path
            will be created. Has no effect if the directory structure already exists.
        :param status_hyperparam_name: The 'status' passed by pytorch_lightning at the end of training
            will be saved as an additional hyperparameter, with this name.
            This can be useful for filtering and searching later on.
            Set to None if you don't want this to happen.
        """
        super(DAGsHubLogger, self).__init__()
        self.status_hyperparam_name = status_hyperparam_name
        self.logger = LoggerImpl(metrics_path=metrics_path, should_log_metrics=should_log_metrics,
                                 hparams_path=hparams_path, should_log_hparams=should_log_hparams,
                                 should_make_dirs=should_make_dirs, eager_logging=False)

    @rank_zero_only
    def log_metrics(self, metrics: dict, step_num: int):
        self.logger.log_metrics(metrics, step_num)

    @rank_zero_only
    def log_hyperparams(self, params: Namespace):
        self.logger.log_hyperparams(params.__dict__)

    @rank_zero_only
    def save(self):
        self.logger.save()

    @rank_zero_only
    def close(self):
        self.logger.close()

    @rank_zero_only
    def finalize(self, status: str):
        if self.status_hyperparam_name is not None and self.status_hyperparam_name not in self.logger.hparams:
            self.logger.log_hyperparams({self.status_hyperparam_name: status})
        self.logger.save_hparams()
