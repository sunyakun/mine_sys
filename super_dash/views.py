# -*- coding: utf-8 -*-
import io
import os
import json
import pandas
import pickle
import logging
import requests
import jsonschema
import importlib

from json.decoder import JSONDecodeError
from django.shortcuts import render, redirect, reverse, HttpResponse, Http404
from django.http import StreamingHttpResponse
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import auth

from . import utils
from . import settings
from . import echart_config
from .echart_config import data_map
from .models import Photo, Dataset, Message
from .signals import user_register
from .utils import get_user_info, get_dataset_status, get_training_result

from mine.signals import on_dataset_finish, on_exception_occur

LOG = logging.getLogger(__name__)


# user_register signal
def user_register_handler(**kwargs):
    admin_user = User.objects.get(username=settings.ADMIN_USER_NAME)
    init_msg = Message()
    init_msg.user = kwargs.get('user')
    init_msg.sender = admin_user
    init_msg.type = 'message'
    init_msg.msg = settings.MESSAGE
    init_msg.save()


user_register.connect(user_register_handler)


# dataset finish signal
def on_dataset_finish_handler(sender, **kwargs):
    models = kwargs.get('models')
    name = kwargs.get('name')
    predict = kwargs.get('predict')
    utils.cache_models(name, models)
    utils.cache("predict_%s" % name, pickle.dumps(predict))


on_dataset_finish.connect(on_dataset_finish_handler)


# exception signal
def on_exception_occur_handler(sender, **kwargs):
    name = kwargs.get('name')
    exception = kwargs.get('exception')
    LOG.warning("%s exception:<%s>" % (name, str(exception)))
    utils.cache_models(name, exception)


on_exception_occur.connect(on_exception_occur_handler)


def response_not_found_handler(request, exception):
    return render(request, '404.html', get_user_info(request.user), status=404)


@login_required(login_url=settings.LOGIN_URL)
def index_view(request):
    return render(request, 'index.html', get_user_info(request.user))


@login_required(login_url=settings.LOGIN_URL)
def message_view(request):
    return render(request, 'message.html', get_user_info(request.user))


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return render(request, 'index.html', get_user_info(user))
        else:
            return render(request, 'login.html', {'error': True})
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        if password == repassword and username and email:
            try:
                user = User.objects.create_user(username, email, password)
            except IntegrityError:
                return render(request, 'register.html', {'error': True})
            user.first_name = firstname if firstname else None
            user.last_name = lastname if lastname else None

            photo = Photo()
            photo.user = user
            photo.photo_url = 'photo.jpg'
            photo.save()

            user.save()
            user_register.send(user.__class__, request=request, user=user)
            user_info = get_user_info(user)
            auth.login(request, user)
            return render(request, 'index.html', user_info)
        else:
            return render(request, 'register.html', {'error': True})

    return render(request, 'register.html')


def forgot_password_view(request):
    return render(request, 'forgot-password.html')


@login_required(login_url=settings.LOGIN_URL)
def logout_view(request):
    auth.logout(request)
    return render(request, 'login.html')


@login_required(login_url=settings.LOGIN_URL)
def profile_view(request):
    return render(request, 'profile.html', get_user_info(request.user))


@login_required(login_url=settings.LOGIN_URL)
def update_profile_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    photo_file = request.FILES.get('photo')
    user = request.user
    if username:
        user.username = username
        if password:
            user.set_password(password)
        if photo_file:
            photo_path = os.path.join(settings.BASE_UPLOAD_PHOTO_DIR,
                                      photo_file.name)
            photo = user.photo
            photo.photo_url = photo_file.name
            with open(photo_path, 'wb+') as fp:
                for chunk in photo_file.chunks():
                    fp.write(chunk)
            photo.save()
        user.save()
    else:
        user_info = get_user_info(user)
        user_info.setdefault('error', True)
        return render(request, 'profile.html', user_info)

    return render(request, 'profile.html', get_user_info(user))


@login_required(login_url=settings.LOGIN_URL)
def get_task_status_view(request):
    name = request.GET.get('name')
    return HttpResponse(json.dumps({
        "status": get_dataset_status(name)
    }))


@login_required(login_url=settings.LOGIN_URL)
def upload_dataset_view(request):
    dataset_file = request.FILES.get('dataset')
    name = request.POST.get('name')
    if not dataset_file and not name:
        return render(request, 'index.html', get_user_info(request.user))
    dataset_model = Dataset()
    dataset_model.user = request.user
    dataset_model.file = dataset_file.name
    dataset_model.name = name
    try:
        dataset_model.validate_unique()
    except ValidationError:
        return render(request, 'index.html', get_user_info(request.user))

    upload_to = os.path.join(settings.BASE_UPLOAD_DATASET_DIR,
                             dataset_file.name)
    with open(upload_to, 'wb+') as fp:
        for chunk in dataset_file.chunks():
            fp.write(chunk)

    dataset_model.save()
    # return render(request, 'index.html', get_user_info(request.user))
    return redirect("super_dash:settings")


@login_required(login_url=settings.LOGIN_URL)
def show_reports_view(request):
    user_info = get_user_info(request.user)
    return render(request, 'reports.html', user_info)


@login_required(login_url=settings.LOGIN_URL)
def get_dataset_index_view(request):
    name = request.GET.get('dataset')
    try:
        dataset = Dataset.objects.get(user=request.user, name=name)
    except Dataset.DoesNotExist:
        return HttpResponse(json.dumps({"index": []}))
    file_name = dataset.file
    file_path = os.path.join(settings.BASE_UPLOAD_DATASET_DIR, file_name)
    index = pandas.read_csv(file_path).columns
    return HttpResponse(json.dumps({"index": list(index)}))


@login_required(login_url=settings.LOGIN_URL)
def get_dataset_view(request):
    name = request.GET.get('dataset')
    echart_type = request.GET.get('echart_type')
    index = request.GET.get('index')

    try:
        Dataset.objects.get(user=request.user, name=name)
    except Dataset.DoesNotExist:
        raise Http404()

    res = get_training_result(name)
    if 'exp_stk' in res:
        return HttpResponse(json.dumps({
            "error": True,
            "exception": str(res.get('exp'))
        }))

    try:
        res = res.get(getattr(data_map, echart_type.upper()), [])
    except AttributeError:
        raise Http404()

    if echart_type.upper() not in ["TREE", "SCATTER"]:
        for item in res:
            if index == item.get('name'):
                res = item.get('data')

    return HttpResponse(json.dumps(res))


@login_required(login_url=settings.LOGIN_URL)
def get_dataset_overview(request):
    dataset_name = request.GET.get('dataset')
    try:
        dataset = Dataset.objects.get(user=request.user, name=dataset_name)
    except Dataset.DoesNotExist:
        raise Http404()
    if dataset:
        ds_file_path = os.path.join(settings.BASE_UPLOAD_DATASET_DIR, dataset.file)
        df = pandas.read_csv(ds_file_path).head()
        return render(request, 'dataset_overview.html', {
            "column_index": df.columns,
            "table": (row[1] for row in df.iterrows())
        })


@login_required(login_url=settings.LOGIN_URL)
def settings_view(request):
    return render(request, 'settings.html', get_user_info(request.user))


@login_required(login_url=settings.LOGIN_URL)
def update_settings_view(request):
    name = request.POST.get('name')
    algorithm = request.POST.get('algorithm')
    raw_config = request.POST.get('config')

    user_info = get_user_info(request.user)

    try:
        config = json.loads(raw_config)
        importlib.import_module(algorithm)
        schema = utils.get_schema(algorithm)
        if schema:
            jsonschema.validate(config, schema)
    except JSONDecodeError as e:
        # for dataset in user_info.get('datasets'):
        #     if dataset['name'] == name:
        #         dataset['algorithm'] = algorithm
        #         dataset['config'] = config
        user_info.setdefault('error', '配置信息错误')
        return render(request, 'settings.html', user_info)
    except jsonschema.exceptions.ValidationError as e:
        user_info.setdefault('error', e.message)
        return render(request, 'settings.html', user_info)
    except ImportError as e:
        user_info.setdefault('error', '无法找到算法插件')
        return render(request, 'settings.html', user_info)
    dataset = Dataset.objects.get(name=name, user=request.user)
    dataset.algorithm = algorithm
    dataset.config = raw_config
    dataset.save()

    # using "requests" library request to the mine API
    # FIXME: How to use post method with csrf token
    host_origin = request.META.get('HTTP_ORIGIN')
    data = {
        "name": dataset.name,
        "algorithm": dataset.algorithm,
        "dataset_file_path": os.path.join(settings.BASE_UPLOAD_DATASET_DIR,
                                          dataset.file),
        "config": dataset.config
    }
    utils.del_cache(name)
    resp = requests.get(host_origin + reverse('mine:training'), params=data)
    if resp.status_code == 200:
        return redirect('super_dash:settings')
    else:
        user_info.setdefault('error', '数据分析失败')
        return render(request, 'settings.html', user_info)


@login_required(login_url=settings.LOGIN_URL)
def delete_dataset_view(request):
    name = request.GET.get('dataset')
    try:
        ds = Dataset.objects.get(user=request.user, name=name)
    except Dataset.DoesNotExist:
        return redirect("super_dash:index")
    ds.delete()
    utils.del_cache(name)
    return redirect("super_dash:index")


@login_required(login_url=settings.LOGIN_URL)
def echart_view(request):
    name = request.GET.get('dataset')
    echart_type = request.GET.get('echart_type')
    index = request.GET.get('index')

    try:
        e_config = getattr(echart_config, echart_type.upper())
    except AttributeError:
        raise Http404()

    if echart_type.upper() == 'SCATTER':
        return render(request, 'echart/scatter.html', {
            "dataset": name,
            "echart_config": json.dumps(e_config),
            "echart_type": echart_type,
        })

    return render(request, 'echart/echart.html', {
        "dataset": name,
        "echart_config": json.dumps(e_config),
        "echart_type": echart_type,
        "index": index
    })


@login_required(login_url=settings.LOGIN_URL)
def get_dataset_config_view(request):
    name = request.GET.get('dataset')
    try:
        ds = Dataset.objects.get(user=request.user, name=name)
    except Dataset.DoesNotExist:
        return HttpResponse("config not exist")
    else:
        return HttpResponse(ds.config)


@login_required(login_url=settings.LOGIN_URL)
def predict_view(request):
    name = request.POST.get('dataset_name')
    file = request.FILES.get('dataset')

    try:
        Dataset.objects.get(user=request.user, name=name)
    except Dataset.DoesNotExist:
        return HttpResponse("ERROR!")

    ds = pandas.read_csv(file)
    bin_func = utils.get_cache('predict_%s' % name)
    func = pickle.loads(bin_func)

    labels = func(ds)
    sio = io.StringIO()
    pandas.DataFrame(labels).to_csv(sio, header=False, index=False)

    sio.seek(0)
    resp = StreamingHttpResponse((line for line in sio),
                                 content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="result.csv"'
    return resp
