import json
import os
import time

from dtos.req_res import ChatIQRequest
from dtos.vector_db_connection import Confirmation
from service.base.components.admin.admn_client import Admin
from service.base.components.admin.os_admn_client import VectorDBAdminService
from service.base.components.admin.snapsot_client import Snapshot
from service.base.components.utils.constants import *

class AdminService:
    def __init__(self, os_admin=None, snapshot=None):
        if os_admin == None:
            os_admin = VectorDBAdminService()
        if admin == None:
            admin = Admin()
        if snapshot == None:
            snapshot = Snapshot()

        self.os_admin = os_admin
        self.admin = admin
        self.snapshot = snapshot

    def create_os_index(self):
        self.os_amdin.create_os_index()

    def delete_os_index(self, payload: Confirmation):
        _payload = {"confirmation": payload.confirmation}
        indices = self.os_admin.delete_os_index(_payload)
        return {"current_indices": indices}
    
    def os_cluster_status(self):
        return self.os_admin.os_clsuter_status()
    

    def delete_crescendo_id(self, cid, payload):
        res = self.os_admin.delete_crescendo_id(cid, payload)
        return {"deleted": res.get("deleted")}

    def get_crescendo_id(self, cid):
        res = self.os_admin.get_crescendo_id(cid)
        return {"deleted": res.get("hits")}

    def query_os(self, query, index_name):
        return self.os_admin.query_os(query, index_name)
    
    def purge_queue(self, url, confirmation):
        return self.admin.purge_queue(url, confirmation)
    
    def delete_sqs_message(self, q_url, receipt_handle, confirmation):
        return self.admin.delete_sqs_message(
            q_url, receipt_handle,  confirmation
        )
    
    def openai_embed_query_demo(self, query):
        return {"embeddings": self.admin.openai_embed_query_demo(query)}
    
    def get_request_id(self, request_id, date):
        try:
            return self.admin.get_response_id(request_id, date)
        except:
            return 404,  {"error": "Not Found"}
    
    def get_repositories(self):
        return self.snapshot.get_repositories()
    
    def get_snapshots(self, repository):
        return self.snapshot.get_snapshots(repository)
    
    def restore_from_snapshot(self, repository, snapshot, index=None):
        if index:
            index = {"indices": index}
        
        return self.snapshot.restore(repository, snapshot, index)