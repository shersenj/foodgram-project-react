from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from users.models import CustomUser, AuthorSubscription
from api.serializers import (
    CustomUserSerializer, SubscriptionShowSerializer, SubscriptionSerializer
    )
from api.permissions import AnonimOrAuthenticatedReadOnly
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet


class CustomUserViewSet(UserViewSet):
    """
    Класс представления для пользователей с дополнительными действиями.

    Методы:
    - `get_me`: Получить информацию о текущем
        пользователе или отредактировать её.
    - `get_subscribe`: Подписаться или отписаться от автора.
    - `get_subscriptions`: Получить список подписок пользователя.

    Атрибуты:
    - `queryset`: Запрос, возвращающий всех пользователей.
    - `serializer_class`: Сериализатор для пользователей.
    - `permission_classes`: Классы разрешений для доступа к методам.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AnonimOrAuthenticatedReadOnly,)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_me(self, request):
        """
        Получить информацию о текущем пользователе или отредактировать её.

        Если метод запроса - `GET`,
            возвращает информацию о текущем пользователе.

        Если метод запроса - `PATCH`,
            позволяет пользователю отредактировать свой профиль.
        В этом случае, передайте данные пользователя в теле запроса.

        """
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        """
        Подписаться или отписаться от автора.

        Если метод запроса - `POST`, создает подписку на указанного автора.

        Если метод запроса - `DELETE`, удаляет подписку на указанного автора.
        """
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'subscriber': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            AuthorSubscription, subscriber=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """
        Получить список подписок пользователя.

        Возвращает список авторов, на которых подписан текущий пользователь.
        """
        authors = CustomUser.objects.filter(author__subscriber=request.user)
        paginator = PageNumberPagination()
        result_pages = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = SubscriptionShowSerializer(
            result_pages, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)
