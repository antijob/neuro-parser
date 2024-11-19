from django.contrib import admin


class DownvoteFilter(admin.SimpleListFilter):
    title = "Минимальное количество downvote"
    parameter_name = "downvote"

    def lookups(self, request, model_admin):
        return [
            ("0", "0 downvotes"),
            ("1", "1 и более"),
            ("2", "2 и более"),
            ("5", "5 и более"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(downvote=0)
        elif self.value():
            return queryset.filter(downvote__gte=int(self.value()))
        return queryset
