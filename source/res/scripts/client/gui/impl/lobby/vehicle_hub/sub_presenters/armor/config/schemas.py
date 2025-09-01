# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/config/schemas.py
from __future__ import absolute_import
from dict2model import schemas, fields, validate
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config.models import ArmorScaleModel, ColorListModel, TierModel, ConfigModel, TierListModel
TIER_MIN_VALUE = 1
TIER_MAX_VALUE = 11
colorListSchema = schemas.Schema(fields={'normalArmor': fields.UniCapList(fieldOrSchema=fields.String(required=True), required=True, deserializedValidators=validate.Length(minValue=2)),
 'spacedArmor': fields.UniCapList(fieldOrSchema=fields.String(required=True), required=True, deserializedValidators=validate.Length(minValue=2))}, modelClass=ColorListModel)
armorScaleSchema = schemas.Schema(fields={'min': fields.Integer(required=True),
 'max': fields.Integer(required=True)}, modelClass=ArmorScaleModel)
tierSchema = schemas.Schema(fields={'number': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=TIER_MIN_VALUE, maxValue=TIER_MAX_VALUE)),
 'normalArmor': fields.Nested(schema=armorScaleSchema, required=True),
 'spacedArmor': fields.Nested(schema=armorScaleSchema, required=True)}, modelClass=TierModel)
tierListSchema = schemas.Schema(fields={'tier': fields.UniCapList(fieldOrSchema=tierSchema, required=True)}, modelClass=TierListModel)
configSchema = schemas.Schema(fields={'tierList': fields.Nested(schema=tierListSchema, required=True),
 'colorList': fields.Nested(schema=colorListSchema, required=True),
 'blindColorList': fields.Nested(schema=colorListSchema, required=True),
 'blendingAlpha': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0, maxValue=1))}, modelClass=ConfigModel)
__config = None
