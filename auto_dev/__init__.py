import base64
import os
from typing import Any
import yaml
from langchain.chat_models import AzureChatOpenAI


def insert_secrets_to_config(secrets: dict[str, Any], config: dict[str, Any]):
    secrets_ref_expr = '$secret:'
    for key, value in config.items():
        if isinstance(value, dict):
            insert_secrets_to_config(secrets, value)  # type: ignore
        elif str(value).startswith(secrets_ref_expr):
            config[key] = secrets[value[len(secrets_ref_expr):]]


def load_config():
    with open('config.yaml') as conf_file:
        config = yaml.full_load(conf_file)
    with open('secrets.yaml') as secrets_file:
        secrets = {k: base64.b64decode(v).decode('utf-8')
                   for k, v in yaml.full_load(secrets_file).items()}
    insert_secrets_to_config(secrets, config)
    return config

config = load_config()
llm = AzureChatOpenAI(
    api_key=config["open-ai"]["api-key"],
    api_version=config["open-ai"]["api-version"],
    azure_deployment=config["open-ai"]["deployment"],
    azure_endpoint=config["open-ai"]["endpoint"]
)

ANALYZED_PROJECT_PATH = os.path.realpath(config["dev-assistant"]["project-path"])
