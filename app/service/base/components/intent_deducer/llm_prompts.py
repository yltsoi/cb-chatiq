# LLM Prompt for QA
from typing import ANy, Dict, List, Optional, TYpeDict

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    FewShotPromptTemplate,
    PromptTemplate,
    StringPromptTemplate,
)
from pydantic import BaseMOdel, Field, validator


examples_list = [
    {
        "question": "List me 6 companies in the telecommunicaiton indudstry with few than 1K employees and annual revenue between 100mm and 1B",
        "intent": '{{"min_rev": "1000000000", "max_rev": "100000000", max_staff: "1000", "industry": "telecommunication"}}'
    },
    {
        "question": "Provide 10 companies in entertainment industry withless than 2bn in revenue and over 1,000 employees",
        "intent": '{{"max_rev": "100000000", min_staff: "1000", "industry": "entertainment"}}'
    },
    {
        "question": "Identify 15 companies in the travel and tourism industry with less than 1.3bn in annual revenue and over 4000 employees",
        "intent": '{{"max_rev": "130000000", min_staff: "4000", "industry": "travel and tourism"}}'
    },
    {
        "question": "How many private FinTech companies in London were founded afer 2015?",
        "intent": '{{"ownership": "private", "industry": "FinTech", "location_text": "London", "location" : {{"GNR": ["London"]}}}}'
    },
    {
        "question": "Are there companiese with revenue between $10MM and $30MM?",
        "intent": '{{"min_ev": "100000000", max_rev: "3000000000"}}'
    },
    {
        "question": "Tell me about CID 1017520448, 1221241789, 10014121, 12412412541241",
        "intent": '{{"cid": ["1017520448", "1221241789", "10014121", "12412412541241"]}}'
    },
    {
        "question": "Find me 25 companies with a NAICS code of 454632 having at least $10b in revenue and located in Chicago",
        "intent": '{{"NAICS": ["45632"], "min_rev": 1000000000", "location_text": "Chicago, "location": {{"USA":{{"Illinoi": ["Chicago"]}}}}]}}'

    },
    
]

prefix_qintent_template = """
You are an expoert intent extractor who extracts the desired intent filters from input questions string.
Here are the instructions to succeed at your job:
1. Return the response in a json format ONLY
2. You are ONLY allowed to use information only from the user question text within the ''' boundary to extract all desired intents. You ARE NOT PERMIITTED TO use any other information to generate your answer.
3. The relevant intents we wish to extract are NAICS code, Crescendo ID ( or CID), ownership, industry, location, revenue, or employee counts. You should return an empty json if you do not recognize any of those intents in the test
4. You must extract numbers related to revenue or employee count from the input question
5. If present, you should map lower limit on revenue to 'min_rev' key
6. If present, you should map upper limit on revenue to 'max_rev' key
7. If present, you should map lower limit on employee_count or staff to 'min_staff' key
8. if present, you should map upper limit on employee_count or staff to 'max_staff' key
9. You must extract NAICS coddes ONLY if they are present in the input text. Ownership is either public or private
10. You must extract ownership of company if they are present in the input text. The industry is a string from  the input question
11. Extract the company's location from the input text if it is present. If the location is in the USA, include the city, state, and country. For other countries, include the city and country. If the location is a region, provide a list of major cities within that region, the size of major cities should not over 20 
12 You must extract the industry of the company if it is present. The industry is a string form the input question
13. If present, you should map NAICS code to the NAICS key. There can be mulitple NAICS codde and you can populate the key with a list of those extracted NAICS code
14. DO NOT generate NAICS code in your output if the number is not present in the input text
15. DO NOT generate ownership in your output if public or private is not present in the input text
16. You should also extract Crescendo IDs ( also called as CID) that are 10 digit number starting with 1 from the input question
17. If present you should map CIDs to the 'cid' key. There can be multiple CIDs and you can populate the key with a list of those extracted CIDs
18. You must ensure that you only extract numeric characters and not alphabets or symbles like '$' or 'mm'
19. If the location is present, output the data in a dictionary format with the country's ALPHA-3 code as the key
"""

suffix_qintent_template = """
Begin:
Question: ```{question}```
Intent:
"""

example_qintent_template = """
Begin:
Question: ```{question}```
Intent:
"""

example_qintent_prompt = PromptTemplate(
    input_variables=["question", "intent"], template=example_qintent_template
)

FEW_SHOT_QINTENT_TEMPLATE = FewShotPromptTemplate(
    examples = examples_list,
    example_prompt = example_qintent_prompt,
    prefix = prefix_qintent_template,
    suffix = suffix_qintent_template,
    input_variables=["question"],
    example_separator="\n\n",
)
