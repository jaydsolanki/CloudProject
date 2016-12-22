from django.conf.urls import url
from . import views

urlpatterns = {
    url('^$', views.index, name="home"),
    url('^collect_data/', views.collect_data, name="collect_data"),
    url('^add_parking_data/', views.add_parking_data, name="add_parking_data"),
    url('^remove_parking_data/', views.remove_parking_data, name="remove_parking_data"),
    url('^user_testing', views.user_testing, name="user_testing"),
    ################# mobile App Services #####################
    url('^check_username/', views.check_username, name="check_username"),
    url('^registration/', views.registration, name="registration"),
    url('^login/', views.login, name="login"),
    url('^logout/', views.logout, name="logout"),
    url('^get_parking_locations/', views.get_parking_locations, name="get_parking_locations"),
    url('^get_parking_locations_kafka/', views.get_parking_locations_kafka, name="get_parking_locations_kafka"),
    url('^upload_profile_pic/', views.upload_profile_pic, name="upload_profile_pic"),
    url('^add_home_coordinates/', views.add_home_coordinates, name="add_home_coordinates"),
    url('^add_office_coordinates/', views.add_office_coordinates, name="add_office_coordinates"),
    url('^add_office_timing/', views.add_office_timing, name="add_office_timing"),
    url('^park_vehicle/', views.park_vehicle, name="park_vehicle"),
    url('^unpark_vehicle_by_user/', views.unpark_vehicle_by_user, name="unpark_vehicle_by_user"),
    url('^user_help_request/', views.user_help_request, name="user_help_request"),
    url('^sns_request', views.sns_request, name="sns_request")
}
