from dash import html, dcc, ctx
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from generic.callbacks import app
import dash_daq as daq
from bfabric_web_apps.utils.components import charge_switch
import pandas as pd 
from dash.dash_table import DataTable
from bfabric_web_apps import (
    SCRATCH_PATH
)
from sushi_utils.dataset_utils import dataset_to_dictionary as dtd

from sushi_utils.component_utils import submitbutton_id
import os

######################################################################################################
####################### STEP 1: Get Data From the User! ##############################################
######################################################################################################
### We will define the following items in this section:   ############################################
###     A. Sidebar content                                ############################################
###     B. Application layout                             ############################################
###     C. Application callbacks (to handle user input)   ############################################
###     D. Populate some UI components with default vals  ############################################
######################################################################################################

####################################################################################
##### A. First we define the sidebar content (Step 1: Get data from the user) ######
####################################################################################
component_styles = {"margin-bottom": "18px", 'borderBottom': '1px solid lightgrey'}

title = 'FastqScreen'

label_style = {
    "font-size": "0.85rem",   # Smaller text
    "margin-left": "6px",     # Indent the label a bit
    "margin-bottom": "4px"
}

def id(name):
    return f"{title}_{name}"


sidebar = dbc.Container(children=charge_switch + [
    html.P(f"{title} Generic Parameters: ", style={"margin-bottom": "0px", "font-weight": "bold"}),

    html.Div([
        dbc.Label("Name", style=label_style),
        dbc.Input(id=id("name"), value='', type='text', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Comment", style=label_style),
        dbc.Input(id=id("comment"), value='', type='text', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("RAM", style=label_style),
        dbc.Select(id=id("ram"), options=[{'label': str(x), 'value': x} for x in [15, 32, 64]], style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cores", style=label_style),
        dbc.Select(id=id("cores"), options=[{'label': str(x), 'value': x} for x in [1, 2, 4, 8]], style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Scratch", style=label_style),
        dbc.Select(id=id("scratch"), options=[{'label': str(x), 'value': x} for x in [10, 50, 100]], style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Partition", style=label_style),
        dbc.Select(id=id("partition"), options=[{'label': x, 'value': x} for x in ['employee', 'manyjobs', 'user']], style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Process Mode", style=label_style),
        dbc.Select(id=id("process_mode"), options=[{'label': x, 'value': x} for x in ['DATASET']], style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Mail", style=label_style),
        dbc.Input(id=id("mail"), value='', type='email', style={"margin-bottom": "18px"})
    ]),

    html.P(f"{title} App Specific Parameters: ", style={"margin-bottom": "0px", "font-weight": "bold"}),

    daq.BooleanSwitch(
        id=id("paired"),
        on=False,
        label="Paired",
        labelPosition="top",
        style={"margin-bottom": "18px"}
    ),
    daq.BooleanSwitch(
        id=id("showNativeReports"),
        on=False,
        label="Show Native Reports",    
        labelPosition="top",
        style={"margin-bottom": "18px"}
    ),
    html.Div([
        dbc.Label("n Reads", style=label_style),
        dbc.Input(id=id("nReads"), value=100000, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("n Top Species", style=label_style),
        dbc.Input(id=id("nTopSpecies"), value=5, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Min Alignment Score", style=label_style),
        dbc.Input(id=id("minAlignmentScore"), value=-20, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Command Options", style=label_style),
        dbc.Input(id=id("cmdOptions"), value='', type='text', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Trim Front", style=label_style),
        dbc.Input(id=id("trim_front"), value=0, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Trim Tail", style=label_style),
        dbc.Input(id=id("trim_tail"), value=0, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Front", style=label_style),
        dbc.Input(id=id("cut_front"), value=False, type='text', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Front Window Size", style=label_style),
        dbc.Input(id=id("cut_front_window_size"), value=4, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Front Mean Quality", style=label_style),
        dbc.Input(id=id("cut_front_mean_quality"), value=20, type='number', style={"margin-bottom": "18px"})
    ]), 
    html.Div([
        dbc.Label("Cut Tail", style=label_style),
        dbc.Input(id=id("cut_tail"), value=False, type='text', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Tail Window Size", style=label_style),
        dbc.Input(id=id("cut_tail_window_size"), value=4, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Tail Mean Quality", style=label_style),
        dbc.Input(id=id("cut_tail_mean_quality"), value=20, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Right", style=label_style),
        dbc.Input(id=id("cut_right"), value=False, type='text', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Right Window Size", style=label_style),
        dbc.Input(id=id("cut_right_window_size"), value=4, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Cut Right Mean Quality", style=label_style),
        dbc.Input(id=id("cut_right_mean_quality"), value=20, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Average Quality", style=label_style),
        dbc.Input(id=id("average_qual"), value=0, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Max Len 1", style=label_style),
        dbc.Input(id=id("max_len1"), value=0, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Max Len 2", style=label_style),
        dbc.Input(id=id("max_len2"), value=0, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Poly X Min Len", style=label_style),
        dbc.Input(id=id("poly_x_min_len"), value=10, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Length Required", style=label_style),
        dbc.Input(id=id("length_required"), value=18, type='number', style={"margin-bottom": "18px"})
    ]),
    html.Div([
        dbc.Label("Command Options fastp", style=label_style),
        dbc.Input(id=id("cmdOptionsFastp"), value='', type='text', style={"margin-bottom": "18px"})
    ]),
    dbc.Button("Submit", id=submitbutton_id(f'{title}_submit1'), n_clicks=0, style={"margin-top": "18px", 'borderBottom': '1px solid lightgrey'})

], style={"max-height":"62vh", "overflow-y":"auto", "overflow-x":"hidden"})


####################################################################################
##### B. Now we define the application layout (Step 1: Get data from the user) #####
####################################################################################

layout = dbc.Container(
    children = [
        html.Div(id=id("Layout"), style={"max-height":"62vh", "overflow-y":"auto", "overflow-x":"hidden"}),
        dcc.Store(id=id("dataset"), data={})
    ]
)

alerts = html.Div(
    [
        dbc.Alert("Success: Job Submitted!", color="success", id=id("alert-fade-success"), dismissable=True, is_open=False),
        dbc.Alert("Error: Job Submission Failed!", color="danger", id=id("alert-fade-fail"), dismissable=True, is_open=False),
    ],
    style={"margin": "20px"}
)
####################################################################################
### C. Now we define the application callbacks (Step 1: Get data from the user) ####
####################################################################################

@app.callback(
    Output(id("Layout"), "children"),
    [
        Input(id("dataset"), "data"),
        Input("sidebar", "children"),
    ]
)
def callback(data, sidebar):
    """
    Update the dataset in the layout.
    """

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

        container = html.Div([
            html.H4("Dataset"),
            table
        ])

        return container


##############################################################################################
##### C. Now we populate components with default values (Step 1: Get data from the user) #####
##############################################################################################

@app.callback(
    [
        Output(id("name"), "value"),
        Output(id("comment"), "value"),
        Output(id("ram"), "value"),
        Output(id("cores"), "value"),
        Output(id("scratch"), "value"),
        Output(id("partition"), "value"),
        Output(id("process_mode"), "value")
    ],
    [
        Input("entity", "data"),
    ],
    [
        State("app_data", "data")
    ]
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
        tuple:
            - name (str): Default job name.
            - comment (str): Default comment or description.
            - ram (str): Default RAM allocation.
            - cores (str): Default number of CPU cores.
            - scratch (str): Default scratch disk allocation.
            - partition (str): Default SLURM partition.
            - process_mode (str): Default processing mode.
    """

    name = entity_data.get("name", "Unknown") + "_FastqScreen"

    return name, "", 32, 4, 50, 'employee', 'DATASET'

######################################################################################################
####################### STEP 2: Get data from B-Fabric! ##############################################
###################################################################################################### 
### This is a short section, because we've already generalized most      #############################
### of the data acquisition for Sushi apps which you get out of the box  #############################
######################################################################################################

@app.callback(
    Output(id("dataset"), "data"),
    Input("entity", "data"),
    State(id("dataset"), "data"),
)
def update_dataset(entity_data, dataset):
    
    df = dtd(entity_data.get("full_api_response", {}))
    return df



######################################################################################################
############################### STEP 3: Submit the Job! ##############################################
###################################################################################################### 
@app.callback(
    [
        Output(id("alert-fade-success"), "is_open"),
        Output(id("alert-fade-fail"), "is_open"),
    ],
    [
        Input("Submit", "n_clicks"),
    ],
    [
        State(id("name"), "value"),
        State(id("comment"), "value"),
        State(id("ram"), "value"),
        State(id("cores"), "value"),
        State(id("scratch"), "value"),
        State(id("partition"), "value"),
        State(id("process_mode"), "value"),
        State(id("mail"), "value"),
        State(id("paired"), "on"),
        State(id("showNativeReports"), "on"),
        State(id("nReads"), "value"),
        State(id("nTopSpecies"), "value"),
        State(id("minAlignmentScore"), "value"),
        State(id("cmdOptions"), "value"),
        State(id("trim_front"), "value"),
        State(id("trim_tail"), "value"),
        State(id("cut_front"), "value"),
        State(id("cut_front_window_size"), "value"),
        State(id("cut_front_mean_quality"), "value"),
        State(id("cut_tail"), "value"),
        State(id("cut_tail_window_size"), "value"),
        State(id("cut_tail_mean_quality"), "value"),
        State(id("cut_right"), "value"),
        State(id("cut_right_window_size"), "value"),
        State(id("cut_right_mean_quality"), "value"),
        State(id("average_qual"), "value"),
        State(id("max_len1"), "value"),
        State(id("max_len2"), "value"),
        State(id("poly_x_min_len"), "value"),
        State(id("length_required"), "value"),
        State(id("cmdOptionsFastp"), "value"),
        State(id("dataset"), "data"),
        State("datatable", "selected_rows"),
        State("token_data", "data"),
        State("entity", "data"),
        State("app_data", "data")
    ],
    prevent_initial_call=True
)
def submit_fastp_job(
    n_clicks, name, comment, ram, cores, scratch, partition, process_mode, mail,
    paired, showNativeReports, nReads, nTopSpecies, minAlignmentScore, cmdOptions,
    trim_front, trim_tail, cut_front, cut_front_window_size, cut_front_mean_quality,
    cut_tail, cut_tail_window_size, cut_tail_mean_quality,
    cut_right, cut_right_window_size, cut_right_mean_quality,
    average_qual, max_len1, max_len2, poly_x_min_len, length_required,
    cmdOptionsFastp, dataset, selected_rows, token_data, entity_data, app_data
):
    """
    Construct the bash command which calls the FastpApp via the Sushi backend.

    This Dash callback is triggered by a click on the "Submit" button. It collects user-specified
    input parameters from the app-specific sidebar layout, constructs the dataset and parameters
    files, builds a bash command to invoke the Sushi job runner, and returns alerts indicating 
    the success or failure of the job submission.

    Args:
        n_clicks (int): Number of times the "Submit" button has been clicked.
        name (str): Name of the job.
        comment (str): Optional user-provided comment or description for the job.
        ram (int): Amount of RAM requested (in GB).
        cores (int): Number of CPU cores requested.
        scratch (int): Amount of scratch disk space requested (in GB).
        partition (str): Target partition (queue) to submit the job to.
        process_mode (str): Mode in which the job should be processed.
        mail (str): Email address for job status notifications.
        paired (bool): Whether the input data is paired-end (True) or single-end (False).
        showNativeReports (bool): Whether to include native reports in the output.
        nReads (int): Number of reads to process.
        nTopSpecies (int): Number of top species to report.
        minAlignmentScore (int): Minimum alignment score threshold.
        cmdOptions (str): Additional command-line options for Fastp.
        trim_front (int): Number of bases to trim from the front.
        trim_tail (int): Number of bases to trim from the tail.
        cut_front (str): Whether to enable quality cutting from the front (True/False as string).
        cut_front_window_size (int): Window size for cutting from the front.
        cut_front_mean_quality (int): Quality threshold for cutting from the front.
        cut_tail (str): Whether to enable quality cutting from the tail (True/False as string).
        cut_tail_window_size (int): Window size for cutting from the tail.
        cut_tail_mean_quality (int): Quality threshold for cutting from the tail.
        cut_right (str): Whether to enable quality cutting from the right (True/False as string).
        cut_right_window_size (int): Window size for cutting from the right.
        cut_right_mean_quality (int): Quality threshold for cutting from the right.
        average_qual (int): Minimum average quality of reads to retain.
        max_len1 (int): Maximum allowed length for read 1.
        max_len2 (int): Maximum allowed length for read 2.
        poly_x_min_len (int): Minimum polyX length to trigger trimming.
        length_required (int): Minimum read length required to retain a read.
        cmdOptionsFastp (str): Additional Fastp-specific command-line options.
        dataset (list): List of dataset records displayed in the frontend.
        selected_rows (list): Indices of selected rows from the dataset table.
        token_data (dict): Authentication token data for secure backend communication.
        entity_data (dict): Metadata related to the user or organization entity.
        app_data (dict): Metadata or configuration specific to the FastpApp being submitted.

    Returns:
        tuple:
            - is_open_success (bool): True if job submission succeeded, to show the success alert.
            - is_open_fail (bool): True if job submission failed, to show the failure alert.
    """

    print("ASDFASDFASDF")

    try:
        ### Build dataset file
        dataset_df = pd.DataFrame(dtd(entity_data.get("full_api_response", {})))
        dataset_path = f"{SCRATCH_PATH}/{name}/dataset.tsv"
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        dataset_df.to_csv(dataset_path, sep="\t", index=False)

        ### Build parameter file
        param_dict = {
            'cores': cores,
            'ram': ram,
            'scratch': scratch,
            'node': '',
            'process_mode': process_mode,
            'partition': partition,
            'paired': str(paired).lower(),
            'name': name,
            'mail': mail,
            'nReads': nReads,
            'nTopSpecies': nTopSpecies,
            'minAlignmentScore': minAlignmentScore,
            'cmdOptions': cmdOptions,
            'cmdOptionsFastp': cmdOptionsFastp,
            'trim_front': trim_front,
            'trim_tail': trim_tail,
            'cut_front': cut_front,
            'cut_front_window_size': cut_front_window_size,
            'cut_front_mean_quality': cut_front_mean_quality,
            'cut_tail': cut_tail,
            'cut_tail_window_size': cut_tail_window_size,
            'cut_tail_mean_quality': cut_tail_mean_quality,
            'cut_right': cut_right,
            'cut_right_window_size': cut_right_window_size,
            'cut_right_mean_quality': cut_right_mean_quality,
            'average_qual': average_qual,
            'max_len1': max_len1,
            'max_len2': max_len2,
            'poly_x_min_len': poly_x_min_len,
            'length_required': length_required,
            'showNativeReports': str(showNativeReports).lower(),
            'comment': comment
        }

        param_df = pd.DataFrame({
            "col1": list(param_dict.keys()),
            "col2": list(param_dict.values())
        })

        param_path = f"{SCRATCH_PATH}/{name}/parameters.tsv"
        os.makedirs(os.path.dirname(param_path), exist_ok=True)
        param_df.to_csv(param_path, sep="\t", index=False, header=False)

        ### Build bash command
        app_id = app_data.get("id", "")
        project_id = "2220"  # TEMP FIX
        dataset_name = entity_data.get("name", "")
        mango_run_name = "None"

        bash_command = f"""
            bundle exec sushi_fabric --class FastpApp --dataset \
            {dataset_path} --parameterset {param_path} --run \
            --input_dataset_application {app_id} --project {project_id} \
            --dataset_name {dataset_name} --mango_run_name {mango_run_name} \
            --next_dataset_name {name}
        """

        print("[SUSHI BASH COMMAND]:", bash_command)
        return True, False

    except Exception as e:
        print("[SUSHI ERROR]:", str(e))
        return False, True
