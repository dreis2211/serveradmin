from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings

from adminapi.utils.parse import parse_query
from serveradmin.graphite.models import GraphGroup
from serveradmin.dataset import query, filters, DatasetError
from serveradmin.serverdb.models import AttributeValue, ServerType, Segment
from serveradmin.servermonitor.getinfo import get_information

@ensure_csrf_cookie
def index(request):
    """Index page of the Graphite tab
    """

    term = request.GET.get('term', request.session.get('term', ''))

    template_info = {
        'search_term': term,
        'segments': Segment.objects.order_by('segment'),
        'servertypes': ServerType.objects.order_by('name')
    }

    hostname_filter = set()
    matched_servers = set()
    if term:
        try:
            query_args = parse_query(term, filters.filter_classes)
            host_query = query(**query_args).restrict('hostname', 'xen_host')
            for host in host_query:
                matched_servers.add(host['hostname'])
                if 'xen_host' in host:
                    hostname_filter.add(host['xen_host'])
                else:
                    # If it's not guest, it might be a server, so we add it
                    hostname_filter.add(host['hostname'])
            understood = host_query.get_representation().as_code()
            request.session['term'] = term

            if not matched_servers:
                template_info.update({
                    'understood': understood,
                    'hosts': []
                })
                return TemplateResponse(request, 'servermonitor/index.html',
                        template_info)
        except (ValueError, DatasetError), e:
            template_info.update({
                'error': e.message
            })
            return TemplateResponse(request, 'servermonitor/index.html',
                    template_info)
    else:
        understood = query().get_representation().as_code() # It's lazy :-)

    hw_query_args = {'physical_server': True, 'cancelled': False}
    if hostname_filter:
        hw_query_args['hostname'] = filters.Any(*hostname_filter)

    periods = ('hourly', 'daily', 'yesterday')
    hardware = {}
    for hw_host in query(**hw_query_args).restrict('hostname', 'servertype'):
        host_data = {
                'hostname': hw_host['hostname'],
                'servertype': hw_host['servertype'],
                'image': '{url}graph_sprite/{hostname}.png'.format(
                        url=settings.MEDIA_URL,
                        hostname=hw_host['hostname']),
                'cpu': {},
                'io': {}
        }
        for period in periods:
            for what in ('io', 'cpu'):
                host_data[what][period] = None
        hardware[hw_host['hostname']] = host_data
    hostnames = hardware.keys()
    template_info.update(get_information(hostnames, hardware))

    # All of the graph groups marked as overview should have the same
    # structure, we will just get one of them for the table headers.
    group = GraphGroup.objects.filter(overview=True)[0]
    names = [unicode(t) + ' ' + unicode(v) for t in group.get_templates()
                                                 for v in group.get_variations()]
    offsets = [i * 120 for i in range(len(names))]

    template_info.update({
        'graph_names': names,
        'graph_offsets': offsets,
        'matched_servers': matched_servers,
        'understood': understood,
        'error': None
    })
    return TemplateResponse(request, 'graphite/index.html', template_info)

@login_required
@ensure_csrf_cookie
def graph_table(request, hostname):
    """Graph table page

    We will accept all GET parameters and pass them to Graphite.
    """

    custom_params = request.GET.urlencode()

    # For convenience we will create a dictionary of attributes and store
    # array of values in it.  They will be used to filter the graphs and
    # to format the URL parameters of the graphs.
    attribute_dict = {}
    for row in AttributeValue.objects.filter(server__hostname=hostname):
        if row.attrib.name not in attribute_dict:
            attribute_dict[row.attrib.name] = [row.value]
        else:
            attribute_dict[row.attrib.name].append(row.value)

    graph_table = []
    for group in GraphGroup.objects.all():
        if group.attrib.name not in attribute_dict:
            continue    # The server hasn't got this attribute at all.
        if group.attrib_value not in attribute_dict[group.attrib.name]:
            continue    # The server hasn't got this attribute value.

        if custom_params == '':
            graph_table += group.graph_table(hostname, attribute_dict)
        else:
            column = group.graph_column(hostname, attribute_dict,
                                        custom_params)
            graph_table += [(k, [('Custom', v)]) for k, v in column]

    return TemplateResponse(request, 'graphite/graph_table.html', {
        'hostname': hostname,
        'graph_table': graph_table,
        'is_ajax': request.is_ajax(),
        'base_template': 'empty.html' if request.is_ajax() else 'base.html',
        'link': request.get_full_path(),
        'from': request.GET.get('from', ''),
        'until': request.GET.get('until', ''),
    })

@login_required
def graph_popup(request):
    try:
        hostname = request.GET['hostname']
        graph = request.GET['graph']
    except KeyError:
        return HttpResponseBadRequest('You have to supply hostname and graph')

    # It would be more efficient to filter the groups on the database, but we
    # don't bother because they are unlikely to be more than a few graph
    # groups marked as overview.
    for graph_group in GraphGroup.objects.filter(overview=True):
        if hostname in graph_group.query_hostnames():
            table = graph_group.graph_table(hostname)
            image = [v2 for k1, v1 in table for k2, v2 in v1][int(graph)]

            return TemplateResponse(request, 'graphite/graph_popup.html', {
                'hostname': hostname,
                'graph': graph,
                'image': image
            })