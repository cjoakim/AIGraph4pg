# 3.0 AIGraph4pg - Quick Start Documentation

These instructions are intended to help you deploy Azure PaaS Services
and run this reference application on your workstation.

## 3.1 Recommended Skills

- Some programming language experience, especially with Python 3
- Some understanding of Python virtual environments
- Some understanding of Environment Variables
- Some command-line experience, Windows PowerShell or linux/macOS bash shell

There will be several steps to execute in this Quick Start,
**it is not a "one-click" deploy**.

---

## 3.2 Workstation Requirements

- **Windows 11** or recent **Linux** or **macOS** desktop operating system
- The **git** source-control system. See https://git-scm.com/
- The **Azure CLI** (i.e. - az).  See https://learn.microsoft.com/en-us/cli/azure/
- An **Azure Subscription**
- **Standard Python 3.12.x**; not Conda or other distributions.  See https://www.python.org/downloads/
- **Visual Studio Code (VSC)** or similar IDE/editor.  See https://code.visualstudio.com/
- **A PostgreSQL client program, such as psql**.  See https://www.postgresql.org/docs/current/app-psql.html
- **A local/desktop PostgreSQL database installation**.  This is optional, but useful for learning the basics of PostgreSQL
- **Docker Desktop**.  Optional, used only for executing the public DockerHub image.

---

## 3.3 Azure PaaS Services to Deploy

### 3.3.1 Azure PostgreSQL

- See the **az/** directory in this repo
- Copy file **az/provision-config-example.json** to **az/provision-config.json**
- Edit the **az/provision-config.json** per your subscription.  The entry names are self-explanatory
- Execute **az login**.  See https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli
- Execute the **az/provision.ps1** script to provision your Azure PostgreSQL server
- Alternatively, provision this manually in Azure Portal.
Enable the VECTOR and AGE extensions.
See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-extensions

### 3.3.2 Azure OpenAI

- Recommended, for this project, to provision this manually in Azure Portal
- Create a **text-embedding-ada-002** model deployment, for embeddings and vector search
- Create a **gpt-4o** model deployment, for generative AI of openCypher queries

---

## 3.4 A Note on Windows PowerShell and macOS bash Terminal

The remaining instructions on this page describe how you should
execute **command-line** commands in either Windows PowerShell
or the macOS Terminal program with the bash shell.  These instructions
are primarily Windows-based, but macOS is supported, too.

In the remaining documentation on this page, the relative directory
location is shown for your reference.  For example, in Windows PowerShell, 
when you are in the **root directory** of the GitHub project you'll
see instructions like this:

```
AIGraph4pg> some command in the root directory
```

Likewise, when you're in the **python directory** beneath the AIGraph4pg 
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

## 3.5 Set the Environment Variables for this project

Per the [Twelve-Factor App methodology](https://12factor.net/config),
configuration is stored in environment variables.  

### 3.5.1 List of enviroment variables

This reference implementation uses the following environment variables.
They begin with the prefix **AIG4PG_**.

| Name | Description |
| --------------------------------- | --------------------------------- |
| AIG4PG_LLM_CONTEXT_MAX_NTOKENS | Optional.  Defaults to 0, no truncation.
| AIG4PG_LOG_LEVEL | See values in class LoggingLevelService - notset, debug, info, warning, error, or critical |
| AIG4PG_OPENAI_COMPLETIONS_DEP | The name of your Azure OpenAI completions deployment |
| AIG4PG_OPENAI_EMBEDDINGS_DEP | The name of your Azure OpenAI embeddings deployment |
| AIG4PG_OPENAI_KEY | The Key of your Azure OpenAI account |
| AIG4PG_OPENAI_URL | The URL of your Azure OpenAI account |
| AIG4PG_PG_AGE_GRAPH_NAME | The name of the PostgreSQL AGE graph |
| AIG4PG_PG_FLEX_DB | Azure PostgreSQL Flex Server database |
| AIG4PG_PG_FLEX_PASS | Azure PostgreSQL Flex Server user password |
| AIG4PG_PG_FLEX_PORT | Azure PostgreSQL Flex Server port |
| AIG4PG_PG_FLEX_SERVER | Azure PostgreSQL Flex Server hostname |
| AIG4PG_PG_FLEX_USER | Azure PostgreSQL Flex Server user |
| LOCAL_PG_PASS | Optional.  Used by the psql.ps1/psql.sh scripts for local PostgreSQL access |

### 3.5.2 Setting these Environment Variables

The repo contains generated PowerShell script **set-env-vars-sample.ps1**
which sets all of these AIG4PG_ environment values.
You may find it useful to edit and execute this script rather than set them manually on your system


### 3.5.3 python-dotenv

The [python-dotenv](https://pypi.org/project/python-dotenv/) library is used
in  this implementation.  It allows you to define environment variables in a
file named **`.env`** and thus can make it easier to use this project during local development.

Please see the **dotenv_example** files in each subapplication for examples.

It is important for you to have a **.gitignore** entry for the **.env** file
so that application secrets don't get leaked into your source control system.

--- 

## 3.6 Clone the GitHub repo and create the Python Virtual Environment

These are one-time tasks in the use of this project.

### 3.6.1 Clone the Repo

This will copy the code, scripts, and curated data files to your computer.

```
> cd some-parent-directory-on-your-computer

> git clone https://github.com/cjoakim/aigraph4pg.git

> cd AIGraph4pg    <-- this is the project root directory
```

### 3.6.2 Create the Python Virtual Environment

A Python Virtual Environment is an isolated location on your computer
containing a well-defined set of required libraries, defined in the 
**requirements.in** file.  The libraries are downloaded from [PyPi](https://pypi.org/).
The application code in this project then uses these Python libraries.

This is conceptually similar to NuGet (DotNet ecosystem), MavenCentral (Java ecocystem),
NPM (Node.js and JavaScript ecosystem), etc..

```
AIGraph4pg> cd python       

python>                   <-- You'll primarily use this directory in this project

python> .\venv.ps1

python> pip list          <-- pip is the library installer program; you'll see smilar output below

Package                   Version
------------------------- -----------
aiofiles                  23.2.1
... many lines omitted here ...
yarl                      1.16.0
```

### 3.6.3 Activate the Python Virtual Environment (venv)

**Each time** you navigate to the python directory of this project
and want to execute a python program you will need to **"activate"** the
virtual environment, as shown below:

Notice how when the Virtual Environment is activated your shell
prompt changes to have the **(venv)** prefix.
This is a useful visual cue.

### 3.6.4 Windows 11 PowerShell

```
PS ...\python>
PS ...\python> .\venv\Scripts\Activate.ps1
(venv) PS ...\python>
```

### 3.6.5 macOS bash shell

```
[~/AIGraph4pg]$ cd python
[~/AIGraph4pg/python]$ source venv/bin/activate
(venv) [~/AIGraph4pg/python]$
```

---

## 3.7 Prepare your Azure PostgreSQL Server

TODO

---

## 3.8 Load Azure PostgreSQL with the Python Libraries Dataset

The dataset is a curated set of information on 10,000+ **Python Libraries**
from web crawling and other tools.  This dataset provides a foundation to
demonstrate both **traditional graph** as well as **vector search**
capabilities in Azure PostgreSQL.

The Python libraries have both dependencies and authors, and this graph
can be traversed.  Likewise, Python library data has rich text fields
(descriptions, keywords) that showcase vector search.

It is hoped that this dataset is relatable to an IT audience, particularly
application developers, and data scientists.

### 3.8.1 main.py

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

### 3.8.2 main.py - delete_define_libraries_table

```
python> python .\main.py delete_define_libraries_table
```

### 3.8.3 main.py - load_libraries_table

```
python> python .\main.py load_libraries_table
```

### 3.8.4 main.py - vector_search_similar_libraries

```
python> python .\main.py vector_search_similar_libraries flask 10
```

### 3.8.5 main.py - vector_search_words

```
python> python .\main.py vector_search_words web framework asynchronous swagger endpoints
```
