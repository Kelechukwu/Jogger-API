import datetime

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView

from api.models import User, Jog
from django.db.utils import IntegrityError
from .serializers import SignUpSerializer, UserSerializer, JogSerializer
from .permissions import IsOwnerOrAdmin, CanCRUDUsers, IsUserOwner, IsAdminRole
from api.forms import SignUpValidationForm
from django.http import JsonResponse
from django.db.models import Q

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from api.helpers import parse_query_string
from django.db.models import Sum

from django.utils import timezone

from django.shortcuts import get_object_or_404


class SignUp(APIView):
    def post(self, request):
        """Create an account"""

        form = SignUpSerializer(data = request.data)
        if not form.is_valid():
            return JsonResponse(
                form.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            user = User.objects.create_user(
                request.data["email"], request.data["password"])
            refresh = RefreshToken.for_user(user)
            return JsonResponse(
                {'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'id': str(user.id),
                    },
                status=status.HTTP_201_CREATED,
            )

class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanCRUDUsers, IsUserOwner]

    # queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset_list = User.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            parsed_query = parse_query_string(query)
            queryset_list = queryset_list.filter(eval(parsed_query)).order_by('-id')
        return queryset_list

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated, CanCRUDUsers]
        else:
            permission_classes = [IsAuthenticated, IsUserOwner]
        return [permission() for permission in permission_classes]

    def create(self, request):
        response = {
            'message': 'Create function is not offered in this path. Use /signup'}
        return JsonResponse(response, status=status.HTTP_403_FORBIDDEN)


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin, )
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        This view should return a list of all the Jogs
        for the currently authenticated user.
        """
        user = self.request.user
        return User.objects.filter(pk=user.id)


class JogsViewSet(viewsets.ModelViewSet):
    """
    This view allows only admin users to perform CRUD on Jogs
    """
    permission_classes = (IsAuthenticated, IsAdminRole)

    serializer_class = JogSerializer

    def get_queryset(self):
        queryset_list = Jog.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            parsed_query = parse_query_string(query)
            queryset_list = queryset_list.filter(eval(parsed_query)).order_by('-id')
        return queryset_list


class UserJogsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin, )
    serializer_class = JogSerializer

    def get_queryset(self):
        user = self.request.user
        queryset_list = Jog.objects.filter(user=user).order_by('-id')
        query = self.request.GET.get('q')
        if query:
            parsed_query = parse_query_string(query)
            queryset_list = queryset_list.filter(eval(parsed_query)).order_by('-id')
        return queryset_list

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class UserWeeklyReportView(APIView):
    permission_classes = (IsAuthenticated, IsUserOwner)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        date = self.request.query_params.get('date')
        date = datetime.datetime.strptime(
            date, "%Y-%m-%d") if date else timezone.now()

        user = User.objects.get(pk=user_id)
        self.check_object_permissions(self.request, user)

        self.start_of_week = (
            date - datetime.timedelta(days=date.weekday())).strftime('%Y-%m-%d')
        self.end_of_week = (
            date + datetime.timedelta(days=6-date.weekday())).strftime('%Y-%m-%d')

        queryset_list = Jog.objects.filter(
            user=str(user_id), date__gte=self.start_of_week, date__lte=self.end_of_week)

        return queryset_list

    def get(self, request, user_id):
        """Get Weekly report."""

        avg_speed, avg_distance = self.get_weekly_report(self.get_queryset())

        if avg_speed == -1:
            return JsonResponse(
                {"error": "Cannot calculate average speed or distance due to ZeroDivisionError"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return JsonResponse(
            {
                "start_of_week": self.start_of_week,
                "end_of_week": self.end_of_week,
                "average_speed": avg_speed,
                "average_distance": avg_distance,
            },
            status=status.HTTP_200_OK,
        )

    def get_weekly_report(self, jog_query_set):
        record_count = jog_query_set.count()

        if record_count == 0:
            return (0, 0)

        total_distance_dict = jog_query_set.aggregate(Sum('distance'))
        total_time_dict = jog_query_set.aggregate(Sum('time'))

        try:
            avg_speed = float(
                total_distance_dict['distance__sum']) / total_time_dict['time__sum']
            avg_distance = float(
                total_distance_dict['distance__sum']) / record_count
            return (round(avg_speed, 2), round(avg_distance, 2))
        except ZeroDivisionError:
            return (-1, -1)
