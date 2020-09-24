import datetime

from django.core.cache import cache
from django.conf import settings


def active_user_middleware(get_response):

    def middleware(request):
        """ Update user online status. """
        if request.user.is_authenticated:
            now = datetime.datetime.now()
            cache.set('seen_{}'.format(request.user.username), now,
                      settings.USER_ONLINE_TIMEOUT)

        return get_response(request)

    return middleware
