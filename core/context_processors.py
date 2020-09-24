from collections import namedtuple

from .models import Thread, UnreadThread


def unread_threads(request):
    """ Get unread messages. """
    threads = []
    unread_threads_counter = 0

    if request.user.is_authenticated:
        threads = UnreadThread.objects.filter(user=request.user)\
            .order_by('-date')\
            .values_list('thread__id', 'thread__name')[:10]

        # Rename fields (thread__id to id, thread__name to name).
        threads = [
            namedtuple('Row', ('id', 'name'))(id=thread[0], name=thread[1])
            for thread in threads
        ]

        unread_threads_counter = len(threads)

        # If there no unread_threads_counter - show last threads.
        if not threads:
            threads = Thread.objects.filter(
                users=request.user, last_message__isnull=False
            ).order_by('-last_message').values_list(
                'id', 'name', named=True
            )[:10]

    return {'threads': list(threads), 'unread_threads': unread_threads_counter}
