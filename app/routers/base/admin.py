import os
import requests
from fastapi import APIRouter, Security, HTTPException, status
from fastapi.security import APIKeyHeader

from service.base.admin_service import AdminService
from service.base.components.authorizer.authorizer import Authorizer

from dtos.vector_db_connection import Confirmation, SQSData, OSQuery
from dtos.req_res import ChatIQRequest, RestoreRequest, LLMRequest, UserToken
from service.base.components.utils.constants import CHATIQ_BASE
from srevice.base.componetns.utils.jpmc_auth import (
    get_openai_access_token
)
from service.base.chatiq_qaservice import ChatIQ_QAService

router = APIRouter()

API_USER = 'API_USER'
API_PRIVILEGED_USER = 'API_PRIVILEGED_USER'
API_ADMIN = 'API_ADMIN_USER'

def get_api_key(
    api_key_header: str = Security(
        APIKeyHeader(name = "Authorization", auto_error=False)
    )
):
    #print(api_key_header)
    if api_key_header is not None:
        return api_key_header
    raise HTTPException(
        stauts_code = status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )

def validate(role, token):
    try:
        return Authorizer().validate_token(
            os.environ["ENVIRONMENT"] + "_" + role, str(token)
        )   
    except Exception:
        return False

@router.get("/create-os-index")
def create_os_index(api_key: str = Security(get_api_key)):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    if validate( API_ADMIN, api_key):
        return AdminService().create_os_index()
    else:
        return {"Error": "UNauthorized"}

@router.get("/delete-os-index")
async def delete_os_index(api_key: str = Security(get_api_key)):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    if validate( API_ADMIN, api_key):
        return AdminService().delete_os_index()
    else:
        return {"Error": "UNauthorized"}


@router.get("/get-os-cluster-status")
async def os_cluster_status(api_key: str = Security(get_api_key)):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    if validate( API_ADMIN, api_key):
        return AdminService().os_cluster_status()
    else:
        return {"Error": "UNauthorized"}

@router.post("/delete-crescendo-id/{crecendo_id}")
async def delete_crescendo_id(
    crescendo_id: str,
    payload: Confirmation,
    api_key: str = Security(get_api_key),
):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    if validate( API_ADMIN, api_key):
        return AdminService().delete_crescendo_id(crescendo_id, payload)
    else:
        return {"Error": "UNauthorized"}


@router.post("/query-os")
async def query_os(payload: OSQuery):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    response =  AdminService().query_os(payload.os_query, payload.index_name)
    return response

@router.post("/query-os-driver")
async def query_os_driver(payload: OSQuery):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    response =  AdminService().query_os(payload.os_query, payload.index_name)
    return response


@router.post("/purge-queue")
async def purge_queue(
    q_payload: SQSData, api_key: str = Security(get_api_key)
):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    if validate( API_ADMIN, api_key):
        return AdminService().purge_queue( q_payload.url, q_payload.confirmation)
    else:
        return {"Error": "UNauthorized"}


@router.get("/get_azure_token")
async def get_azure_token(api_key: str= Security(get_api_key)):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    if validate(API_PRIVILEGED_USER, api_key):
        return get_openai_access_token()
    else:
        return {"Error": "UNauthorized"}
    
@router.post("/get_embedding")
async def get_embeddding(request: ChatIQRequest):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    return ChatIQ_QAService().get_embeddings(request)
    