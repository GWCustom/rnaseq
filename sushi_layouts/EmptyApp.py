
from generic.callbacks import app
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from bfabric_web_apps import DEVELOPER_EMAIL_ADDRESS

component_styles = {"margin-bottom": "18px", 'borderBottom': '1px solid lightgrey'}

sidebar = []

alerts = []

layout = dbc.Container(
    [
        html.H2("Welcome to Sushi Runner."),
        html.Br(), 
        html.P(f"""
            If you found this page, it likely means you have either tried invoking an application from B-Fabric which has not yet been developed / registerred,
               or you are trying to access an applicaiton outside the context of a parent entity. 
        """),
        html.Br(),
        html.P(f"""
            If you believe you've reached this page in error, please first consult
               the B-Fabric App Paradigm documentation, and / or submit a bug report in the tab above, and / or reach out directly to the developer at {DEVELOPER_EMAIL_ADDRESS}
        """),
    ]
)

def callback():
    """
    Empty placeholder callback to maintain consistency with other app objects.
    """
    pass
