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
from bfabric_web_apps import run_main_job, get_logger, read_file_as_bytes, dataset_to_dictionary
from datetime import datetime
from utils.samplesheet_utils import create_sample_sheet_csv
from utils.layout_components import app_specific_layout, documentation_content, app_title



######################################################################################################
####################### STEP 1: Get Data From the User! ##############################################
######################################################################################################
# ------------------------------------------------------------------------------
# SET APPLICATION LAYOUT
# ------------------------------------------------------------------------------
# Use the get_static_layout function from bfabric_web_apps to set up the app layout.
app.layout = bfabric_web_apps.get_static_layout(
    app_title,                # The app title we defined previously
    app_specific_layout,      # The main content layout
    documentation_content,    # Documentation content
    layout_config={"workunits": True, "queue": True, "bug": False}  # Example config
)

# ------------------------------------------------------------------------------
# CALLBACK TO TOGGLE MODAL
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
# CALLBACK TO POPULATE DEFAULT VALUES
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
# CALLBACK TO UPDATE DATASET IN UI
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

        # 2. Files as bytes -> samplesheets usw
        files_as_byte_strings = {}

        files_as_byte_strings["./samplesheet.csv"] = read_file_as_bytes("./samplesheet.csv")
        L.log_operation("Info | ORIGIN: rnaseq web app", "Pipeline samplesheet loaded from ./samplesheet.csv.")
        files_as_byte_strings["./NFC_RNA.config"] = read_file_as_bytes("./NFC_RNA.config")
        L.log_operation("Info | ORIGIN: rnaseq web app", "NFC_RNA configuration loaded from ./NFC_RNA.config.")

        # 3. Bash command

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "/STORAGE/OUTPUT_rnaseq_" + timestamp
        work_dir = "/STORAGE/temp_rnaseq_run"

        run_pipeline_command = (
            f"/home/nfc/.local/bin/nextflow run nf-core/rnaseq "
            f"--input {work_dir}/samplesheet.csv "
            f"--fasta {work_dir}/fasta_and_gtf_files/Homo_sapiens.GRCh38.dna.primary_assembly.fa "
            f"--gtf {work_dir}/fasta_and_gtf_files/Homo_sapiens.GRCh38.109.gtf "
            f"--skip_trimming "
            f"--outdir {output_dir} "
            f"-profile docker "
            f"--custom_config_base {work_dir}"
        )

        # Use echo in subprocess
        bash_command = f'echo "{run_pipeline_command}"'
        create_out_dir = f"mkdir {output_dir}"
        delete_old_work_dir = f"rm -Rf {work_dir}/work"

        bash_commands = [delete_old_work_dir, create_out_dir ,bash_command]

        project_id = 37767

        # Update charge_run based on its value
        if charge_run and project_id:
            charge_run = [project_id]
        else:
            charge_run = []


        # 4. Create resource paths mapping file or folder to container IDs.
        resource_paths = {f'{output_dir}': 37767}

        # 5. Set attachment paths (e.g., for reports)
        attachment_paths = {
            f'{output_dir}/multiqc/star_salmon/multiqc_report.html': 'multiqc_report.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_12/qualimapReport.html': 'Run_1913_12_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_11/qualimapReport.html': 'Run_1913_11_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_10/qualimapReport.html': 'Run_1913_10_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_9/qualimapReport.html': 'Run_1913_9_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_6/qualimapReport.html': 'Run_1913_6_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_2/qualimapReport.html': 'Run_1913_2_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_4/qualimapReport.html': 'Run_1913_4_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_1/qualimapReport.html': 'Run_1913_1_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_3/qualimapReport.html': 'Run_1913_3_qualimapReport.html',
            f'{output_dir}/star_salmon/qualimap/Run_1913_8/qualimapReport.html': 'Run_1913_8_qualimapReport.html',
            f'{output_dir}/star_salmon/deseq2_qc/deseq2.plots.pdf': 'deseq2.plots.pdf',
            f'{output_dir}/pipeline_info/execution_report_2025-04-18_11-37-24.html': 'execution_report_2025-04-18_11-37-24.html',
            f'{output_dir}/multiqc/star_salmon/multiqc_report_plots/pdf/fastqc_raw_per_base_sequence_quality_plot.pdf': 'fastqc_raw_per_base_sequence_quality_plot.pdf',
            f'{output_dir}/multiqc/star_salmon/multiqc_report_plots/pdf/general_stats_table.pdf': 'general_stats_table.pdf',
            f'{output_dir}/multiqc/star_salmon/multiqc_report_plots/pdf/dupradar.pdf': 'dupradar.pdf',
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

    app.run(
        debug=bfabric_web_apps.DEBUG,
        port=bfabric_web_apps.PORT,
        host=bfabric_web_apps.HOST
    )