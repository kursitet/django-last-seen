

from models import user_seen


class LastSeenMiddleWare(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            user_seen(request.user)

        return None
