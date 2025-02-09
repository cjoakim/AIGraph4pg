"""
Usage:
    python main.py log_defined_env_vars
    python main.py list_pg_extensions_and_settings
    python main.py delete_define_legal_cases_table
    python main.py relational_search_case_id 594079
    python main.py load_age_graph_with_agefreighter <graph-naame> <do-load-bool>
    python main.py load_age_graph_with_agefreighter legal_cases_af1 true
    python main.py execute_graph_validation_queries legal_cases_af1
    python main.py vector_search_similar_cases 594079 10
    python main.py vector_search_words word1 word2 word3 etc
    python main.py vector_search_words Woolworth Co. v. City of Seattle
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# This script implements "console app" functionality for the AIG4PG project.
# Chris Joakim, Microsoft

import asyncio
import json
import logging
import os
import sys
import traceback

#import psycopg_pool

from docopt import docopt
from dotenv import load_dotenv

from src.services.ai_service import AiService
from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

from src.util.age_graph_loader import AGEGraphLoader
from src.services.db_service import DBService
from src.util.fs import FS

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)

VECTOR_QUERY_LOGGED_LENGTH = 140


def print_options(msg):
    """
    Use the docopt python library to display the script
    usage comments at the top of this module.
    """
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def log_defined_env_vars():
    """
    Log the set of environment variables that are defined
    in class ConfigService.
    """
    logging.info("log_defined_env_vars")
    ConfigService.log_defined_env_vars()


async def execute_query(sql) -> list:
    """
    Execute the given SQL query and return the results
    as a list of tuples.
    """
    results_list = list()
    async with DBService.pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            results = await cursor.fetchall()
            for row in results:
                results_list.append(row)
    return results_list


async def list_pg_extensions_and_settings():
    """
    Query several tables such as pg_extension, and
    pg_available_extensions and display the resulting rows.
    """
    queries, lines = list(), list()
    queries.append("select * FROM pg_extension")
    queries.append("select * FROM pg_available_extensions")
    queries.append("select * FROM pg_settings")

    for query in queries:
        lines.append("---")
        lines.append(query)
        rows = await execute_query(query)
        for row in rows:
            logging.info(row)
            lines.append(str(row))

    FS.write_lines(lines, "tmp/pg_extensions_and_settings.txt")


async def execute_ddl(ddl_filename: str, tablename: str
):
    ddl = FS.read(ddl_filename)
    logging.info(ddl)
    async with DBService.pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(ddl)

    validation_queries = [
        "select * FROM information_schema.tables WHERE table_schema='public';",
        "select column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = '{}';".format(
            tablename
        ),
    ]
    for validation_query in validation_queries:
        logging.info("==========")
        logging.info("validation_query: {}".format(validation_query))
        rows = await execute_query(validation_query)
        for row in rows:
            logging.info(row)


def filter_files_list(files_list, suffix):
    filtered = list()
    for f in files_list:
        if f.endswith(suffix):
            filtered.append(f)
    return filtered


def quoted_attr_value(doc, attr, jsonb=False):
    if attr in doc.keys():
        if jsonb:
            return "'{}'".format(json.dumps(doc[attr]))
        else:
            return "'{}'".format(str(doc[attr]).replace("'", ""))
    else:
        if attr == "embedding":
            return "[]"
        else:
            return "'?'"


async def relational_search_case_id(case_id: str):
    sql = (
        """
select id, name, name_abbreviation, case_url, decision_date, court_name, citation_count
 from legal_cases where id = {}
 offset 0 limit 1""".format(
            case_id
        )
        .replace("\n", " ")
        .replace("  ", " ")
    )

    results = await execute_query(sql)
    if (results is not None) and (len(results) > 0):
        logging.info("sql: {}".format(sql))
        results = await execute_query(sql)
        for row in results:
            obj = dict()
            obj["id"] = row[0]
            obj["name"] = row[1]
            obj["name_abbreviation"] = row[2]
            obj["case_url"] = row[3]
            obj["decision_date"] = str(row[4])
            obj["court_name"] = row[5]
            obj["citation_count"] = row[6]
            print(json.dumps(obj, sort_keys=False, indent=2))
    else:
        logging.info("No results found for case id: {}".format(case_id))


async def vector_search_similar_cases(case_id: str, count: int
):
    """
    First execute a traditional SELECT to find the given case_id.
    Then use its embedding to find the other similar legal_cases
    via a vector search query.
    """
    logging.info(
        "vector_search_similar_cases, id: {}, count: {}".format(case_id, count)
    )
    sql = "select id, name_abbreviation, embedding from legal_cases where id = {} limit {};".format(
        case_id, count
    )
    logging.info("sql1: {} ...".format(sql))

    results = await execute_query(sql)
    if (results is not None) and (len(results) > 0):
        embedding = results[0][2]
        sql = vector_query_sql(embedding, count)
        logging.info("sql2: {} ... ]".format(sql[0:VECTOR_QUERY_LOGGED_LENGTH]))
        results = await execute_query(sql)
        for row in results:
            logging.info(row)
    else:
        logging.info("No results found for case id: {}".format(case_id))


def vector_query_sql(embedding, count):
    return (
        """
select id, name_abbreviation, case_url, decision_date
 from  legal_cases
 order by embedding <-> '{}'
 limit {};
    """.format(
            embedding, count
        )
        .strip()
        .replace("\n", " ")
        .replace("  ", " ")
    )


async def vector_search_words():
    words = sys.argv[2:]
    logging.info("vector_search_words: {}".format(words))
    await asyncio.sleep(0.1)
    try:
        # Call Azure OpenAI to generate an embedding for the given CLI words.
        embedding = None
        ai_svc = AiService()
        resp = ai_svc.generate_embeddings(" ".join(words))
        embedding = resp.data[0].embedding
        if (embedding is not None) and (len(embedding) == 1536):
            sql = vector_query_sql(embedding, 10)
            logging.info("sql: {} ... ]".format(sql[0:VECTOR_QUERY_LOGGED_LENGTH]))
            results = await execute_query(sql)
            for row in results:
                logging.info(row)
    except Exception as e:
        logging.critical(str(e))


async def load_age_graph_with_agefreighter(graph_name: str, do_load: bool):
    loader = AGEGraphLoader()
    await loader.load_legal_cases_dataset(graph_name, do_load)
    if do_load == 9:
        await loader.execute_validation_queries(graph_name)

async def execute_graph_validation_queries(graph_name: str):
    loader = AGEGraphLoader()
    await loader.execute_validation_queries(graph_name)


async def async_main():
    """
    This is the asyncronous main logic, called from the entry point
    of this module with "asyncio.run(async_main())".

    This project chose to demonstrate asyncronous programming
    rather than synchronous programming as it is more performant
    and production-oriented.
    """
    try:
        await DBService.initialze_pool(True)
        if len(sys.argv) < 2:
            print_options("- no command-line args given")
        else:
            func = sys.argv[1].lower()
            logging.info("func: {}".format(func))

            if func == "log_defined_env_vars":
                log_defined_env_vars()
            elif func == "list_pg_extensions_and_settings":
                await list_pg_extensions_and_settings()
            elif func == "delete_define_legal_cases_table":
                await execute_ddl("sql/legal_cases_ddl.sql", "legal_cases")
            elif func == "relational_search_case_id":
                case_id = sys.argv[2]
                await relational_search_case_id(case_id)
            elif func == "vector_search_similar_cases":
                library_name = sys.argv[2].lower()
                count = int(sys.argv[3])
                await vector_search_similar_cases(library_name, count)
            elif func == "vector_search_words":
                library_name = sys.argv[2].lower()
                await vector_search_words()
            elif func == "load_age_graph_with_agefreighter":
                graph_name = sys.argv[2].lower()
                do_load = sys.argv[3].lower() == "true"
                await load_age_graph_with_agefreighter(graph_name, do_load)
            elif func == "execute_graph_validation_queries":
                graph_name = sys.argv[2].lower()
                await execute_graph_validation_queries(graph_name)
            else:
                print_options("- unknown command-line arg: {}".format(func))
    except Exception as e:
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)
        logging.error("Stack trace:\n%s", traceback.format_exc())

    finally:
        await DBService.close_pool()


if __name__ == "__main__":
    load_dotenv(override=True)
    if sys.platform == "win32":
        logging.info("Running on Windows, setting WindowsSelectorEventLoopPolicy")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        logging.info("Not running on Windows")

    asyncio.run(async_main())
