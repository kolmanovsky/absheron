from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('texts/', views.text_list, name='text_list'),
    path('images/', views.image_list, name='image_list'),
    path('texts/<int:pk>/', views.text_detail, name='text_detail'),
    path('images/<int:pk>/', views.image_detail, name='image_detail'),

    # дерево (любой вложенный путь, слэшем заканчивается необязательно)
    re_path(r'^tree/(?P<path>.*)$', views.node_by_path, name='node_by_path'),
]