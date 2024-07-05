from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationListView, OrganisationDetailView, CreateOrganisationView

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('api/users/<uuid:user_id>', UserDetailView.as_view(), name='user-detail'),  # Changed 'pk' to 'user_id'
    path('api/organisations', OrganisationListView.as_view(), name='organisation-list'),
    path('api/organisations/<uuid:orgId>', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('api/organisations', CreateOrganisationView.as_view(), name='create-organisation')
]

