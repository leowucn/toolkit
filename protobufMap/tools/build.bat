set SOURCE_DIR=../proto
set DESTINATION_DIR=../as/protobuf

::protoc --plugin=protoc-gen-as3="protoc-as3.bat" --as3_out=%DESTINATION_DIR% --proto_path=%SOURCE_DIR% %SOURCE_DIR%/*.proto

python .\generateMapFile.py ../proto/ ../as/protobuf/


