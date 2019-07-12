import io
import traceback
import logging
import importlib

from concurrent.futures import ThreadPoolExecutor
from mine.signals import on_dataset_finish, on_exception_occur
from mine import settings

thread_pool = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT)
LOG = logging.getLogger(__name__)


def training(file_path, cfg):
    def func():
        """
        cfg = {
            'name': 'the training name(id)',
            'algorithm_module': 'algorithm.package.path',
            'function_name': 'algorithm entry point' | default 'entry',
            ...
        }
        """
        name = cfg.get('name')
        module_path = cfg.get('algorithm_module',
                              'mine.algorithm.C45.interface')
        function_name = cfg.get('function_name', 'entry')
        algorithm_module = importlib.import_module(module_path)
        alg_func = getattr(algorithm_module, function_name)
        res = None
        try:
            res, predict = alg_func(ds=file_path, cfg=cfg)
        except Exception as e:
            string_io = io.StringIO()
            traceback.print_stack(file=string_io)
            string_io.seek(0)
            on_exception_occur.send(func, name=name,
                                    exception={
                                        "exp": e,
                                        "exp_stk": string_io.read()
                                    })
        else:
            on_dataset_finish.send(res.__class__, name=name, models=res,
                                   predict=predict)
    return thread_pool.submit(func)
