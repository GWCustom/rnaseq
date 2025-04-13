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
from dash.dash_table import DataTable
import pandas as pd
from bfabric_web_apps.utils.redis_queue import q
from bfabric_web_apps import run_main_job, get_logger, read_file_as_bytes

bfabric_web_apps.DEBUG = True  # Set to True for debugging mode


######################################################################################################
####################### STEP 1: Get Data From the User! ##############################################
######################################################################################################

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
        html.P(id="sidebar_text_3", children="Submit job to which queue?"),
        dcc.Dropdown(
            options=[
                {'label': 'light', 'value': 'light'},
                {'label': 'heavy', 'value': 'heavy'}
            ],
            value='light',
            id='queue'
    ),
    html.Br(),
    html.Br(),
        # Submit Button
        dbc.Button("Submit", id='submit_btn', n_clicks=0),
    ],
    style={
        "maxHeight": "100vh",
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
                    dcc.Store(id="dataset", data={}),
                    html.Div(id="auth-div")  # Placeholder for `auth-div` to be updated dynamically.
                ],
                style={
                    "margin-top": "2vh",
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

app_title = "rnaseq-UI"

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


# ------------------------------------------------------------------------------
# 8) CALLBACK TO POPULATE DEFAULT VALUES
# ------------------------------------------------------------------------------
@app.callback(
        Output("name", "value"),
        Output("fasta", "value"),
        Output("gtf", "value"),
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
    fasta = "FASTA_1"
    gtf = "GTF_1"
    return name, fasta, gtf


######################################################################################################
####################### STEP 2: Get data from B-Fabric! ##############################################
######################################################################################################

# ------------------------------------------------------------------------------
# 1) CALLBACK TO UPDATE DATASET IN UI
# ------------------------------------------------------------------------------

@app.callback(
    Output("dataset", "data"),
    Input("entity", "data"),
)
def update_dataset(entity_data):
    df = dataset_to_dictionary(entity_data.get("full_api_response", {}))
    return df


# ------------------------------------------------------------------------------
# 2) FUNCTION TO CREATE DATAFRAME FROM B-FABRIC API RESPONSE
# ------------------------------------------------------------------------------

def dataset_to_dictionary(dataset): 

    """
    Convert B-Fabric API Dataset Response 
    to a pandas dataframe

    Args: 
        dataset (dict): B-Fabric API Dataset Response

    Returns:
        pd.DataFrame: Dataframe containing the dataset information
    """

    # Check if the dataset is empty
    if not dataset:
        return pd.DataFrame()

    attributes = dataset.get("attribute", []) 
    items = [elt.get("field") for elt in dataset.get("item", [])]

    position_map = {str(elt.get("position")): elt.get("name") for elt in attributes} # Create a mapping of attribute positions to names
    df_dict = {elt : [] for elt in position_map.values()} # Create a dictionary to hold the dataframe data

    for item in items: 
        for field in item: 
            attribute_position = field.get("attributeposition")
            df_dict[position_map.get(attribute_position)].append(field.get("value")) # Append the field value to the corresponding attribute name in the dictionary
                
    # Create a dataframe from the dictionary
    return df_dict


# ------------------------------------------------------------------------------
# 3) CALLBACK TO UPDATE UI BASED ON AUTHENTICATION & ENTITY
# ------------------------------------------------------------------------------
@app.callback(
    Output('auth-div', 'children'),
    Input("dataset", "data"),
    State("token_data", "data"),
    State("entity", "data")
)
def load_dataset_to_ui(data, token_data, entity_data):
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

            df = pd.DataFrame(data) 

            if df.empty:
                return html.Div("No dataset loaded")

            else:
                table = DataTable(
                id='datatable',
                data=df.to_dict('records'),        
                columns=[{"name": i, "id": i} for i in df.columns], 
                selected_rows=[i for i in range(len(df))],
                row_selectable='multi',
                page_action="native",
                page_current=0,
                page_size=15,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_table={
                    'overflowX': 'auto', 
                    'maxWidth': '90%'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'fontSize': '0.85rem',
                    'font-family': 'Arial',
                    'border': '1px solid lightgrey'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
                )

                auth_div_content = html.Div([
                    html.H4("Dataset"),
                    table
                ])
                        
        except Exception as e:
            # In case something goes wrong
            auth_div_content = html.P(f"Error Logging into B-Fabric: {str(e)}")

    return (
        auth_div_content
    )



######################################################################################################
############################### STEP 3: Submit the Job! ##############################################
###################################################################################################### 

# ------------------------------------------------------------------------------
# 1) FUNCTION TO CREATE RESOURCE PATHS
# ------------------------------------------------------------------------------

def create_resource_paths(token_data):
    pass


# ------------------------------------------------------------------------------
# 2) FUNCTION TO CREATE SAMPLE SHEET CSV
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# 3) CALLBACK TO RUN MAIN JOB
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
        State("queue", "value"),
    ],
    prevent_initial_call=True
)
def run_main_job_callback(n_clicks,
                     name_val, comment_val,
                     ram_val, cpu_val,
                     mail_val, fasta_val,
                     gtf_val,
                     token_data, queue):
    """
    1. Files as bytes -> samplesheets usw
    2. Bash Comments -> Run NF Core pipline
    3. Resource Paths
    4. Attachments Paths
    5. Create Charges -> True
    """

    L = get_logger(token_data)
    try:
        # Log that the user has initiated the main job pipeline.
        L.log_operation("Info | ORIGIN: rnaseq web app", "Job started: User initiated main job pipeline.")


        # 1. Create csvs samplesheet

        # 2. Files as bytes -> samplesheets usw


        # 3. Bash command

        # Define the output directory for the pipeline.
        base_dir = "/STORAGE/OUTPUT_rnaseq"

        # Construct the bash command to run the nf-core rnaseq pipeline.
        bash_commands = [

            "rm -rf /APPLICATION/temp_rnaseq_run/work"
            ,
            f"""/home/nfc/.local/bin/nextflow run nf-core/rnaseq \
            -profile docker \
            --input /APPLICATION/temp_rnaseq_run/samplesheet.csv \
            --fasta /APPLICATION/temp_rnaseq_run/fasta_and_gtf_files/Homo_sapiens.GRCh38.dna.primary_assembly.fa \
            --gtf /APPLICATION/temp_rnaseq_run/fasta_and_gtf_files/Homo_sapiens.GRCh38.109.gtf \
            --skip_trimming \
            --outdir {base_dir} \
            --max_cpus 6 \
            -c /APPLICATION/temp_rnaseq_run/NFC_RNA.config \
            > /STORAGE/{base_dir}/nextflow.log 2>&1"""
        ]


        # 4. Create resource paths mapping file or folder to container IDs.


        # 5. Set attachment paths (e.g., for reports)


        # 6. Enqueue the main job into the Redis queue for asynchronous execution.
        
        """
        
        q(queue).enqueue(run_main_job, kwargs={
            "files_as_byte_strings": files_as_byte_strings,
            "bash_commands": bash_commands,
            "resource_paths": resource_paths,
            "attachment_paths": attachment_paths,
            "token": url_params
        })
      
        """

        # Log that the job was submitted successfully.
        L.log_operation("Info | ORIGIN: rnaseq web app", f"Job submitted successfully to {queue} Redis queue.")
        # Return success alert open, failure alert closed, no error message, and a success message.
        return True, False, "", "Job submitted successfully"

    except Exception as e:
        # Log that the job submission failed.
        L.log_operation("Info | ORIGIN: rnaseq web app", f"Job submission failed: {str(e)}")
        # If an error occurs, return failure alert open with the error message.
        return False, True, f"Job submission failed: {str(e)}", "Job submission failed"


debug=bfabric_web_apps.DEBUG = True

# ------------------------------------------------------------------------------
# 10) RUN THE APP
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=bfabric_web_apps.DEBUG,
                   port=bfabric_web_apps.PORT,
                   host=bfabric_web_apps.HOST)
