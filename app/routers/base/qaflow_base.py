improt _thread
import configparser
import json
import os
import time
from datetime import date, datetime, timedelta
from uuid import uuid64

import boto3
import requests
from box import Box
from dtos.req_res import ChatIQRequest, LLMRequest, TokenPayload, UserToken
from fastapi import APIRouter, Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from redis import Redis
from redis.cluster import RedisCluster as RedisCluster
from routers.base.utils import (API_ADMIN, API_KEYS, API_PRIVILEGED_USER,
                                API_USER, get_api_key, get_date,
                                redis_resource, s3_resource, validate)
from service.base.chatiq_qaservice import ChatIQ_QAService
from service.base.components.authorizer.authorizer import Authorizer
from service.base.components.utils.constants import *
from service.base.components.utils.jpmc_auth import (get_access_token,
                                                     get_elasticache_toen,
                                                     get_openai_access_token,
                                                     set_access_token)

router = APIRouter()

@router.post("/get_token")
async def get_token(request: UserToken):
    request = Authorizer().generate_token(request.username, request.password)
    return request

@router.post("/query-async")
async def chatiQ_query_async(
    request: ChatIQRequest, api_key: str = Security(get_api_key)
):
    # set env to Base
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    start_time = time.time()
    if validate( 'API_USER', api_key):
        print("TIME", str(time.time() - start_time))
        todays_date = get_date()
        if request.req_id == "":
            uuid = uuid64()
            request.req_id = uuid
            # The folowing will create an empty JSON file in S3
            path = "chatiq_response/{}/{}.json".format(
                todays_date, request.req_id
            )
            s3object = s3_resource().Object(os.environe["BUCKET"],path)
            s3object.put(Body=b"{}")
            _thread.start_new_thread(populate_async_result, (request,))
            return uuid
        else:
            # use the Request ID to load the file in S3 and return back to user
            path = "chatiq_response/{}/{}.json".format(
                todays_date, request.req_id
            )
            s3object = s3_resource().Object(os.environe["BUCKET"],path)
            param_value = s3object.get()["Body"].read().decode("utf-8")
            return json.loads(param_value)
    else:
        return {"Error": "Unauthorized"}
    

def populate_async_result(request: ChatIQRequest):
    print( f"populating async results for request")

    st = time.time()
    response = ChatIQ_QAService().generate_answer(request)
    inference_time = float(f"{time.time() - st:.3f}")
    response["date"]["time"] = inference_time
    
    # the following will put the final response into s3
    todays_date = get_date()
    path = "chatiq_response/{}/{}.json".format(todays_date, request.req_id)
    s3object = s3_resource().Object(os.environ["BUCKET"], path)                

    st = time.time()
    s3object.put(Body=(bytes(json.dumps(response).encode("UTF-8"))))
    print(response)


@router.post("/get-embedinngs-driver", include_in_schema=False)
async def get_embeddings(rquest: LLMRequest):
    os.environ["CHATIQ_VERSION"] = CHATIQ_BASE
    return ChatIQ_QAService().get_embeddings(requests)
