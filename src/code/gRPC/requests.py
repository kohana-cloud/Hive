import src.code.gRPC.proto.query_pb2_grpc as rpc
import src.code.gRPC.proto.query_pb2 as query

from datetime import datetime
from time import perf_counter
import grpc
import json

SERVER_HOST = "localhost"
SERVER_PORT = 15001

class QueryClient(object):
    def __init__(self, tls:bool=False):
        if tls:
            with open('cert/server.crt', 'rb') as fio:
                tls_secret = grpc.ssl_channel_credentials(fio.read())
            self.channel = grpc.secure_channel(f"{SERVER_HOST}:{SERVER_PORT}", tls_secret)
        else:
            self.channel = grpc.insecure_channel(f"{SERVER_HOST}:{SERVER_PORT}")

        self.stub = rpc.QueryServerStub(self.channel)
    
    def get_honeypots(self):
        return self.stub.GetHoneypots(query.Empty())
    
    def new_honeypot(self):
        return self.stub.NewHoneypot(query.Honeypot())

def query_for_honeypots():
    client = QueryClient(tls=False)
    honeypots = client.get_honeypots().HoneypotsAsJSON

    return json.loads(honeypots)

def new_honeypot():
    client = QueryClient(tls=False)
    client.new_honeypot()
