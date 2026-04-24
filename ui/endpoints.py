import requests
import os
import json
from vectordb_doc_reranker.reranker import Reranker
reranker = Reranker()

def get_query_intent(query):
    endpoint = "https://chatiq-ecs-prod.prod.aws.jpmchase.net/base/get-query-intent"
    response = requests.post(endpoint, json={"question":(query)})
    return response.json()["query_intent"]

def get_embeddings(query):
    endpoint = "https://chatiq-ecs-prod.prod.aws.jpmchase.net/base/get-embedding"
    response = requests.post(endpoint, json={"question":(query)})
    return response.json()["embedded_query"]


def query_os(query):
    try:
        headers = {
            "accept": "applicaiton/json",
            "Content-Type": "applicaiton/json",
        }
        endpoint = "https://chatiq-ecs-prod.prod.aws.jpmchase.net/base/query-os"
        response = requests.post(endpoint, json=query, headers=headers)
        resp = response.json()["hits"]["hits"]
        return resp
    except Exception as e:
        print(e)

def rerank(docs, query, intent, size):
    results = []
    print(len(docs))
    reranker.extract_query_and_location_intent(query, intent)
    reranked_docs = reranker.filter_retrievals_by_location(docs, size)
    print(len(reranked_docs))
    for company in reranked_docs:
        results.append({
            "name": company["_source"]["company_name"],
            "id": company["_source"]["company_crescendo_id"]
            "url":"https://companyiq.prod.aws.jpmchase.net/dashboard?crescendo="+str(company["_source"]["company_crescendo_id"]),
            "relevancy_score":company["_score"],
            "address": company["_source"]["company_address"],
            "zip":company["_source"]["company_zip"],
            "city":company["_source"]["company_city"],
            "state":company["_source"]["company_state"],
            "date_founded":company["_source"]["company_date_founded"],
            "revenue":company["_source"]["company_annual_revenue"],
            "employee_count":company["_source"]["company_num_employees"],
            "naics":company["_source"]["company_naics_code"],
            "ownership":company["_source"]["company_ownership_class"],

        })
        if(len(results) == size):
            break
    return results




