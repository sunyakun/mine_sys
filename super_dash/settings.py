import os

from django.conf import settings

LOGIN_URL = 'super_dash:login'

BASE_UPLOAD_PHOTO_DIR = os.path.join(settings.BASE_DIR, 'super_dash', 'static',
                                     'img', 'photo')

BASE_UPLOAD_DATASET_DIR = os.path.join(settings.BASE_DIR, 'super_dash',
                                       'upload', 'dataset')

ADMIN_USER_NAME = 'admin'

# the message send to the user when first register
MESSAGE = '欢迎成为大数据分析平台的会员'

REDIS = {
    'host': 'localhost'
}
