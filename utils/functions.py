from django.db.models.query_utils import Q
from accounts.models import User
import itertools
import logging
import re

from django.db.models.query_utils import Q

from django.contrib.admin.utils import NestedObjects
from django.db import router

from management.models import Module

from MultiTenantSAML import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


from accounts.models import User
from tenants.models import Tenant


logger = logging.getLogger(__name__)


def related_objects(obj):
    """ Return a generator to the objects that would be deleted if we delete "obj" (excluding obj) """

    collector = NestedObjects(using=router.db_for_write(obj))
    collector.collect([obj])

    def flatten(elem):
        if isinstance(elem, list):
            return itertools.chain.from_iterable(map(flatten, elem))
        elif obj != elem:
            return (elem,)
        return ()

    return flatten(collector.nested())


def get_query_filter(query_string, search_fields, excluded_columns=[], model=None):
    '''
    Returns a query, that is a combination of Q objects.
    That combination aims to search keywords within a model by testing the given search fields.
    '''
    from django.core.exceptions import FieldDoesNotExist
    query = None  # Query to search for every search term
    q = None
    exclude_fields = ["", "options", "actions", "action"]
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            # Excluding the created_by and updated_by in search

            if field_name not in excluded_columns and field_name not in exclude_fields:
                # check model is defined or not
                if model:
                    try:
                        field = model._meta.get_field(field_name)
                    except FieldDoesNotExist as field_not_exist:
                        # name is probably a lookup or transform such as __contains
                        break

                    if hasattr(field, 'related_model'):
                        # field is a relation
                        releated_model = field.related_model
                        if releated_model:
                            all_fields = releated_model._meta.get_fields()
                            for a_field in all_fields:
                                metaOfAField = a_field.related_model

                                if a_field.get_internal_type() != 'JSONField':
                                    # logger.info(field.name)

                                    # logger.info(a_field.name)
                                    # logger.info(term)

                                    if metaOfAField is None:
                                        if q is None:
                                            q = Q(
                                                **{"%s__%s__icontains" % (field.name, a_field.name): term})
                                        else:
                                            q |= Q(
                                                **{"%s__%s__icontains" % (field.name, a_field.name): term})

                            if or_query is None and q is not None:
                                or_query = q
                            else:
                                or_query = or_query | q
                            continue
                    else:
                        # field is not a relation, any name that follows is
                        # probably a lookup or transform
                        break
                # preparing the query
                q = Q(**{"%s__iregex" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            elif field_name == 'jdoc':
                model_name = model.__name__.lower()
                content_type = ContentType.objects.get(model=model_name)
                module_instance = Module.objects.get(content_type=content_type)
                # custom_fields = CustomFields.objects.filter(
                #     module=module_instance)
                qdic = {}
                # for field in custom_fields:
                #     qdic[field.identifier] = term
                if qdic:
                    # preparing the query
                    q = Q(**{"%s__json_contains" % field_name: qdic})
                    if or_query is None:
                        or_query = q
                    else:
                        or_query = or_query | q
                else:
                    continue
            else:
                continue
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.\n
        Example:
            >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            Output:
                ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def clean_filter_dict(filter_set):
    """
    Clean the dictionary for before sending to queryset filter
    """
    return {
        k: v
        for k, v in filter_set.items()
        if not "columns" in k
        and not "order[" in k
        and not "draw" in k
        and not "search[" in k
        and not "length" in k
    }

def get_recepients_from_model(model, module_record_id):
    fields = model._meta.get_fields()
    record = model.objects.get(id=module_record_id)
    recipeints = []
    for field in fields:
        if field.related_model is User:
            f = (str(field)).split(".")[2]
            if field.many_to_one:
                user = getattr(record, f)
                if user:
                    recipeints.append(user)
            elif field.many_to_many:
                users = getattr(record, f)
                for user in users.all():
                    if user:
                        recipeints.append(user)
    return recipeints

def get_details_for_notification(slug):
    try:
        details = {}
        module = Module.objects.get(slug=slug)
        app_label = module.content_type.app_label
        model_name = module.content_type.model
        details = {
            "module": slug,
            "app_label": app_label,
            "model_name": model_name,
            "flag": False,
        }
        return details
    except:
        logger.exception("Module matching query doesn't exist with the slug %s", slug)

def gen_object_id(model_instance):
    """
    Generate object id
    """
    import uuid

    obj_id = uuid.uuid4()
    count = model_instance.objects.filter(object_id=obj_id).count()
    if count:
        gen_object_id(model_instance)
    else:
        return obj_id
def prepare_django_request(request):
    path_info = request.META['PATH_INFO']

    result = {
        'https': settings.SECURE_SAML,
        'http_host': request.META['HTTP_HOST'],
        'script_name': path_info,
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return result

def extract_claims(attributes):
    claim_keys = {
        '/displayname':'full_name',
        '/givenname':'first_name',
        '/surname':'last_name',
        '/emailaddress':'email'
    }
    claims = {}
    for key,value in claim_keys.items():
        for akey,avalue in attributes.items():
            if key in akey:
                claims[value] = avalue[0]
                break
    return claims

def hostname_from_request(request):
    return request.get_host().split(':')[0].lower()


def tenant_from_request(request):
    hostname = hostname_from_request(request)
    subdomain_prefix = hostname.split('.')[0]
    if subdomain_prefix == 'multitenant':
        subdomain_prefix='master'
    return Tenant.objects.filter(subdomain_prefix=subdomain_prefix).first()

def tenant_db_from_request(request):
    hostname = hostname_from_request(request)
    subdomain_prefix = hostname.split('.')[0]
    return Tenant.objects.filter(subdomain_prefix=subdomain_prefix).first().db_name