import pickle
import logging

from collections import Iterable
from redis import StrictRedis, ConnectionPool
from mine.algorithm.models import \
    (DecisionTree, PieGraph, ThreeDHistogram, Scatter)
from .settings import REDIS
from super_dash import jsonschema

LOG = logging.getLogger(__name__)

_REDIS_POOL = None


def init_redis(db=0):
    global _REDIS_POOL
    if not _REDIS_POOL:
        _REDIS_POOL = ConnectionPool(host=REDIS.get('host', 'localhost'),
                                     port=REDIS.get('port', 6379),
                                     db=db,
                                     password=REDIS.get('password'))
    redis = StrictRedis(connection_pool=_REDIS_POOL)
    return redis


def get_dataset_status(name):
    redis = init_redis()
    try:
        status = redis.get(name)
    except TimeoutError:
        LOG.info('redis连接超时')
        raise
    if status:
        return 'ok'
    else:
        LOG.info('未在redis中查询到%s数据集的状态' % name)
        return 'loading'


def get_user_info(user):
    user_info = {
        'username': user.get_username(),
        'email': user.email,
        'password': None,
        'photo_url': '/static/img/photo/%s' % user.photo.photo_url,
        'message_nu': user.recv_msg.filter(type='message').count(),
        'messages': [(message.date, message.msg,
                      '/static/img/photo/%s' % message.sender.photo.photo_url)
                     for message in user.recv_msg.filter(type='message')],
        'alter_nu': user.recv_msg.filter(type='alter').count(),
        'alters': [(message.date, message.msg, message.user.photo.photo_url)
                   for message in user.recv_msg.filter(type='alter')],
        'datasets': [{
            "name": item.name,
            "file": item.file,
            "algorithm": item.algorithm,
            "config": item.config,
            "status": get_dataset_status(item.name)}
            for item in user.dataset.all()
        ]
    }
    return user_info


def cache(key, value):
    redis = init_redis()
    redis.set(key, value)


def get_cache(key):
    redis = init_redis()
    return redis.get(key)


def cache_models(name, models):
    redis = init_redis()
    redis.set(name, pickle.dumps(models))


def get_models_cache(name):
    redis = init_redis()
    bin_model = redis.get(name)
    if not bin_model:
        return []
    return pickle.loads(bin_model)


def del_cache(name):
    redis = init_redis()
    redis.delete(name)


def get_training_result(name):
    models = get_models_cache(name)
    if isinstance(models, dict):
        LOG.warning(models.get('exp_stk'))
        return models
    if not isinstance(models, Iterable):
        raise Exception("Unknown exception")
    res = {}
    for item in models:
        if isinstance(item, DecisionTree):
            if 'decision_tree' not in res:
                res.setdefault('decision_tree', [])
            res.get('decision_tree').append(item.to_json_able())
        elif isinstance(item, PieGraph):
            if 'pie_graphs' not in res:
                res.setdefault('pie_graphs', [])
            res['pie_graphs'].append(item.to_json_able())
        elif isinstance(item, ThreeDHistogram):
            if 'threeD_histogram' not in res:
                res.setdefault('threeD_histogram', [])
            res.get('threeD_histogram').append(item.to_json_able())
        elif isinstance(item, Scatter):
            if 'scatter' not in res:
                res.setdefault('scatter', [])
            res.get('scatter').append(item.to_json_able())
    return res


def get_schema(name):
    try:
        schema = getattr(jsonschema, name.replace('.', '_'))
    except AttributeError:
        return None
    return schema
