from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.ocr_image_upload, name='ocr_image_upload'),
    path('result/<str:task_id>/', views.ocr_result, name='ocr_result'),
]
