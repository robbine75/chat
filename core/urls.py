from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from .views import (about_page, log_in, log_out, sign_up, user_list, user_map,
                    ThreadView, call_view, ProfileView)


app_name = "Chat"

urlpatterns = [
    path('about', about_page, name='about_page'),
    path('login', log_in, name='login'),
    path('logout', log_out, name='logout'),
    path('signup', sign_up, name='signup'),
    path('', user_list, name='user_list'),
    path('users', user_map, name='users_map'),
    path('user/<str:username>', ProfileView.as_view(), name='user'),
    path('chat/<str:username>', ThreadView.as_view(), name='chat'),
    path('thread/<int:thread_id>', ThreadView.as_view(), name='thread'),
    path('call/<str:username>', call_view, name='call'),
]
admin.site.site_header = _('Chat administration')

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
