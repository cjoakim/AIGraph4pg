# AIGraph4pg - Quick Start Documentation

These instructions are intended to help you deploy Azure PaaS Services
and run this reference application on your workstation.

## Recommended Skills

- Some programming language experience, especially with Python 3
  - See https://www.python.org/

- Some understanding of Python virtual environments
  - See https://realpython.com/python-virtual-environments-a-primer/

- Some understanding of Environment Variables

- Some command-line experience, Windows PowerShell or linux/macOS bash shell
  - https://learn.microsoft.com/en-us/powershell/scripting/overview?view=powershell-7.4 
  - https://support.apple.com/guide/terminal/welcome/mac

There will be several steps to execute in this Quick Start;
**it is NOT a "one-click" deploy**.

---

## Workstation Requirements

- **Windows 11** or recent **linux or macOS** desktop operating system
  - This solution is mostly Windows and PowerShell oriented, with *.ps1 scripts
  - But the *.sh scripts have been tested on macOS with the bash shell

- The **git** source-control system
  - Used here only to clone the public repository
  - See https://git-scm.com/

- The **Azure CLI** (i.e. - az)
  - See https://learn.microsoft.com/en-us/cli/azure/

- An **Azure Subscription**

- **Standard Python 3.12.x**
  - See https://www.python.org/downloads/
  - Not Conda or other Python distributions

- **Visual Studio Code (VSC)** or similar IDE/editor
  - See https://code.visualstudio.com/

- **A PostgreSQL client program, such as psql**
  - See https://www.postgresql.org/docs/current/app-psql.html
  - Alternatively, the PostgreSQL extension in Azure Data Studio
    - https://learn.microsoft.com/en-us/azure-data-studio/extensions/postgres-extension

- **A local/desktop PostgreSQL database installation**
  - This is optional, but useful for learning the basics of PostgreSQL

- **Docker Desktop**
  - This is optional, used only for executing the public DockerHub image
  - macOS users on Apple Silicon (i.e. - m1 to m4) will have to build the Docker image for that platform

---

## Azure PaaS Services to Deploy

- **Azure Database for PostgreSQL - Flexible Server**
  - See the **az/** directory in this repo
  - Copy file **az/provision-config-example.json** to **az/provision-config.json**
    - az/provision-config.json is not in git source control, it is git-ignored for security purposes
  - Edit the **az/provision-config.json** per your subscription
    - The entry names are self-explanatory
  - Execute **az login**
    - See https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli
  - Execute the **az/provision.ps1** script to provision your Azure PostgreSQL server
  - Alternatively, provision this manually in Azure Portal
    - Enable the VECTOR and AGE extensions
    - See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-extensions

- **Azure OpenAI**
  - Recommended, for this project, to provision this manually in Azure Portal
  - Create a **text-embedding-ada-002** model deployment, for embeddings and vector search
  - Create a **gpt-4o** model deployment, for generative AI of openCypher queries

---

## A Note on Windows PowerShell and macOS bash Terminal

The remaining instructions on this page describe how you should
execute **command-line** commands in either Windows PowerShell
or the macOS Terminal program with the bash shell.  These instructions
are primarily Windows-based, but macOS is supported, too.

In the remaining documentation on this page, the relative directory
location is shown for your reference.  For example, in Windows PowerShell, 
when you are in the **root directory** of the GitHub project you'll
see instructions like this:

```
aigraph4pg> some command in the root directory
```

Likewise, when you're in the **python directory** beneath the aigraph4pg 
directory, the instructions will look like this:

```
python> some command in the python directory
```

The project directory structure looks like this:

```
├── az
├── data
│   ├── cypher               <-- curated list of statements to populate the Apache AGE graph
│   └── pypi
│       └── wrangled_libs    <-- the curated libraries dataset, pre-vectorized
├── docs
│   └── img
└── python
    ├── docker               <-- Dockerfile and docker-compose.yml
    ├── sql                  <-- DDL and SQL files for psql and python logic
    ├── src                  <-- Python source code
    │   ├── models
    │   ├── services
    │   └── util
    ├── static               <-- static files used by the Web UI application
    ├── templates            <-- jinga2 text templates 
    ├── tests                <-- Unit tests built on the pytest framework
    ├── venv                 <-- The Python virtual environment, not in Git (git ignored)
    └── views                <-- Web UI HTML page templates
```

---

## Set the Environment Variables for this project

See the list of [Environment Variables](environment_variables.md)
used in this project.

These generally begin with the previx **AIG4PG_** or **AZURE_**.

--- 

## Clone the GitHub repo and create the Python Virtual Environment

These are one-time tasks in the use of this project.

### Clone the Repo

This will copy the code, scripts, and curated data files to your computer.

```
> cd <some-parent-directory-on-your-computer>

> git clone https://github.com/cjoakim/AIGraph4pg.git

> cd AIGraph4pg    <-- this is the project root directory
```

### Create the Python Virtual Environment

A Python Virtual Environment is an isolated location on your computer
containing a well-defined set of required libraries, defined in the 
**requirements.in** file.  The libraries are downloaded from [PyPi](https://pypi.org/).
The application code in this project then uses these Python libraries.

This is conceptually similar to NuGet (DotNet ecosystem), MavenCentral (Java ecocystem),
NPM (Node.js and JavaScript ecosystem), etc..

```
AIGraph4pg> cd python       

python>                   <-- You'll primarily use this directory in this project

python> .\venv.ps1        <-- Execute the script to create the python virtual environment

...

pip install requirements.txt ...
activating virtual environment ...

displaying the python version ...
Python 3.12.3

listing the python libraries installed in this virtual environment ...
Package                   Version
------------------------- -----------
aiofiles                  23.2.1
aiohappyeyeballs          2.4.3
aiohttp                   3.10.10
aiosignal                 1.3.1
annotated-types           0.7.0
...                                   many libs omitted here
urllib3                   2.2.3
uvicorn                   0.32.0
Werkzeug                  3.0.6
wheel                     0.45.1
wsproto                   1.2.0
yarl                      1.16.0
```

### Activate the Python Virtual Environment (venv)

**Each time** you navigate to the python directory of this project
and want to execute a python program you will need to **"activate"** the
virtual environment, as shown below:

Notice how when the Virtual Environment is activated your shell
prompt changes to have the **(venv)** prefix.
This is a useful visual cue.

#### Activate the Python Virtual Environment in Windows 11 PowerShell

```
PS ...\python>
PS ...\python> .\venv\Scripts\Activate.ps1
(venv) PS ...\python>
```

#### Activate the Python Virtual Environment macOS/Linux bash shell

```
[~/aigraph4pg]$ cd python
[~/aigraph4pg/python]$ source venv/bin/activate
(venv) [~/aigraph4pg/python]$
```

---

## Prepare your Azure PostgreSQL Flexible Server

The repo contains scripts named **pg.ps1** (Windows) and **pg.sh** (macOS/Linux)
are wrappers for the **psql** shell program.  These pg.xx scripts
use your above-defined environment variables so as to make psql
easier to use.

For example, to create a psql shell that connects to the **postgres**
database of your Azure Database for PostgreSQL Flexible Server:

```
> .\pg.ps1 flex postgres
```

### Enable extensions



---

## Load Azure PostgreSQL with the Python Libraries Dataset

The dataset is a curated set of information on 10,000+ **Python Libraries**
from web crawling and other tools.  This dataset provides a foundation to
demonstrate both **traditional graph** as well as **vector search**
capabilities in Azure PostgreSQL.

The Python libraries have both dependencies and authors, and this graph
can be traversed.  Likewise, Python library data has rich text fields
(descriptions, keywords) that showcase vector search.

It is hoped that this dataset is relatable to an IT audience, particularly
application developers, and data scientists.

### main.py

This is the Python program (i.e. - *.py suffix) that implements the
**"console app"** in this project.  You can see its **help content**
by executing the following:

```
python> python .\main.py help

...
Usage:
    python main.py log_defined_env_vars
    python main.py list_pg_extensions_and_settings
    python main.py delete_define_libraries_table
    python main.py load_libraries_table
    python main.py create_libraries_table_vector_index sql/libraries_ivfflat_index.sql
    python main.py vector_search_similar_libraries flask 10
    python main.py vector_search_words word1 word2 word3 etc
    python main.py vector_search_words running calculator miles kilometers pace speed mph
    python main.py load_age_graph ../data/cypher/us_openflights.json
Options:
  -h --help     Show this screen.
  --version     Show version.
```

### main.py - delete_define_libraries_table

```
python> python .\main.py delete_define_libraries_table
```

### main.py - load_libraries_table

```
python> python .\main.py load_libraries_table
```

### main.py - vector_search_similar_libraries

```
python> python .\main.py vector_search_similar_libraries flask 10
```

### main.py - vector_search_words

```
python> python .\main.py vector_search_words web framework asynchronous swagger endpoints
```
