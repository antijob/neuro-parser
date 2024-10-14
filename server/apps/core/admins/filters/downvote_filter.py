from django.contrib import admin


class DownvoteFilter(admin.SimpleListFilter):
    title = 'Минимальное количество downvote'
    parameter_name = 'downvote'

    def lookups(self, request, model_admin):
        return [
            ('1', 'Больше 1'),
            ('2', 'Больше 2'),
            ('5', 'Больше 5'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(downvote__gte=int(self.value()))
        return queryset
