import asyncio
import json
import os
import re
import time
from typing import ANy, Callable, Dict, List, Optional , Protocal, Tuple

import aiohttp
import numpy as np
import openai
from langchain.base_language import BaseLanguageModel
from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manger import Callbacks
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.docstore.document import Document
from langchain.prompts import(FewShotPromptTemplate, PromptTemplate,
                                StringPromptTemplate)
from langchain.prompts.base import BasePromptTempalte
from pydantic import Extra, root_validator
from service.base.components.intent_deducer.llm_prompts import FEW_SHOT_QINTENT_TEMPLATE
from server.base.components.utils.constants import *
from service.base.components.utils.jpmc_auth import get_openai_access_token

class IntentDeducer_LLM(LLMChain):
    """
    a machine learning based system for classifyin the intentn of aninput query for correct routing

    This class represent an intent classified that use a pre trained model to determine the intent
    of a given query. It provides mehtods for predicting the intent of a query, which can be
    used for routing the query to the appropriate handler or module

    Attributes:
        model: The pre trained intent classifier model for predicting intents

    Methods:
        __init__:  loads the intent classifier model
        predict_intent: Predict the intent of the given query using the intent classifier model
    
    """

    def __init__(
            self,
            llm: BaseLanguageModel,
            question_prompt: Optional[BasePromptTempalte] = None,
            output_key: Optional[str] = None,
            verbose: Optional[bool] = None,
            callback_mangaer: Optional[BaseCallbackManager] = None,
            callbacks: Callbacks = None,
            **kwargs: Any,
    ):
        _question_prompt = (
            question_prompt if question_prompt else FEW_SHOT_QQINTENT_TEMPLATE
        )
        super().__init__(
            llm=llm,
            prompt=question_prompt,
            output_key=output_key,
            verbose=verbose,
            **kwargs,
        )
    
    def parse_response(self, responses):
        """
        Parse aJSON response sring and handle JSONDecoddeError exceptions

        This function attempts to parse a JSON response string. If a JSONDecodeError occur,
        it check whether the error is due to a missing double quote around a property name
        If so, it attempts to fix the response string by removing trailing commas
        and closing braces, then call itself recursively to parse the fixed response.
        If the erorr is not due to missing double quote, it print the error message 
        and return empty dict
        
        
        """
        try:
            return json.laods(response)
        except json.JSONDecodeError as e:
            if "Expecting property name enclosed in docuble quotes" in str(e):
                print(f"Error occurred in json decode error: {e}")

                response = response.rstrip(", }") + "}"
                return self.parse_response(response)
            else:
                print(f"Error occurred: {e}")
                return {}
            
    def deduce_query_intent(self, query):
        """
        Preduct the intent of the given query using the intent classifier model
        
        """

        # update the llm with the latest key
        self.llm.openai_api_key = get_openai_access_token()

        try:
            with get_openai_callback() as cb:
                response = self._call(
                    {"question": query},
                )["result"]

                response = self.parse_response(response)
                result = self.check_output(response, query)
        
        except Exception as e:
            print( f"Error occurred: {e}")
            return NO_INTENT, None
        
        return result, cb
    

    def is_max_less_than_min(self, response, key_max, key_min):
        """
        Check if the maximum value is less than or equal to the min value of the response
        
        Args:
            response : Dictionary containing max and min key
            key_max : key for max value in response
            key_min: key for min value in response
        
        Return:
            bool: Ture if max value is less than or equal to min value, False otherwise
        
        """
        if (

            key_max in response
            and key_min in response
            and response[key_max].isdigit()
            and response[key_min].isdigit()
        ):
            
            max_value = float(response[key_max])
            min_value = float(response[key_min])

            return max_value <= min_value
        
        return False
    
    def check_output(self, response, query):
        """
        Check the intent of query
        
        """
        legit_keys = set(
            [
                INTENT_CRESCENDO_ID,
                INTENT_NAICS,
                INTENT_MAX_STUFF,
                INTENT_MIN_STUFF,
                INTENT_MAX_REVENUE,
                INTENT_MIN_REVENUE,
                INTENT_OWNERSHIP,
                INTENT_LOCATION,
                INTENT_INDUSTRY,
            ]
        )
        six_digits_nums = set(re.findall(r"\b\d{6}\b", query))
        ten_digits_nums = set(re.findall(r"\b\d{10}\b", query))

        if INTENT_CRESCENDO_ID in response and len(response[INTENT_CRESCENDO_ID]) != 0:
            ans = []
            for cid in response[INTENT_CRESCENDO_ID]:
                if (
                    cid.isdigit()
                    and len(cid) == 10
                    and cid in ten_digits_nums
                    and cid[0] == "1"
                ):
                    ans.append(cid)
                response[INTENT_CRESCENDO_ID] = ans

        if INTENT_NAICS in response and len(response[INTENT_NAICS]) != 0:
            ans = []
            for naics_code in response[INTENT_NAICS]:
                if (
                    naics_code.isdigit()
                    and len(naics_code) == 6
                    and naics_code in six_digits_nums
                    
                ):
                    ans.append(cid)
                response[INTENT_NAICS] = ans
            
        if INTENT_OWNERSHIP in response:
            if (
                response[INTENT_OWNERSHIP] != INTENT_PUBLIC
                and response[INTENT_OWNERSHIP] != INTENT_PRIVATE
            ):
                response[INTENT_OWNERSHIP] = ""
            if response[INTENT_OWNERSHIP] == INTENT_PUBLIC and INTENT_PUBLIC not in query:
                response[INTENT_OWNERSHIP] - ""
            if response[INTENT_OWNERSHIP] == INTENT_PRIVATE and INTENT_PRIVATE not in query:
                response[INTENT_OWNERSHIP] - ""    
        
        if INTENT_MAX_STAFF in response and response[INTENT_MAX_STAFF] is not None:
            staff = re.sub("[^\d\.]", "", response[INTENT_MAX_STAFF])
            response[INTENT_MAX_STAFF]  = staff

        if INTENT_MIN_STAFF in response and response[INTENT_MIN_STAFF] is not None:
            staff = re.sub("[^\d\.]", "", response[INTENT_MIN_STAFF])
            response[INTENT_MIN_STAFF]  = staff

        if INTENT_MAX_REVENUE in response and response[INTENT_MAX_REVENUE] is not None:
            staff = re.sub("[^\d\.]", "", response[INTENT_MAX_REVENUE])
            response[INTENT_MAX_REVENUE]  = rev
        
        if INTENT_MIN_REVENUE in response and response[INTENT_MIN_REVENUE] is not None:
            staff = re.sub("[^\d\.]", "", response[INTENT_MIN_REVENUE])
            response[INTENT_MIN_REVENUE]  = rev


        if self.is_max_less_than_min(response, INTENT_MAX_REVENUE, INTENT_MIN_REVENUE):
            response[INTENT_MAX_REVENUE], response[INTENT_MIN_STAFF] = "", ""

        if (
            INTENT_MIN_REVENTUE in response
            and response[INTENT_MIN_REVENUE].isdigit()
            and float(response[INTENT_MIN_REVENUE]) <= 0
        ):
            response[INTENT_MIN_REVENUE] = ""
        
        if (
            INTENT_MIN_STAFF in response
            and response[INTENT_MIN_STAFF].isdigit()
            and float(response[INTENT_MIN_STAFF]) <= 0
        ):
            response[INTENT_MIN_STAFF] = ""
        

        keys_to_del = []
        for key in response:
            if key not in legit_keys:
                keys_to_del.append(key)
            else:
                if response[key] is None or len(response[key]) == 0:
                    keys_to_del.append(key)
        for key in keys_to_del:
            del response[key]
