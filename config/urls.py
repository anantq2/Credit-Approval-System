from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/customers/', include('customers.urls')),
    path('api/loans/', include('loans.urls')),
]

# Conditional static and media serving for development (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Media serving (optional - remove if not using uploads; now with import fixed)
    urlpatterns += static('/media/', document_root=os.path.join(settings.BASE_DIR, 'media'))
