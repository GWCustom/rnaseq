<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/GWCustom/rnaseq">
    <img src="https://drive.google.com/uc?export=view&id=1_RekqDx9tOY-4ziZLn7cG9sozMXIhrfE" alt="Logo" width="80" height="50.6">
  </a>

<h3 align="center">NF-Core RNA-seq App</h3>

<p align="center">
  A proof-of-concept Dash application for bulk transcriptomics processing with NF-Core pipelines and B-Fabric integration.
  <br />
  <br />
  <a href="https://github.com/GWCustom/rnaseq/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
  ·
  <a href="https://github.com/GWCustom/rnaseq/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
</p>
</div>

> **Note**: This repository was forked from the [bfabric-web-app-template](https://github.com/GWCustom/bfabric-web-app-template), and was built using the [bfabric-web-apps](https://github.com/GWCustom/bfabric-web-apps) Python library.

---

## About

The **NF-Core RNA-seq App** demonstrates integration between [B-Fabric](https://fgcz-bfabric.uzh.ch/bfabric/), the [Nextflow/NF-Core RNA-seq pipeline](https://nf-co.re/rnaseq), and a Redis-based compute backend. Built using Dash and the [`bfabric-web-apps`](https://github.com/GWCustom/bfabric-web-apps) module, it enables a structured, interactive interface for RNA-seq data analysis.

- Retrieves and displays sample metadata from B-Fabric.
- Enqueues jobs for NF-Core RNA-seq execution using Redis.
- Links results back to B-Fabric automatically.

![Architecture Overview](https://i.imgur.com/JgOI3Xx.jpeg)

---

## Features

- Dash web UI with form-based job submission.
- Automated retrieval of metadata via B-Fabric API.
- Redis-powered job dispatch to remote compute server.
- Integrated output registration in B-Fabric.

![NF-Core Pipeline Overview](https://raw.githubusercontent.com/nf-core/rnaseq/3.14.0//docs/images/nf-core-rnaseq_metro_map_grey.png)

---

## Built With

- [Python](https://www.python.org/)
- [Dash](https://dash.plotly.com/)
- [Plotly](https://plotly.com/)
- [Flask](https://flask.palletsprojects.com/)
- [bfabric-web-apps](https://github.com/GWCustom/bfabric-web-apps)

---

## Quickstart

Follow these steps to install and run the app locally:

### 1. Clone the Repository

```bash
git clone https://github.com/GWCustom/rnaseq.git
cd rnaseq
```

### 2. Create and Activate a Virtual Environment

#### Using `virtualenv` (Linux/Mac):

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Using `virtualenv` (Windows):

```bash
python -m venv venv
venv\Scripts\activate
```

#### Or use `conda`:

```bash
conda create -n rnaseq-app pip
conda activate rnaseq-app
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up `.bfabricpy.yml`

Create a file in your home directory at `~/.bfabricpy.yml` with your credentials:

```yaml
GENERAL:
  default_config: PRODUCTION

PRODUCTION:
  login: your_username
  password: your_password
  base_url: https://your-bfabric-api-endpoint
```

> This file is required to authenticate with the B-Fabric API.

### 5. Run the Application

```bash
python3 index.py
```

Then open [http://localhost:8050](http://localhost:8050) in your browser.

---

## License

Distributed under the MIT License. See [LICENSE](https://github.com/GWCustom/rnaseq/blob/main/LICENSE) for details.

---

## Contact

GWC GmbH - [GitHub](https://github.com/GWCustom)  
Griffin White - [LinkedIn](https://www.linkedin.com/in/griffin-white-3aa20918a/)  
Marc Zuber - [LinkedIn](https://www.linkedin.com/in/marc-zuber-1161b3305/)
