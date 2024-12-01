from django.urls import path

from tasks import views

app_name = 'tasks'

urlpatterns = [
    path('', views.home, name='home'),
    path('listing', views.listing, name='listing'),
    path('add', views.add, name='add'),
    path('<int:task_pk>/change', views.change, name='change'),
    path('<int:task_pk>/delete_complete', views.delete_complete, name='delete_complete'),
    
    path('<int:task_pk>/material/listing', views.task_material_listing, name='task_material_listing'),
    path('<int:task_pk>/material/add', views.task_material_add, name='task_material_add'),
    path('material/<int:task_material_pk>/change', views.task_material_change, name='task_material_change'),
    path('material/<int:task_material_pk>/delete_complete', views.task_material_delete_complete, name='task_material_delete_complete'),
    
]