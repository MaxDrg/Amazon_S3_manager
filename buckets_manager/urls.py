from django.urls import path
from . import views
import hashlib

urlpatterns = [
    path(hashlib.sha256('buckets'.encode('utf8')).hexdigest(), views.buckets, name='buckets'),
    path(hashlib.sha256('files_json'.encode('utf8')).hexdigest(), views.files_json, name='files_json'),
    path(hashlib.sha256('form_json'.encode('utf8')).hexdigest(), views.form_json, name='form_json'),
    path(hashlib.sha256('form_bucket'.encode('utf8')).hexdigest(), views.form_bucket, name='form_bucket'),
    path(hashlib.sha256('settings'.encode('utf8')).hexdigest(), views.settings, name='settings'),
]