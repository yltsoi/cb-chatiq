# MODELS
CHAT_GPT = "chatgpt"
GPT4 = "gpt4"
CHAT_GPT_16K = "chatgpt-16k"
GPT4_32K = "gpt4-32k"
GPT4_TURBO = "gpt4-turbo"
GPT4O = "gpt4o"
GPT4O_NEW = "gpt4o-new"
GPT4O_APIM = "gpt4o-multitenant-apim"

# ENVIRONMENT
PROD = "PROD"

# CHATIQ_VERSION
CHATIQ_BASE = "chatiq_base"
CHATIQ_V2 = "chatiq_v2"

# LLM QA
ZERO_SHOT = "zero-shot"
MAP_REDUCE = "map-reduce"

# EMBEDDINGS
SBERT = "sbert"
OPENAI = "openai"
OPENAI_EMBEDDING_DIM = 1536

# NO_INTENT
No_INTENT = {}

# NO ANSUERS
NO_ANSWER_PHRASES = [
    "don't have any information",
    "I don't know",
    "I cannot answer this question",
    "no companies that meet the given criteria",
    "I cannot provide",
    "cannot provide a final answer",
    "I did not find any results'"
] 

# ERROR HANDLING
QUERY_TOO_SHORT = "I'm sorry, but I need more information to assist you.\nCould you please provide more details ?"
NO_AZURE_OPENAI_RESPONSE = "We're currently experiencing a temporary issue retrieving the necessary data. We apprepreciate your patience and understanding as we work to resolve this. Please try again later"
NO_COVERAGE_API_RESPONSE = "We're currently experiencing a temporary issue retrieving the necessary coverage data. We apprepreciate your patience and understanding as we work to resolve this. Please try again later"
ANSWER_NOT_FOUND = "I couldn't find that information from the given data. \n Please ask another question, and I'll be glad to help!"
NO_DOCUMENTS_FOUND = "I couldn't find any companies that meet your specifc criteria. This ",
TIMEOUT_ERROR_RESPONSE = "We're currently experiencing a temporary issue retrieving the necessary response to your query. We apprepreciate your patience and understanding as we work to resolve this. Please try again later"

DISCOVERY_OPENAI_INDEX = "openai-emb-may_23_opensearch_2_5_nmslib_5m-1"
PROD_VPC = "vpc-chatiq-opensearch-.....us-east-1.es.amazonaws.com"

# ANSWER CHUNK FORMAT
LIST_FORMAT = "list"
TEXT_BLOB_FORMAT = "text_blob"

SOURCE = "_source"

# DEFINED INTENTS
INTENT_CRESCENDO_ID = "cid"
INTENT_NAICS = "naics"
INTENT_OWNERSHIP = "ownership"
INTENT_INVESTOR_TYPE = "inv_typ"
INTENT_INVESTOR_NAME = "inv_name"
INTENT_MIN_STAFF = "min_staff"
INTENT_MAX_STAFF = "max_staff"
INTENT_MIN_REVENUE = "min_rev"
INTENT_MAX_REVENUE = "max_rev"
INTENT_MIN_FUNDING = "min_funding"
INTENT_MAX_FUNDING = "max_funding"
INTENT_INDUSTRY = "industry"
INTENT_INDUSTRY_TEXT = "industry_text"
INTENT_RELATIONSHIP = "relationship"
INTENT_LOCATION_TEXT = "location_text"
INTENT_LOCATION = "structured_location"
INTENT_RELATIONSHIP_STATUS = "relationship_status"
INTENT_PUBLIC = "public"
INTENT_PRIVATE = "private"
INTENT_ECI = "eci"
INTENT_YES = "Yes"
INTENT_NO = "No"
INTENT_COVERED = "covered"

# ATTRIBUTES FROM COMAPNY CARD
ATTR_CRESCENTO_ID
ATTR_COMPANY_ID
ATTR_COMPANY_NAME
ATTR_COMPANY_DESCRIPTION
ATTR_COMPANY_NAICS_DESCRIPTION
ATTR_NAICS
ATTR_OWNERSHIP
ATTR_OWNERSHIP_PUBLIC
ATTR_STAFF
ATTR_REVENUE
ATTR_FUNDING
ATTR_INVESTOR_NAME
ATTR_INVESTOR_TYPE
ATTR_TEXT_DOC
ATTR_RELATIONSHIP
ATTR_COMPANY_ADDRESS
ATTR_COMPANY_STREET_ADDRESS
ATTR_COUNTRY
ATTR_STATE
ATTR_CITY
ATTR_RELATIONSHIP_STATUS
ATTR_CLIENT_STATUS
ATTR_EXPANDED_VERTICAL
ATTR_EXPANDED_OFFERING
ATTR_COMPANY_SPONSOPSHIP
ATTR_COMPANY_CEO
ATTR_COMPANY_DATE_FOUNDED
ATTR_COMPANY_PARENT  = "company_parent"
ATTR_EXPANDED_BUSINESS_MODEL = "expanded_business_model"
ATTR_ECI = "jpmc_eci"
ATTR_ZIP = "company_zip"
ATTR_LATITURE = "company_latitude"
ATTR_LONGITUDE = "company_longitude"
ATTR_COVERED = "covered"
ATTR_YES = "Yes"
ATTR_NO = "NO"


COUNTRY = "country"
STATE = "state"
CITY = "city"

CLIENT_STATUS_LIST = ["Active", "Prospect", "Format", "Inactive", "Non Client"]

COMPANY_INDEX = "company"
INVESTOR_INDEX = "investor"

