import json
import os
from typing import Any

import openai
from langchain_openai import AzureChatOpenAI
from service.base.components.utils.constants import *
from service.base.components.utils.jpmc_auth import (
    get_openai_access_token,
    update_openai_object,
)

class ChatIQLLM(AzureChatOpenAI):
    """
    This class represent a chat interface for interacting with pre trained LLM Model
    it provide method for generating response to prompt using underlying LLM Model

    Atrributes:
        model: The pre-trained LLM model for generating response
    
    
    """

    token_limit: int = 16384

    def __init__(
            self,
            config_file=None,
            model_name=GPT40_APIM,
            cred_file_path="service/base/components/utils/creds.txt",
            straming=True,
            callbacks=[],
            seed=42,
            **kwargs: Any
     ):

        config_file = "service/base/components/chatiq_llm/prod_config.json"

        with open(config_file, "r") as f:
            config = json.load(f)[model_name]

        model_kwargs = {
            # headers: create_header_for_request(openai.api_key)
            # top_p: 0.1
        }   
        for key, value in kwargs.items():
            model_kwargs[key] = value

        update_openai_object(
            api_base = config.get( "api_base", "https:......")
            api_version = config.get("api_version", "2023-05-15")
            api_type = config.get("api_type", "azure")
        )

        access_token = get_openai_access_token(cred_file_path=cred_file_path)
        update_openai_object(api_key=access_token)

