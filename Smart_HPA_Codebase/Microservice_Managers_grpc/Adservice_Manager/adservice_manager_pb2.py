# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: Microservice_Managers_grpc/Adservice_Manager/adservice_manager.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'Microservice_Managers_grpc/Adservice_Manager/adservice_manager.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nDMicroservice_Managers_grpc/Adservice_Manager/adservice_manager.proto\x12\x11\x61\x64service_manager\"\x19\n\x17MicroserviceDataRequest\"\xa4\x01\n\x10MicroserviceData\x12\x19\n\x11microservice_name\x18\x01 \x01(\t\x12\x16\n\x0escaling_action\x18\x02 \x01(\t\x12\x18\n\x10\x64\x65sired_replicas\x18\x03 \x01(\x05\x12\x18\n\x10\x63urrent_replicas\x18\x04 \x01(\x05\x12\x13\n\x0b\x63pu_request\x18\x05 \x01(\x05\x12\x14\n\x0cmax_replicas\x18\x06 \x01(\x05\x32~\n\x10\x41\x64serviceManager\x12j\n\x17\x45xtractMicroserviceData\x12*.adservice_manager.MicroserviceDataRequest\x1a#.adservice_manager.MicroserviceDatab\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MICROSERVICEDATAREQUEST']._serialized_start=91
  _globals['_MICROSERVICEDATAREQUEST']._serialized_end=116
  _globals['_MICROSERVICEDATA']._serialized_start=119
  _globals['_MICROSERVICEDATA']._serialized_end=283
  _globals['_ADSERVICEMANAGER']._serialized_start=285
  _globals['_ADSERVICEMANAGER']._serialized_end=411
# @@protoc_insertion_point(module_scope)
