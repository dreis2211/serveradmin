# -*- coding: utf-8 -*-
from copy import deepcopy
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from adminapi.filters import Empty
from serveradmin.dataset import Query

datacenters = {
    'Süderstraße S198.1': {
        'name': 'af',
        'rowgroups': [
            [
                {
                    'row': 'A',
                    'columns': [
                        '01', '02', '03', '04', '05', '06', '07',
                        '08', '09', '10', '11', '12', '13', '14'
                    ],
                    'rowseparator': 'hot',
                },
            ],
            [
                {
                    'row': 'B',
                    'columns': [
                        '01', '02', '03', '04', '05', '06', '07',
                        '08', '09', '10', '11', '12', '13', '14'
                    ],
                    'rowseparator': 'hot',
                    'static': {
                        '07': 'Storage',
                    }

                },
            ],
            [
                {
                    'row': 'C',
                    'columns': [
                        '01', '02', '03', '04', '05', '06', '07',
                        '08', '09', '10', '11', '12', '13', '14'
                    ],
                    'rowseparator': 'hot',
                }
            ],
            [
                {
                    'row': 'D',
                    'columns': [
                        '01', '02', '03', '04', '05', '06', '07',
                        '08', '09', '10', '11', '12', '13', '14'
                    ],
                    'rowseparator': 'hot',
                    'static': {
                        '03': 'Work rack',
                    }

                }
            ],
            [
                {
                    'row': 'E',
                    'columns': [
                        '01', '02', '03', '04', '05', '06', '07',
                        '08', '09', '10', '11', '12', '13', '14'
                    ],
                    'rowseparator': 'hot',
                }
            ],
        ],
    },
    'Wendenstraße W408, Colocation 1': {
        'name': 'aw',
        'colocation': '1',
        'rowgroups': [
            [
                {
                    'row': 'D',
                    'columns': [
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
                    ],
                    'rowseparator': 'cold',
                },
            ],
            [
                {
                    'row': 'C',
                    'columns': [
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
                    ],
                    'rowseparator': 'hot',
                },
            ],
            [
                {
                    'row': 'B',
                    'columns': [
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
                    ],
                    'rowseparator': 'cold',
                },
                {
                    'row': 'F',
                    'columns': [
                        '1', '2', '3', '4', '5', '6', '7', '8', '9'
                    ],
                    'rowseparator': 'cold',
                },
            ],
            [
                {
                    'row': 'A',
                    'columns': [
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
                    ],
                },
                {
                    'row': 'E',
                    'columns': [
                        '1', '2', '3', '4', '5', '6', '7', '8', '9'
                    ],
                },
            ],

        ],
    },
    'Wendenstraße W408, Colocation 2': {
        'name': 'aw',
        'colocation': '2',
        'rowgroups': [
            [
                {
                    'row': 'B',
                    'columns': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    'rowseparator': 'cold',
                },
                {
                    'row': 'D',
                    'columns': ['1', '2', '3'],
                    'rowseparator': 'cold',
                },
                {
                    'row': 'F',
                    'columns': ['1', '2', '3', '4', '5', '6',
                                '7', '8', '9', '10', '11', '12'],
                    'rowseparator': 'cold',
                },

            ],
            [
                {
                    'row': 'A',
                    'columns': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
                },
                {
                    'row': 'C',
                    'columns': ['1', '2', '3'],
                },
                {
                    'row': 'E',
                    'columns': ['1', '2', '3', '4', '5', '6',
                                '7', '8', '9', '10', '11', '12'],
                },
            ],
        ]
    },
}


@login_required
def index(request):

    # Do not work on configuration.
    dcs = deepcopy(datacenters)

    for dc_k, dc_v in dcs.items():
        for rgroup in dc_v['rowgroups']:
            for row in rgroup:
                row['igcolumns'] = []
                for col in row['columns']:
                    hardware = ()
                    if row['row'] != '_' and col != '_':
                        rack = list(Query({
                            'servertype': 'rack',
                            'datacenter': dc_v['name'],
                            'rack_colo': dc_v.get('colocation', Empty()),
                            'rack_row': row['row'],
                            'rack_number': col,
                        }))
                        if rack:
                            rack = rack[0]
                            hardware = list(Query({
                                'rack': rack['hostname'],
                                'bladecenter': Empty(),
                            }).restrict(
                                'hostname',
                                'hardware_model',
                            ))
                            hardware += list(Query({
                                'rack': rack['hostname'],
                                'servertype': 'blade_enclosure',
                            }).restrict(
                                'hostname',
                                'hardware_model',
                            ))
                    row['igcolumns'].append({
                        'style': 'extreme' if [
                            hw for hw in hardware if
                            hw.get('hardware_model') == 'EX670'
                        ] else 'normal',
                        'name': col,
                        'ighw': len(hardware),
                        'hw': [hw['hostname'] for hw in hardware],
                        'static': row.get('static', {}).get(col),
                    })
    return TemplateResponse(request, 'colo/index.html', {
        'dcs': dcs,
    })
