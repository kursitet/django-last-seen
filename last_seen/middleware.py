from typing import Callable

from django.http import HttpRequest, HttpResponse

from .models import user_seen


class LastSeenMiddleware(object):
    """Middleware to set timestamp when a user has been last seen."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            user_seen(request.user)

        return self.get_response(request)
