"""
This program is used for the development of the AIGraph4PG project
and not for users of the project.  It is used to generate various
files and code artifacts.
Usage:
    python dev_main.py log_defined_env_vars
    python dev_main.py gen_dotenv_examples
    python dev_main.py gen_ps1_env_var_script
    python dev_main.py gen_docker_compose_fragment
    python dev_main.py gen_docker_requirements_txt
    python dev_main.py gen_environment_variables_md
    python dev_main.py tutorials_to_md
    python dev_main.py gen_all
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# THIS SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
# Chris Joakim, Microsoft

import logging
import os
import sys
import yaml

from docopt import docopt
from dotenv import load_dotenv

from markdownify import markdownify as md

from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService
from src.util.fs import FS

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)


def print_options(msg):
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version=ConfigService.project_version())
    print(arguments)


def log_defined_env_vars():
    logging.info("log_defined_env_vars")
    ConfigService.log_defined_env_vars()


def gen_dotenv_examples():
    envvars = ConfigService.defined_environment_variables()
    samples = ConfigService.sample_environment_variable_values()
    sample_lines, actuals_lines = list(), list()

    for name in sorted(envvars.keys()):
        sample_value = samples[name]
        actual_value = ""
        try:
            actual_value = ConfigService.envvar(name, "")
        except:
            pass
        sample_lines.append('{}="{}"'.format(name, sample_value))
        actuals_lines.append('{}="{}"'.format(name, actual_value))

    FS.write_lines(sample_lines, "dotenv_example")
    FS.write_lines(actuals_lines, "tmp/dotenv_example")
    logging.info("Note: file dotenv_example contains sample values")
    logging.info(
        "Note: file tmp/dotenv_example contains your actual environment variable values"
    )


def gen_ps1_env_var_script():
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    samples = ConfigService.sample_environment_variable_values()
    lines = list()
    lines.append(
        "# PowerShell script to set the necessary AIG4PG_ environment variables,"
    )
    lines.append("# Edit ALL of these generated values per your actual deployments.")
    lines.append("")
    lines.append('Write-Host "Setting AIG4PG environment variables ..."')

    for name in env_var_names:
        value = ""
        if name in samples:
            value = samples[name]
        lines.append("")
        lines.append("Write-Host 'setting {}'".format(name))
        lines.append(
            "[Environment]::SetEnvironmentVariable(|{}|, |{}|, |User|)".format(
                name, value
            ).replace("|", '"')
        )
    lines.append("")
    lines.append('Write-Host "done"')
    lines.append("")
    FS.write_lines(lines, "set-env-vars-sample.ps1")


def gen_docker_compose_fragment():
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    excluded_env_vars = compose_excluded_envvars()
    filtered_env_var_names = list()
    compose_env_lines = list()

    for env_var_name in env_var_names:
        if env_var_name not in excluded_env_vars:
            filtered_env_var_names.append(env_var_name)

    for env_var_name in sorted(filtered_env_var_names):
        name_with_colon = env_var_name + ":"
        compose_env_lines.append(
            "      {:<35} ${}".format(name_with_colon, env_var_name)
        )

    FS.write_lines(compose_env_lines, "tmp/generated.compose.env")


def gen_docker_requirements_txt():
    """
    Automation to replace tedious manual editing of the requirements.txt
    file used to build the Docker image.
    """
    dev_requirements = FS.read_lines("requirements.txt")
    docker_lines = list()
    docker_lines.append(
        "# This File excludes Windows-specific Python libraries\n# from the Docker image."
    )
    docker_lines.append("")
    exclude_libs = "pywin32".split(",")
    for line in dev_requirements:
        stripped = line.strip()  # example: pywin32==308
        if (stripped.startswith("#")) or (len(line) == 0):
            pass
        else:
            lib_version_tokens = stripped.split("==")
            if len(lib_version_tokens) == 2:
                lib_name = lib_version_tokens[0]
                if lib_name not in exclude_libs:
                    docker_lines.append(line.strip())
                else:
                    docker_lines.append(
                        "# {}  <-- excluded from Docker image".format(line.strip())
                    )
            else:
                print("unexpected requirements.txt line: {}".format(line))

    FS.write_lines(docker_lines, "requirements-docker.txt")


def compose_excluded_envvars():
    """
    Return a list of the environment variable names
    that should be excluded from Docker compose.
    """
    vars = list()
    vars.append("AIG4PG_HOME")
    vars.append("AIG4PG_WEB_APP_PORT")
    vars.append("AIG4PG_WEB_APP_URL")
    vars.append("LOCAL_PG_PASS")
    return vars


def gen_envvars_master_entries():
    """generate a partial config file for my personal envvar solution - cj"""
    samples = ConfigService.sample_environment_variable_values()
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    lines = list()
    for name in env_var_names:
        value = ConfigService.envvar(name, "")
        if len(value) == 0:
            if name in samples.keys():
                value = samples[name]
        padded = name.ljust(35)
        lines.append("{} ||| {}".format(padded, value))
    FS.write_lines(lines, "tmp/app-envvars-master.txt")


def gen_environment_variables_md():
    lines = list()
    lines.append("# AIGraph4pg Implementation 1 : Environment Variables")
    lines.append("")
    lines.append(
        "Per the [Twelve-Factor App methodology](https://12factor.net/config),"
    )
    lines.append("configuration is stored in environment variables.  ")
    lines.append("")
    lines.append("## Defined Variables")
    lines.append("")
    lines.append(
        "This reference implementation uses the following environment variables."
    )
    lines.append("| Name | Description |")
    lines.append(
        "| --------------------------------- | --------------------------------- |"
    )
    env_var_names = sorted(ConfigService.defined_environment_variables().keys())
    for name in env_var_names:
        desc = ConfigService.defined_environment_variables()[name]
        lines.append("| {} | {} |".format(name, desc))

    lines.append("")
    lines.append("## Setting these Environment Variables")
    lines.append("")
    lines.append(
        "The repo contains generated PowerShell script **set-env-vars-sample.ps1**"
    )
    lines.append("which sets all of these AIG4PG_ environment values.")
    lines.append(
        "You may find it useful to edit and execute this script rather than set them manually on your system"
    )
    lines.append("")

    lines.append("")
    lines.append("## python-dotenv")
    lines.append("")
    lines.append(
        "The [python-dotenv](https://pypi.org/project/python-dotenv/) library is used"
    )
    lines.append("in each subapplication of this implementation.")
    lines.append(
        "It allows you to define environment variables in a file named **`.env`**"
    )
    lines.append(
        "and thus can make it easier to use this project during local development."
    )
    lines.append("")
    lines.append(
        "Please see the **dotenv_example** files in each subapplication for examples."
    )
    lines.append("")
    lines.append(
        "It is important for you to have a **.gitignore** entry for the **.env** file"
    )
    lines.append(
        "so that application secrets don't get leaked into your source control system."
    )
    lines.append("")

    FS.write_lines(lines, "tmp/environment_variables.md")


def gen_all():
    gen_dotenv_examples()
    gen_ps1_env_var_script()
    gen_docker_compose_fragment()
    gen_docker_requirements_txt()
    gen_environment_variables_md()
    tutorials_to_md()


def convert_to_utf8(s):
    return s.encode("utf-8").decode("utf-8")


def tutorials_to_md():
    dirname = "views/"
    pages_list = read_mkdocs_yml()
    for basename in sorted(FS.list_files_in_dir(dirname)):
        if basename.startswith("tutorial_"):
            page_index = lookup_page_index(pages_list, basename)
            print("page: {} index: {}".format(basename, page_index))
            if page_index > 0:
                path = "{}{}".format(dirname, basename)
                outfile = "tmp/{}.md".format(basename.replace(".html", ""))
                html = FS.read(path)
                markdown = md(html)  # convert html to md with markdownify
                md_lines, pruned_lines = markdown.split("\n"), list()
                for line in md_lines:
                    keep_line = True
                    if line.strip().startswith("{%"):
                        keep_line = False
                    # if line.strip().startswith("##### Tutorial : "):
                    #     tokens = line.strip().split(":")
                    #     line = "## AIGraph4pg Tutorial : {}".format(tokens[1].strip())
                    if keep_line == True:
                        if line.startswith("![](static/img/"):
                            line = line.replace("static/", "")
                            #print("image line: {}".format(line))
                        pruned_lines.append(line)

                new_lines = add_outline_sequence(pruned_lines, page_index)
                FS.write_lines(new_lines, outfile)

def read_mkdocs_yml():
    # Read the mkdocs.yml file and extract a list of markdown pages
    # from the "nav" section of the file.  Used for outline sequence.
    pages = list()
    with open("../mkdocs.yml", 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        nav = data["nav"]
        for item in nav:
            if type(item) == dict:
                for key in item.keys():
                    docs = item[key]
                    for doc in docs:
                        pages.append(doc.split(".")[0])
            else:
                pages.append(item.split(".")[0])
        FS.write_json(nav, "tmp/mkdocs_nav.json")
    FS.write_json(pages, "tmp/mkdocs_pages.json")
    return pages

def lookup_page_index(pages, filename):
    for page in pages:
        if filename.startswith(page):
            return pages.index(page) + 1
    return -1

def add_outline_sequence(pruned_lines, page_index):
    new_lines, lev = list(), 0
    for line in pruned_lines:
        stripped = line.strip()
        if stripped.startswith("#### "):
            left, right = stripped[:5], stripped[5:]
            lev = lev + 1
            new_line = "{} {}.{} {}".format(left, page_index, lev, right)
            print(new_line)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return new_lines


def ad_hoc_development():
    """Experimental code"""
    tutorials = read_mkdocs_yml()
    print(tutorials)


if __name__ == "__main__":
    load_dotenv(override=True)

    if len(sys.argv) < 2:
        print_options("- no command-line args given")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "log_defined_env_vars":
                log_defined_env_vars()
            elif func == "gen_dotenv_examples":
                gen_dotenv_examples()
            elif func == "gen_ps1_env_var_script":
                gen_ps1_env_var_script()
            elif func == "gen_docker_compose_fragment":
                gen_docker_compose_fragment()
            elif func == "gen_docker_requirements_txt":
                gen_docker_requirements_txt()
            elif func == "gen_environment_variables_md":
                gen_environment_variables_md()
            elif func == "gen_all":
                gen_all()
            elif func == "tutorials_to_md":
                tutorials_to_md()
            elif func == "ad_hoc":
                ad_hoc_development()
            else:
                print_options("- error - invalid function: {}".format(func))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
