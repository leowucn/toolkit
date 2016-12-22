#!/bin/bash
SOURCE_DIR=../proto/
DESTINATION_DIR=../as/protobuf/

#./protoc --plugin=protoc-gen-as3="protoc-as3" --as3_out=$DESTINATION_DIR  --proto_path=$SOURCE_DIR $SOURCE_DIR*

python ./generateMapFile.py ../proto/ ../as/protobuf/
