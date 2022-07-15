import src.code.gRPC.proto.query_pb2_grpc as rpc
import src.code.gRPC.proto.query_pb2 as query

from datetime import datetime
from time import perf_counter
import grpc
import json

SERVER_HOST = "172.17.0.1"
SERVER_PORT = 15001

TLS_ENABLED = False

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
    
    def control_honeypot(self, control_message:str):
        return self.stub.ControlHoneypot(query.HoneypotControlCommand(
                message=control_message
            ))


def query_honeypots(tls_enabled:bool, public_key:str) -> str:
    client = QueryClient(tls_enabled, public_key)
    honeypots = client.get_honeypots().HoneypotsAsJSON

    return json.loads(honeypots)


def control_honeypot(control_message:str, tls_enabled:bool, public_key:str) -> str:
    client = QueryClient(tls_enabled, public_key)
    client.control_honeypot(control_message)
