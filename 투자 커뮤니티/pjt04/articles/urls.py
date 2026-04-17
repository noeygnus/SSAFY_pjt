from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:asset_id>/', views.asset_board, name='asset_board'),
    path('<str:asset_id>/create/', views.create, name='create'),
    path('<str:asset_id>/<int:article_pk>/', views.detail, name='detail'),
    path('<str:asset_id>/<int:article_pk>/update/', views.update, name='update'),
    path('<str:asset_id>/<int:article_pk>/delete/', views.delete, name='delete'),
]