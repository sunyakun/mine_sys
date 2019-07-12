import json

from django.shortcuts import HttpResponse

from mine.algorithm import common


def training_view(request):
    dataset_file = request.GET.get('dataset_file_path')
    name = request.GET.get('name')
    cfg = request.GET.get('config')
    algorithm = request.GET.get('algorithm')
    if not dataset_file:
        return HttpResponse(json.dumps({
            'data': {
                'msg': 'please provide dataset file!',
            }
        }))
    cfg = json.loads(cfg)
    cfg.setdefault('name', name)
    cfg.setdefault('algorithm_module', algorithm)
    common.training(dataset_file, cfg)
    return HttpResponse(json.dumps({
        'data': {
            'msg': 'please wait...',
        }
    }))
