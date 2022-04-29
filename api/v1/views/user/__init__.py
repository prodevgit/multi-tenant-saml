
import datetime
import logging

from django.db import connection

from accounts.models import Roles
from api.v1.views.user.functions import create_token
from api.v1.views.user.serializer import (LoginSerializer, TokenSerializer,
                                          UserListSerializer)
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.http import HttpResponseRedirect
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.filters import UserFilter
from utils.functions import (clean_filter_dict, extract_claims,
                             get_query_filter, prepare_django_request)

logger = logging.getLogger(__name__)
User = get_user_model()





class LoginView(GenericAPIView):

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = Token

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        if self.user.is_superuser == True:
            django_login(self.request,self.user,backend='django.contrib.auth.backends.ModelBackend')
        else:
            django_login(self.request, self.user,backend='accounts.backend.LDAPCustomBackend')

    def get_response_serializer(self):
        response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        self.token = create_token(self.token_model, self.user, self.serializer)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {'user': self.user, 'token': self.token}
            serializer = serializer_class(
                instance=data, context={'request': self.request}
            )
        else:
            serializer = serializer_class(
                instance=self.token, context={'request': self.request}
            )

        return serializer.data

    def post(self, request, *args, **kwargs):

        context = {}
        response = None
        self.request = request
        email = self.request.data.get('email')

        try:
            self.serializer = self.get_serializer(
                data=self.request.data, context={'request': request}
            )
            self.serializer.is_valid(raise_exception=True)
            self.login()
            user = authenticate(username=email, password=self.request.data['password'])
            max_age = 365 * 24 * 60 * 60  # one year

            expires = datetime.datetime.strftime(
                datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                "%a, %d-%b-%Y %H:%M:%S GMT",
            )
            request.session.set_expiry(float(max_age))

            data = self.get_response()

            data['message'] = "Login Successful"
            data['user_name'] = user.get_full_name()
            data['role'] = user.role.name
            response = Response(data, status=200)
        except Exception as error:
            logger.exception(
                "Exception while trying to connect with workspace. Error: {}".format(
                    error
                )
            )
            context['message'] = self.serializer.errors['non_field_errors'][0]
            # context['message'] = "There was an error with your E-Mail/Password combination. Please try again"
            response = Response(context, status=404)

        return response

class LoginSamlView(APIView):
    permission_classes = (AllowAny,)

    def get(self,request):
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, saml_settings)
        return Response({'url':auth.login()})

class SetSAMLTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self,request):
        req = prepare_django_request(request)
        
        auth = OneLogin_Saml2_Auth(req, saml_settings)
        auth.process_response()
        host_url = settings.HOST_URL
        try:
            department = settings.CLIENT_DEPARTMENT
            if department == 'IT Operations':
                path = f'it'
            elif department == 'Undersecretary Office':
                path = f'us'
        except:
            pass
        
        if auth.is_authenticated():

            claims = extract_claims(auth._attributes)
            try:
                user = User.objects.get(email=claims['email'])
            except User.DoesNotExist:
                role = Roles.objects.get(name='User')
                try:
                    default_entity = settings.CLIENT_DEPARTMENT
                    if default_entity == 'IT Operations':
                        default_entity = 'Support Services'
                except:
                    default_entity = 'Chairman Office'
                user = User.objects.create(
                    email=claims['email'],
                    first_name=claims['first_name'],
                    last_name=claims['last_name'],
                    full_name=claims['full_name'],
                    is_active=True,
                    username=claims['email'].split('@')[0],
                    role=role,
                    )
            token = Token.objects.filter(user=user).first()
            if token:
                token.delete()
            token = Token.objects.create(user=user)
            response={
                'key': token.key,
                'message': 'Login Successful',
                'user_name': user.full_name,
                'role': user.role.name
            }
            
            return HttpResponseRedirect(f'{host_url}/validate?key={token.key}&user_name={user.full_name}&role={user.role.name}')
        
        logger.info(auth.__dict__)
        return HttpResponseRedirect(f'{host_url}/login')

class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.
    Accepts/Returns nothing.
    """

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass

        django_logout(request)

        response = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )

        response.delete_cookie("auth")

        return response



class AllUserListView(ListAPIView):
    """
    List of all User Records
    """
    serializer_class = UserListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = User.objects.filter(is_superuser=False).only('id','first_name','username', 'last_name','email','entity', 'role').order_by('-created_date')
        # get the query string
        if "q" in self.request.GET:
            query = self.request.GET.get("q").strip()
            # get the column number for column based search
            search_column = self.request.GET.get(u'search_column', None)
            # list of tablecolumns
            columns = ['id','first_name','username', 'last_name','email','entity', 'role']

            self.list_of_columns = columns
            # converting tp integer if we got string
            if search_column:
                search_column = int(search_column)

            if query:
                # generating the query
                search_query = get_query_filter(
                    query, columns, ['jdoc'], User)
                # filtering the search results
                queryset_list = queryset_list.filter(search_query)


        filtered_dict = clean_filter_dict(self.request.GET.dict())

        filter_query = UserFilter(
            filtered_dict, queryset=queryset_list)

        return filter_query.qs
