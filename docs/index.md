# 1.0 Introduction

<p align="center">
  <img src="img/AIGraph4pg.png" width="99%">
</p>

**AIGraph4pg** is a tutorial and reference application, implemented with
**Azure Database for PostgreSQL**, for both Graph and AI use-cases.
It is an open-source project that customers can learn from, and
possibly model their projects based on the provided codebase.

This reference application demonstrates the use of several PostgreSQL
extensions including **Apache AGE**, **pgvector**, and **azure_ai**
to implement the graph and AI functionality.
Apache AGE uses the **openCypher** graph query language, similar to Neo4j.

**Azure OpenAI** is used in this application for embeddings generation
for vector search, as well as for generative-AI of openCypher queries.

This GitHub repository application contains a **curated dataset** of USA Legal Cases
primarily in Washington state.  The dataset nicely demonstrates vector search
functionality (i.e. - case descriptions) as well as graph use cases (i.e. - case citations).
This dataset is **pre-vectorized** as the necessary embeddings have already
been created by invoking Azure OpenAI.

The curated dataset is used to load one relational table named **legal_cases**,
which contains both embeddings/vector data as well as interesting JSONB data.
The dataset also contains a zipped file that can be used to load the corresponding
Apache AGE graph, also named "legal_cases".

This application is implemented in **Python**, and also uses the **psql**
command-line tool.  Users of this application are expected to have some
familiarity with these tools, and have them **installed** in on their 
Windows 11 or macOS workstations/laptops.  Setup and use of these are
described elsewhere in the docs.

This reference application uses your instance of **Azure Database for PostgreSQL**,
and includes a web application UI that is intended to run on your 
**workstation or laptop**.  The web app can be executed locally either as a
Python process or as a public Docker image available on DockerHub.
Some **console app** functionality is also available in Python file main.py.

Each page in the web application demonstrates specific topics (i.e. -
Administrative queries, SQL queries, SQL JSONB queries, Graph queries,
Vector Search, etc.).  Each page contains a Library icon that can be clicked
to display **context-sensitive tutorial content** on that topic.
You can then click the Library icon again to return to the functional
non-tutorial page.

These topics are presented in a **left-to-right** manner in the Top Navigation
area of each page, with each topic building on the previous page.

The following image shows this **Top Navigation UI**, along with the Library icon.

<p align="center">
  <img src="img/top-nav.png" width="70%">
</p>

---

## 1.1 Architecture

<p align="center">
  <img src="img/AIGraph4pg-architecture.jpg" width="90%">
</p>

---

## 1.2 Next Steps

The context-sensitive **tutorial content** is embedded into the
web application that runs locally on your workstation/laptop.
See it by clicking the books icon on the Top-Nav.

The following are the markdown versions of the **tutorials**
that are embedded into the Web Application UI:

The [Frequently Asked Questions (FAQ)](faq.md) page may
answer some of your questions about Azure PostgreSQL
and this reference application.

---

## 1.3 Directory Structure of this GitHub Repository

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
