import os
import sys
import pytest

from dotenv import load_dotenv

from src.services.config_service import ConfigService

# pytest -v tests/test_config_service.py


def test_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.envvar("SAMPLE_IATA_CODE") == "CLT"
    assert ConfigService.envvar("MISSING") == ""
    assert ConfigService.envvar("MISSING", None) == None
    assert ConfigService.envvar("UNIVERSAL_ANSWER", "42") == "42"


def test_int_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.int_envvar("SAMPLE_INT_VAR") == 98
    assert ConfigService.int_envvar("MISSING") == -1
    assert ConfigService.int_envvar("AIG4PG_GRAPH_SOURCE_TYPE") == -1
    assert ConfigService.int_envvar("MISSING", 13) == 13
    assert ConfigService.int_envvar("SAMPLE_IATA_CODE", 13) == 13


def test_float_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.float_envvar("SAMPLE_FLOAT_VAR") == 98.6
    assert ConfigService.float_envvar("MISSING") == -1.0
    assert ConfigService.float_envvar("AIG4PG_GRAPH_SOURCE_TYPE") == -1.0
    assert ConfigService.float_envvar("MISSING", 13.1) == 13.1
    assert ConfigService.float_envvar("SAMPLE_IATA_CODE", 13.1) == 13.1


def test_boolean_envvar():
    ConfigService.set_standard_unit_test_env_vars()
    os.environ["TRUE_ARG"] = "TRuE"
    os.environ["FALSE_ARG"] = "FALse"
    os.environ["T_ARG"] = "t"
    os.environ["F_ARG"] = "F"
    os.environ["YES_ARG"] = "yeS"
    os.environ["Y_ARG"] = "Y"
    os.environ["N_ARG"] = "N"
    assert ConfigService.boolean_envvar("MISSING", True) == True
    assert ConfigService.boolean_envvar("MISSING", False) == False
    assert ConfigService.boolean_envvar("TRUE_ARG", False) == True
    assert ConfigService.boolean_envvar("FALSE_ARG", True) == False
    assert ConfigService.boolean_envvar("T_ARG", False) == True
    assert ConfigService.boolean_envvar("F_ARG", True) == False
    assert ConfigService.boolean_envvar("YES_ARG", False) == True
    assert ConfigService.boolean_envvar("Y_ARG", False) == True
    assert ConfigService.boolean_envvar("N_ARG", True) == False


def test_boolean_arg():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.boolean_arg(sys.argv[0]) == True
    assert ConfigService.boolean_arg("MISSING") == False


def test_project_version():
    assert ConfigService.project_version() == "0.9.0, 2024/11/10"


def test_defined_and_sample_environment_variables():
    ConfigService.print_defined_env_vars()
    defined = ConfigService.defined_environment_variables()
    samples = ConfigService.sample_environment_variable_values()
    assert "AIG4PG_LOG_LEVEL" in defined.keys()
    assert "AIG4PG_LOG_LEVEL" in samples.keys()
    assert len(defined.keys()) == 16
    assert len(samples.keys()) == 13


def test_log_defined_env_vars():
    try:
        ConfigService.log_defined_env_vars()
        assert True
    except Exception as e:
        assert False


def test_azure_postgresql_variables():
    ConfigService.set_standard_unit_test_env_vars()
    assert ConfigService.postgresql_server() == "gbbcj.postgres.database.azure.com"
    assert ConfigService.postgresql_port() == "5432"
    assert ConfigService.postgresql_database() == "aig"
    assert ConfigService.postgresql_user() == "cj"
    assert ConfigService.postgresql_password() == "topSECRET!"


def test_azure_openai_variables():
    ConfigService.set_standard_unit_test_env_vars()
    assert (
        ConfigService.azure_openai_url() == "https://gbbcjcaigopenai3.openai.azure.com/"
    )
    assert ConfigService.azure_openai_key() == "xj48"
    assert ConfigService.azure_openai_embeddings_deployment() == "embeddings"
    assert ConfigService.azure_openai_completions_deployment() == "gpt4"

    version = ConfigService.azure_openai_version()
    assert version.startswith("2023")


def test_verbose():
    # this is a challenge to test as tests.ps1 contains -v itself!
    # pytest -v --cov=pysrc/ --cov-report html tests/
    if "-v" in sys.argv:
        assert ConfigService.verbose() == True
    else:
        assert ConfigService.verbose() == False

    assert ConfigService.verbose(["-wordy"]) == False


def test_epoch():
    e = ConfigService.epoch()
    print(e)
    assert e > 1730061780  # 2024-10-27
    assert e < 1800000000

