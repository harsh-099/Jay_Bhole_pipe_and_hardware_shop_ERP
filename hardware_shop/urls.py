from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include


urlpatterns = [

path(
    "",
    include("accounts.urls")
),
    path('admin/', admin.site.urls),

    path('', include('dashboard.urls')),

    path('products/', include('products.urls')),

    path('customers/', include('customers.urls')),

    path('billing/', include('billing.urls')),

    path('suppliers/', include('suppliers.urls')),

    path('purchases/', include('purchases.urls')),

    path('expenses/', include('expenses.urls')),

    path('reports/', include('reports.urls')),

    

    path(
        'inventory/',
        include('inventory.urls')
    ),

    path(
        'backup/',
        include('backup.urls')
    ),
    path(
    'sale-return/',
    include('salesreturn.urls')
),
    path(
        'purchase-return/',
        include('purchasereturn.urls')
    ),
    path(
    "shopsettings/",
    include("shopsettings.urls")
),
path(
    "quotation/",
    include("quotation.urls")
),
path(
    "purchase-order/",
    include("purchaseorder.urls")
),

path(
    "activity-log/",
    include("activitylog.urls")
),

   path(
    "search/",
    include("globalsearch.urls")
),

]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)