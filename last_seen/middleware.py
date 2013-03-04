

from models import user_seen


class LastSeenMiddleWare(object):

    def process_request(request):
        if request.user.is_autheticated():
            user_seen(request.user)

        return None
