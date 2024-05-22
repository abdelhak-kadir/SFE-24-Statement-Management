from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('',views.Releve_Bank,name="bank1"),
    path('fil/', views.Filter_Releves_By_Date, name='filter_releves_by_date'),
    path('inv', views.invoice , name='inv' ),
    path('upload', views.upload_pdf_form, name='upload_pdf_form'),
    path('save_match/', views.save_match, name='save_match'),
    path('view/', views.view_matches, name='view_matches'),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
