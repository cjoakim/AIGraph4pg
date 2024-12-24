# This is the entry-point for this web application, built with the
# FastAPI web framework
#
# Chris Joakim, Microsoft

import asyncio
import json
import logging
import time
import traceback
import sys

import psycopg_pool

from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ageqrp import QueryResultParser

# Pydantic models defining the "shapes" of requests and responses
from src.models.webservice_models import PingModel
from src.models.webservice_models import HealthModel

# Services with Business Logic
from src.services.ai_service import AiService
from src.services.config_service import ConfigService
from src.services.logging_level_service import LoggingLevelService
from src.util.fs import FS
#from src.util.query_result_parser import QueryResultParser
from src.util.sample_queries import SampleQueries

# standard initialization
load_dotenv(override=True)
logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)
ConfigService.print_defined_env_vars()
logging.error("project_version: {}".format(ConfigService.project_version()))

if sys.platform == "win32":
    logging.warning("Windows platform detected, setting WindowsSelectorEventLoopPolicy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    logging.warning(
        "platform is {}, not Windows.  Not setting event_loop_policy".format(sys.platform)
    )


def get_database_connection_string():
    db = ConfigService.postgresql_database()
    user = ConfigService.postgresql_user()
    password = ConfigService.postgresql_password()
    host = ConfigService.postgresql_server()
    port = ConfigService.postgresql_port()
    conn_str = "host={} port={} dbname={} user={} password={}".format(
        host, port, db, user, password
    )
    logging.info(
        "get_database_connection_string: {} password=<omitted>".format(
            conn_str.split("password")[0]
        )
    )
    return conn_str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Automated startup and shutdown logic for the FastAPI app.
    Create the AiService and async database connection pool for Azure PostgreSQL.
    See https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
    conn_pool_max_size = 1
    try:
        # Initialize the AiService used for embeddings and cypher generation.
        app.ai_svc = AiService()

        # Initialize the psycopg_pool.AsyncConnectionPool, set the search_path, and
        # execute some initial queries to check connectivity.
        conn_str = get_database_connection_string()
        app.async_pool = psycopg_pool.AsyncConnectionPool(
            conninfo=conn_str, open=False, min_size=1, max_size=conn_pool_max_size)
        logging.info("FastAPI lifespan, pool created: {}".format(app.async_pool))
        await app.async_pool.open()
        logging.info("FastAPI lifespan, pool opened")
        await app.async_pool.check()
        logging.info("FastAPI lifespan, pool checked")

        for n in range(conn_pool_max_size):
            logging.debug("FastAPI lifespan, conn {} init".format(n))
            try:
                set_search_path_stmt = 'SET search_path = "$user", ag_catalog, public;'
                async with app.async_pool.connection() as conn:
                    async with conn.cursor() as cursor:
                        try:
                            await cursor.execute(set_search_path_stmt)
                            logging.info("FastAPI lifespan, executed: {}".format(set_search_path_stmt))
                        except:
                            pass
            except:
                pass
            try:
                # priming AGE query
                async with app.async_pool.connection() as conn:
                    async with conn.cursor() as cursor:
                        try:
                            query = "SELECT * FROM ag_catalog.cypher('legal_cases', $$ MATCH (c:Case) RETURN c limit 10 $$) as (v agtype);"
                            await cursor.execute(query)
                            logging.debug("FastAPI lifespan, executed {}".format(set_search_path_stmt))
                        except Exception as e0:
                            pass  # exception is expected on initial query?
            except Exception as e0:
                pass
        logging.info("FastAPI lifespan, pool stats: {}".format(app.async_pool.get_stats()))
    except Exception as e:
        logging.error("FastAPI lifespan exception: {}".format(str(e)))
        logging.error(traceback.format_exc())

    yield

    logging.info("FastAPI lifespan, shutting down...")
    await app.async_pool.close()
    logging.info("FastAPI lifespan, pool closed")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
views = Jinja2Templates(directory="views")
logging.error("webapp.py started")


@app.get("/ping")
async def get_ping() -> PingModel:
    resp = dict()
    resp["epoch"] = str(time.time())
    return resp


@app.get("/health")
async def get_health(req: Request, resp: Response) -> HealthModel:
    """
    Return a HealthModel indicating the health of this web app.
    This endpoint may be invoked by a container orchestrator, such as
    Azure Container Apps (ACA) or Azure Kubernetes Service (AKS).
    The implementation validates the environment variable and url configuration.
    """
    alive = True
    data = dict()
    data["row_count"] = 0
    data["epoch"] = time.time()
    data["app_version"] = ConfigService.project_version()
    try:
        async with req.app.async_pool.connection() as conn:
            async with conn.cursor() as cursor:
                try:   
                    sql = "select count(*) from legal_cases"
                    await asyncio.wait_for(cursor.execute(sql), timeout=5.0)
                    query_results = await cursor.fetchall()
                    for row_idx, row in enumerate(query_results):
                        if row_idx == 0:
                            data["row_count"] = row[0]
                except Exception as e:
                    alive = False
                    logging.critical((str(e)))
    except Exception as e:
        pass
    logging.info("liveness_check: {}".format(data))

    data["alive"] = alive
    if alive == True:
        resp.status_code = status.HTTP_200_OK
    else:
        resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return data


@app.get("/")
async def get_home(req: Request):
    view_data = dict()
    view_data["tutorial_topic"] = "?topic=home"
    return views.TemplateResponse(request=req, name="home.html", context=view_data)


@app.get("/architecture")
async def get_architecture(req: Request):
    view_data = dict()
    view_data["tutorial_topic"] = "?topic=architecture"
    view_data["project_version"] = ConfigService.project_version()
    return views.TemplateResponse(request=req, name="architecture.html", context=view_data)

@app.get("/sample_queries")
async def get_sample_queries(req: Request):
    """ This endpoint is used by JavaScript in the UI."""
    return SampleQueries.read_queries()

@app.get("/tutorial")
async def get_tutorial(req: Request):
    params = req.query_params
    topic, template_name = "", "architecture.html"
    view_data = dict()
    view_data["tutorial_topic"] = ""
    view_data["project_version"] = ConfigService.project_version()
    if "topic" in params.keys():
        topic = params["topic"]
        template_name = "tutorial_{}.html".format(topic)
    logging.info("get_tutorial - {} {}".format(topic, template_name))

    return views.TemplateResponse(request=req, name=template_name, context=view_data)


# ---

@app.get("/pg_admin_queries")
async def get_pg_admin_queries(req: Request):
    query_type = "ADMIN"
    view_data = queries_view_data("", query_type)
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )

@app.post("/pg_admin_queries")
async def post_pg_admin_queries(req: Request):
    query_type = "ADMIN"
    form_data = await req.form()
    logging.info("/pg_admin_queries form_data: {}".format(form_data))
    view_data = await post_query(req, query_type)
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )


@app.get("/relational_queries")
async def get_pg_admin_queries(req: Request):
    query_type = "SQL"
    view_data = queries_view_data("", query_type)
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )


@app.post("/relational_queries")
async def post_pg_admin_queries(req: Request):
    query_type = "SQL"
    form_data = await req.form()
    logging.info("/relational_queries form_data: {}".format(form_data))
    view_data = await post_query(req, query_type)
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )


@app.get("/graph_queries")
async def get_pg_admin_queries(req: Request):
    query_type = "CYPHER"
    view_data = queries_view_data("", query_type)
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )
@app.post("/graph_queries")
async def post_pg_admin_queries(req: Request):
    query_type = "CYPHER"
    form_data = await req.form()
    logging.info("/graph_queries form_data: {}".format(form_data))
    view_data = await post_query(req, query_type)
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )


@app.get("/queries")
async def get_queries(req: Request):
    view_data = queries_view_data()
    return views.TemplateResponse(
        request=req, name="queries.html", context=view_data
    )


async def post_query(req: Request, query_type):
    """
    This method is called by the above post_xxx_queries(req) methods.
    """
    form_data = await req.form()
    logging.info("/post_query form_data: {}".format(form_data))
    query_text = form_data.get("query_text").strip()
    view_data = queries_view_data(query_text, query_type)
    qrp = QueryResultParser()

    if len(query_text) > 10:
        results_tuples: list[str] = list()
        result_objects = list()
        start_time = time.time()
        try:
            # alter user chjoakim set search_path='ag_catalog','public';
            async with req.app.async_pool.connection() as conn:
                stmt = query_text.replace("\r\n", "")
                logging.info("queries - stmt: {}".format(stmt))
                async with conn.cursor() as cursor:
                    try:
                        await asyncio.wait_for(cursor.execute(stmt), timeout=30.0)  # timeout in seconds
                        results = await cursor.fetchall()
                        view_data["elapsed_seconds"] = "elapsed_seconds: {}".format(time.time() - start_time)
                        for row in results:
                            #logging.warning("row for qrp: {}".format(row))
                            result_objects.append(qrp.parse(row))
                            results_tuples.append(str(row))
                        
                        view_data["tuples_results_message"] = results_message(
                            "Results as Python Tuples", results_tuples)
                        view_data["tuples_results"] = "\n".join(results_tuples)
                        view_data["query_text"] = query_text
                        view_data["json_results_message"] = results_message(
                            "Results as JSON", result_objects)
                        view_data["json_results"] = json.dumps(
                            result_objects, sort_keys=False, indent=2
                        )
                        graph_data = inline_graph_data(query_text, result_objects)
                        view_data["inline_graph_json"] = graph_data
                        if len(graph_data) > 0:
                            view_data["vis_message"] = "Legal Case Citation Graph"
                        write_query_results_to_file(view_data, result_objects, graph_data)
                    except asyncio.TimeoutError:
                        view_data["error_message"] = "Error: query timeout"
                    except Exception as e:
                        logging.critical((str(e)))
                        view_data["error_message"] = "Error: {}".format(str(e))
        except Exception as e:
            logging.critical((str(e)))
            view_data["error_message"] = "Error: {}".format(str(e))
    return view_data

def results_message(prefix, results_list_object):
    """
    Return a message string for the results of a query, with a singular or plural
    number of rows.
    """
    count = len(results_list_object)
    if count < 2:
        return "{} ({} row):".format(prefix, count)
    else:
        return "{} ({} rows):".format(prefix, count)

def write_query_results_to_file(view_data, result_objects, graph_data):
    """
    Write the query results to a JSON file for visual inspection.
    """
    try:
        data = dict()
        data["view_data"] = dict()
        for key in sorted(view_data.keys()):
            include = True
            if key == 'sample_queries':
                include = False
            if include == True:
                data["view_data"][key] = view_data[key]
        FS.write_json(data, "tmp/query_view_data.json")
        FS.write_json(result_objects, "tmp/query_result_objects.json")
        if graph_data is not None:
            FS.write_json(graph_data, "tmp/query_graph_data.json")
    except Exception as e2:
        logging.warning(str(e2))
        logging.warning(traceback.format_exc())


def queries_view_data(query_text="", query_type="SQL"):
    """
    Return an initial dict with all fields necessary for the
    queries.html view.
    """
    view_data = dict()
    if query_type == "ADMIN":
        view_data["query_type"] = "PG Admin Queries"
        view_data["tutorial_topic"] = "?topic=pg_admin"
        queries = SampleQueries.admin_queries()
    elif query_type == "SQL":
        view_data["query_type"] = "Relational Queries"
        view_data["tutorial_topic"] = "?topic=relational"
        queries = SampleQueries.sql_queries()
    else:
        view_data["query_type"] = "Graph Queries"
        view_data["tutorial_topic"] = "?topic=graph"
        queries = SampleQueries.cypher_queries()

    view_data["sample_queries"] = queries
    view_data["query_text"] = query_text
    view_data["elapsed_seconds"] = ""
    view_data["tuples_results_message"] = ""
    view_data["tuples_results"] = ""
    view_data["tuples_results_message"] = ""
    view_data["json_results_message"] = ""
    view_data["inline_graph_json"] = "{}"
    return view_data

def inline_graph_data(query_text, result_objects):
    wrapper, data = dict(), dict()
    if "$$" in query_text:
        # these two dicts are to ensure uniqueness
        nodes_dict = dict()  # key is id, value is node
        edges_dict = dict()  # key is id, value is node
        data["nodes"] = list()
        data["edges"] = list()
        try:
            for obj in result_objects:
                if isinstance(obj, list):
                    for elem in obj:
                        if isinstance(elem, dict):
                            label = elem["label"]
                            if label == "Case":
                                node = dict()
                                row_id, case_id = str(elem["id"]), str(elem["properties"]["id"])
                                node["rowid"] = row_id
                                node["type"] = label
                                node["id"] = case_id
                                node["url"] = str(elem["properties"]["url"])
                                node["name"] = str(elem["properties"]["name"])
                                node["year"] = str(elem["properties"]["decision_year"])
                                nodes_dict[case_id] = node
                            elif label == "cites":
                                edge = dict()
                                start_id = str(elem["properties"]["case_id"])
                                end_id   = str(elem["properties"]["cited_case_id"])
                                edge["source"] = start_id
                                edge["target"] = end_id
                                edge["case_name"] = str(elem["properties"]["case_name"])
                                edge["cited_case_name"] = str(elem["properties"]["cited_case_name"])
                                edge["rel"] = label
                                edge["weight"] = 1
                                key = '-'.join(sorted([start_id, end_id]))
                                edges_dict[key] = edge
                        elif isinstance(elem, list):
                            for list_elem in elem:
                                label = list_elem["label"]
                                if label == "cites":
                                    edge = dict()
                                    start_id = str(list_elem["properties"]["case_id"])
                                    end_id   = str(list_elem["properties"]["cited_case_id"])
                                    edge["source"] = start_id
                                    edge["target"] = end_id
                                    edge["case_name"] = str(list_elem["properties"]["case_name"])
                                    edge["cited_case_name"] = str(list_elem["properties"]["cited_case_name"])
                                    edge["rel"] = label
                                    edge["weight"] = 1
                                    key = '-'.join(sorted([start_id, end_id]))
                                    edges_dict[key] = edge

            for key in nodes_dict.keys():
                data["nodes"].append(nodes_dict[key])

            for key in edges_dict.keys():
                edge = edges_dict[key]
                data["edges"].append(edge)
                start_id = edge["source"]
                end_id   = edge["target"]
                if start_id in nodes_dict.keys():
                    if end_id in nodes_dict.keys():
                        pass # No need to create a new/dummy node
                    else:
                        new_node = dict()
                        new_node["id"] = end_id
                        new_node["type"] = "Case"
                        new_node["id"] = end_id
                        new_node["url"] = ""
                        new_node["name"] = edge["cited_case_name"]
                        new_node["year"] = ""
                        nodes_dict[end_id] = new_node
                        data["nodes"].append(new_node)
                else:
                    new_node = dict()
                    new_node["id"] = start_id
                    new_node["type"] = "Case"
                    new_node["cid"] = "0"
                    new_node["url"] = ""
                    new_node["name"] = edge["case_name"]
                    new_node["year"] = ""
                    nodes_dict[start_id] = new_node
                    data["nodes"].append(new_node)

            if (len(data["nodes"]) > 0) and (len(data["edges"]) > 0):
                wrapper["graph_data"] = data
            else:
                wrapper["graph_data"] = data  # TODO - remove this else
        except Exception as e:
            logging.critical((str(e)))
            logging.exception(e, stack_info=True, exc_info=True)
    return wrapper


@app.get("/vector_search")
async def get_vector_search(req: Request):
    view_data = vector_search_view_data()
    return views.TemplateResponse(
        request=req, name="vector_search.html", context=view_data
    )


@app.post("/vector_search")
async def post_vector_search(req: Request):
    form_data = await req.form()
    logging.info("/vector_search form_data: {}".format(form_data))
    search_text = form_data.get("search_text").strip()
    search_words = search_text.split()
    embedding = None
    logging.debug("vector_search - search_text: {}".format(search_text))
    view_data = vector_search_view_data(search_text)
    case_name = None

    # First, get the embedding - either from the DB or from the AI service
    if len(search_words) == 0:
        view_data["error_message"] = "No search words provided"
    elif len(search_words) == 1:
        try:
            # Lookup the given legal_case ID in the relational table, and get its embedding
            case_name, embedding = await lookup_legal_case_name_and_embedding(
                req, search_words[0])
            view_data["case_message"] = "Legal Case ID: {}, Name: {}".format(
                search_words[0], case_name)
        except Exception as e:
            view_data["error_message"] = "Error reading the database; {}".format(str(e))
            logging.critical((str(e)))
            logging.exception(e, stack_info=True, exc_info=True)
    else:
        try:
            #ai_svc = AiService()
            ai_svc_resp = req.app.ai_svc.generate_embeddings(search_text)
            embedding = ai_svc_resp.data[0].embedding
        except Exception as e:
            view_data["error_message"] = "Error calling the AiService: {}".format(
                str(e)
            )
            logging.critical((str(e)))
            logging.exception(e, stack_info=True, exc_info=True)

    # Next, execute the vector search vs the DB using the embedding
    if embedding is not None:
        results_list = await execute_vector_search(req, embedding)
        view_data["results_message"] = "Vector Search Results, {} rows:".format(
            len(results_list)
        )
        view_data["results"] = json.dumps(results_list, sort_keys=False, indent=2)

    return views.TemplateResponse(
        request=req, name="vector_search.html", context=view_data
    )


def vector_search_view_data(search_text=""):
    """
    Return an initial dict with the fields necessary for the
    vector_search.html view.
    """
    view_data = dict()
    view_data["tutorial_topic"] = "?topic=vector_search"
    view_data["search_text"] = search_text
    view_data["case_message"] = "" 
    view_data["results_message"] = ""
    view_data["results"] = ""
    return view_data


async def lookup_legal_case_name_and_embedding(req: Request, id) -> list[float] | None:
    """
    Lookup the given ID in the legal_cases table and return
    its name_abbreviation and embedding as a two-tuple.
    """
    case_name = None
    embedding = None
    try:
        sql = "select id, name_abbreviation, embedding from legal_cases where id = {} offset 0 limit 1".format(id)
        logging.info("lookup_legal_case_name_and_embedding - sql: {}".format(sql))
        async with req.app.async_pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql)
                async for row in cursor:
                    case_name = row[1]
                    embedding = json.loads(row[2])
    except Exception as e:
        logging.critical((str(e)))
        logging.exception(e, stack_info=True, exc_info=True)
    return (case_name, embedding)


def legal_cases_vector_search_sql(embeddings, limit=10):
    return (
        """
select id, name_abbreviation, to_char(decision_date, 'YYYY-MM-DD')
 from legal_cases
 order by embedding <-> '{}'
 offset 0 limit 10;
    """.format(
            embeddings
        )
        .replace("\n", " ")
        .strip()
    )

async def execute_vector_search(req: Request, embedding) -> list:
    """Execute a vector search with the given embedding value."""
    result_list = list()
    try:
        sql = legal_cases_vector_search_sql(embedding)
        async with req.app.async_pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql)
                async for row in cursor:
                    result_list.append(row)
    except Exception as e:
        logging.critical((str(e)))
        logging.exception(e, stack_info=True, exc_info=True)
    return result_list


@app.get("/opencypher_gen")
async def get_opencypher_gen(req: Request):
    view_data = opencypher_gen_view_data()
    return views.TemplateResponse(
        request=req, name="opencypher_gen.html", context=view_data
    )


@app.post("/opencypher_gen")
async def post_opencypher_gen(req: Request):
    form_data = await req.form()
    logging.info("/opencypher_gen form_data: {}".format(form_data))
    view_data = opencypher_gen_view_data()
    natural_language = form_data.get("natural_language")
    cypher = form_data.get("cypher")

    if natural_language is not None:
        view_data["natural_language"] = natural_language
        # TODO - call the AI service to generate the Cypher

    elif cypher is not None:
        view_data["cypher"] = cypher
        # TODO - execute the given cypher query

    return views.TemplateResponse(
        request=req, name="opencypher_gen.html", context=view_data
    )


def opencypher_gen_view_data(query_text=""):
    """
    Return an initial dict with all fields necessary for the
    opencypher_gen.html view.
    """
    view_data = dict()
    view_data["tutorial_topic"] = "?topic=cypher_gen_ai"
    view_data["natural_language"] = ""
    view_data["cypher"] = ""
    view_data["results_message"] = ""
    view_data["results"] = ""
    view_data["elapsed_seconds"] = ""
    return view_data

def checkbox_checked(form_data, html_id):
    try:
        value = form_data.get(html_id)
        if value is not None:
            return True
    except Exception as e:
        pass
    return False
