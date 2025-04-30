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
import os
import pandas as pd
from bfabric_web_apps.utils.redis_queue import q
from bfabric_web_apps import run_main_job, get_logger, read_file_as_bytes

######################################################################################################
####################### STEP 1: Get Data From the User! ##############################################
######################################################################################################


# ------------------------------------------------------------------------------
# 1) SIDEBAR DEFINITION
# ------------------------------------------------------------------------------
sidebar = bfabric_web_apps.components.charge_switch + [dbc.Container(
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
                {'label': 'Homo_sapiens.GRCh38.dna.primary_assembly.fa', 'value': 'Homo_sapiens.GRCh38.dna.primary_assembly.fa'},
                {'label': 'Homo_sapiens.GRCh38.dna.toplevel.fa', 'value': 'Homo_sapiens.GRCh38.dna.toplevel.fa'},
                {'label': 'Homo_sapiens.GRCh38.cdna.all.fa', 'value': 'Homo_sapiens.GRCh38.cdna.all.fa'},
            ],
        ),
        html.Br(),

        # GTF
        html.P("GTF"),
        dbc.Select(
            id='gtf',
            options=[
                {'label': 'Homo_sapiens.GRCh38.109.gtf', 'value': 'Homo_sapiens.GRCh38.109.gtf'},
                {'label': 'Homo_sapiens.GRCh38.110.gtf', 'value': 'Homo_sapiens.GRCh38.110.gtf'},
                {'label': 'gencode.v38.annotation.gtf', 'value': 'gencode.v38.annotation.gtf'},
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
]
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

# FGCZ Infrastructure Warning Alert
infra_warning_alert = dbc.Alert(
    children=[
        html.H5("Warning: This app does not run on FGCZ infrastructure.", className="alert-heading"),
        html.P("It was built to demonstrate the generic B-Fabric web app framework. "
               "Please check the in-app documentation tab for more information.")
    ],
    color="warning",
    is_open=True,
    dismissable=False,
    style={"margin": "20px"}
)


# ------------------------------------------------------------------------------
# 4) MAIN LAYOUT: SIDEBAR + CONTENT
# ------------------------------------------------------------------------------
# Here we define a Dash layout, which includes the sidebar, and the main content of the app.
app_specific_layout = dbc.Row(
    id="page-content-main",
    children=[
        dbc.Col(  # <-- NEW COLUMN FOR ALERT
            html.Div([infra_warning_alert]),
            width=12
        ),
        dcc.Loading(alerts),
        modal,  # Modal defined earlier.
        dbc.Col(
            html.Div(
                id="sidebar",
                children=sidebar,
                style={
                    "border-right": "2px solid #d4d7d9",
                    "height": "100%",
                    "padding": "20px",
                    "font-size": "20px",
                    "overflowY": "scroll",
                    "maxHeight": "54vh",
                    "overflowX": "hidden",
                }
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content",
                children=[
                    dcc.Store(id="dataset", data={}),
                    html.Div(id="auth-div")
                ],
                style={
                    "margin-top": "2vh",
                    "margin-left": "2vw",
                    "font-size": "20px"
                }
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)


# ------------------------------------------------------------------------------
# 5) DOCUMENTATION CONTENT
# ------------------------------------------------------------------------------
documentation_content = [
    html.H2("Welcome to the NF-Core RNA-seq App"),
    html.P("""
        This app serves as a proof-of-concept for integrating B-Fabric with NF-Core RNA-seq workflows.
        It demonstrates the capabilities of the new bfabric_web_apps module in the context of
        bulk transcriptomics data processing.
    """),
    html.Br(),
    html.P([
        "The underlying Nextflow / NF-Core workflow used by this app can be found ",
        html.A("here", href="https://nf-co.re/rnaseq", target="_blank"),
        "."
    ]),
    html.Br(),
    html.P([
        "The RNA-seq app project source code is available on GitHub: ",
        html.A("rnaseq GitHub repository", href="https://github.com/GWCustom/rnaseq", target="_blank"),
        "."
    ]),
    html.Br(),
    html.P([
        "The bfabric_web_apps Python library, which generalizes concepts for creating and invoking B-Fabric-based web applications, is available here: ",
        html.A("bfabric-web-apps GitHub repository", href="https://github.com/GWCustom/bfabric-web-apps", target="_blank"),
        "."
    ]),
    html.P([
        "The documentation for the bfabric_web_apps library can be found here: ",
        html.A("bfabric-web-apps Documentation", href="https://bfabric-docs.gwc-solutions.ch/", target="_blank"),
        "."
    ]),
    html.Br(),
    html.P(
        "This RNA-seq app is built on the redis_index.py template from the "
        "bfabric_web_app_templates repository. It simplifies the management and execution of "
        "Nextflow RNA-seq pipelines through a structured and interactive web interface."
    ),
    html.Br(),
    html.H4("1. Architecture Overview"),
    html.Img(src="https://i.imgur.com/JgOI3Xx.jpeg", style={"width": "100%", "maxWidth": "1000px", "marginBottom": "20px"}),
    html.P("""
        The RNA-seq app follows a three-tier architecture involving a local UI server, a compute server,
        and the B-Fabric system at FGCZ. Users interact with the Dash-based web app hosted on the Local GWC Server.
        Submitted jobs are sent to the GWC Compute Server via Redis, where the core job function run_main_job()
        executes the NF-Core RNA-seq pipeline. Pipeline output is stored locally and registered in B-Fabric as
        linked resources and attachments using the B-Fabric API.
    """),
    html.Br(),
    html.H4("2. How the App Works"),
    html.Div([
    html.P("The app is structured into three core steps:"),
    html.Ul([
        html.Li("Step 1: Users input key parameters like CPU/RAM, FASTA/GTF files, and email via the web UI."),
        html.Li("Step 2: The app retrieves sample metadata from B-Fabric through its API and displays it for review and editing."),
        html.Li("Step 3: Upon submission, the app generates necessary config files, enqueues the job to a Redis queue, and triggers execution on the compute server. "
                "The compute server runs the NF-Core RNA-seq pipeline and links the resulting output back to B-Fabric as accessible resources and attachments.")
        ])
    ]),
    html.Br(),
    html.H4("3. What is Nextflow?"),
    html.P("""
        Nextflow is a data-driven workflow framework that enables scalable and reproducible
        computational pipelines. It supports parallel and distributed execution across environments
        like local machines, clusters, and the cloud. NF-Core is a collection of community-curated
        Nextflow pipelines that follow best practices and support a wide range of biological analysis
        tasks, including RNA-seq, ATAC-seq, and more.
    """),
    html.Br(),

    html.P("""
        The NF-Core RNA-seq pipeline is a widely used workflow for analyzing RNA sequencing data.
        It provides a comprehensive set of tools for quality control, alignment, quantification,
        and differential expression analysis. The pipeline is designed to be flexible and customizable,
        allowing users to adapt it to their specific needs and datasets. A visual representation of the pipeline
           can be found below:"""), 
    html.Img(src="https://raw.githubusercontent.com/nf-core/rnaseq/3.14.0//docs/images/nf-core-rnaseq_metro_map_grey.png", style={"width": "100%", "maxWidth": "1000px", "marginBottom": "20px"}),
    html.Br(), 
    html.H4("4. Summary"),
    html.P("""
        By combining a Dash UI, Redis-based job handling, and Nextflow/NF-Core workflows,
        this RNA-seq app provides a modular and scalable foundation for transcriptomics data processing.
        It is built using the `bfabric_web_apps` module, which simplifies development by providing reusable
        components and seamless integration with the B-Fabric system.
    """)
]

app_title = "Nextflow RNAseq UI"

# ------------------------------------------------------------------------------
# 6) SET APPLICATION LAYOUT
# ------------------------------------------------------------------------------
# Use the get_static_layout function from bfabric_web_apps to set up the app layout.
app.layout = bfabric_web_apps.get_static_layout(
    app_title,                # The app title we defined previously
    app_specific_layout,      # The main content layout
    documentation_content,    # Documentation content
    layout_config={"workunits": True, "queue": True, "bug": False}  # Example config
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
    if not entity_data:
        # If no entity data is provided, return default values
        return "Unknown", None, None
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
    if not entity_data: 
        return {}
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


    print("dataset", dataset)
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
############################### STEP 3: Submit the Main Job! #########################################
###################################################################################################### 

# ------------------------------------------------------------------------------
# 1) FUNCTION TO CREATE RESOURCE PATHS
# ------------------------------------------------------------------------------

def create_resource_paths():
    pass


# ------------------------------------------------------------------------------
# 2) FUNCTION TO CREATE SAMPLE SHEET CSV
# ------------------------------------------------------------------------------

def create_sample_sheet_csv(dataset=None):
    """
    Create a samplesheet CSV file required for nf-core/rnaseq.

    Assumes dataset is a dictionary containing:
    - 'Name' for sample names
    - 'Read1' for R1 FASTQ file paths
    - 'Read2' for R2 FASTQ file paths

    Output:
        Creates './samplesheet.csv' in the current directory
    """

    # Fallback if no dataset provided (e.g., during standalone testing)
    if dataset is None:
        raise ValueError("No dataset provided to create_sample_sheet_csv().")

    try:
        print("dataset", dataset)
        df = pd.DataFrame(dataset)
        print("df", df)

        # Ensure necessary columns exist
        for col in ["Sample", "FASTQ Read 1", "FASTQ Read 2"]:
            if col not in df.columns:
                raise KeyError(f"Missing required column in dataset: {col}")


        df["fastq_1"] = df["FASTQ Read 1"]
        df["fastq_2"] = df["FASTQ Read 2"]
        df["sample"] = df["Sample"]
        df["strandedness"] = "auto"

        # Final samplesheet
        samplesheet_df = df[["sample", "fastq_1", "fastq_2", "strandedness"]]

        # Save to CSV
        samplesheet_df.to_csv("./samplesheet.csv", index=False)

        print("samplesheet.csv created successfully.")

    except Exception as e:
        print(f"Error while creating samplesheet: {e}")



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
        State("charge_run", "on"),
        State('url', 'search'),
        State("dataset", "data"),
    ],
    prevent_initial_call=True
)
def run_main_job_callback(n_clicks,
                     name_val, comment_val,
                     ram_val, cpu_val,
                     mail_val, fasta_val,
                     gtf_val,
                     token_data, queue, charge_run, url_params, dataset):
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


        # 1. Create samplesheet csv
        create_sample_sheet_csv(dataset)
        print(dataset)

        # 2. Files as bytes -> samplesheets usw
        files_as_byte_strings = {}

        files_as_byte_strings["./samplesheet.csv"] = read_file_as_bytes("./samplesheet.csv")
        L.log_operation("Info | ORIGIN: rnaseq web app", "Pipeline samplesheet loaded from ./samplesheet.csv.")
        files_as_byte_strings["./NFC_RNA.config"] = read_file_as_bytes("./NFC_RNA.config")
        L.log_operation("Info | ORIGIN: rnaseq web app", "NFC_RNA configuration loaded from ./NFC_RNA.config.")

        # 3. Bash command


        # Define the output directory for the pipeline.
        base_dir = "/STORAGE/OUTPUT_rnaseq"

        bash_commands = []

        '''
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

        '''

        project_id = 37767

        # Update charge_run based on its value
        if charge_run and project_id:
            charge_run = [project_id]

        # 4. Create resource paths mapping file or folder to container IDs.
        resource_paths = {'/STORAGE/OUTPUT_rnaseq': 37767}

        # 5. Set attachment paths (e.g., for reports)
        attachment_paths = {
            '/STORAGE/OUTPUT_rnaseq/multiqc/star_salmon/multiqc_report.html': 'multiqc_report.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_12/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_11/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_10/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_9/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_6/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_2/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_4/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_1/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_3/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/qualimap/Run_1913_8/qualimapReport.html': 'qualimapReport.html',
            '/STORAGE/OUTPUT_rnaseq/star_salmon/deseq2_qc/deseq2.plots.pdf': 'deseq2.plots.pdf',
            '/STORAGE/OUTPUT_rnaseq/pipeline_info/execution_report_2025-04-17_11-45-38.html': 'execution_report_2025-04-17_11-45-38.html',
            '/STORAGE/OUTPUT_rnaseq/pipeline_info/execution_report_2025-04-13_18-12-15.html': 'execution_report_2025-04-13_18-12-15.html',
            '/STORAGE/OUTPUT_rnaseq/pipeline_info/execution_report_2025-04-09_12-24-13.html': 'execution_report_2025-04-09_12-24-13.html',
            '/STORAGE/OUTPUT_rnaseq/pipeline_info/execution_report_2025-04-17_11-37-16.html': 'execution_report_2025-04-17_11-37-16.html',
            '/STORAGE/OUTPUT_rnaseq/pipeline_info/execution_report_2025-04-15_14-16-40.html': 'execution_report_2025-04-15_14-16-40.html',
            '/STORAGE/OUTPUT_rnaseq/multiqc/star_salmon/multiqc_report_plots/pdf/fastqc_raw_per_base_sequence_quality_plot.pdf': 'fastqc_raw_per_base_sequence_quality_plot.pdf',
            '/STORAGE/OUTPUT_rnaseq/multiqc/star_salmon/multiqc_report_plots/pdf/general_stats_table.pdf': 'general_stats_table.pdf',
            '/STORAGE/OUTPUT_rnaseq/multiqc/star_salmon/multiqc_report_plots/pdf/dupradar.pdf': 'dupradar.pdf',
        }

        # 6. Enqueue the main job into the Redis queue for asynchronous execution.        
        q(queue).enqueue(run_main_job, kwargs={
            "files_as_byte_strings": files_as_byte_strings,
            "bash_commands": bash_commands,
            "resource_paths": resource_paths,
            "attachment_paths": attachment_paths,
            "token": url_params,
            "service_id":bfabric_web_apps.SERVICE_ID,
            "charge": charge_run
        })


        # Log that the job was submitted successfully.
        L.log_operation("Info | ORIGIN: rnaseq web app", f"Job submitted successfully to {queue} Redis queue.")
        # Return success alert open, failure alert closed, no error message, and a success message.
        return True, False, "", "Job submitted successfully"

    except Exception as e:
        # Log that the job submission failed.
        L.log_operation("Info | ORIGIN: rnaseq web app", f"Job submission failed: {str(e)}")
        # If an error occurs, return failure alert open with the error message.
        return False, True, f"Job submission failed: {str(e)}", "Job submission failed"


# ------------------------------------------------------------------------------
# 10) RUN THE APP
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    app.run(debug=bfabric_web_apps.DEBUG,
                   port=bfabric_web_apps.PORT,
                   host=bfabric_web_apps.HOST)