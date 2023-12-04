import datetime
import time

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from . import settings


class LastSeenManager(models.Manager):
    """Define a manager for LastSeen objects.

    Provides 2 utility methods.
    """

    def seen(self, user, module=settings.LAST_SEEN_DEFAULT_MODULE, site=None, force=False):
        """Mask an user last on database seen with optional module and site.

        If module not provided uses LAST_SEEN_DEFAULT_MODULE from settings.
        If site not provided uses current site.
        The last seen object is only updates is LAST_SEEN_INTERVAL seconds passed from last update or force=True.
        """
        if not site:
            site = Site.objects.get_current()
        args = {
            'user': user,
            'site': site,
            'module': module,
        }
        seen, created = self.get_or_create(**args)
        if created:
            return seen

        # If we get the object, see if we need to update
        limit = timezone.now() - \
            datetime.timedelta(seconds=settings.LAST_SEEN_INTERVAL)
        if seen.last_seen < limit or force:
            seen.last_seen = timezone.now()
            seen.save()

        return seen

    def when(self, user, module=None, site=None):
        args = {'user': user}
        if module:
            args['module'] = module
        if site:
            args['site'] = site
        return self.filter(**args).latest('last_seen').last_seen


class LastSeen(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.CharField(default=settings.LAST_SEEN_DEFAULT_MODULE, max_length=20)
    last_seen = models.DateTimeField(default=timezone.now)

    objects = LastSeenManager()

    class Meta:
        unique_together = (('user', 'site', 'module'),)
        ordering = ('-last_seen',)

    def __str__(self):
        return f'{self.user} on {self.last_seen}'


def get_cache_key(site, module: str, user):
    """Get cache database to cache last database write timestamp."""
    return f'last_seen:{site.id}:{module}:{user.pk}'


def user_seen(user, module: str = settings.LAST_SEEN_DEFAULT_MODULE, site=None):
    """Mask an user last seen on database if LAST_SEEN_INTERVAL seconds have passed from last database write.

    Uses optional module and site.

    If module not provided uses LAST_SEEN_DEFAULT_MODULE from settings.
    If site not provided uses current site.
    """
    if not site:
        site = Site.objects.get_current()
    cache_key = get_cache_key(site, module, user)
    # Compute limit to update DB
    limit = time.time() - settings.LAST_SEEN_INTERVAL
    seen = cache.get(cache_key)
    if not seen or seen < limit:
        # Mark the database and the cache, if interval is cleared force database write
        if seen == -1:
            LastSeen.objects.seen(user, module=module, site=site, force=True)
        else:
            LastSeen.objects.seen(user, module=module, site=site)
        timeout = settings.LAST_SEEN_INTERVAL
        cache.set(cache_key, time.time(), timeout)


def clear_interval(user):
    """Clear cached interval from last database write timestamp.

    Useful if you want to force a database write for an user
    """
    keys = {}
    for last_seen in LastSeen.objects.filter(user=user):
        cache_key = get_cache_key(last_seen.site, last_seen.module, user)
        keys[cache_key] = -1

    if keys:
        cache.set_many(keys)
