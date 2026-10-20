from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

SOURCE_ORDERING_FIELDS = ["url", "is_active"]
ARTICLE_ORDERING_FIELDS = ["create_date", "publication_date", "title"]
INCIDENT_ORDERING_FIELDS = ["create_date", "update_date", "status"]


class StrictOrderingFilter(OrderingFilter):
    """`order_by` that only accepts the fields a view explicitly allows.

    Unlike the stock OrderingFilter, an unknown field is an error instead of
    being silently dropped, and a view without `ordering_fields` allows none.
    A view may override the list per action with `action_ordering_fields`.
    """

    ordering_param = "order_by"

    def get_valid_fields(self, queryset, view, context={}):
        per_action = getattr(view, "action_ordering_fields", {})
        fields = per_action.get(getattr(view, "action", None))
        if fields is None:
            fields = getattr(view, "ordering_fields", None) or []
        return [(field, field) for field in fields]

    def get_ordering(self, request, queryset, view):
        value = request.query_params.get(self.ordering_param)
        if value:
            allowed = {f for f, _ in self.get_valid_fields(queryset, view)}
            requested = [p.strip() for p in value.split(",") if p.strip()]
            if any(p.lstrip("-") not in allowed for p in requested):
                raise ValidationError(
                    {
                        self.ordering_param: "Allowed fields: "
                        + ", ".join(sorted(allowed))
                    }
                )
        return super().get_ordering(request, queryset, view)
