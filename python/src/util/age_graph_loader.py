import asyncio
import json
import logging
import traceback

import psycopg_pool

from docopt import docopt
from dotenv import load_dotenv

from agefreighter import Factory

from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService

from src.services.db_service import DBService
from src.util.fs import FS

# This class is used to load specific CSV datasets into Apache AGE graphs
# in Azure PostgreSQL.  The implementation uses the agefreighter library.
# Chris Joakim, Microsoft


class AGEGraphLoader:

    def __init__(self):
        self.graph_name = None

    async def load_legal_cases_dataset(self, graph_name: str, do_load: bool) -> None:
        self.graph_name = graph_name
        logging.info("AGEGraphLoader#load_legal_cases_dataset: {} {}".format(self.graph_name, do_load))
        try:
            conn_str = ConfigService.pg_connection_str()
            freighter = Factory.create_instance("MultiCSVFreighter")
            logging.info("freighter: {}".format(freighter))

            await freighter.connect(
                dsn=conn_str,
                max_connections=64,
            )
            logging.info("freighter connected: {}".format(freighter))

            if do_load == True:
                await freighter.load(
                    graph_name=graph_name,
                    vertex_csv_paths=[
                        "../data/legal_cases/graph_csv/legal_cases_case_vertices.csv"
                    ],
                    vertex_labels=["Case"],
                    edge_csv_paths=[
                        "../data/legal_cases/graph_csv/legal_cases_cites_edges.csv",
                        "../data/legal_cases/graph_csv/legal_cases_cited_by_edges.csv",
                    ],
                    edge_types=["cites", "cited_by"],
                    use_copy=True,
                    drop_graph=True,
                    create_graph=True,
                    progress=True
                )
                logging.info("freighter loaded")
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

    async def execute_validation_queries(self, graph_name) -> None:
        try:
            logging.info("AGEGraphLoader#execute_validation_queries: {}".format(graph_name))
            await DBService.execute_query(self.list_age_graphs_sql())
            await DBService.execute_query(self.count_vertices_in_graph_sql(graph_name))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
        finally:
            await DBService.close_pool()

    # async def execute_query(self, sql) -> list:
    #     async with DBService.pool.connection() as conn:
    #         await DBService.set_search_path(conn)
    #         async with conn.cursor() as cursor:
    #             logging.info("AGEGraphLoader#execute_query: {}".format(sql))
    #             await cursor.execute(sql)
    #             results = await cursor.fetchall()
    #             for row in results:
    #                 print(row)
    
    def list_age_graphs_sql(self) -> str:
        return "select graphid, name, namespace from ag_catalog.ag_graph order by graphid;" 
    
    def count_vertices_in_graph_sql(self, graph_name):
        t = "select * from ag_catalog.cypher('{}', $$ MATCH (n) RETURN count(n) as count $$) as (v agtype);"
        return t.format(graph_name).strip()