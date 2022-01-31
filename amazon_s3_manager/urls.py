from django.contrib import admin
from django.urls import path, include
import hashlib

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{hashlib.sha256("amazonBuckets".encode("utf8")).hexdigest()}/', include('buckets_manager.urls'))
]

# print()
# ffdccf0a7a1db7a7e8b3c453fa43c5e4bc67de6f2a3ba38430590ef773e5ca98