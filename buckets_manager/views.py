from datetime import datetime
from django.shortcuts import render
from . import amazon
from . import json_data
from . import models
from . import log as l
import threading
import json
import pytz

log = l.Logs()

class Bucket:
    def __init__(self, id, bucket_name, region_name,created ,count) -> None:
        self.id = id
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.created = created
        self.count = count

def buckets(request):
    current_sidebar = "buckets"
    response = ''
    if request.method == "POST":
        files = json_data.Data('json/data.json')
        s3 = amazon.Amazon(files.get_data())
        if request.POST['from'] == 'buckets':
            id_list = []
            for data_id in request.POST.getlist('data_list'):
                models.buckets.objects.filter(id = data_id).delete()
                id_list.append(data_id)
            threading.Thread(
                target=delete_buckets,
                args=(id_list, )
            ).start()
        elif request.POST['from'] == 'form':
            response = s3.create_bucket(
                request.POST['bucket_name'], 
                request.POST['region_name']
            )
            if response:
                return render(request, "form_bucket.html", {"current_sidebar": '', 
                "names": models.buckets.objects.all(), "error_message": response})
            else:
                models.buckets(
                    bucket_name = request.POST['bucket_name'],
                    region_name = request.POST['region_name'],
                    created = datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d/%m/%y %H:%M"),
                ).save()
                log.add_bucket(request.POST['bucket_name'])
    data = []
    for bucket in models.buckets.objects.all():
        data.append(Bucket(
            id = bucket.id,
            bucket_name = bucket.bucket_name,
            region_name = bucket.region_name,
            created = bucket.created,
            count = models.json_files.objects.filter(bucket=bucket.id).count()
        ))
    return render(request, "buckets.html", {"current_sidebar": current_sidebar, 
    "data": data})

def files_json(request):
    current_sidebar = "json"
    bucket_name = ''
    bucket_id = 0
    
    if request.method == "GET" and not request.GET.get('bucket') == None:
        bucket_name = request.GET.get('bucket')
        bucket_id = models.buckets.objects.filter(bucket_name=bucket_name).values("id")[0]['id']
    elif request.method == "POST":
        bucket_name = request.POST['bucket_name']
        files = json_data.Data('json/data.json')
        s3 = amazon.Amazon(files.get_data())
        bucket_id = models.buckets.objects.filter(bucket_name=bucket_name).values("id")[0]['id']
        if request.POST['from'] == 'files_json':
            threading.Thread (
                target=delete_files,
                args=(bucket_name, request.POST.getlist('list_data'),)
            ).start()
        elif request.POST['from'] == 'form_json':
            file_json = { "Admobnumb": request.POST['Admobnumb'],
                "Version": request.POST['Version'],
                "AppId" : request.POST['AppId'],
                "BannerId": request.POST['BannerId'],
                "InterstitialAdId": request.POST['InterstitialAdId'],
                "RewardedAdId": request.POST['RewardedAdId'],
                "NativeAdId": request.POST['NativeAdId']
            }
            file_name = create_file_name(bucket_id)
            if s3.add_file(bucket_name, file_name, file_json):
                return render(request, "form_json.html", 
                {
                    "error_message": True,
                    "current_sidebar": '', 
                    "bucket_name": bucket_name, 
                    "buckets_names": models.buckets.objects.values('bucket_name')
                })
            models.json_files(
                    file_name = file_name,
                    content = json.dumps(file_json),
                    last_update = datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d/%m/%y %H:%M"),
                    bucket = models.buckets.objects.filter(bucket_name=bucket_name)[0]
                ).save()
            log.add_file(bucket_name, file_name)
        elif request.POST['from'] == 'change_json':
            file_name = request.POST['name']
            bucket_name = request.POST['bucket_name']
            file_json = { "Admobnumb": request.POST['Admobnumb'],
                "Version": request.POST['Version'],
                "AppId" : request.POST['AppId'],
                "BannerId": request.POST['BannerId'],
                "InterstitialAdId": request.POST['InterstitialAdId'],
                "RewardedAdId": request.POST['RewardedAdId'],
                "NativeAdId": request.POST['NativeAdId']
            }
            threading.Thread(
                target=s3.add_file,
                args=(bucket_name, file_name, file_json, )
            ).start()
            new_file = models.json_files.objects.get(
                file_name = file_name,
                bucket = models.buckets.objects.filter(bucket_name=bucket_name).values("id")[0]['id']
            )
            new_file.content = json.dumps(file_json)
            new_file.last_update = datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d/%m/%y %H:%M")
            new_file.save()
            log.change_file(bucket_name, file_name)
    return render(request, "json.html", 
    {
        "current_sidebar": current_sidebar, 
        "data": models.json_files.objects.filter(bucket=bucket_id), 
        "bucket": bucket_name, 
        "buckets_names": models.buckets.objects.values('bucket_name'), 
        "region": models.buckets.objects.filter(
            id=bucket_id).values('region_name')[0]['region_name']
    })

def form_json(request):
    current_sidebar = ''
    bucket_name = ''
    if request.method == "GET":
        if not request.GET.get('bucket') == None:
            bucket_name = request.GET.get('bucket')
        if not request.GET.get('key') == None:
            bucket_id = models.buckets.objects.filter(bucket_name=bucket_name).values("id")[0]['id']
            return render(request, "form_json_change.html",
            {
                "current_sidebar": current_sidebar, 
                "bucket_name": bucket_name, 
                "buckets_names": models.buckets.objects.values('bucket_name'), 
                "data": json.loads(models.json_files.objects.filter(
                    file_name=request.GET.get('key'), 
                    bucket=bucket_id).values('content')[0]['content']), 
                "file_name": request.GET.get('key')
            })
    return render(request, "form_json.html", 
    {
        "error_message": False,
        "current_sidebar": current_sidebar, 
        "bucket_name": bucket_name, 
        "buckets_names": models.buckets.objects.values('bucket_name')
    })

def form_bucket(request):
    current_sidebar = ''
    return render(request, "form_bucket.html", 
    {
        "current_sidebar": current_sidebar, 
        "buckets_names": models.buckets.objects.all().values('bucket_name')
    })

def settings(request):
    files = json_data.Data('json/data.json')
    current_sidebar = 'settings'

    if request.method == "POST":
        files.set_data(
            request.POST['aws_access_key_id'],
            request.POST['aws_secret_access_key']
        )
        models.buckets.objects.all().delete()
        models.json_files.objects.all().delete()
        
        s3 = amazon.Amazon(files.get_data())
        for bucket in s3.get_buckets():
            models.buckets(
                bucket_name = bucket.name,
                region_name = bucket.region,
                created = bucket.date,
            ).save()

        for file in models.buckets.objects.values('bucket_name'):
            for content in s3.get_files(file['bucket_name']):
                models.json_files(
                    file_name = content.name,
                    content = json.dumps(content.content),
                    last_update = content.date,
                    bucket = models.buckets.objects.filter(bucket_name=file['bucket_name'])[0]
                ).save()

    return render(request, "settings.html", 
    {
        "current_sidebar": current_sidebar, 
        "buckets_names": models.buckets.objects.all(), 
        "data": files.get_data()
    })

def logs(request):
    return render(request, "logs.html", 
    {
        "current_sidebar": "logs", 
        "buckets_names": models.buckets.objects.all(),
        "logs": models.logs.objects.all().reverse()
    })

def create_file_name(bucket_id: int):
    files = models.json_files.objects.filter(bucket=bucket_id).values('file_name')
    new_name = 0
    for name in files:
        if int(name['file_name']) > new_name:
            new_name = int(name['file_name'])
    return new_name + 1

def delete_buckets(id_list: list):
    files = json_data.Data('json/data.json')
    s3 = amazon.Amazon(files.get_data())
    for bucket_id in id_list:
        bucket_name = models.buckets.objects.filter(id = bucket_id).values('bucket_name')[0]['bucket_name']
        s3.delete_bucket(bucket_name)
        log.del_bucket(bucket_name)

def delete_files(bucket_name: str, id_list: list):
    files = json_data.Data('json/data.json')
    s3 = amazon.Amazon(files.get_data())
    for file_id in id_list:
        file_number = models.json_files.objects.filter(id=file_id).values('file_name')[0]['file_name']
        s3.delete_file(
                    bucket_name, 
                    file_number
                )
        log.del_file(bucket_name, file_number)