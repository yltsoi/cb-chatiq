from allcities import cities
import numpy as np
import os
import json
from .CityLookup import CityLookup


class Reranker:
    """
    This class represent a reranker module that tkaes a list of response retrieved from a
    database and reranks them based on their relevance to the original query. It provides
    methods for reranking response, which can be used for various information retrieval tasks

    Methods:

        __init__: Initializes the Reranker instance and sets up the reranking model
        rerank_retrievals: reranks the retrivals based on their relevance to the original query
    
    """
    config = None
    num_docs = None
    distance_threshold = None
    country_converter = None
    city_lookup = None
    state_converter = None

    def __init__(
            self, config="vectordb_doc_reranker/config.json"
    ):
        """
        Initialized the Reranker instance and sets up the reranking model

        Args:
            config(str): Path to the JSON configuration file for the reranker

        This method initialize the Reranker instance by loading the configuration file
        and setting up the necessary data structure for location-based filtering and reranking
        
        """
    
        prefix_config_file = "service/base/components/vectodb_doc_reranker/"
        config_file = ""

        config_file += "prod"

        self.state_and_country = False
        config_file += "_config.json"
        config_file = prefix_config_file + config_file
        if Reranker.config is None:
            with open(config, "r") as f:
                Reranker.config = json.load(f)
            
        if Reranker.num_docs is None:
            Reranker.num_docs = Reranker.config.get("num_docs", 25)

        if Reranker.distance_threshold is None:
            Reranker.distance_threshold = Reranker.config.get("distance", 30)
        
        if Reranker.country_converter is None:
            Reranker.country_converter, _ = self.init_country_converter()
        
        if Reranker.city_lookup is None:
            Reranker.city_lookup = CityLookup()

        if Reranker.state_converter is None:
            Reranker.state_converter = self.init_state_converter()

    def init_state_converter(self):
        """
        Initialize a dictionary for converting state names to state code

        Returns:
            dict: A dictionary that maps state names to state codes
        
        This method initialzied a dictionary for converting state names to their corresponding
        state code, which can be used for matching locations in the retrieved documetns
        
        """
        with open(
            "vectordb_doc_reranker/geographical_data/states.csv"
            "r",
        ) as f:
            lines = f.readlines()
        state_dict = {}
        for line in lines:
            elements = line.split(",")
            state_dict[elements[0].strip().strip('"')] = (
                elements[1].strip().strip('"')
            )
        return state_dict
    
    def init_country_converter(self):
        """
        Initialized dictionaries for converting country codes to country names and abbrebations

        Returns:
            tuple: Two dictionaries that map country codes to country name and abbreviation

        
            This method initialzie two dictionaries for converting country codes to their corresponding
            country names and abbreviations, which can be used for matching locations inthe retrieved documents
               
        """
        with open(
            "vectopdb_doc_reranker/geographical_data/countries_codes_and_coordinates.csv",
            "r",
        ) as f:
            lines = f.readlines()
        code_to_abbreviation, code_to_full_name = {}, {}
        for line in lines:
            elements = line.split(",")
            code_to_abbreviation[elements[2]].strip().strip('"')] = (
                elements[1].strip().strip('"')
            )
            code_to_full_name[elements[2]].strip().strip('"')] = (
                elements[1].strip().strip('"')
            )

        return code_to_abbreviation, code_to_full_name



        
        
        