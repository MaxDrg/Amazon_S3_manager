from django.shortcuts import render
from . import amazon_boto3
from . import json_data

def buckets(request):
    current_sidebar = "buckets"
    response = ''
    json = json_data.Data('json/data.json')
    amazon_bucket = amazon_boto3.Amazon(json.get_data())
    if request.method == "POST":
        if request.POST['from'] == 'buckets':
            for data in request.POST.getlist('list_data'):
                amazon_bucket.delete_bucket(data)
        elif request.POST['from'] == 'form':
            response = amazon_bucket.create_bucket(request.POST['bucket_name'], 
            request.POST['region_name'])
            if response:
                return render(request, "form_bucket.html", {"current_sidebar": '', 
                "names": amazon_bucket.get_buckets(), "error_message": response})
    return render(request, "buckets.html", {"current_sidebar": current_sidebar, 
    "data": amazon_bucket.get_buckets_data()})

def json(request):
    json = json_data.Data('json/data.json')
    amazon_bucket = amazon_boto3.Amazon(json.get_data())

    current_sidebar = "json"
    data = []
    bucket_name = ''
    
    if request.method == "GET" and not request.GET.get('json') == None:
        bucket_name = request.GET.get('json')
    elif request.method == "POST":
        if request.POST['from'] == 'json':
            bucket_name = request.POST['bucket_name']
            for data in request.POST.getlist('list_data'):
                amazon_bucket.delete_file(bucket_name, data + '.json')
        elif request.POST['from'] == 'form':
            bucket_name = request.POST['bucket_name']
            file_json = { "Admobnumb": request.POST['Admobnumb'],
                "Version": request.POST['Version'],
                "AppId" : request.POST['AppId'],
                "BannerId": request.POST['BannerId'],
                "InterstitialAdId": request.POST['InterstitialAdId'],
                "RewardedAdId": request.POST['RewardedAdId'],
                "NativeAdId": request.POST['NativeAdId']
            }
            amazon_bucket.add_new_json(bucket_name, file_json)
        elif request.POST['from'] == 'change':
            key = request.POST['name']
            bucket_name = request.POST['bucket_name']
            file_json = { "Admobnumb": request.POST['Admobnumb'],
                "Version": request.POST['Version'],
                "AppId" : request.POST['AppId'],
                "BannerId": request.POST['BannerId'],
                "InterstitialAdId": request.POST['InterstitialAdId'],
                "RewardedAdId": request.POST['RewardedAdId'],
                "NativeAdId": request.POST['NativeAdId']
            }
            amazon_bucket.update_json(bucket_name, file_json, key)
    
    data, region = amazon_bucket.get_json(bucket_name)
    return render(request, "json.html", {"current_sidebar": current_sidebar, 
    "data": data, "bucket": bucket_name, "names": amazon_bucket.get_buckets(), 
    "region": region})

def form_json(request):
    json = json_data.Data('json/data.json')
    amazon_bucket = amazon_boto3.Amazon(json.get_data())
    current_sidebar = ''
    bucket_name = ''
    if request.method == "GET":
        if not request.GET.get('bucket') == None:
            bucket_name = request.GET.get('bucket')
        if not request.GET.get('key') == None:
            data = amazon_bucket.get_data_from_json(bucket_name, f"{request.GET.get('key')}.json")
            return render(request, "form_json_change.html", {"current_sidebar": current_sidebar, 
            "bucket_name": bucket_name, "names": amazon_bucket.get_buckets(), 
            "data": data, "file_name": request.GET.get('key')})
    return render(request, "form_json.html", {"current_sidebar": current_sidebar, 
        "bucket_name": bucket_name, "names": amazon_bucket.get_buckets()})

def form_bucket(request):
    json = json_data.Data('json/data.json')
    amazon_bucket = amazon_boto3.Amazon(json.get_data())
    current_sidebar = ''
    return render(request, "form_bucket.html", {"current_sidebar": current_sidebar, 
    "names": amazon_bucket.get_buckets()})

def settings(request):
    json = json_data.Data('json/data.json')
    amazon_bucket = amazon_boto3.Amazon(json.get_data())
    current_sidebar = ''
    if request.method == "POST":
        json.set_data(
            request.POST['aws_access_key_id'],
            request.POST['aws_secret_access_key']
        )
    names = []
    try:
        names = amazon_bucket.get_buckets_data()
    except:
        pass
    return render(request, "settings.html", {"current_sidebar": current_sidebar, 
    "names": names, "data": json.get_data()})