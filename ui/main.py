import streamlit as st
import requests
import os
import json
import time
import pandas as pd
from endpoints import ( get_query_intent, get_embeddings, query_os, rerank)
st.title("QueryIQ")

if 'input_os_query' not in st.session_state:
    st.session_state.input_os_query = ""
if 'filter' not in st.session_state:
    st.session_state.filter = None
if 'filter_text' not in st.session_state:
    st.session_state.query = ""
if 'query' not in st.session_state:
    st.session_state.result = None
if 'time' not in st.session_state:
    st.session_state.time = {}
if 'intent' not in st.session_state:
    st.session_state.intent = None

results_dataframe = None

def create_query(embeddings, number_of_record, min_num_of_employees, max_num_of_employees, min_revenue, max_revenue, naics_code, ownership):
    query = {"size": ( number_of_record), "query": {"bool" : {"filter": {"bool": {"must": []}}}, "should": [{"knn": {"embed_text_doc": {"vector": embeddings, "k": 25}}}]}}
    if (min_num_of_employees != "" or max_num_of_employees != ""):
        key = {
            "range": {
                "company_num_employees": {}
            }
        }
        key["range"]["company_num_employees"].update({"gte":min_num_of_employees}) if min_num_of_employees != "" else ""
        st.session_state.filter_text += "\nGreater Than {} Employees\n".format(min_num_of_employees) if min_num_of_employees != "" else ""
        key["range"]["company_num_employees"].update({"gte":max_num_of_employees}) if max_num_of_employees != "" else ""                                                          
        st.session_state.filter_text += "\nLess Than {} Employees\n".format(max_num_of_employees) if max_num_of_employees != "" else ""
        query["query"]["bool"]["filter"]["bool"]["must"].append(key)
    if (min_revenue != "" or max_revenue != ""):
        key = {
            "range":{
                "company_annual_revenue": {}
            }
        }
        key["range"]["company_annual_revenue"].update({"get":min_revenue}) if min_revenue !=  "" else ""         
        st.session_state.filter_text += "\nGreater Than {} Employees\n".format(min_num_of_employees) if min_num_of_employees != "" else ""
        key["range"]["company_num_employees"].update({"gte":max_num_of_employees}) if max_num_of_employees != "" else ""                                                          
        st.session_state.filter_text += "\nLess Than {} Employees\n".format(max_num_of_employees) if max_num_of_employees != "" else ""
        query["query"]["bool"]["filter"]["bool"]["must"].append(key)

    query["query"]["bool"]["filter"]["bool"]["must"].append({"terms":{"company_naics_code":[naics_code]}}) if naics_code != "" else ""
    st.session_state.filter_text += "\nWith NAICS Code\n".format(naics_code) if naics_code != "" else ""
    query["query"]["bool"]["filter"]["bool"]["must"].append({"terms":{"company_ownership_class":ownership}}) if naics_code != "" else ""
    st.session_state.filter_text += "\nWith {} Ownership\n Code\n".format(ownership) if ownership != "" else ""
    st.session_state.input_os_query = query
    return query

def submit(query, number_of_record, min_num_of_employees, max_num_of_employees, min_revenue, max_revenue, maics_code, ownership):
    total_time = time.time()
    st.session_state.query = query
    st.session_state.filter_text = ""
    with st.spinner("Generating Response"):
        start_time = time.time()
        embeddings = get_embeddings(query)
        st.session_state.time["embeddings"] = time.time() - start_time

        start_time = time.time()
        os_query_input = create_query(embeddings, number_of_record, min_num_of_employees, max_num_of_employees, min_revenue, max_revenue, naics_code, ownership)
        st.session_state.time["query_creation"] = time.time() - start_time

        start_time = time.time()
        docs = query_os(os_query_input)
        st.session_state.time["query_os"] = time.time() - start_time

        start_time = time.time()
        st.session_state.result = rerank( docs, query, st.session_state.intent, number_of_record)
        st.session_state.time["reranker"] = time.time() - start_time

    st.session_state.time["infernence_time"] = time.time() - total_time

def generate_filters(query):
    with st.spinner("Generating Filters"):
        st.session_state.filter = {
            "min_rev": "",
            "max_rev": "",
            "min_staff": "",
            "max_staff": "",
            "ownership": ""
        }

        response = get_query_intent(query)
        print(response)
        st.session_state.intent=response
        st.session_state.filter["min_staff"] = response["min_staff"] if "min_staff" in response else ""
        st.session_state.filter["max_staff"] = response["max_staff"] if "max_staff" in response else ""

        st.session_state.filter["max_rev"] = response["max_rev"] if "max_rev" in response else ""
        st.session_state.filter["min_rev"] = response["min_rev"] if "min_rev" in response else ""

        st.session_state.filter["ownership"] = response["ownership"] if "ownership" in response else ""

def download_csv():
    return pd.DataFrame.from_dict(st.session_state.result).to_csv().encode('utf-8')


if ( st.session_state.result == None):
    query = st.text_area("Enter Query")
    generate_filters_button = st.button("Generate Filters", on_click = generate_filters, args=[query])
    if(st.session_state.filter != None):
        st.write("Fill Out Any Filters")
        number_of_record = st.number_input("Enter Number of Records (Default is 200)", min_values=200, max_value=3000)
        c1, c2 = st.columns(2)
        with c1:
            min_num_of_employees = st.text_input("Enter Minimum Number of Employees", key="min_num_of_employees", value=st.session_state.filter["min_staff"])
        with c2:
            max_num_of_employees = st.text_input("Enter Maximum Number of Employees", key="max_num_of_employees", value=st.session_state.filter["max_staff"])            
        r1, r2 = st.columns(2)
        with r1:
            min_revenue = st.text_input("Enter Minimum Revenue", key="min_revenue", value=st.session_state.filter["min_rev"])
        with r2:
            max_revenue = st.text_input("Enter Maximum Revenue", key="max_revenue", value=st.session_state.filter["max_rev"])

        naics_code = st.text_input("Enter NAICS code")
        ownership = st.selectbox("Is Public or Private Company", ["", "private", "public"])
        investor_type = st.selectbox("Enter Investor Type", ["", "Private Equity", "Venture Capital", "Angel Investors", "Strategic Acquirers", "Instituional", "Government", "Lenders"])

        submitButton = st.button(label = 'Search', on_click=submit, args=[query, int(float(number_of_record)), (min_num_of_employees), max_num_of_employees, min_revenue, max_revenue, naics_code, ownership])

if st.session_state.result != None:
    st.write(st.session_state.time)
    st.write("Query:" + st.session_state.query)
    st.write("Filters Applied: \n" + st.session_state.filter_text)
    open = st.checkbox('Open Input To OpenSearch')
    if open:
        expanded = True
    else:
        expanded = False
    st.json(st.session_state.input_os_query, expanded = expanded)
    st.write("Result Table")
    st.dateframe(
        pd.DataFrame.from_dict(
            st.session_state.result
        ),
        column_config={
            "name": "Company Name",
            "id": st.column_config.NumberColumn("id", format="%d"),
            "url": st.column_config.LinkColumn("URL (Double Click to View)"),
            "naics": st.column_config.NumberColumn("NAICS", format="%d"),
            "relevancy_score": st.column_config.ProgressColumn("Relevancy Score", format='%.2f', min_value=0,max_value=1)
            "date_founded": st.column_config.NumberColumn("Date Founded", format="%d")

        },
        hide_index=True,
        width=3000,
    )
    csv = download_csv()
    st.download_button(label="Download To CSV", data=csv, file_name="results.csv", mine="text/csv")
    st.sidebar.header("Form")
    with st.sidebar:
        query = st.text_area("Enter Query")
        if(st.session_state.filter != None):
            st.write("Fill Out Any Filters")
            number_of_record = st.number_input("Enter Number Of Records (Defualt is 200)", min_value=200, max_value=3000)
    c1, c2 = st.columns(2)
    with c1:
        min_num_of_employees = st.text_input("Enter Minimum Number of Employees", key="min_num_of_employees", value=st.session_state.filter["min_staff"])
    with c2:
        max_num_of_employees = st.text_input("Enter Maximum Number of Employees", key="max_num_of_employees", value=st.session_state.filter["max_staff"])            
    r1, r2 = st.columns(2)
    with r1:
        min_revenue = st.text_input("Enter Minimum Revenue", key="min_revenue", value=st.session_state.filter["min_rev"])
    with r2:
        max_revenue = st.text_input("Enter Maximum Revenue", key="max_revenue", value=st.session_state.filter["max_rev"])

    naics_code = st.text_input("Enter NAICS code")
    ownership = st.selectbox("Is Public or Private Company", ["", "private", "public"])
    investor_type = st.selectbox("Enter Investor Type", ["", "Private Equity", "Venture Capital", "Angel Investors", "Strategic Acquirers", "Instituional", "Government", "Lenders"])

    submitButton = st.button(label = 'Search', on_click=submit, args=[query, int(float(number_of_record)), (min_num_of_employees), max_num_of_employees, min_revenue, max_revenue, naics_code, ownership])
