from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('releve/',views.Releve_Bank,name="bank1"),
    path('', views.Filter_Releves_By_Date, name='filter_releves_by_date'),
    path('inv', views.invoice , name='inv' ),
    path('upload', views.upload_pdf_form, name='upload_pdf_form'),
    path('save_match/', views.save_match, name='save_match'),
    path('view/', views.view_matches, name='view_matches'),
    path('update_sms/<int:pk>/', views.update_sms, name='update_sms'),
    path('update_releve/<int:pk>/', views.update_releve, name='update_releve'),
    path('update_inv/<int:pk>/', views.update_inv, name='update_inv'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
