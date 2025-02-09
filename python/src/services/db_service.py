
import asyncio
import logging
import psycopg_pool

from src.services.config_service import ConfigService

# Service class for interacting with Azure PostgreSQL via psycopg.
# Chris Joakim, Microsoft


class DBService:

    pool = None

    @classmethod
    async def initialze_pool(cls, set_search_path : bool = False) -> psycopg_pool.AsyncConnectionPool:
        """
        Create and open a psycopg_pool.AsyncConnectionPool
        which is used throughout this module.
        """

        if DBUtil.pool is not None:
            logging.info("DBUtil#initialze_pool already exists...")
            return DBUtil.pool
        
        conn_pool_max_size = 1
        logging.info("DBUtil#initialze_pool creating new...")
        conn_str = ConfigService.pg_connection_str()
        conn_str_tokens = conn_str.split("password")
        logging.info(
            "DBUtil#initialze_pool, conn_str: {} password=<omitted>".format(conn_str_tokens[0])
        )
        DBUtil.pool = psycopg_pool.AsyncConnectionPool(
            conninfo=conn_str, open=False, min_size=1, max_size=conn_pool_max_size)

        logging.info("DBUtil#initialze_pool, pool created: {}".format(DBUtil.pool))
        await DBUtil.pool.open()
        await DBUtil.pool.check()
        logging.info("DBUtil#initialze_pool, pool opened")

        if set_search_path == True:
            for n in range(conn_pool_max_size):
                #set_search_path_stmt = 'SET search_path = "$user", ag_catalog, public;'
                set_search_path_stmt = 'SET search_path = "$user", ag_catalog, public;'
                async with DBUtil.pool.connection() as conn:
                    async with conn.cursor() as cursor:
                        try:
                            logging.info("DBUtil#initialze_pool, setting search_path: {}".format(
                                set_search_path_stmt))
                            await cursor.execute(set_search_path_stmt)
                            logging.info("DBUtil#initialze_pool, search_path set")
                        except:
                            pass

        return DBUtil.pool
    
    @classmethod
    def set_search_path_statement(cls):
        return 'SET search_path = ag_catalog, "$user", public;'

    @classmethod
    async def set_search_path(cls, conn):
        async with conn.cursor() as cursor:
            try:
                stmt = cls.set_search_path_statement()
                logging.info("DBUtil#set_search_path, stmt: {}".format(stmt))
                await cursor.execute(stmt)
                logging.info("DBUtil#set_search_path completed")
            except:
                pass

    @classmethod
    async def close_pool(cls) -> None:
        """
        Close the psycopg_pool.AsyncConnectionPool.
        """
        if DBUtil.pool is not None:
            logging.info("DBUtil#close_pool, closing...")
            await DBUtil.pool.close()
            logging.info("DBUtil#close_pool, closed")
            DBUtil.pool = None

    @classmethod
    async def execute_query(cls, sql) -> list:
        """
        Execute the given SQL query and return the results
        as a list of tuples.
        """
        results_list = list()
        async with DBUtil.pool.connection() as conn:
            await cls.set_search_path(conn)
            async with conn.cursor() as cursor:
                # await asyncio.wait_for(
                #     cursor.execute(sql), timeout=30.0
                # )  # timeout in seconds
                # #results = await cursor.fetchall()

                await cursor.execute(sql)
                results = await cursor.fetchall()
                for row in results:
                    results_list.append(row)
        return results_list
    

