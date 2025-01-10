# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: flights.proto
# Protobuf Python Version: 5.29.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    3,
    '',
    'flights.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rflights.proto\"k\n\x04Info\x12\x19\n\x04\x64\x61ta\x18\x03 \x03(\x0b\x32\x0b.FlightData\x12\x1e\n\npassengers\x18\x08 \x03(\x0e\x32\n.Passenger\x12\x13\n\x04seat\x18\t \x01(\x0e\x32\x05.Seat\x12\x13\n\x04trip\x18\x13 \x01(\x0e\x32\x05.Trip\"\xc5\x01\n\nFlightData\x12\x0c\n\x04\x64\x61te\x18\x02 \x01(\t\x12\x33\n\x0foutbound_flight\x18\x04 \x01(\x0b\x32\x15.ParentOutboundFlightH\x00\x88\x01\x01\x12\x16\n\tmax_stops\x18\x05 \x01(\x05H\x01\x88\x01\x01\x12\x1d\n\x0b\x66rom_flight\x18\r \x01(\x0b\x32\x08.Airport\x12\x1b\n\tto_flight\x18\x0e \x01(\x0b\x32\x08.AirportB\x12\n\x10_outbound_flightB\x0c\n\n_max_stops\"{\n\x14ParentOutboundFlight\x12\x14\n\x0c\x66rom_airport\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61te\x18\x02 \x01(\t\x12\x12\n\nto_airport\x18\x03 \x01(\t\x12\x14\n\x0c\x61irline_code\x18\x05 \x01(\t\x12\x15\n\rflight_number\x18\x06 \x01(\t\"\x1a\n\x07\x41irport\x12\x0f\n\x07\x61irport\x18\x02 \x01(\t*E\n\x04Trip\x12\x10\n\x0cUNKNOWN_TRIP\x10\x00\x12\x0e\n\nROUND_TRIP\x10\x01\x12\x0b\n\x07ONE_WAY\x10\x02\x12\x0e\n\nMULTI_CITY\x10\x03*-\n\tPassenger\x12\x15\n\x11UNKNOWN_PASSENGER\x10\x00\x12\t\n\x05\x41\x44ULT\x10\x01*S\n\x04Seat\x12\x10\n\x0cUNKNOWN_SEAT\x10\x00\x12\x0b\n\x07\x45\x43ONOMY\x10\x01\x12\x13\n\x0fPREMIUM_ECONOMY\x10\x02\x12\x0c\n\x08\x42USINESS\x10\x03\x12\t\n\x05\x46IRST\x10\x04\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'flights_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TRIP']._serialized_start=479
  _globals['_TRIP']._serialized_end=548
  _globals['_PASSENGER']._serialized_start=550
  _globals['_PASSENGER']._serialized_end=595
  _globals['_SEAT']._serialized_start=597
  _globals['_SEAT']._serialized_end=680
  _globals['_INFO']._serialized_start=17
  _globals['_INFO']._serialized_end=124
  _globals['_FLIGHTDATA']._serialized_start=127
  _globals['_FLIGHTDATA']._serialized_end=324
  _globals['_PARENTOUTBOUNDFLIGHT']._serialized_start=326
  _globals['_PARENTOUTBOUNDFLIGHT']._serialized_end=449
  _globals['_AIRPORT']._serialized_start=451
  _globals['_AIRPORT']._serialized_end=477
# @@protoc_insertion_point(module_scope)
