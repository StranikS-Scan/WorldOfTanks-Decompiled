# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/armor_inspector_common/schemas.py
from armor_inspector_common.models import ArmorInspectorConfigModel
from base_schema_manager import GameParamsSchema
from dict2model import fields
armorInspectorConfigSchema = GameParamsSchema[ArmorInspectorConfigModel](gameParamsKey='armor_inspector_config', fields={'enabled': fields.Boolean(required=True),
 'linkButtonURL': fields.String(required=False, default=None),
 'disabledVehicle': fields.UniCapList(fieldOrSchema=fields.String(required=True), required=False, default=list)}, modelClass=ArmorInspectorConfigModel)
