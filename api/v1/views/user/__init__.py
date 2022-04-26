
import logging

from accounts.models import Roles
from api.v1.views.user.serializer import UserListSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.filters import UserFilter
from utils.functions import (clean_filter_dict, extract_claims,
                             get_query_filter, prepare_django_request)

logger = logging.getLogger(__name__)
User = get_user_model()

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
