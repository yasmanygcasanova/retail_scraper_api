# Getting Started

Retail Scraper API.

API para consultar o sortimento de produtos.

## Installation

Installation via requirements.txt:

```bash
1. Install python3.12
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.12
2. Install python3.12 dependencies:
    sudo apt-get install python3.12-distutils
    sudo apt-get install python3.12-dev python3.12-venv
3. Install Locale pt_BR.UTF-8:
    locale
    locale -a
    sudo locale-gen pt_BR.UTF-8
    sudo dpkg-reconfigure locales
    sudo update-locale LANG=pt_BR.UTF-8
```

## Start project

```bash
DEVELOPMENT

Access project directory
cd retail_scraper_api

Set Up a Virtual Environment
python3.11 -m venv env

Ativate Virtual Environment
source env/bin/activate

Deactivate Virtual Environment
deactivate

Install Dependencies
pip3.11 install -r requirements.txt

Create API KEY
python3.12 
import secrets

token: str = secrets.token_urlsafe(32)
copy: token 

Run the project
1) uvicorn main:app --reload --host 127.0.0.1 --port 8000
2) Browser: http://127.0.0.1:8000/docs | http://127.0.0.1:8000/redoc
3) RUNNING ALL THE TESTS: pytest 
4) RUNNING A SCRAPING TEST: pytest tests/wholesale/tendaatacado/test_tendaatacado.py

PRODUCTION
1) docker-compose up -d 
2) docker ps
```

## Help
### Flake8
` flake8 --show-source --statistics source.py `

### Isort
` isort source.py `

` isort dirname `

### Pylint
` pylint source.py `

```bash
CLOUD: GCP

Google Cloud Run setup:

1. If you have already installed gcloud CLI, update it as follows.
gcloud components update

2. Connect the gcloud CLI to your GCP account.
gcloud auth login

3. Set up your project ID
gcloud config set project PROJECT_ID

4. Region settings
gcloud config set run/region REGION

5. Docker settings
gcloud auth configure-docker

CI/CD: BUILDS
Examples:
1. gcloud builds submit --tag gcr.io/PROJECT_ID/PROJECT_NAME
2. gcloud builds submit --region=us-central1 --config cloudbuild.yaml

SERVICES: 
1. Cloud Run
Link: https://console.cloud.google.com/run?project=PROJECT_ID&authuser=1
Link: https://cloud.google.com/sdk/gcloud/reference/run/deploy

2. Container Registry:
Link: https://console.cloud.google.com/gcr/images/PROJECT_ID?authuser=1&project=PROJECT_ID 

```