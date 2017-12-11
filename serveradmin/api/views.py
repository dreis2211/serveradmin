from operator import itemgetter
try:
    import simplejson as json
except ImportError:
    import json

from django.template.response import TemplateResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.admindocs.utils import trim_docstring, parse_docstring

from adminapi.filters import BaseFilter, FilterValueError
from adminapi.request import json_encode_extra
from serveradmin.api import ApiError, AVAILABLE_API_FUNCTIONS
from serveradmin.api.decorators import api_view
from serveradmin.api.utils import build_function_description
from serveradmin.dataset import Query
from serveradmin.dataset.commit import commit_changes
from serveradmin.dataset.create import create_server


class StringEncoder(object):
    def loads(self, x):
        return x

    def dumps(self, x):
        return x

    def load(self, file):
        return file.read()

    def dump(self, val, file):
        return file.write(val)


@login_required
def doc_functions(request):
    group_list = []
    for group_name, functions in AVAILABLE_API_FUNCTIONS.items():
        function_list = []
        for name, function in functions.items():
            heading, body, metadata = parse_docstring(function.__doc__)
            body = trim_docstring(body)
            function_list.append({
                'name': name,
                'description': build_function_description(function),
                'docstring': trim_docstring(
                    '{0}\n\n{1}'.format(heading, body)
                ),
            })
        function_list.sort(key=itemgetter('name'))

        group_list.append({
            'name': group_name,
            'function_list': function_list
        })
    group_list.sort(key=itemgetter('name'))
    return TemplateResponse(request, 'api/list_functions.html', {
        'group_list': group_list
    })


@api_view
def echo(request, app, data):
    return data


# api_view decorator is used after setting an attribute on this function
def dataset_query(request, app, data):
    if not all(x in data for x in ['filters', 'restrict']):
        return {
            'status': 'error',
            'type': 'ValueError',
            'message': 'Invalid query object',
        }

    try:
        if not isinstance(data['filters'], dict):
            raise ValidationError('Filters must be a dictionary')
        filters = {}
        for attr, filter_obj in data['filters'].items():
            filters[attr] = BaseFilter.deserialize(filter_obj)

        query = Query(filters=filters)
        if data['restrict']:
            query.restrict(*data['restrict'])
        if data.get('order_by'):
            query.order_by(*data['order_by'])

        return json.dumps({
            'status': 'success',
            'result': query.get_results(),
        }, default=json_encode_extra)
    except (FilterValueError, ValidationError) as error:
        return json.dumps({
            'status': 'error',
            'type': 'ValueError',
            'message': str(error),
        })


dataset_query.encode_json = False
dataset_query = api_view(dataset_query)


@api_view
def dataset_commit(request, app, data):
    try:
        if 'changes' not in data or 'deleted' not in data:
            raise ValueError('Invalid changes')

        skip_validation = bool(data.get('skip_validation', False))
        force_changes = bool(data.get('force_changes', False))

        # Convert keys back to integers (json doesn't handle integer keys)
        changes = {}
        for server_id, change in data['changes'].items():
            changes[int(server_id)] = change

        commit = {'deleted': data['deleted'], 'changes': changes}
        commit_changes(commit, skip_validation, force_changes, app=app)

        return {
            'status': 'success',
        }
    except (
        ValueError,     # TODO Stop expecting them
        ValidationError,
    ) as error:
        return {
            'status': 'error',
            'type': error.__class__.__name__,
            'message': str(error),
        }


@api_view
def dataset_create(request, app, data):
    try:
        required = [
            'attributes',
            'skip_validation',
            'fill_defaults',
            'fill_defaults_all',
        ]
        if not all(key in data for key in required):
            raise ValueError('Invalid create request')
        if not isinstance(data['attributes'], dict):
            raise ValueError('Attributes must be a dictionary')

        create_server(
            data['attributes'],
            data['skip_validation'],
            data['fill_defaults'],
            data['fill_defaults_all'],
            app=app,
        )

        return {
            'status': 'success',
            'result': Query(filters={
                'hostname': data['attributes']['hostname']
            }).get_results(),
        }
    except ValidationError as error:
        return {
            'status': 'error',
            'type': error.__class__.__name__,
            'message': str(error),
        }


@api_view
def api_call(request, app, data):
    try:
        if not all(x in data for x in ('group', 'name', 'args', 'kwargs')):
            raise ValueError('Invalid API call')

        allowed_methods = app.allowed_methods.splitlines()
        method_name = u'{0}.{1}'.format(data['group'], data['name'])
        if not app.superuser and method_name not in allowed_methods:
            raise PermissionDenied(
                'Method {0} not allowed'.format(method_name)
            )

        try:
            fn = AVAILABLE_API_FUNCTIONS[data['group']][data['name']]
        except KeyError:
            raise ValueError('No such function')

        retval = fn(*data['args'], **data['kwargs'])
        return {
            'status': 'success',
            'retval': retval,
        }

    except (ValueError, TypeError, ApiError) as error:
        return {
            'status': 'error',
            'type': error.__class__.__name__,
            'message': str(error),
        }
