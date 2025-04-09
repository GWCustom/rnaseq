# Ensure version compatibility between bfabric_web_apps and bfabric_web_app_template.
# Both must be the same version to avoid compatibility issues.
# Example: If bfabric_web_apps is version 0.1.3, bfabric_web_app_template must also be 0.1.3.
# Verify and update versions accordingly before running the application.

from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import bfabric_web_apps
from generic.callbacks import app
from generic.components import no_auth
from pathlib import Path

bfabric_web_apps.DEBUG = True  # Set to True for debugging mode

# ------------------------------------------------------------------------------
# 1) SIDEBAR DEFINITION
# ------------------------------------------------------------------------------
sidebar = dbc.Container(
    [
        # Name
        html.P("Name"),
        dbc.Input(id='name', type='text', value=''),
        html.Br(),

        # Comment
        html.P("Comment"),
        dbc.Input(id='comment', type='text', value=''),
        html.Br(),

        # RAM
        html.P("RAM"),
        dbc.Select(
            id='ram',
            options=[{'label': str(x), 'value': x} for x in [16, 32, 64]],
            value=32  # Set 32 as the default
        ),
        html.Br(),

        # CPU
        html.P("CPU"),
        dbc.Select(
            id='cpu',
            options=[{'label': str(x), 'value': x} for x in [1, 2, 4, 6, 8]],
            value=6  # Set 6 as the default
        ),
        html.Br(),

        # Mail
        html.P("Mail"),
        dbc.Input(id='mail', type='email', value=''),
        html.Br(),

        # FASTA
        html.P("FASTA"),
        dbc.Select(
            id='fasta',
            options=[
                {'label': 'FASTA_1', 'value': 'fasta_1'},
                {'label': 'FASTA_2', 'value': 'fasta_2'},
            ],
        ),
        html.Br(),

        # GTF
        html.P("GTF"),
        dbc.Select(
            id='gtf',
            options=[
                {'label': 'GTF_1', 'value': 'gtf_1'},
                {'label': 'GTF_2', 'value': 'gtf_2'},
            ],
        ),
        html.Br(),

        # Submit Button
        dbc.Button("Submit", id='submit_btn', n_clicks=0),
    ],
    style={
        "maxHeight": "60vh",
        "overflowY": "auto",
        "overflowX": "hidden",
        "margin": "10px"
    }
)

# ------------------------------------------------------------------------------
# 2) MODAL DEFINITION
# ------------------------------------------------------------------------------
# Here we define the modal that will pop up when the user clicks the submit button.
modal = html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Ready to Prepare Create Workunits?")),
            dbc.ModalBody("Are you sure you're ready to create workunits?"),
            dbc.ModalFooter(dbc.Button("Yes!", id="Submit", className="ms-auto", n_clicks=0)),
        ],
        id="modal-confirmation",
        is_open=False,
    ),
])

# ------------------------------------------------------------------------------
# 3) ALERTS
# ------------------------------------------------------------------------------
# Here are the alerts which will pop up when the user creates workunits
alerts = html.Div(
    [
        dbc.Alert("Success: Workunit created!", color="success",
                  id="alert-fade-success", dismissable=True, is_open=False),
        dbc.Alert("Error: Workunit creation failed!", color="danger",
                  id="alert-fade-fail", dismissable=True, is_open=False),
    ],
    style={"margin": "20px"}
)

# ------------------------------------------------------------------------------
# 4) MAIN LAYOUT: SIDEBAR + CONTENT
# ------------------------------------------------------------------------------
# Here we define a Dash layout, which includes the sidebar, and the main content of the app.
app_specific_layout = dbc.Row(
    id="page-content-main",
    children=[
        dcc.Loading(alerts),
        modal,  # Modal defined earlier.
        dbc.Col(
            html.Div(
                id="sidebar",
                children=sidebar,  # Sidebar content defined earlier.
                style={
                    "border-right": "2px solid #d4d7d9",
                    "height": "100%",
                    "padding": "20px",
                    "font-size": "20px"
                }
            ),
            width=3,  # Width of the sidebar column.
        ),
        dbc.Col(
            html.Div(
                id="page-content",
                children=[
                    html.Div(id="auth-div")  # Placeholder for `auth-div` to be updated dynamically.
                ],
                style={
                    "margin-top": "20vh",
                    "margin-left": "2vw",
                    "font-size": "20px"
                }
            ),
            width=9,  # Width of the main content column.
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}  # Overall styling for the row layout.
)

# ------------------------------------------------------------------------------
# 5) DOCUMENTATION CONTENT
# ------------------------------------------------------------------------------
documentation_content = [
    html.H2("Welcome to Bfabric App Template"),
    html.P(
        [
            "This app serves as the user-interface for Bfabric App Template, "
            "a versatile tool designed to help build and customize new applications."
        ]
    ),
    html.Br(),
    html.P(
        [
            "It is a simple application which allows you to bulk-create resources, "
            "workunits, and demonstrates how to use the bfabric-web-apps library."
        ]
    ),
    html.Br(),
    html.P(
        [
            "Please check out the official documentation of ",
            html.A("Bfabric Web Apps", href="https://bfabric-docs.gwc-solutions.ch/index.html"),
            "."
        ]
    )
]

app_title = "rnaseq UI"

# ------------------------------------------------------------------------------
# 6) SET APPLICATION LAYOUT
# ------------------------------------------------------------------------------
# Use the get_static_layout function from bfabric_web_apps to set up the app layout.
app.layout = bfabric_web_apps.get_static_layout(
    app_title,                # The app title we defined previously
    app_specific_layout,      # The main content layout
    documentation_content,    # Documentation content
    layout_config={"workunits": True, "queue": False, "bug": True}  # Example config
)

# ------------------------------------------------------------------------------
# 7) CALLBACK TO TOGGLE MODAL
# ------------------------------------------------------------------------------
# This callback is necessary for the modal to pop up when the user clicks the submit button.
@app.callback(
    Output("modal-confirmation", "is_open"),
    [Input("submit_btn", "n_clicks"), Input("Submit", "n_clicks")],
    [State("modal-confirmation", "is_open")],
)
def toggle_modal(submit_btn_clicks, confirm_clicks, is_open):
    if submit_btn_clicks or confirm_clicks:
        return not is_open
    return is_open


@app.callback(
        Output("name", "value"),
        Input("entity", "data"),
        State("app_data", "data")
)
def populate_default_values(entity_data, app_data):
    """
    Populate the default values for the input fields.

    This callback is triggered once on page load using the 'entity' data input.
    It sets default values for the job submission form fields such as name, comment,
    resource allocations, and job configuration, based on the user's entity data.

    Args:
        entity_data (dict): Dictionary containing metadata or configuration settings 
                            associated with the current user or organization. This 
                            may include default values for RAM, cores, partition, 
                            and other submission-related fields.

    Returns:
            - name (str): Default job name.
    """

    name = entity_data.get("name", "Unknown")

    return name




# ------------------------------------------------------------------------------
# 8) CALLBACK TO UPDATE UI BASED ON AUTHENTICATION & ENTITY
# ------------------------------------------------------------------------------
@app.callback(
    [
        Output('name', 'disabled'),
        Output('comment', 'disabled'),
        Output('ram', 'disabled'),
        Output('cpu', 'disabled'),
        Output('mail', 'disabled'),
        Output('fasta', 'disabled'),
        Output('gtf', 'disabled'),
        Output('Submit', 'disabled'),  # The "Yes!" button in the modal
        Output('auth-div', 'children')
    ],
    [
        Input('name', 'value'),
        Input('comment', 'value'),
        Input('ram', 'value'),
        Input('cpu', 'value'),
        Input('mail', 'value'),
        Input('fasta', 'value'),
        Input('gtf', 'value'),
        Input('token_data', 'data'),
    ],
    [State('entity', 'data')]
)
def update_ui(name_val, comment_val, ram_val, cpu_val,
              mail_val, fasta_val, gtf_val,
              token_data, entity_data):
    """
    Disables the sidebar inputs if the user is not authenticated
    or if DEV mode is toggled. Also displays user/entity data in `auth-div`.
    """
    # Decide whether to disable the sidebar elements
    if token_data is None:
        # User not authenticated: disable everything
        disabled = True
    elif not bfabric_web_apps.DEV:
        # In production mode with valid token: everything enabled
        disabled = False
    else:
        # In DEV mode, you can choose your logic; here we enable for demonstration
        disabled = False

    # Prepare the content for the 'auth-div'
    if not entity_data or not token_data:
        # Not authenticated or no entity data
        auth_div_content = html.Div(children=no_auth)
    else:
        # If token and entity data exist, display them
        try:
            auth_div_content = dbc.Row([
                dbc.Col([
                    html.H2("Entered Sidebar Data:"),
                    html.P(f"Name: {name_val}"),
                    html.P(f"Comment: {comment_val}"),
                    html.P(f"RAM: {ram_val}"),
                    html.P(f"CPU: {cpu_val}"),
                    html.P(f"Mail: {mail_val}"),
                    html.P(f"FASTA: {fasta_val}"),
                    html.P(f"GTF: {gtf_val}"),
                ]),
                dbc.Col([
                    html.H2("Entity Data:"),
                    html.P(f"Entity Class: {token_data['entityClass_data']}"),
                    html.P(f"Entity ID: {token_data['entity_id_data']}"),
                    html.P(f"Created By: {entity_data['createdby']}"),
                    html.P(f"Created: {entity_data['created']}"),
                    html.P(f"Modified: {entity_data['modified']}"),
                ]),
            ])
        except Exception as e:
            # In case something goes wrong
            auth_div_content = html.P(f"Error Logging into B-Fabric: {str(e)}")

    return (
        disabled,  # Name field
        disabled,  # Comment field
        disabled,  # RAM
        disabled,  # CPU
        disabled,  # Mail
        disabled,  # FASTA
        disabled,  # GTF
        disabled,  # Submit button in the modal
        auth_div_content
    )

# ------------------------------------------------------------------------------
# 9) CALLBACK TO CREATE WORKUNITS OR RESOURCES
# ------------------------------------------------------------------------------
@app.callback(
    [
        Output("alert-fade-success", "is_open"),
        Output("alert-fade-fail", "is_open"),
        Output("alert-fade-fail", "children"),
        Output("refresh-workunits", "children")
    ],
    [Input("Submit", "n_clicks")],  # "Yes!" button inside the modal
    [
        State("name", "value"),
        State("comment", "value"),
        State("ram", "value"),
        State("cpu", "value"),
        State("mail", "value"),
        State("fasta", "value"),
        State("gtf", "value"),
        State("token_data", "data"),
    ],
    prevent_initial_call=True
)
def create_resources(n_clicks,
                     name_val, comment_val,
                     ram_val, cpu_val,
                     mail_val, fasta_val,
                     gtf_val,
                     token_data):

    # If no clicks yet, do nothing
    return False, False, None, html.Div()

# ------------------------------------------------------------------------------
# 10) RUN THE APP
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=bfabric_web_apps.DEBUG,
                   port=bfabric_web_apps.PORT,
                   host=bfabric_web_apps.HOST)
