
import asyncio
import logging
import psycopg_pool

from ageqrp import QueryResultParser

from src.services.config_service import ConfigService

# Service class for interacting with Azure PostgreSQL via psycopg.
# Chris Joakim, Microsoft


class DBService:

    pool = None

    @classmethod
    async def initialze_pool(cls) -> psycopg_pool.AsyncConnectionPool:
        """
        Create and open a psycopg_pool.AsyncConnectionPool
        which is used throughout this module.
        """
        if DBService.pool is not None:
            logging.info("DBService#initialze_pool already exists...")
            return DBService.pool
        
        conn_pool_max_size = 1
        logging.info("DBService#initialze_pool creating new...")
        conn_str = ConfigService.pg_connection_str()
        conn_str_tokens = conn_str.split("password")
        logging.info(
            "DBService#initialze_pool, conn_str: {} password=<omitted>".format(conn_str_tokens[0])
        )
        DBService.pool = psycopg_pool.AsyncConnectionPool(
            conninfo=conn_str, open=False, min_size=1, max_size=conn_pool_max_size)

        logging.info("DBService#initialze_pool, pool created: {}".format(DBService.pool))
        await DBService.pool.open()
        await DBService.pool.check()
        logging.info("DBService#initialze_pool, pool opened")

        for n in range(conn_pool_max_size):
            logging.debug("DBService#initialze_pool, conn {} init".format(n))
            try:
                set_search_path_stmt = 'SET search_path = "$user", ag_catalog, public;'
                async with cls.pool.connection() as conn:
                    async with conn.cursor() as cursor:
                        try:
                            await cursor.execute(set_search_path_stmt)
                        except Exception as e:
                            logging.critical(str(e))
                            logging.exception(e, stack_info=True, exc_info=True)
            except:
                logging.critical(str(e))
                logging.exception(e, stack_info=True, exc_info=True)

            try:
                # priming AGE query
                async with cls.pool.connection() as conn:
                    async with conn.cursor() as cursor:
                        try:
                            query = "SELECT * FROM ag_catalog.cypher('legal_cases', $$ MATCH (c:Case) RETURN c limit 10 $$) as (v agtype);"
                            await cursor.execute(query)
                        except Exception as e0:
                            pass  # exception is expected on initial query
            except Exception as eprime:
                pass

        return DBService.pool
    
    @classmethod
    def set_search_path_statement(cls):
        return 'SET search_path = ag_catalog, "$user", public;'

    @classmethod
    async def set_search_path(cls, conn):
        async with conn.cursor() as cursor:
            try:
                stmt = cls.set_search_path_statement()
                logging.info("DBService#set_search_path, stmt: {}".format(stmt))
                await cursor.execute(stmt)
                logging.info("DBService#set_search_path completed")
            except:
                pass

    @classmethod
    async def close_pool(cls) -> None:
        """
        Close the psycopg_pool.AsyncConnectionPool.
        """
        if DBService.pool is not None:
            logging.info("DBService#close_pool, closing...")
            await DBService.pool.close()
            logging.info("DBService#close_pool, closed")
            DBService.pool = None

    @classmethod
    async def execute_query(cls, sql) -> list:
        """
        Execute the given SQL query and return the results
        as a list of tuples.
        """
        stmt = sql.replace("\r\n", "")
        logging.info("DBService#execute_query, stmt: {}".format(stmt))
        results_tuples: list[str] = list()
        result_objects = list()
        qrp = QueryResultParser()
        
        async with cls.pool.connection() as conn:
            stmt = sql.replace("\r\n", "")
            async with conn.cursor() as cursor:
                try:
                    await asyncio.wait_for(
                        cursor.execute(stmt), timeout=30.0
                    )  # timeout in seconds
                    results = await cursor.fetchall()
                    for row in results:
                        # logging.warning("row for qrp: {}".format(row))
                        result_objects.append(qrp.parse(row))
                        results_tuples.append(str(row))
                except Exception as e:
                    logging.critical((str(e)))
        return results_tuples
    

