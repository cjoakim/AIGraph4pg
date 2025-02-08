"""
Usage:
    python main.py load_countries_graph_with_agefreighter <graphname> <do-load-bool>
    python main.py load_countries_graph_with_agefreighter Countries false
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# Simple example of using the agefreighter library to load an AGE graph
# using the Countries and Cities data from the data/countries/ directory.
#
# Chris Joakim, Microsoft

import asyncio
import logging
import os
import sys

from datetime import datetime

from agefreighter import Factory

from docopt import docopt
from dotenv import load_dotenv

from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)


def print_options(msg):
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version=ConfigService.project_version())
    print(arguments)


async def load_countries_graph_with_agefreighter(graph_name, do_load):
    try:
        conn_str = get_database_connection_string()
        freighter = Factory.create_instance("MultiCSVFreighter")
        print("freighter: {}".format(freighter))

        await freighter.connect(
            dsn=conn_str,
            max_connections=64,
        )
        print("freighter connected: {}".format(freighter))

        if do_load == True:
            await freighter.load(
                graph_name="Countries",
                vertex_csv_paths=[
                    "../data/countries/country.csv",
                    "../data/countries/city.csv",
                ],
                vertex_labels=["Country", "City"],
                edge_csv_paths=["../data/countries/has_country_city.csv"],
                edge_types=["has"],
                use_copy=True,
                drop_graph=True,
                create_graph=True,
            )
            print("freighter loaded")
    except Exception as e:
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)

    try:
        logging.info("closing freighter...")
        await freighter.close()
        logging.info("closed")
    except Exception as e:
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)


def get_database_connection_string():
    db = ConfigService.postgresql_database()
    user = ConfigService.postgresql_user()
    password = ConfigService.postgresql_password()
    host = ConfigService.postgresql_server()
    port = ConfigService.postgresql_port()
    conn_str = "host={} port={} dbname={} user={} password={}".format(
        host, port, db, user, password
    )
    print("conn_str: {}".format(conn_str))
    return conn_str


if __name__ == "__main__":
    load_dotenv(override=True)

    if len(sys.argv) < 2:
        print_options("- no command-line args given")
        exit(1)
    else:
        if sys.platform == "win32":
            logging.warning(
                "Windows platform detected, setting WindowsSelectorEventLoopPolicy"
            )
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        else:
            logging.warning(
                "platform is {}, not Windows.  Not setting event_loop_policy".format(
                    sys.platform
                )
            )

        try:
            func = sys.argv[1].lower()
            if func == "load_countries_graph_with_agefreighter":
                graph_name = sys.argv[2]
                do_load = sys.argv[3].lower() == "true"
                asyncio.run(load_countries_graph_with_agefreighter(graph_name, do_load))
            else:
                print_options("- error - invalid function: {}".format(func))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
