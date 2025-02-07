"""
Execute the four-step data wrangling process for the 'cases.sql' file
to reduce it to a smaller set of legal cases that are linked and suitable
for use in an Apache AGE graph.  This wrangling process retains the original
embedding values for each identified legal case.
THIS PRIVATE SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
Usage:
    python dev_wrangle_legal_cases.py step1_scan_sqlfile_for_citations <cases-sql-infile>
    python dev_wrangle_legal_cases.py step1_scan_sqlfile_for_citations /Users/chjoakim/Downloads/cases.sql
    python dev_wrangle_legal_cases.py step2_link_cases_from_seeds <iterations>
    python dev_wrangle_legal_cases.py step2_link_cases_from_seeds 10
    python dev_wrangle_legal_cases.py step3_extract_subset_from_sqlfile <cases-sql-infile> <iteration-infile>
    python dev_wrangle_legal_cases.py step3_extract_subset_from_sqlfile /Users/chjoakim/Downloads/cases.sql tmp/iteration_4.json
    python dev_wrangle_legal_cases.py step4_create_cypher_load_file <graphname> <iteration-infile>
    python dev_wrangle_legal_cases.py step4_create_cypher_load_file legal_cases tmp/iteration_4.json
    python dev_wrangle_legal_cases.py step5_scan_cypher_load_file
    python dev_wrangle_legal_cases.py step6_reformat_cases_sql_subset
    python dev_wrangle_legal_cases.py step7_create_csv_load_files
    python dev_wrangle_legal_cases.py adhoc_link_analysis
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# THIS PRIVATE SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
# Chris Joakim, Microsoft

import json
import logging
import os
import sys
import time
import traceback

from docopt import docopt
from dotenv import load_dotenv

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from src.services.ai_service import AiService
from src.services.logging_level_service import LoggingLevelService

from src.util.cite_parser import CiteParser
from src.util.counter import Counter
from src.util.fs import FS
from src.util.template import Template

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
)

# These are the two primary output files produced by this script.
# The Ant script in the ../data/legal_cases directory produces zip
# files for each of these.
age_load_stmts_sql_file = "../data/legal_cases/age_load_statments.sql"
legal_cases_sql_file = "../data/legal_cases/legal_cases.sql"


def print_options(msg):
    """
    Use the docopt python library to display the script
    usage comments at the top of this module.
    """
    print("{} {}".format(os.path.basename(__file__), msg))
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def step1_scan_sqlfile_for_citations(cases_sql_infile: str):
    """
    Read the cases.sql file, parse the JSON in each line, and calculate
    each case url and its citations.
    """
    print(
        "step1_scan_sqlfile_for_citations, reading infile: {}".format(cases_sql_infile)
    )
    data_lines_read, json_parse_ok, json_parse_fail = 0, 0, 0
    case_id_dict = dict()  # key is the case id, value is its metadata
    seeds = initial_seeds()
    start_time = time.time()

    if len(seeds.keys()) < 7:
        print("Error: seeds length: {}".format(len(seeds)))
        return
    print("seeds: {} {}".format(len(seeds), sorted(seeds.keys())))

    with open(cases_sql_infile, "r", encoding="ISO-8859-1") as file:
        for line in file:
            stripped = line.strip()
            if len(stripped) > 10:
                tokens = stripped.split("\t")
                if len(tokens) == 3:
                    try:
                        data_lines_read = data_lines_read + 1
                        if data_lines_read < 999999:
                            if data_lines_read % 1000 == 0:
                                print("data lines read: {}".format(data_lines_read))
                            id, json_str, embeddings = (
                                tokens[0].strip(),
                                tokens[1].strip(),
                                tokens[2].strip(),
                            )
                            try:
                                case_doc = json.loads(json_str)
                                json_parse_ok = json_parse_ok + 1
                                id = str(case_doc["id"])
                                calculate_url(case_doc)
                                collect_cites_to(case_doc)
                                metadata = dict()
                                metadata["id"] = id
                                metadata["name_abbreviation"] = case_doc[
                                    "name_abbreviation"
                                ]
                                metadata["court"] = case_doc["court"]["name"]
                                metadata["court_id"] = case_doc["court"]["id"]
                                metadata["decision_year"] = get_decison_date(case_doc)
                                metadata["__case_url"] = case_doc["__case_url"]
                                metadata["__citations"] = case_doc["__citations"]
                                case_id_dict[id] = metadata
                                # Write the original seed documents to better understand the data
                                if id in seeds.keys():
                                    outfile = "tmp/{}.json".format(id)
                                    FS.write_json(case_doc, outfile)
                            except Exception as jpe:
                                json_parse_fail = json_parse_fail + 1
                    except Exception as e:
                        print("Exception: {}".format(e))
                        print(traceback.format_exc())
                        print(
                            "Exception line {} {} tokens: {} prefix: |{}|".format(
                                data_lines_read,
                                len(stripped),
                                len(tokens),
                                stripped[0:40],
                            )
                        )

    elapsed_time = time.time() - start_time
    print("data lines read: {}".format(data_lines_read))
    print("elapsed time: {} seconds".format(elapsed_time))
    print(
        "json_parse_ok: {} json_parse_fail: {}".format(json_parse_ok, json_parse_fail)
    )
    FS.write_json(case_id_dict, "tmp/case_id_dict.json")
    print("case_id_dict size: {}".format(len(case_id_dict.keys())))

    # flip the above case_id_dict to use the '__case_url' as the key
    case_url_dict = dict()
    for id in case_id_dict.keys():
        metadata = case_id_dict[id]
        case_url = metadata["__case_url"]
        case_url_dict[case_url] = metadata
    FS.write_json(case_url_dict, "tmp/case_url_dict.json")
    print("case_url_dict size: {}".format(len(case_url_dict.keys())))

    cite_parser_dict = CiteParser.get_parsed_values()
    FS.write_json(cite_parser_dict, "tmp/cite_parser.json")
    print("cite_parser_dict size: {}".format(len(cite_parser_dict.keys())))


def initial_seeds():
    infile = "../data/legal_cases/case_seeds_edited.txt"
    lines = FS.read_lines(infile)
    seeds = dict()
    for line in lines:
        tokens = line.split("|")
        if len(tokens) > 1:
            id = tokens[0].strip()
            seeds[id] = tokens[1].strip()
    return seeds


def calculate_url(case_doc):
    """
    Calculate the url for the case document like:
    https://static.case.law/wash/184/cases/0560-01.json
    Populate the '__case_url' in the given case_doc.
    """
    try:
        url_key = "__case_url"
        case_doc[url_key] = "?"
        if "file_name" in case_doc.keys():  # this is expected
            file_name = case_doc["file_name"].strip()
            if "citations" in case_doc.keys():
                cite = case_doc["citations"][0]["cite"]
                cite_parser = CiteParser()
                url = cite_parser.parse(cite, file_name)
                if url is not None:
                    case_doc[url_key] = url
    except Exception as e:
        pass


def collect_cites_to(case_doc):
    citations = list()
    citations_key = "__citations"
    case_doc[citations_key] = citations
    cite_parser = CiteParser()

    try:
        for citation in case_doc["cites_to"]:
            cite = citation["cite"]
            url = cite_parser.parse(cite, None)
            if url is not None:
                citations.append(url)
    except Exception as e:
        pass


def get_court_abbrev(case_doc):
    try:
        abbrev = case_doc["court"]["name_abbreviation"]
        return abbrev.strip().replace(".", "").lower()
    except Exception as e:
        return "?"


def get_decison_date(case_doc):
    try:
        return int(case_doc["decision_date"][0:4])
    except Exception as e:
        return -1


def step2_link_cases_from_seeds(iteration_count: int):
    print("step2_link_cases_from_seeds, iteration_count: {}".format(iteration_count))

    case_id_dict = FS.read_json("tmp/case_id_dict.json")
    case_url_dict = FS.read_json("tmp/case_url_dict.json")
    collected_metadata = dict()  # key is the case url, value is the metadata

    for n in range(iteration_count):
        print("iteration: {}".format(n))
        if n == 0:
            seeds = initial_seeds()
            for seed in seeds:
                print("seed: {}".format(seed))
                if seed in case_id_dict.keys():
                    meta = case_id_dict[seed]
                    meta["iteration"] = n
                    meta["citations_gathered"] = 1
                    url = meta["__case_url"]
                    collected_metadata[url] = meta
                    for url in meta["__citations"]:
                        if url not in collected_metadata.keys():
                            if url in case_url_dict.keys():
                                citation_meta = case_url_dict[url]
                                citation_meta["iteration"] = n + 1
                                citation_meta["citations_gathered"] = (
                                    0  # not yet gathered
                                )
                                collected_metadata[url] = citation_meta
        else:
            metadata_keys = collected_metadata.keys()
            print(
                "iteration {} collected_metadata keys count: {}".format(
                    n, len(metadata_keys)
                )
            )
            for collected_url in sorted(metadata_keys):
                if collected_url in case_url_dict.keys():
                    meta = case_url_dict[collected_url]
                    if "citations_gathered" in meta.keys():
                        if meta["citations_gathered"] == 1:
                            pass  # already gathered its' cites_to citations
                        else:
                            # print("collected_url: {}".format(collected_url))
                            for cite_url in meta["__citations"]:
                                if cite_url not in collected_metadata.keys():
                                    if cite_url in case_url_dict.keys():
                                        citation_meta = case_url_dict[cite_url]
                                        citation_meta["iteration"] = n + 1
                                        citation_meta["citations_gathered"] = 0
                                        collected_metadata[cite_url] = citation_meta
                            meta["citations_gathered"] == 1
        FS.write_json(collected_metadata, "tmp/iteration_{}.json".format(n))


def step3_extract_subset_from_sqlfile(cases_sql_infile: str, iteration_infile: str):
    print(
        "step3_extract_subset_from_sqlfile, reading iteration_infile: {}".format(
            iteration_infile
        )
    )
    collected_metadata = FS.read_json(iteration_infile)
    collected_ids = dict()
    output_lines = list()

    for url in collected_metadata.keys():
        meta = collected_metadata[url]
        id = meta["id"]
        collected_ids[id] = id
        print("adding id: {}".format(id))

    print("collected_ids size: {}".format(len(collected_ids.keys())))

    with open(cases_sql_infile, "r", encoding="ISO-8859-1") as file:
        for line in file:
            stripped = line.strip()
            if len(stripped) > 10:
                tokens = stripped.split("\t")
                if len(tokens) == 3:
                    id = tokens[0].strip()
                    if id in collected_ids.keys():
                        print("match on id: {}".format(id))
                        output_lines.append(stripped)

    FS.write_lines(output_lines, "tmp/filtered_cases.sql")
    print("output_lines size: {}".format(len(output_lines)))


def step4_create_cypher_load_file(graphname, iteration_infile):
    """
    Create a sql statements file that can be used to load the Apache AGE graph.
    The 'iteration_infile' arg was produced in step3 above, and can be used to
    specify small or medium or larger graphs per then number of iterations from
    the original seed cases.
    """
    collected_metadata = FS.read_json(iteration_infile)
    vertex_lines, edge_lines, output_lines = list(), list(), list()

    # Example metadata:
    #   "https://static.case.law/wash/79/cases/0643-01.json": {
    #     "id": "594079",
    #     "name_abbreviation": "Martindale Clothing Co. v. Spokane & Eastern Trust Co.",
    #     "court": "Washington Supreme Court",
    #     "court_id": 9029,
    #     "decision_year": 1914,
    #     "__case_url": "https://static.case.law/wash/79/cases/0643-01.json",
    #     "__citations": [
    #       "https://static.case.law/wash/75/cases/0439-01.json",
    #       "https://static.case.law/wash/75/cases/0255-01.json",
    #       "https://static.case.law/wash/77/cases/0320-01.json",
    #       "https://static.case.law/me/76/cases/0335-01.json",
    #       "https://static.case.law/me/74/cases/0315-01.json"
    #     ],
    #     "iteration": 0,
    #     "citations_gathered": 1
    #   },

    case_vertex_template = get_template("create_cypher_case_vertex.txt")
    citation_edge_template = get_template("create_cypher_case_citation_edge.txt")
    metadata_keys = collected_metadata.keys()

    for case_url in sorted(metadata_keys):
        case1_meta = collected_metadata[case_url]
        values = get_template_values_for_case_vertex(graphname, case1_meta)
        if len(values.keys()) == 8:
            cypher = Template.render(case_vertex_template, values)
            vertex_lines.append(cypher.replace("\n", " ").strip())
        else:
            print("Error - malformed case_meta values for url: {}".format(case_url))
            print(str(values))

        for cite_url in case1_meta["__citations"]:
            if cite_url in metadata_keys:
                case2_meta = collected_metadata[cite_url]
                values = get_template_values_for_case_citation_edge(
                    graphname, "cites", case1_meta, case2_meta
                )
                if len(values.keys()) == 9:
                    cypher = Template.render(citation_edge_template, values)
                    edge_lines.append(cypher.replace("\n", " ").strip())
                values = get_template_values_for_case_citation_edge(
                    graphname, "cited_by", case2_meta, case1_meta
                )
                if len(values.keys()) == 9:
                    cypher = Template.render(citation_edge_template, values)
                    edge_lines.append(cypher.replace("\n", " ").strip())

    # write the output file, containing the verties first, then the edges, both sorted

    output_lines.append('SET search_path = ag_catalog, "$user", public;')
    # output_lines.append('SET AUTOCOMMIT to ON;')

    for line in sorted(vertex_lines):
        output_lines.append(line)
    for line in sorted(edge_lines):
        output_lines.append(line)
    FS.write_lines(output_lines, age_load_stmts_sql_file)
    vertex_lines_count = len(vertex_lines)
    edge_lines_count = len(edge_lines)
    total_lines_count = len(output_lines)
    print(
        "vertices: {}, edges: {}, total: {}".format(
            vertex_lines_count, edge_lines_count, total_lines_count
        )
    )


def get_template(template_name):
    return Template.get_template(os.getcwd(), template_name)


def get_template_values_for_case_vertex(graphname, case_meta):
    values = dict()
    try:
        values["graphname"] = graphname
        values["id"] = case_meta["id"]
        values["url"] = case_meta["__case_url"]
        values["name"] = case_meta["name_abbreviation"]
        values["court"] = case_meta["court"]
        values["court_id"] = case_meta["court_id"]
        values["decision_year"] = case_meta["decision_year"]
        values["citation_count"] = len(case_meta["__citations"])
    except Exception as e:
        print(str(e))
    return values


def get_template_values_for_case_citation_edge(
    graphname, relname, case1_meta, case2_meta
):
    values = dict()
    try:
        values["graphname"] = graphname
        values["relname"] = relname
        values["id1"] = case1_meta["id"]
        values["id2"] = case2_meta["id"]
        values["case_name"] = case1_meta["name_abbreviation"]
        values["cited_case_name"] = case2_meta["name_abbreviation"]
        values["cited_case_year"] = case2_meta["decision_year"]
        values["case_id"] = case1_meta["id"]
        values["cited_case_id"] = case2_meta["id"]
    except Exception as e:
        print(str(e))
    return values


def step5_scan_cypher_load_file():
    seeds = initial_seeds()
    print("seeds keys: {}".format(seeds.keys()))
    load_statements = FS.read_lines(age_load_stmts_sql_file)
    print("load_statements size: {}".format(len(load_statements)))
    for seed in sorted(seeds):
        print("===")
        print("seed: {}".format(seed))
        for line_idx, line in enumerate(load_statements):
            if seed in line:
                # print(line)
                print("{}: {}".format(line_idx, line))


def step6_reformat_cases_sql_subset():
    """
    Reformat the 'filtered_cases.sql' TSV file to have additional columns
    for the new 'legal_cases' table in this project
    """
    case_id_meta_dict = FS.read_json("tmp/case_id_dict.json")
    infile = "tmp/filtered_cases.sql"
    output_lines = list()
    nltk.download("stopwords")
    nltk.download("punkt_tab")
    stop_words = set(stopwords.words("english"))
    print("stop_words: {} {}".format(len(stop_words), stop_words))

    if "--vectorize" in sys.argv:
        ai_svc = AiService()
        try:
            resp = AiService.generate_embeddings(
                ai_svc, "postgresql with apache age is powerful"
            )
            embedding = resp.data[0].embedding
            # print("canary embedding: {}".format(embedding))
            print("sleeping for 5 seconds...")
            time.sleep(5)
        except Exception as ee:
            print("Error: embedding generation failed: {}".format(ee))

    lines = FS.read_lines(infile)
    for line_idx, line in enumerate(lines):
        # the input TSV has these three columns/tokens:
        tokens = line.split("\t")
        id_str = tokens[0].strip()
        id = int(id_str)
        json_str = tokens[1].strip()
        embedding = tokens[2].strip()

        # pluck these additional attributes from the json_str/json_obj:
        json_obj = json.loads(json_str)
        name = json_obj["name"]
        abbrv = json_obj["name_abbreviation"]
        decision_date = json_obj["decision_date"]
        court_name = json_obj["court"]["name"]

        # get the case_url and citation_count attributes from the metdata file
        if id_str in case_id_meta_dict.keys():
            meta = case_id_meta_dict[id_str]
            json_obj["case_url"] = meta["__case_url"]
            json_obj["citation_count"] = len(meta["__citations"])
        else:
            json_obj["case_url"] = ""
            json_obj["citation_count"] = "0"
            print("Error: id {} not in case_id_meta_dict".format(id_str))
        text_data = json.dumps(json_obj)  # json serialize the updated json_obj

        if "--vectorize" in sys.argv:
            try:
                # construct a string to pass to the embeddings model,
                # truncate to 8190 characters per model limit.
                text_parts = list()
                text_parts.append("name: {}".format(abbrv))
                text_parts.append("decision date: {}".format(decision_date))
                text_parts.append(
                    "parties: {}".format(json.dumps(json_obj["casebody"]["parties"]))
                )
                text_parts.append(
                    "opinions: {}".format(json.dumps(json_obj["casebody"]["opinions"]))
                )
                text_data = "\n".join(text_parts)
                print(
                    "vectorize text_data, raw - line: {}, id: {}, len: {}".format(
                        line_idx, id_str, len(text_data)
                    )
                )
                # use the nltk tokenizer to remove stopwords
                word_tokens = word_tokenize(text_data)
                normalize_to_lowercase = True
                if normalize_to_lowercase == True:
                    filtered_words = [
                        w for w in word_tokens if not w.lower() in stop_words
                    ]
                else:
                    filtered_words = list()
                    for w in word_tokens:
                        if w not in stop_words:
                            filtered_words.append(w)
                text_data = (
                    "\n".join(filtered_words)
                    .replace("\\n", " ")
                    .replace("\n", " ")
                    .replace("  ", " ")
                )
                print(
                    "vectorize text_data, filtered - line: {}, id: {}, len: {}".format(
                        line_idx, id_str, len(text_data)
                    )
                )
                # print("final text_data: {}".format(text_data))
                truncated_text_data = text_data[0:8190]
                resp = AiService.generate_embeddings(ai_svc, truncated_text_data)
                embedding = resp.data[0].embedding
                # capacity_tpm = 240000
                # capacity_tps = capacity_tpm / 60
                time.sleep(2.1)
            except Exception as ee:
                print("Error: embedding generation failed: {}".format(ee))

        # build the new augmented TSV line with the additional fields to match the DDL
        template = ("{}\t" * 10).strip()
        tsv_line = template.format(
            id,
            name,
            abbrv,
            json_obj["case_url"],
            decision_date,
            court_name,
            json_obj["citation_count"],
            text_data,
            json.dumps(json_obj),
            embedding,
        )
        output_lines.append(tsv_line)
        new_tokens = tsv_line.split("\t")
        if len(new_tokens) != 10:
            print("Error: malformed new tsv_line: {}".format(tsv_line))

    FS.write_lines(output_lines, legal_cases_sql_file)
    print("output_lines size: {}".format(len(output_lines)))


def step7_create_csv_load_files(iteration_infile):
    print("step7_create_csv_load_files")
    case_url_dict = FS.read_json(iteration_infile)
    print("case_id_dict size: {}".format(len(case_url_dict.keys())))  # 438897

    case_attr_names = "id,name,court,decision_year,case_url,citation_count".split(",")
    node_lines, cites_lines, cited_by_lines = list(), list(), list()
    node_lines.append(",".join(case_attr_names))

    edge_header = "start_id,start_vertex_type,end_id,end_vertex_type,case_id,other_id,case_year,other_year"
    cites_lines.append(edge_header)
    cited_by_lines.append(edge_header)

    for case_url in case_url_dict.keys():
        doc = case_url_dict[case_url]
        id = doc["id"]
        name = doc["name_abbreviation"].replace(",", "")
        court = doc["court"].replace(",", "")
        year = doc["decision_year"]
        citation_count = len(doc["__citations"])
        node_line = "{},{},{},{},{},{}".format(
            id, name, court, year, case_url, citation_count
        )
        node_lines.append(node_line)

        for cite_url in doc["__citations"]:
            if cite_url in case_url_dict.keys():
                cite_doc = case_url_dict[cite_url]
                cited_id = cite_doc["id"]
                cited_year = cite_doc["decision_year"]

                # create edge type: cites
                edge_line = "{},Case,{},Case,{},{},{},{}".format(
                    id,
                    cited_id,
                    id,
                    year,
                    cited_id,
                    cited_year,
                )
                cites_lines.append(edge_line)

                # first 4: start_id,start_vertex_type,end_id,end_vertex_type
                #  last 4: case_id,case_year,other_id,other_year

                # create edge type: cited_by
                edge_line = "{},Case,{},Case,{},{},{},{}".format(
                    cited_id, id, cited_id, cited_year, id, year
                )
                cited_by_lines.append(edge_line)

    # Write the three CSV files
    FS.write_lines(node_lines, "tmp/legal_cases_case_vertices.csv")
    FS.write_lines(cites_lines, "tmp/legal_cases_cites_edges.csv")
    FS.write_lines(cited_by_lines, "tmp/legal_cases_cited_by_edges.csv")
    print("node_lines     size: {}".format(len(node_lines)))
    print("cites_lines    size: {}".format(len(cites_lines)))
    print("cited_by_lines size: {}".format(len(cited_by_lines)))


def adhoc_link_analysis():
    """
    Results:
    seeds keys: dict_keys(['1017660', '12101563', '1095193', '594079', '999494', '1005731', '1086651', '1789753'])
    ['1017660', '594079', '552848', '2417036', '1008240', '1002142', '999413', '2498126', '4976967']
    ['1095193', '1239473', '477678', '622661']
    ['594079', '622661', '615468']
    ['999494', '996526', '807253', '762307', '568326', '660528', '1283434', '4978096']
    ['1005731', '999373', '1002136', '1002129']
    ['1086651', '11337871']
    ['1789753']
    """
    seeds = initial_seeds()
    print("seeds keys: {}".format(seeds.keys()))
    infile = "../data/legal_cases/case_url_dict.json"
    case_url_dict, case_id_dict = FS.read_json(infile), dict()
    print("read infile {}, has {} keys".format(infile, len(case_url_dict.keys())))
    for idx, url in enumerate(case_url_dict.keys()):
        id = case_url_dict[url]["id"]
        case_id_dict[id] = url
        if idx == 10:
            print(case_id_dict)
    FS.write_json(case_id_dict, "tmp/cd.json")

    for seed_id in seeds.keys():
        traverse(seed_id, [seed_id], case_id_dict, case_url_dict)


def traverse(id, path_array, case_id_dict, case_url_dict):
    if id in case_id_dict.keys():
        print(path_array)
        if len(path_array) > 10:
            print("recursion error, > 10")
        else:
            url1 = case_id_dict[id]
            if url1 in case_url_dict.keys():
                meta1 = case_url_dict[url1]
                for url2 in meta1["__citations"]:
                    if url2 in case_url_dict.keys():
                        meta2 = case_url_dict[url2]
                        id2 = meta2["id"]
                        if id2 in path_array:
                            pass
                        else:
                            path_array.append(id2)
                            traverse(id, path_array, case_id_dict, case_url_dict)


if __name__ == "__main__":
    load_dotenv(override=True)
    logging.basicConfig(
        format="%(asctime)s - %(message)s", level=LoggingLevelService.get_level()
    )
    if len(sys.argv) < 2:
        print_options("Error: invalid command-line")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "step1_scan_sqlfile_for_citations":
                cases_sql_infile = sys.argv[2]
                step1_scan_sqlfile_for_citations(cases_sql_infile)
            elif func == "step2_link_cases_from_seeds":
                iteration_count = int(sys.argv[2])
                step2_link_cases_from_seeds(iteration_count)
            elif func == "step3_extract_subset_from_sqlfile":
                cases_sql_infile = sys.argv[2]
                iteration_infile = sys.argv[3]
                step3_extract_subset_from_sqlfile(cases_sql_infile, iteration_infile)
            elif func == "step4_create_cypher_load_file":
                graphname = sys.argv[2]
                iteration_infile = sys.argv[3]
                print(sys.argv)
                step4_create_cypher_load_file(graphname, iteration_infile)
            elif func == "step5_scan_cypher_load_file":
                step5_scan_cypher_load_file()
            elif func == "step6_reformat_cases_sql_subset":
                step6_reformat_cases_sql_subset()
            elif func == "step7_create_csv_load_files":
                iteration_infile = sys.argv[2]
                step7_create_csv_load_files(iteration_infile)
            elif func == "adhoc_link_analysis":
                adhoc_link_analysis()
            else:
                print_options("Error: invalid function: {}".format(func))
        except Exception as e:
            logging.critical(str(e))
            logging.exception(e, stack_info=True, exc_info=True)
