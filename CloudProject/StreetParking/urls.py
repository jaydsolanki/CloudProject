from django.conf.urls import url
from . import views

urlpatterns = {
    url('^$', views.index, name="home"),
    url('^collect_data/', views.collect_data, name="collect_data"),
    url('^add_parking_data/', views.add_parking_data, name="add_parking_data"),
    url('^remove_parking_data/', views.remove_parking_data, name="remove_parking_data"),
}
