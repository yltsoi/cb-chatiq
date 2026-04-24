import os
import boto3
import json
import time
from datetime import date, datetime, timedelta

from redis import Redis
from redis.cluster import RedisCluster as RedisCluster

from fastapi import APIRouter, Security, Header, HTTPException, status
from fastapi.security import APIKeyHeader

from dtos.req_res import ChatIQRequest, TokenPayload, UserToken, LLMRequest
from service.base.components.authorizer.authoirzer import Authorizer
from service.base.componetns.utils.jpmc_auth import (
    set_access_token,
    get_access_token,
    get_openai_access_token,
    get_elasticache_token
)
from service.base.component.utils.constants import *

API_KEYS = []
API_USER = 'API_USER'
API_PRIVILEDG_USER = 'API_PRIVILEDG_USER'
API_ADMIN_USER = 'API_ADMIN_USER'

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


def s3_resource():
    region = "us-east-1"
    try:
        region = boto3.session.Session().region_name
        if region is None:
            region = "us-east-1"
    except Exception as e:
        print(f"Error fetching region name, defaulting to us-east-1: {e}")
    return boto3.resource("s3", endpoint_url=f"https://s3.{region}.amazonaws.com", verify=False)

def redis_resource():
    token = get_elesticache_token()
    token = json.loads(token)
    return RedisCluster(host=str(os.environ["REDIS_HOST"]), port=int(os.environ('REDIS_PORT'),ssl=True, password=str(token['authToken'])))


def get_date():
    new_date = date.today()
    date_str = new_date.isoformat()
    todays_date = date_str.replace("-", "")[:8]
    return todays_date

