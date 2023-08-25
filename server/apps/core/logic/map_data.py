from django.db.models import Count, F, Q, Sum

from server.apps.core.models import (MediaIncident, UserIncident, Tag)


def incident_table_data(incident_model, start, end, category, tag):
    """Return map data from one incident table."""

    incidents = (incident_model.objects
                 .filter(status__in=UserIncident.PUBLIC_STATUSES)
                 .filter(create_date__gte=start, create_date__lte=end))
    if tag:
        incidents = incidents.filter(tags__contains=[tag])
    if category:
        incidents = incidents.filter(incident_type=category)

    data = (incidents
            .values('region')
            .distinct()
            .annotate(total=Sum('count'))
            .annotate(prosecution=Sum('count', filter=Q(incident_type=1)))
            .annotate(administrative=Sum('count', filter=Q(incident_type=2)))
            .annotate(access=Sum('count', filter=Q(incident_type=6)))
            .annotate(regulation=Sum('count', filter=Q(incident_type=4)))
            .annotate(violence=Sum('count', filter=Q(incident_type=5)))
            .annotate(civil=Sum('count', filter=Q(incident_type=7)))
            .annotate(cyberattack=Sum('count', filter=Q(incident_type=8)))
            .annotate(business=Sum('count', filter=Q(incident_type=9)))
            .annotate(shutdown=Sum('count', filter=Q(incident_type=10)))
            .annotate(other=Sum('count', filter=Q(incident_type=0)))
            .values('region', 'total', 'other', 'prosecution',
                    'administrative', 'violence', 'civil', 'cyberattack',
                    'access', 'regulation', 'business', 'shutdown'))
    tags = Tag.objects.filter(is_active=True)
    annotations = {}
    for tag in tags:
        annotations[tag.name] = Sum('count', filter=Q(tags__contains=[tag.name]))
    data = data.annotate(**annotations)
    return data


def incident_map_data(start, end, category, tag):
    media_map_data = incident_table_data(MediaIncident, start, end, category, tag)
    user_map_data = incident_table_data(UserIncident, start, end, category, tag)
    united_map_data = media_map_data.union(user_map_data)
    for region_data in united_map_data:
        region_data['region'] = region_data['region'].replace('RU-', '').replace('UA-', '')
    return list(united_map_data)

def chart_field_value(form_data, chart_field):
    if not form_data:
        return None
    for field in form_data:
        if field['name'] == chart_field:
            if 'userData' in field:
                return field['userData'][0]
            else:
                return "0"
