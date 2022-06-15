#!/bin/bash
echo "Generating proto grpc files..."
python3 -m grpc_tools.protoc -I=src/code/gRPC/proto/ --python_out=src/code/gRPC/proto/ --grpc_python_out=src/code/gRPC/proto/ src/code/gRPC/proto/query.proto
echo "DONE"