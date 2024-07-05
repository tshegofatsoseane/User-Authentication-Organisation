from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Moved out of the method

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            org_name = f"{user.first_name}'s Organisation"
            org = Organisation.objects.create(name=org_name)
            org.users.add(user)
            org.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'errors': serializer.errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': 401
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.pk)

class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        org_id = self.kwargs['orgId']
        return user.organisations.filter(pk=org_id)

class CreateOrganisationView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])
