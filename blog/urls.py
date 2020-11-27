from django.urls import path
from . import views
from . feeds import LatestPostsFeed


app_name = 'blog'

urlpatterns = [
    # post views
    path('', views.post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',views.post_detail, name='post_detail'),
    path('<int:post_id>/share/',views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/',views.post_list, name='post_list_by_tag'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    #path('home/', views.post_home, name='post_home'),
    path('notifications/', views.notifications, name='notifications'),
    path('about_us/', views.post_about_us, name='post_about_us'),
]