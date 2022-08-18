from server.apps.core.models import MediaIncident, UserIncident


def count_status(status):
    media_count = MediaIncident.objects.filter(status=status).count()
    user_count = UserIncident.objects.filter(status=status).count()
    return media_count + user_count


def count_unprocessed_userincidents():
    media_count = UserIncident.objects \
        .filter(status=UserIncident.UNPROCESSED) \
        .count()
    return media_count


def count_userincidents():
    media_count = UserIncident.objects.all().count()
    return media_count


def count_unprocessed_mediaincidents():
    media_count = MediaIncident.objects \
        .filter(status=MediaIncident.UNPROCESSED) \
        .count()
    return media_count


def count_mediaincidents():
    media_count = MediaIncident.objects.all().count()
    return media_count


def count_assigned_incidents(user):
    media_count = MediaIncident.objects \
        .filter(assigned_to=user, status__in=MediaIncident.ACTIVE_STATUSES) \
        .count()
    user_count = UserIncident.objects \
        .filter(assigned_to=user, status__in=UserIncident.ACTIVE_STATUSES) \
        .count()
    return media_count + user_count


def count_all():
    media_count = MediaIncident.objects.count()
    user_count = UserIncident.objects.count()
    return media_count + user_count
