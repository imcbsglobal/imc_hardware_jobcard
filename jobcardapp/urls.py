from django.urls import path
from . import views



urlpatterns = [
    path('', views.jobcard_list, name='jobcard_list'),
    path('create/', views.jobcard_create, name='jobcard_create'),
    path('<int:pk>/edit/', views.jobcard_edit, name='jobcard_edit'),
    path('<int:pk>/delete/', views.jobcard_delete, name='jobcard_delete'),
]



