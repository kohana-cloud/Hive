import src.code.gRPC.proto.query_pb2_grpc as rpc
import src.code.gRPC.proto.query_pb2 as query

from datetime import datetime
from time import perf_counter
import grpc
import json

SERVER_HOST = "localhost"
SERVER_PORT = 15001

class QueryClient(object):
    def __init__(self, tls_enabled:bool, public_key:str):
        if tls_enabled:
            tls_secret = grpc.ssl_channel_credentials(public_key)
            self.channel = grpc.secure_channel(f"{SERVER_HOST}:{SERVER_PORT}", tls_secret)
        else:
            self.channel = grpc.insecure_channel(f"{SERVER_HOST}:{SERVER_PORT}")

        self.stub = rpc.QueryServerStub(self.channel)
    
    def get_honeypots(self):
        return self.stub.GetHoneypots(query.Empty())
    
    def new_honeypot(self, type:str):
        return self.stub.NewHoneypot(query.StartHoneypot(
                type=type
            ))


def query_for_honeypots(tls_enabled:bool, public_key:str) -> str:
    client = QueryClient(tls_enabled, public_key)
    honeypots = client.get_honeypots().HoneypotsAsJSON

    return json.loads(honeypots)


def new_honeypot(type:str, tls_enabled:bool, public_key:str) -> str:
    client = QueryClient(tls_enabled, public_key)
    client.new_honeypot(type=type)
