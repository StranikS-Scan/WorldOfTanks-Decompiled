# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/battle/lore_settings_model.py
import ResMgr
import section2dict
import typing
from dict2model import models, schemas, fields, validate
_LORE_SETTINGS_PATH = 'story_mode/gui/lore.xml'

class MissionLoreModel(models.Model):
    __slots__ = ('id', 'music', 'vo', 'battleMusic')

    def __init__(self, id, music, vo, battleMusic):
        super(MissionLoreModel, self).__init__()
        self.id = id
        self.music = music
        self.vo = vo
        self.battleMusic = battleMusic


class EpilogueLoreModel(models.Model):
    __slots__ = ('music', 'vo')

    def __init__(self, music, vo):
        super(EpilogueLoreModel, self).__init__()
        self.music = music
        self.vo = vo


class LoreSettingsModel(models.Model):
    __slots__ = ('mission', 'epilogue')

    def __init__(self, mission, epilogue):
        super(LoreSettingsModel, self).__init__()
        self.mission = mission
        self.epilogue = epilogue


missionLoreSchema = schemas.Schema(fields={'id': fields.Integer(required=True, serializedValidators=validate.Range(minValue=1), deserializedValidators=validate.Range(minValue=1)),
 'music': fields.String(required=True),
 'vo': fields.String(required=True),
 'battleMusic': fields.String(required=True)}, modelClass=MissionLoreModel, checkUnknown=True)
epilogueLoreSchema = schemas.Schema(fields={'music': fields.String(required=True),
 'vo': fields.String(required=True)}, modelClass=EpilogueLoreModel, checkUnknown=True)
loreSchema = schemas.Schema(fields={'mission': fields.UniCapList(fieldOrSchema=missionLoreSchema, required=True, deserializedValidators=validate.Length(minValue=1)),
 'epilogue': fields.Nested(schema=epilogueLoreSchema, required=True, public=False)}, modelClass=LoreSettingsModel, checkUnknown=True)
__loreSchema = None

def getLoreSettings():
    global __loreSchema
    if __loreSchema:
        return __loreSchema
    root = ResMgr.openSection(_LORE_SETTINGS_PATH)
    rawData = section2dict.parse(root)
    __loreSchema = loreSchema.deserialize(rawData)
    return __loreSchema
