import logging
import os

import tiktoken

from openai import AzureOpenAI

from src.services.config_service import ConfigService
from src.services.ai_completion import AiCompletion
from src.util.template import Template

# Instances of this class are used to execute AzureOpenAI functionality.
# Chris Joakim, 3Cloud


class AiService:
    """Constructor method; call initialize() immediately after this."""

    def __init__(self, opts={}):
        """
        Get the necessary environment variables and initialze an AzureOpenAI client.
        Also read the OWL file.
        """
        try:
            self.opts = opts
            self.aoai_endpoint = ConfigService.azure_openai_url()
            self.aoai_api_key = ConfigService.azure_openai_key()
            self.aoai_version = ConfigService.azure_openai_version()
            self.chat_function = None
            self.max_ntokens = ConfigService.truncate_llm_context_max_ntokens()

            # tiktoken, for token estimation, doesn't work with gpt-4 at this time
            self.tiktoken_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            self.enc = tiktoken.get_encoding("cl100k_base")

            self.aoai_client = AzureOpenAI(
                azure_endpoint=self.aoai_endpoint,
                api_key=self.aoai_api_key,
                api_version=self.aoai_version,
            )
            self.completions_deployment = (
                # deployment name/model = gpt4/gpt-4
                ConfigService.azure_openai_completions_deployment()
            )
            self.embeddings_deployment = (
                # deployment name/model = embeddings/text-embedding-ada-002
                ConfigService.azure_openai_embeddings_deployment()
            )
            logging.info("aoai endpoint:     {}".format(self.aoai_endpoint))
            logging.info("aoai version:      {}".format(self.aoai_version))
            logging.info("aoai client:       {}".format(self.aoai_client))
            logging.info(
                "aoai completions_deployment: {}".format(self.completions_deployment)
            )
            logging.info(
                "aoai embeddings_deployment:  {}".format(self.embeddings_deployment)
            )
        except Exception as e:
            logging.critical("Exception in AiService#__init__: {}".format(str(e)))
            logging.exception(e, stack_info=True, exc_info=True)
            return None

    def num_tokens_from_string(self, s: str) -> int:
        try:
            return len(self.tiktoken_encoding.encode(s))
        except Exception as e:
            logging.critical(
                "Exception in AiService#num_tokens_from_string: {}".format(str(e))
            )
            logging.exception(e, stack_info=True, exc_info=True)
            return 10000

    def generate_embeddings(self, text):
        """
        Generate an embeddings array from the given text.
        Return an CreateEmbeddingResponse object or None.
        Invoke 'resp.data[0].embedding' to get the array of 1536 floats.
        """
        try:
            # <class 'openai.types.create_embedding_response.CreateEmbeddingResponse'>
            return self.aoai_client.embeddings.create(
                input=text, model=self.embeddings_deployment
            )
        except Exception as e:
            logging.critical(
                "Exception in AiService#generate_embeddings: {}".format(str(e))
            )
            logging.exception(e, stack_info=True, exc_info=True)
            return None

    def text_to_chunks(self, text):
        max_chunk_size, chunks = 2048, list()
        current_chunk = ""
        for sentence in text.split("."):
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + "."
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def generate_cypher_from_user_prompt(self, resp_obj):
        """
        Generate a Cypher query from the user's prompt.
        """
        try:
            natural_language = resp_obj["natural_language"]
            system_prompt = self.generate_cypher_system_prompt(natural_language)
            logging.info("system_prompt: {}".format(system_prompt))
            resp_obj["system_prompt1"] = system_prompt

            completion = self.aoai_client.chat.completions.create(
                model=self.completions_deployment,
                temperature=ConfigService.cypher_temperature(),
                response_format={"type": "text"},
                messages=[{"role": "system", "content": system_prompt}],
            )
            cypher = completion.choices[0].message.content.strip()
            resp_obj["cypher"] = cypher
        except Exception as e:
            logging.critical(
                "Exception in AiService#generate_cypher_from_user_prompt: {}".format(
                    str(e)
                )
            )
            logging.exception(e, stack_info=True, exc_info=True)
            return None
        return resp_obj

    def wrap_opencypher_in_age_sql(self, resp_obj):
        """
        Generate a Cypher query from the user's prompt.

        The above generate_cypher_from_user_prompt() method generates an openCypher query.
        This method takes that generated openCypher query and wraps it in an AGE SQL query.
        """
        try:
            open_cypher = resp_obj["cypher"]
            graph_name = resp_obj["graph_name"]
            system_prompt = self.wrap_opencypher_in_age_sql_system_prompt(
                graph_name, open_cypher
            )
            logging.info("system_prompt: {}".format(system_prompt))
            resp_obj["system_prompt"] = system_prompt

            completion = self.aoai_client.chat.completions.create(
                model=self.completions_deployment,
                temperature=ConfigService.cypher_temperature(),
                response_format={"type": "text"},
                messages=[{"role": "system", "content": system_prompt}],
            )
            query_text = completion.choices[0].message.content.strip()
            resp_obj["query_text"] = query_text
        except Exception as e:
            logging.critical(
                "Exception in AiService#wrap_opencypher_in_age_sql: {}".format(str(e))
            )
            logging.exception(e, stack_info=True, exc_info=True)
            return None
        return resp_obj

    def generate_cypher_system_prompt(self, natural_language) -> str:
        """
        Generate and return the system prompt for the LLM, given the natural language.

        The actual prompt is a Jinja2 text template so as to enable easier editing of it,
        and altering it at runtime without causing the webapp to restart.
        """
        t = Template.get_template(os.getcwd(), "cypher_gen_llm_prompt.txt")
        assert t != None
        values = dict()
        values["natural_language"] = str(natural_language).strip()
        return Template.render(t, values)

    def wrap_opencypher_in_age_sql_system_prompt(
        self, graph_name: str, open_cypher: str
    ) -> str:
        """
        Generate and return the system prompt for the LLM, given the open_cypher text.

        The actual prompt is a Jinja2 text template so as to enable easier editing of it,
        and altering it at runtime without causing the webapp to restart.
        """
        t = Template.get_template(os.getcwd(), "wrap_opencypher_in_age_sql.txt")
        assert t != None
        values = dict()
        values["graph_name"] = str(graph_name).strip()
        values["open_cypher"] = str(open_cypher).strip()
        return Template.render(t, values)
