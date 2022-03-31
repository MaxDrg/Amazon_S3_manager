from django.db import models

class buckets(models.Model):
    bucket_name = models.CharField("Название бакета", max_length=255, unique=True)
    region_name = models.CharField("Регион", max_length=255)
    created = models.CharField("Создан", max_length=40)

class json_files(models.Model):
    file_name = models.CharField("Название приложения", max_length=255)
    content = models.JSONField("Содержимое", max_length=255)
    last_update = models.CharField("Последнее обновление", max_length=40)
    bucket = models.ForeignKey(buckets, on_delete = models.CASCADE)

class logs(models.Model):
    operation = models.IntegerField("Operation's number", default=1)
    bucket_name = models.CharField("Bucket's name", max_length=255)
    file_name = models.CharField("File's name", max_length=255, null=True ,default=None)