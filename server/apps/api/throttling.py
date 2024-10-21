from rest_framework.throttling import UserRateThrottle


class StaffUserRateThrottle(UserRateThrottle):
    scope = "staff_user"

    def allow_request(self, request, view):
        # Проверяем, является ли пользователь администратором (is_staff)
        if request.user.is_staff:
            self.scope = "staff_user"
        else:
            return True  # Позволяем другим throttling-классам обрабатывать запросы
        return super().allow_request(request, view)


class RegularUserRateThrottle(UserRateThrottle):
    scope = "regular_user"

    def allow_request(self, request, view):
        # Ограничиваем только для обычных пользователей (не администраторов)
        if not request.user.is_staff:
            self.scope = "regular_user"
        else:
            return True  # Позволяем другим throttling-классам обрабатывать запросы
        return super().allow_request(request, view)
