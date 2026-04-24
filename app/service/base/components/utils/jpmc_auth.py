import getpass
import os
import subprocess
from datetime import datetime
from time import sleep
from service.base.components.utils.utils import get_region_name
import boto3
import openai
import requests
from openai import cli

region = get_region_name()
s3 = boto3.client("s3", region_name=region, endpoint_url= f"https://s3.{region}.amazonaws.com/", verify=False)
secrets_manager = boto3.client("secretsmanger", region,  endpoint_url= f"https://secretsmanager.{region}.amazonaws.com/", verify=False)

if "no_proxy" in os.environ:
    if "jpmchase.net" not in os.environ["no_proxy"]:
        os.environ["no_proxy"] = os.environ["no_proxy"] + ",jpmcahse.net"

if "no_proxy" in os.environ:
    if os.environ["no_proxy"].split(","[-1] != "openai.azure.com"):
        os.environ["no_proxy"] = os.environ["no_proxy"] + ",openai.azure.com"




def update_openai_object(
        api_key=None,
        api_base=None,
        api_type=None,
        api_version=None,
):
    """
    Update the OpenAI API object with the provided configuration parameters

    this function take in optional parameter for API key, gateway URL, API type,
    and API version, and updates the OpenAI object accordingly. If any of 
    parameters is not provided, the corresponding attribute of the object
    will remain unchanged

    :param api_key: str, The API key use for authentication
    :param gateway_url: str, The gateway URL for API requestt
    :param api_type: str, The type of API to be used
    :param api_version: str, The version of the API 
    
    """
    if api_type:
       openai.api_type = api_type

    if api_base:
       openai.api_base = api_base

    if api_version:
       openai.api_version = api_version

    if api_key:
       openai.api_key = api_key

def get_openai_attributes():
    attrs = {}
    attrs["api_base"]  = openai.api_base
    attrs["api_version"]  = openai.api_version
    attrs["api_type"]  = openai.api_type
    return attrs

def create_header_for_requests(access_token)  :
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
   
def set_access_token(access="No_value"):
    access_token = access

def get_access_token():
    return access_token

def get_openai_access_token(
        cred_file_path="service/base/components/utils/creds.txt"
):
    access_token = ""
    if cred_file_path and os.path.exists(cred_file_path):
            f= open(cred_file_path, "r")
            access_token = f.read().strip()
            f.close()
    
    if len(access_token) == 0:
        token_obj = secrets_manager.get_secret_value(
            SecretId = "/application/openai-chatiq/access_token_test"
        )
        print("Token retrieved from SecretManagger")
        token = token_obj["SecretString"]
        return token
    else:
        f = open(cred_file_path, "r")
        access_token = f.read().strip()
        f.close()
        return access_token


def get_elasticache_token():
    try:
        token_obj = secrets_manager.get_secret_value(
            SecretId="/application/elasticache-token-app-elasticache-cluster"
        )
        print("Token retrieved from SecretManagger")
        token = token_obj["SecretString"]
        return token
    except Exception as e:
        print(e)


def get_coverage_token():
    try:
        token_obj = secrets_manager.get_secret_value(
            SecretId="/application/openai-ts/cbds_token"
        )
        
        secret = get_secret_value_response["SecretString"]
        return secret
    except Exception as e:
        print(e)

