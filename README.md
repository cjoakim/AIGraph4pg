## Documentation

Please see the [Documentation site](https://cjoakim.github.io/AIGraph4pg/)

---

<p align="center">
  <img src="docs/img/AIGraph4pg.png" width="99%">
</p>

---

<p align="center">
  <img src="docs/img/AIGraph4pg-architecture.jpg" width="70%">
</p>

### Links

- repo: https://github.com/cjoakim/AIGraph4pg
- docs: https://cjoakim.github.io/AIGraph4pg/

Both will move to an AzureSamples or similar repo soon.

---

## Directory Structure of this GitHub Repository

```
Directory/File                       Description

├── az                           <-- az CLI deployment script for Azure PostgresSQL
├── data
│   ├── countries                <-- small dataset for script agefreighter_example.py
│   └── legal_cases              <-- the relational curated dataset for this repo, zipped
│       └── graph_csv            <-- the graph curated dataset, csv files
├── docs                         <-- documentation in markdown format
├── jupyter                      <-- sample Jypyter notebook for AGE and the agefreighter library
├── pg_scripts                   <-- scripts for using PostgreSQL CLI programs, like pg_dump
└── python                       <-- the python3 implementation code for this project
    ├── agefreighter_example.py  <-- simple python program to load an AGE graph with agefreighter
    ├── docker-compose.yml       <-- yaml file used to run the web app with docker compose
    ├── Dockerfile               <-- file used to create the Docker image
    ├── dotenv_example           <-- example file for creating your optional .env file
    ├── main.py                  <-- the primary python "console application"
    ├── pg.ps1                   <-- script to run the psql program in an easy manner
    ├── requirements.in          <-- the python required libraries list, used by venv.ps1
    ├── set-env-vars-sample.ps1  <-- editable generated script used to set your environment variables
    ├── venv.ps1                 <-- powershell script to create your python virthal environment
    ├── webapp.ps1               <-- powershell script to start the web UI application
    ├── webapp.py                <-- web app implementation python file
    ├── sql                      <-- sql scripts, such as to delete/define the legal_cases table and indexes
    ├── src                      <-- primary python source code directory
    ├── static                   <-- static assets served by the web application
    ├── templates                <-- jinja2 templates for dynamic content generation; queries, prompts
    ├── tests                    <-- unit tests using the pytest testing framework
    ├── tmp                      <-- not in GitHub; manually create this directory yourself
    ├── venv                     <-- not in GitHub; this is the python virtual environment
    └── views                    <-- web UI html views/pages
```
