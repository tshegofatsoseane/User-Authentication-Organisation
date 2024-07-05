from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from rest_framework.exceptions import ValidationError

class RegisterView(APIView):
    permission_classes = [AllowAny]

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
                    'user': {
                        'userId': str(user.user_id),
                        'firstName': user.first_name,
                        'lastName': user.last_name,
                        'email': user.email,
                        'phone': user.phone
                    }
                }
            }, status=status.HTTP_201_CREATED)
        
        errors = [{"field": key, "message": value[0]} for key, value in serializer.errors.items()]
        return Response({
            'status': 'Bad request',
            'message': 'Registration unsuccessful',
            'statusCode': 400,
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            user_data = {
                'userId': str(user.user_id),
                'firstName': user.first_name,
                'lastName': user.last_name,
                'email': user.email,
                'phone': user.phone
            }
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': user_data
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
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        user = User.objects.filter(user_id=user_id).first()
        
        if not user:
            return Response({
                "status": "error",
                "message": "No User matches the given query."
            }, status=status.HTTP_404_NOT_FOUND)

        if user == request.user or request.user.organisations.filter(users=user).exists():
            serializer = self.get_serializer(user)
            user_data = {
                "userId": str(user.user_id),
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "phone": user.phone
            }
            return Response({
                "status": "success",
                "message": "User retrieved successfully",
                "data": user_data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "You do not have permission to access this user's data."
        }, status=status.HTTP_403_FORBIDDEN)
    

class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Organisations retrieved successfully',
            'data': {
                'organisations': serializer.data
            }
        }, status=status.HTTP_200_OK)

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
