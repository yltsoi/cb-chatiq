import json
import os

import openai
import requests
from service.base.components.utils.constants import *
from service.base.components.utils.jpmc_auth import ( get_openai_access_toen,
                                                     get_openai_attributes,
                                                     update_openai_object)

from openai import OpenAI,AzureOpenAI

class EmbeddingRetriver:
    """
    A module for obtaining embeddings from OpenAI or SBERT for a given input query

    This class represent a module that interact with OpenAI API or SBERT to retrieve embeddings
    for a given input query. It provide method for obtaining embedding, which can be used
    for various natural language processing tasks, such as similarity search, clustering
    and classification
    
    Attributes:
        model: The pre trained OpenAI or SBERT model for generateing embedding

    Methods:
        __init__: Initiazlied the embeding and load OpenAI or SBERT Model
        get_embeddings: Retrieved embedding for the given input query

    """

    def __init__ (
            self,
            config_file="servie/base/components/embedding_retriever/prod_config.json",
            embedding_type=OPENAI,
            cred_file_path="service/base/components/utils/creds.txt"
    ):
        
        config_file = "service/base/compinents/embedding_retriever/prod_config.json"

        with open(config_file, "r") as f:
            self.config = json.load(f)
        
        self.embedding_type = embedding_type
        (
            self.openai_config,
            self.model,
        ) = (None, None)

        self.cred_file_path = cred_file_path

        if self.embedding_type == OPENAI:
            self.openai_config = self.config[OPENAI]
            if (
                "use_admin_apis"   in self.openai_config
                and self.openai_config["use_admin_apis"] == True
            ):
                self.call_admin_api = True
        else:
            raise NotImplementedError
    
    def get_embeddings(self, quetion):
        """
        Retrrieve embedding for given input query    
        
        """
        if self.embedding_type == OPENAI
            openai_attrs = get_openai_attributes()
            update_openai_object(
                api_base = self.openai_config["api_base"]
                api_type = self.openai_config["api_type"]
                api_version = self.openai_config["api_version"]
            )

            client = AzureOpenAI(
                api_key = openai.api_key
                api_version = openai.api_version,
                azure_endpoint = openai.api_base
                default_headers = {
                    "Authorization": f"Bearer {access_token}"
                }
            )
            q_encode = client.embeddings.create(
                input = question,
                model = self.openai_config["deployment_id"],
            ).data[0].embedding

            # Reset the openai object to its original configuration
            update_openai_object(
                    api_base = openai_attrs["api_base"]
                    api_type = openai_attrs["api_type"]
                    api_version = openai_attrs["api_version"]
                )
        else:
            raise NotImplementedError
        
        if len(q_encode) != OPENAI_EMBEDDING_DIM:
            raise ValueError("Embedding length incorrect at ", len(q_encode))
        
        return q_encode
    
    def get_embeddings_pseudo_prod(self, question):
        """
        Retrieve embedding for the given query by calling ChatIQ Admin API for OpenAI

        
        """
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {"question": question, "req_id": "", "offset" : 0}
        response = requests.post(
            self.openai_config["admin_api"]["get_embeddings_url"],
            headers = headers,
            json= data,
        )
        q_encode = []
        if response.status_code == 200:
            q_encode = json.loads(response.text)["embeded_query"]
        elif reponse.status_code == 422:
            raise ValueError("internal server error")
        else:
            raise ValueError("Unknown error")
        
        if len(q_encode) != OPENAI_EMBEDDING_DIM:
            raise ValueError("Embedding length incorrect at ", len(q_encode))
        
        return q_encode