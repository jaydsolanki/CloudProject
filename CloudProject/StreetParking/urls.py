from django.conf.urls import url
from . import views

urlpatterns = {
    url('^$', views.index, name="home"),
    url('^collect_data/', views.collect_data, name="collect_data"),
}
