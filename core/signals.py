from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache
from django.dispatch import receiver

from .models import Profile


def get_client_ip(request):
    """ Get user ip. """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def on_user_loggedin(sender, user, request, **kwargs):
    """ Update user coordinates if they are empty. """
    if user.is_authenticated:
        # If there no user profile - create it.
        profile, _ = Profile.objects.get_or_create(user=user)

        ip = get_client_ip(request)
        if ip and ip != '127.0.0.1' and not all([profile.lon, profile.lat]):
            g = GeoIP2()
            profile.lon, profile.lat = g.lon_lat(ip)
            profile.save()


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    """ Update user online status. """
    user = kwargs.get('user')
    if user.is_authenticated:
        cache.delete('seen_{}'.format(user.username))
