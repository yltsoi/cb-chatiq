import os
import boto3
import jwt
import requests

from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException, status
from service.base.componetns.utils.utils import get_region_name

class Authorizer:

    def __init__(self, s3_client=None):
        if s3_cleitn == None:
            region = get_region_name()
            s3_client = bot3.client("lambda", region_name =region, endpoint_url=f"https://lambda.{region}.amazonaws.com", verify=False)
        self.s3_client = s3_client

        self.roles_lookup = {
            "PROD_API_USER" : "APIUser-122474-10866-PROD",
            "PROD_API_PRIVILED_USER" : "APIPriviledgedUser-122474-10866-PROD",
            "PROD_API_ADMIN_USER": "APIAdmin-122474-10866-PROD"
        }

    def generate_token( self, username, password):
        authTokenURL = os.environ["IDA_URL"]

        if username is None or password is None:
            raise ValueError(("Invalid username and/or password\n"))
        payload = {
            "client_id": os.environ["CLIENT_ID"],
            "resource":  os.environ["RESOURCE_ID"],
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        request = requests.post(authTokenURL, data=payload)
        access_token = request.json().get("access_token", request.json())

        return f"Bearer {access_token}"
    
    def validate_token(self, role, token):
        try:
            token = token.replace("Bearer ", "")
            decode_token = jwt.decode(
                token, options={"verify_signature": False}
            )
            roles = decoded_token["Role"]
            if roles is not None and self.roles_lookup[role] in roles:
                return True
            return False
        except Exception as e:
            return False

    def get_api_key(
            api_key_header: str=Security(
                APIKeyHeader(name="Authorization", auto_error=False)
            )
    ):
        print(api_key_header)
        if api_key_header is not None:
            return api_key_header
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Unauthorized",
        )
    
    def validate(role, token):
        try:
            return Authorizer().valide_token(
                os.environ["ENVIRONMENT"] + "_" + role, str(token)
            )
        except Exception:
            return False
    
    