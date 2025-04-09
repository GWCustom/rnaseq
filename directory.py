from sushi_layouts import MergeRunDataApp
from sushi_layouts import FastqcApp 
from sushi_layouts import FastqScreenApp 
from sushi_layouts import EmptyApp

UNKNOWN_APP = {
    'layout': EmptyApp.layout,
    'sidebar': EmptyApp.sidebar,
    'alerts': EmptyApp.alerts
}

DIRECTORY = {
    'default': UNKNOWN_APP,
    'test': {
        '373': {
            'layout': MergeRunDataApp.layout,
            'sidebar': MergeRunDataApp.sidebar
        },
        '434': {
            'layout': FastqcApp.layout,
            'sidebar': FastqcApp.sidebar,
            'alerts': FastqcApp.alerts
        },
        '377': {
            'layout': FastqScreenApp.layout,
            'sidebar': FastqScreenApp.sidebar
        }
    }
}

