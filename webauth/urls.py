from django.urls import path

from . import views


urlpatterns = [
    path('auth/', views.KeyAuthenticate.as_view(), name='webauthn-auth'),
    path('keys/', views.KeyList.as_view(), name='key-list'),
    path('keys/add/', views.KeyCreate.as_view(), name='key-add'),
    path('keys/<int:pk>/', views.KeyDetail.as_view(), name='key-detail'),
    path('keys/<int:pk>/delete/', views.KeyDelete.as_view(), name='key-delete'),
]
