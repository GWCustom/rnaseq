
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
