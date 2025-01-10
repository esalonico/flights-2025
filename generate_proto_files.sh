cd fast_flights
protoc --proto_path=. --python_out=. common.proto 
protoc --proto_path=. --python_out=. flights.proto 
protoc --proto_path=. --python_out=. return_flights.proto 

 