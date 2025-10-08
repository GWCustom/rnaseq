<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/GWCustom/rnaseq">
    <img src="https://drive.google.com/uc?export=view&id=1_RekqDx9tOY-4ziZLn7cG9sozMXIhrfE" alt="Logo" width="80" height="50.6">
  </a>

<h3 align="center">NF-Core RNA-seq App</h3>

<p align="center">
  A proof-of-concept B-Fabric WebApp for invoking bulk transcriptomics processing with NF-Core pipelines, tightly integrated with B-Fabric.
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

### 5. Create Your `.env` File

The app uses a `.env` file to store environment variables required for running nextflow.
An example file (`.env.example`) is included in the repository.

Create your own `.env` file by copying the example:

```bash
cp .env.example .env
```

Then open `.env` in a text editor and adjust the values to match your environment.

### 6. Run the Application

```bash
python3 index.py
```

Then open [http://localhost:8050](http://localhost:8050) in your browser.

---


## Docker Deployment

You can deploy the **RNA-seq App** using Docker Compose, which automatically sets up all required services.

---

### 1. Clone the Repository

```bash
git clone https://github.com/GWCustom/rnaseq.git
cd rnaseq
```

---

### 2. Configure `.bfabricpy.yml`

Before launching the containers, ensure your B-Fabric API credentials are configured in `~/.bfabricpy.yml`:

```yaml
GENERAL:
  default_config: PRODUCTION

PRODUCTION:
  login: your_username
  password: your_password
  base_url: https://your-bfabric-api-endpoint
```


---

### 3. Create Your `.env` File

The app uses a `.env` file for environment variables required by Docker Compose. If an example file exists:

```bash
cp .env.example .env
```

Then open `.env` and adjust values to match your environment.

> **Important:** Comment out the `REDIS_HOST` line so the app can connect to the Redis service correctly within Docker Compose.
> When Redis runs as part of the same Compose network, it is automatically reachable via the service name `redis`.

---

### 4. Review and adjust configuration files

Update these paths so they match your host setup and the volumes you mount.

#### A. `index.py` (absolute paths inside the container)

Edit the following lines:

```python
work_dir = "/home/azureuser/APPLICATION/temp_rnaseq_run"
output_dir = "/home/azureuser/STORAGE/OUTPUT_rnaseq_" + timestamp
NEXTFLOW_BIN = "/home/azureuser/.local/bin/nextflow"
```

---

#### B. `NFC_RNA.config`

Set the working directory and ensure resource profiles match your host capacity:

```groovy
workDir = "/home/azureuser/APPLICATION/temp_rnaseq_run/work"
```

---

#### C. `docker-compose.yml`

Review the `docker-compose.yml` and update all path-related entries under `environment:` and `volumes:`.

Environment variables with paths:

```yaml
environment:
  BASE_DIR: "/home/azureuser/APPLICATION/temp_rnaseq_run"   # must contain samplesheet & config
  OUTPUT_DIR: "/home/azureuser/STORAGE"                    # parent of timestamped output_dir
  NEXTFLOW_BIN: "/home/azureuser/.local/bin/nextflow"      # must match Dockerfile install path
  NXF_HOME: "/workspace/.nextflow"                         # Nextflow cache inside container
```

Volume mounts (host → container):

```yaml
volumes:
  - .:/workspace
  - /home/azureuser/APPLICATION:/home/azureuser/APPLICATION  # contains temp_rnaseq_run (+/work)
  - /home/azureuser/STORAGE:/home/azureuser/STORAGE          # receives outputs
  - /var/run/docker.sock:/var/run/docker.sock                # Nextflow launches containers
  - /home/azureuser/.ssh:/home/azureuser/.ssh:ro             # shh key
  - /home/azureuser/.ssh:/root/.ssh:ro                       # known_hosts
  - /home/azureuser/.bfabricpy.yml:/home/azureuser/.bfabricpy.yml:ro # B-Fabric credentials
```

> Make sure to adjust the paths in both the web and worker services.

---

#### D. `Dockerfile`

In the `Dockerfile`, you can **adjust the user** if your environment requires a different username:

```dockerfile
RUN useradd -ms /bin/bash azureuser
USER azureuser
WORKDIR /workspace
```

If you change the username (e.g. from `azureuser` to `myuser`), make sure to update:

* All path references (e.g. `/home/azureuser/...`)
* The mounted paths in your `docker-compose.yml`

---

### 5. Build and Start the Containers

**Build:**

```bash
docker compose build
```

**Start:**

```bash
docker compose up
```

---

### 6. Access the App

```
http://localhost:8050
```

---

### 7. Stop the Containers

```bash
docker compose down
```

> This stops and removes the containers but keeps volumes and images intact.

---


## License

Distributed under the MIT License. See [LICENSE](https://github.com/GWCustom/rnaseq/blob/main/LICENSE) for details.

---

## Contact

GWC GmbH - [GitHub](https://github.com/GWCustom)  
Griffin White - [LinkedIn](https://www.linkedin.com/in/griffin-white-3aa20918a/)  
Marc Zuber - [LinkedIn](https://www.linkedin.com/in/marc-zuber-1161b3305/)
