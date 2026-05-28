from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(user_id=self.request.user.id).prefetch_related('logs').order_by('-created_at')
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.strip().lower() in {'1', 'true', 'yes', 'on'})
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        unread_count = Notification.objects.filter(user_id=request.user.id, is_read=False).count()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['unread_count'] = unread_count
            return response
        serializer = self.get_serializer(queryset, many=True)
        return Response({'unread_count': unread_count, 'results': serializer.data})

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        # Busca globalmente para devolver 403, no 404, si existe pero es de otro usuario.
        notification = get_object_or_404(Notification.objects.prefetch_related('logs'), pk=pk)
        notification = NotificationService.mark_read(actor=request.user, notification=notification)
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['patch'], url_path='read-all')
    def read_all(self, request):
        from django.utils import timezone
        updated = Notification.objects.filter(user_id=request.user.id, is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({'marked_as_read': updated})
