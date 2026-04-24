import os
import sys

sys.path.insert(0, 'app')
import argparse
import asyncio
import json
import pickle
import time
from collections import OrderedDict
from pathlib import Path

import requests
from dtos.req_res import ChatIQRequest, LLMRequest
from dtos.vector_db_connection import VectorDbConnection
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
from service.base.components.chatiq_llm.chatiq_llm import ChatIQLLM
from service.base.components.embedding_retriever.embedding_retriver import (
    EmbeddingRetriever,
)
from service.base.components.intent_deducer.intent_deducer_llm import IntentDeducer_LLM
from service.base.components.llm_response_retriver.few_shot_qa import FewShortQA
from service.base.components.response_validator.response_validator import (
    LLMResponseValidator,
)
from service.base.components.utils.constants import *
from service.base.components.utils.jpmc_auth import (
    create_header_for_requests,
    get_openai_access_token,
    update_openai_object,
)
from service.base.components .utils.utils import load_config_filepaths
from service.base.components.vectordb_doc_reranker.reranker import Reranker
from service.base.components.vectordb_doc_retriever.open_search import(
    OpenSearchRetriever,
)
from service.base.components.vectordb_doc_retriever.query_builder import QueryBulder
from service.base.components.vectordb_doc_retriever.retrieval_aggregator import (
    RetrievalAggregator,
)

# Global reranker init
reranker = Reranker()

class ChatIQ_QAServices:
    """
    ChatIQ_QAService is a class that encapsulate the entire workflow for processing
    a query and returning the final result. It initalized all required components
    and providdes a generate_answer function to execute the workflow steps

    Functions:
        generate_answer(query: str) -> dict
    
    """

    def __init__(
        self,
        intent_classifier_config=None,
        embedder_config=None,
        open_search_db_config=None,
        llm_config=None,
        qa_config=None,
        cred_file_path=None,
        reranker_config=None,
        embedding_type=OPENAI,
        verbose=True,
        os_retriever=None,
    ):
        """
        
        Args:
            intent_classifier_config (str,optional): Path to the intent classifier config file
            embedder_config (str, optional) : Path to the embedder config file
            open_search_db_config ( str, optional)  : Path to search database config file
            llm_config (str, optional) : Path to LLM Config file
            qa_config (str, optional): Path to QA config file
            reranker(Reranker, optional): an instance of the reranker class. Default None
            retrieval_aggregator(RetrievalAggregator, optional): an instance of the RetrievalAggregator class. Default None
                    
        """
        # get_base_config
        config_file_dict = load_config_filepaths(
                env = os.environ["ENVIRONMENT"]
                chatiq_version = CHATIQ_BASE  
        )

        if not intent_classifier_config:
            intent_classifier_config = config_file_dict.get(
                    "intent_classifier_config",
                    "service/base/components/intent_deduce/config.json"
            )
        with open(intent_classifier_config, 'r') as f:
            intent_classifier_config_params = json.load(f)
        if not embedder_config:
            embedder_config = config_file_dict.get(
                'embedder_config',
                '/service/base/components/embedding_retriever/prod_config.json'
            )        
        if not open_search_db_config:
            open_search_db_config = config_file_dict.get(
                'embedder_config',
                '/service/base/components/vectordb_doc_retriever/prod_base_config.json'
            )            
        if not llm_config:
            llm_config = config_file_dict.get(
                'llm_config',
                '/service/base/components/chatiq_llm/config.json'
            )              
        if not qa_config:
            qa_config = config_file_dict.get(
                'qa_config',
                '/service/base/components/llm_response_retriever/config.json'
            )                        
        with open(qa_config, 'r') as f:
            qa_config_params = json.load(f)
        
        if not cred_file_path:
            cred_file_path = config_file_dict.get(
                'cred_file_path',
                "service/base/components/utils/creds.txt"
            )

        if not reranker_config:
            reranker_config = config_file_dict.get(
                'reranker_config',
                "service/base/components/vectordb_doc_reranker/prod_base_config.json"
            )    

        self.intent_llm_model_name = intent_classifer_config_params.get(
            'intent_llm_model_name',
            GPT40_APIM
        )
        
        self.qa_llm_model_name = qa_config_params.get(
            'qa_llm_model_name',
            GPT40_APIM
        )
        
        self.access_token = get_openai_access_token(
            cred_file_path=cred_file_path
        )
        
        self.cred_file_path = ced_file_path
        update_openai_object(api_key=self.access_token)

        self.embedder = EmbeddingRetriever(
            config_file=embedder_config
            embedding_type=embedding_type,
            cred_file_path=self.cred_file_path
        )

        self.llm_config_file = llm_config
        self.intent_classifier = IntentDeducer_LLM(
            llm=ChatIQLLM(
                config_file=self.llm_config_file,
                model_name=self.intent_llm_model_name,
                cred_file_path=self.cred_file_path,
            ),
            verbose=verbose,
            output_key='result'
        )

        self.open_search_db = os_retriever
        if os_retriever == None:
            self.open_search_db = OpenSearchRetriever(
                config_file=open_search_db_config,
                embedding_type=embedding_type
            )

        self.reranker = reranker
        self.reranker.update_config(reranker_config)        

        with open(qa_config, "r") as f:
            qa_config_params = json.load(f)

        self.retrieval_aggregator = RetrievalAggregator(
            config_file=open_search_db_config,
            docs_per_mapper=None
        )
        self.qq = FewShotQA(
            llm=ChatIQLLM(
                config_file=self.llm_config_file,
                model_name=self.qa_llm_model_name,
                cred_file_path=self.cred_file_path,
            ),
            verbose=verbose,
            output_key='result',
            timeout=qa_config_parames.get('timeout', None),
        )

        self.query_builder = QueryBuilder(
                config_file = open_search_db_config,
                open_search_db = self.open_search_db,
            )

    def generate_answer(self, request: ChatIQRequest):
        """
        Main function to execute the ChatIQPipeline workflow steps

        Args:
            request(ChatIQRequest): ChatIQRequest object

        Returns:
            dict: The final result after processeing the query    
        """

        st = time.time()

        chatiq_result = {
            "data": {
                'gpt_response': [ANSWER_NOT_FOUND],
                'cited_cids': [],
                'reason': '',
            },
            'error': [],
            'success': 'false'
        }

        if type(request) != str:
            query = request.question
        else:
            query = request
        query = query.rstrip(
            "".join(c for c in query[::-1] if not c.isalnum())
        )
        if len(query) < 3:
            chatiq_result["error"] = "Query length too short"
            chatiq_result["data"["gpt_response"]] = [QUERY_TOO_SHORT]
            chatiq_result["success"] = "true"
            inference_time = float(f"{time.time() -  st:.3f}")
            chatiq_result["data"]["time"] = inference_time
            return chatiq_result
        
        vector_db_connection = VectorDbConnection()
        query_intent_output = {}
        self.access_token = get_openai_access_token(
            cred_file_path=self.cred_file_path
        )
        update_openai_object(api_key=self.access_token)

        try:
            print("Running query intent module:")
            intent, intent_cb = self.intent_classifer.deduce_query_intent(
                query
            )
            print("Completed query intent module. Intent:", str(intent))
        except:
            print("Unable to deduce query intent, using the default settings")           

        try:
            print("Running query embedding modules") 
            embedded_query = self.embedder.get_embeddings(query)
            print("Completed query embedding module")
        except:
            print("Unable to get embeddings for query")
            chatiq_result["error"] = "Unable to get embeddings for query"
            chatiq_result["data"]["gpt_response"] = [NO_AZURE_OPENAI_RESPONSE]
            inference_time = float(f"{time.time() - st:.3f}")
            chatiq_result["data"["time"]] = inference_time
            return chatiq_result
        
        try:
            print("Running query builder module:")
            updated_query, query_db = self.query_builder.build_query(
                query, embedded_query, intent
            )
            print("Completed query builder module")
        except:
            print("Unable to generate OpenSearch query from intent")
            chatiq_result["error"] = (
                "Unable to generate OpenSearch query from intent"
            )
            chatiq_result["data"]["gpt_response"] = [NO_AZURE_OPENAI_RESPONSE]
            inference_time = float(f"{time.time() - st:.3f}")
            chatiq_result["data"["time"]] = inference_time
            return chatiq_result
        
        try:
            print("Running OS retrieval module:")
            retrieved_docs = self.open_search_db.execute_query(query_db)
            print("Completed OS retrieval module")
        except:
            print("Unable to get documents from VectorDB")
            chatiq_result["error"] = (
                "Unable to get documents from VectorDB"
            )
            chatiq_result["data"]["gpt_response"] = [NO_AZURE_OPENAI_RESPONSE]
            inference_time = float(f"{time.time() - st:.3f}")
            chatiq_result["data"["time"]] = inference_time
            return chatiq_result        
        
        try:
            if self.ranker:
                try:
                    print("Reranking OS retrievals")
                    self.reranker.extract_query_and_location_intent(
                        query, intent
                    )
                    ranked_docs = self.reranker.filter_retrievals_by_location(
                        retrieved_docs
                    )
                    print("Completed reranking OS retrievals")
                except:
                    reranked_docs = retrieved_docs[: self.reranker.num_docs]
            else:
                ranked_docs = retrieved_docs

            if len(ranked_docs) == 0:
                chatiq_result["data"]["gpt_response"]    = [NO_DOCUMENTS_FOUND]
                inference_time = float(f"{time.time() - st:.3f}")
                chatiq_result["data"]["time"] = inference_time
                return chatiq_result
            
            print("Formatting OS retrievals")

            formatted_ranked_docs = (
                self.retrieval_aggregator.reformat_retrievals(
                    retrievals=ranked_docs,
                    intent=intent,
                )
            )
            print("Completed formatting OS retrievals")
        except:
            print("Unable to get format retrieved docs")            
            chatiq_result["error"] = (
                "Unable to get format retrieved_docs"
            )
            chatiq_result["data"]["gpt_response"] = [NO_AZURE_OPENAI_RESPONSE]
            inference_time = float(f"{time.time() - st:.3f}")
            chatiq_result["data"]["time"] = inference_time
            return chatiq_result        
        
        try:
            print(f"running GPT prompt completion")
            print( f"Running with config file: {self.llm_config_file}, and model name: {self.qa_llm_del_name}")
            self.qa.llm= ChatIQLLM(
                cofnig_file=self.llm_config_file,
                model_name =self.qa_llm_model_name,
                cred_file_path=self.cred_file_path,
            )
            qa_result, cb = self.qa.qa_llm(
                question=updated_query, docs=formatted_ranked_docs
            )
            print("completed running GPT prompt completion" )
        except:
            print("Unable to get GPT response")            
            chatiq_result["data"]["gpt_response"] = [NO_AZURE_OPENAI_RESPONSE]
            inference_time = float(f"{time.time() - st:.3f}")
            chatiq_result["data"]["time"] = inference_time
            return chatiq_result        
        
        try:
            print(f"Validating response")
            chatiq_result = LLMResponseValidator.validate_result(
                ranked_docs=ranked_docs,
                sources=",".join(
                    [doc.metadata["source"] for doc in formatted_ranked_docs]
                ),
                llm_output=qa_result,
                chatiq_response=chatiq_result,
            )
            print("completed Validating response" )
        except:
            print("Unable to Validate LLM output")            
            chatiq_result["data"]["gpt_response"] = [NO_AZURE_OPENAI_RESPONSE]
            inference_time = float(f"{time.time() - st:.3f}")
            chatiq_result["data"]["time"]] = inference_time
            return chatiq_result        
        
        print("\n Inference time: {:.3f} sec\n".format(time.time() -st))
        inference_time = float(f"{time.time() - st:.3f}")
        chatiq_result["data"]["time"] = inference_time
        chatiq_result["success"] = "ture"

        for i in range(len(chatiq_result["data"]["get_response"])):
            print(chatiq_result["data"]["gpt_response"][i])
            print()

        return chatiq_result

    def generate_answer_debug(self, request: ChatIQRequest):
        """
        Main function to execute the ChatIQPipeline workload steps

        Args:
            request (ChatIQRequest): ChatIQRequest object
        
        Returns:
            dict: thefinal result after processing the query
        """
        chatiq_result = {
            "data": {
                "gpt_response": [ANSWER_NOT_FOUND],
                "cited_cids": [],
                "error": [],
                "success": "true",
            }
        }

        st = time.time()
        vector_db_connection = VectorDbConnection()
        query_intent_output = {}
        query_debug_result = OrderedDict()
        query_debug_result["time"] = dict()
        query_debug_result["time"]["query_intent"] = 0
        query_debug_result["time"]["embeddings"] = 0
        query_debug_result["time"]["os_query_builder"] = 0
        query_debug_result["time"]["os_retrieval"] = 0
        query_debug_result["time"]["reranker"] = 0
        query_debug_result["time"]["reformat_retrievals"] = 0
        query_debug_result["time"]["gpt_prompt"] = 0
        query_debug_result["time"]["response_valiator"] = 0
        query_debug_result["time"]["total"] = 0

        if type(request) != str:
            query = request.question
        else:
            query = request
        query = query.rstrip(
            "".join(c for c in query[::-1] if not c.isalnum())
        )
        if len(query) < 3:
            query_debug_result["error"] = "Query length too short"
            query_debug_result["chatiq_Answer"] = QUERY_TOO_SHORT
            inference_time = float(f"{time.time() - st:.3f}")
            query_debug_result["time"]["total"] = inference_time
            return query_debug_result
        
        self.access_token = get_openai_access_token(
            cred_file_path=self.cred_file_path
        )
        update_openai_object(api_key=self.access_token)

        start_time = time.time()
        try:
            print("Running query intent module")
            intent, intent_cb = self.intent_classifier.dedue_query_intent(
                query
            )
            if intent_cb:
                query_debug_result["Intent Prompt Tokens"] = (
                    intent_cb.prompt_tokens
                )
                query_debug_result["Intent Completion Tokens"] = (
                    intent_cb.completion_tokens
                )
                query_debug_result["Intent Cost"] = intent_cb.total_cost

            query_debug_result["query_intent"] = intent
            print("Completed query intent module. Intent:", str(intent))
            chatiq_result["error"] = []
        except:
            print("Unalbe to deduce query intent, using the default settings")            
            query_debug_result["error"] = (
                "Unable to deduce query intent, using the default setting"
            )
            query_debug_result["query_intent"] = (
                "Unable to deduce query intent, using the default setting"
            )
        query_debug_result["time'"]["query_intent"] = float(
            f"{time.time() - start_time:.3f}"
        )

        start_time = time.time()
        try:
            print("Running query embedding module")
            embedded_query = self.embedder.get_embeddings(query)
            print("Completed query embedding module")
        except:
            print("Unalbe to get embeddings for query")            
            query_debug_result["error"] = (
                "Unable to get embedding for query"
            )
            inference_time = float(f"{time.time() - st:.3f}")          
            query_debug_result["time"]["total"] = inference_time
            return query_debug_result

        query_debug_result["time'"]["embedding"] = float(
            f"{time.time() - start_time:.3f}"
        )

        start_time = time.time()
        try:
            print("Running query builder module")
            updated_query , query_db = self.query_builder.build_query(
                query, embedded_query, intent
            )

            print("Completed query builder module")
        except:
            print("Unalbe to generate OpenSearch query from intent")            
            query_debug_result["error"] = (
                "Unable to get generate OpenSearch query from intent"
            )
            inference_time = float(f"{time.time() - st:.3f}")          
            query_debug_result["time"]["total"] = inference_time
            return query_debug_result

        query_debug_result["time'"]["os_query_builder"] = float(
            f"{time.time() - start_time:.3f}"
        )


        start_time = time.time()
        try:
            print("Running OS retrieval_module" )
            retrieved_docs = self.open_search_db.exeucte_query(query_db)
            print("Completed OS retrieval module")
        except:
            print("Unalbe to get docummetns from VectorDB")            
            query_debug_result["error"] = (
                "Unable to get get documents from VectorDB"
            )
            inference_time = float(f"{time.time() - st:.3f}")          
            query_debug_result["time"]["total"] = inference_time
            return query_debug_result

        query_debug_result["time'"]["os_retrieval"] = float(
            f"{time.time() - start_time:.3f}"
        )


        start_time = time.time()
        try:
            print("Reranking" )
            if self.reranker:
                try:
                    self.reranker.extract_query_and_location_intent(
                        query, intent
                    )
                    ranked_docs = self.reranker.filter_retrievals_by_location(
                        retrieved_docs
                    )
                except:
                    ranked_docs = retrieved_docs[: sekf,reranker.num_docs]
            else:
                print("Unable to Rerank")
                ranked_docs = retrieved_docs[:25]

            query_debug_result["time'"]["reranker"] = float(
                f"{time.time() - start_time:.3f}"
            )
 
            if len(ranked_docs) == 0:
                query_debug_result["chatiq_Ansuer"] = NO_DOCUMENT_FOUND                
                inference_time = float(f"{time.time() - st:.3f}")          
                query_debug_result["time"]["total"] = inference_time
                return query_debug_result


            print("Formattign OS retrievals")
            formatted_ranked_docs = (
                self.retrieval_aggregator.reformat_retrievals(
                    retrievals = ranked_docs
                    intent = intent
                )
            )
            doc_list = []
            for foc in formatted_ranked_docs:
                doc_list.qppend(doc.page_content)
            query_debug_result["llm_input-docs"] = doc_list
            print("Completed formatting OS retrieval")
        except:
            print("Unalbe to format and rerank retrieved docs")            
            query_debug_result["error"] = (
                "Unable to get format and rerank retrieved docs"
            )
            inference_time = float(f"{time.time() - st:.3f}")          
            query_debug_result["time"]["total"] = inference_time
            query_debug_result["llm_inoput_docs"] = (
                "Unable to format and rerank retrieved docs"
            )
            return query_debug_result

        query_debug_result["time'"]["os_retrieval"] = float(
            f"{time.time() - start_time:.3f}"
        )
        if query_db["query"].get("bool", None):
            query_db["query"]["bool"]["should"][0]["knn"]["embed_text_doc"][
                "vector"
            ] = "Removed for brevity"
        elif query_db["query"].get("scruipt_score", None):
            query_db["query"]["script_score"]["script"]["params"][
                "query_value"
            ] = "Removed for brevity"

        for each_document in retrieved_docs:
            each_document["_source"]["embed_text_doc"] = "Removed for brevity"
        query_debug_result["os_result"] = retrieved_docs


        start_time = time.time()
        try:
            print("Running GPT prompt completion" )
            print(f"Running with config file: {self.llm_config_file}, and model name: {self.qa_llm_model_name}")
            qa_result, cb = self.qa.qa_llm(
                question=updated_query, docs=formatted_ranked_docs
            )                  

            query_debug_result["llm_qa_result"] = qa_result
            if cb.successful_requests:
                query_debug_result["QA Prompt Token"] = cb.prompt_tokens
                query_debug_result["QA_Completion_Token"] = (
                    cb.completion_tokens
                )
                query_debug_result["QA Cost"] = cb.total_cost
            print("Completed running GPT prompt completion")
        except:
            print("Unalbe to get GPT response")            
            query_debug_result["error"] = (
                "Unable to get GPT response"
            )
            inference_time = float(f"{time.time() - st:.3f}")          
            query_debug_result["time"]["total"] = inference_time
            query_debug_result["llm_qa_result"] = "unable to get GPT response"
            return query_debug_result

        query_debug_result["time'"]["gpt_prompt"] = float(
            f"{time.time() - start_time:.3f}"
        )

        start_time = time.time()
        try:
            print("Validating response" )
            chatiq_result = LLMResponseValidator.validate_result(
                ranked_docs = ranked_docs,
                sources=",".join(
                    [doc.metadata["source"] for doc in formatted_ranked_docs]
                ),
                llm_output=qa_result,
                chatiq_response = chatiq_result,
            )

            validated_result = ""
            for i in range(len(chatia_result["data"]["gpt_response"])):
                validated_result += (
                    chatiq_result["data"]["gpt_response"][i] + "\n\n"
                )                  
            if chatiq_result["data"].get("reason", None):
                validated_result += (
                    "\n\nReason: " + chatiq_result["data"]["reasone"]
                )                  
            query_debug_result["QA Cost"] = cb.total_cost
            print("Completed valdiating response")
        except:
            print("Unalbe to validate LLM output")            
            query_debug_result["error"] = (
                "Unable to Validate LLM utput"
            )
            query_debug_result["chatiqa_Answer"] = (
                "Unable to Validate LLM utput"
            )
            inference_time = float(f"{time.time() - st:.3f}")          
            query_debug_result["time"]["total"] = inference_time
            
            return query_debug_result

        query_debug_result["time'"]["response_validator"] = float(
            f"{time.time() - start_time:.3f}"
        )

        print("\nInfrerence time: {:.3f} sec\n".format(time.time() -st))
        inference_time = float(f"{time.time() - st:.3f}")          
        query_debug_result["time"]["total"] = inference_time
        
        print(query_debug_result["chatiq_Answer"])

        return query_debug_result
    
    def get_query_intent(self, request: ChatIQRequest):
        """
        Function to Fetch the query intent from ChatIQ

        Args:
            request (ChatIQRequest): ChatIQRequest object

        Returns:
            dict: The intent extracted from the input query in the value of the 'intent' key
        """

        query = request.question
        query = query.rstrip(
            "".join(c for c in query[::-1] if not c.isalnum())
        )
        self.access_token = get_openai_access_token(
            cred_file_path = self.cred_file_path
        )
        update_openai_object(api_key=self.access_token)
        try:
            print("Running query intent modules:")
            intent, intent_cb = self.intent_classifier.deduce_query_intent(
                query
            )
            print("Completed query intent module. intent:", str(intent))
            return {"query_intent": intent}
        
        except:
            print("Unable to deduce query intent, using the default settings")
            return {"query_intent": {}}

    def get_embeddings(self, request: ChatIQRequest):
        """
        Function to Fetch the embeddings from OpenAI

        Args:
            request (LLMrequest): LLMRequest object

        Returns:
            dict: The embedding for input text in the value of the embedded_query key
        """

        query = request.question
        response = {}
        
        try:
            query = str(query)
            print("Running query embedding modules:")
            self.access_token = get_openai_access_token(
                cred_file_path = self.cred_file_path
            )
            update_openai_object(api_key=self.access_token)
            embedded_query = self.embedder.get_embedding(query)
            response["embedded_query"] = embedded_query
            print("Completed query embedding module")
        except:
            print("Unable to get embedding for query")
            response["embedded_query"] = "Unable to get embeddings"
            
        
        return response

    def ptu_access(self, request: LLMRequest):
        """
        This function processes the input 'request' which could be a ChatIQRequest or a plain string
        It make a call to OpenAI API and return the mode's response as a dictiorny which
        include completion content

        :param request: could be a ChatIQRequest object or a simple string
        :return: Dictionary with the 'result' key containing model completion content or blank upon error
        
        """

        if type(request) != str:
            llm_input_text = request.prompt
        else:
            llm_input_text = request

        self.access_token = get_openai_access_token(
                cred_file_path = self.cred_file_path
        )
        update_openai_object(api_key=self.access_token)

        llm_response = {}

        try:
            print("running GPT prompt completion")
            print(f"Runnign with config file: {self.llm_config_file}, and model name: {self.qa_llm_model_name}")

            # update the no proxy environment
            os.environ["no_proxy"] = (
                os.environ["no_porxy"] + ",opanai.azure.com"
            )

            # initialize LLM model
            llm = ChatIQLLM(
                config_file = self.llm_config_file,
                model_name = self.qa_llm_model_name

            )
        
            # Fetch the response
            response_message = llm.invoke([HumanMessage(content=llm_input_text)])

            print("Completed running GPT prompt completion")

            llm_response["result"] = response_message.content
        except:
            print("Unable to get GPT response")

            return {"result" : ""}
        
        return llm_response


# if __name__ == "__main__":
#   chatiq_obj = ChatIQ_QAService()
#   query = "Give me 15 AdTech companies located in San Fransciao by area with revenue greater than $20 million with employee count greater than 20"
#   ans = chaiq_obj.generate_answer_debug(query)
