from django.contrib import admin
from django.urls import path, include
import hashlib

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{hashlib.sha256("amazonBuckets".encode("utf8")).hexdigest()}/', include('buckets_manager.urls'))
]