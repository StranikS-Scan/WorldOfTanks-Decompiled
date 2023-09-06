# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/resources/cdn/config.py
import typing
from dict2model import fields, schemas, validate
from gui.collection.resources.cdn.models import ConfigModel, Group, ImageModel, Sub
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
imageSchema = schemas.Schema(fields={'group': fields.Enum(Group, required=True),
 'sub': fields.Enum(Sub, required=True),
 'name': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'url': fields.Url(required=True, relative=False)}, modelClass=ImageModel, checkUnknown=True)
configSchema = schemas.Schema(fields={'images': fields.List(fieldOrSchema=imageSchema, required=True)}, modelClass=ConfigModel, checkUnknown=True)

def createConfigModel(rawData):
    return configSchema.deserialize(rawData, silent=True)
