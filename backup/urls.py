from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.backup_database,
        name='backup_database'
    ),
    path(
    'restore/',
    views.restore_database,
    name='restore_database'
),

]