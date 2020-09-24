from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import (Profile, Thread, UnreadThread, Message, FriendshipRequest,
                     Friend)

User = get_user_model()


class BaseModelAdmin(admin.ModelAdmin):
    list_select_related = ['user']

    def get_changelist_instance(self, request):
        changelist = super().get_changelist_instance(request)

        # Get all related user usernames and send to the cache,
        # we will use it later in __str__ method to improve performance.
        uids = {instance.user_id for instance in changelist.result_list}
        elements = User.objects.filter(pk__in=uids)\
            .values_list('pk', 'username')
        cache.set_many({
            'username_by_id_{}'.format(element[0]): element[1]
            for element in elements
        }, settings.USER_ONLINE_TIMEOUT)

        return changelist


class ProfileAdmin(BaseModelAdmin):
    readonly_fields = ('preview', 'location')
    search_fields = ('user__username',)


class ThreadAdmin(admin.ModelAdmin):
    list_filter = ('users__username',)
    readonly_fields = ('last_message', 'link_to_thread',)
    search_fields = ('users__username',)


class UnreadThreadAdmin(BaseModelAdmin):
    readonly_fields = ('date', 'link_to_thread',)
    search_fields = ('user__username',)


class MessageAdmin(BaseModelAdmin):
    list_filter = ('user__username', 'thread__name',)
    readonly_fields = ('date', 'link_to_thread',)
    search_fields = ('user__username', 'text',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(UnreadThread, UnreadThreadAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(FriendshipRequest)
admin.site.register(Friend)
