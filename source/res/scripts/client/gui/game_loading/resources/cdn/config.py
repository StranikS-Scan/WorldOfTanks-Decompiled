# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/cdn/config.py
import typing
from dict2model import fields
from dict2model import schemas
from dict2model import validate
from dict2model import exceptions
from gui.game_loading import loggers
from gui.game_loading.resources.cdn.consts import SequenceOrders, SequenceCohorts, MAX_CONFIG_SEQUENCE_SLIDES_COUNT, MAX_CONFIG_SEQUENCES_COUNT
from gui.game_loading.resources.consts import ImageVfxs
from gui.game_loading.resources.cdn.models import ConfigSequenceModel, ConfigModel, ConfigSlideModel
_logger = loggers.getCdnConfigLogger()

def _validateSequenceLifeTime(model):
    if model.start >= model.finish:
        raise exceptions.ValidationError('Started date: {} >= finished: {}'.format(model.start, model.finish))


def _validateSequencesNames(model):
    sequencesNames, nameDuplicates = set(), set()
    for sequence in model.sequences:
        if sequence.name in sequencesNames:
            nameDuplicates.add(sequence.name)
        sequencesNames.add(sequence.name)

    if nameDuplicates:
        raise exceptions.ValidationError('Sequence name duplicates: {}'.format(nameDuplicates))


slideSchema = schemas.Schema(fields={'image': fields.Url(required=True, relative=False),
 'vfx': fields.Enum(ImageVfxs, required=False, default=None),
 'localization': fields.Url(required=False, relative=False, default=None)}, modelClass=ConfigSlideModel, checkUnknown=True)
sequenceSchema = schemas.Schema(fields={'name': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'start': fields.DateTime(required=True),
 'finish': fields.DateTime(required=True),
 'priority': fields.Integer(required=True, serializedValidators=validate.Range(minValue=0), deserializedValidators=validate.Range(minValue=0)),
 'order': fields.Enum(SequenceOrders, required=True),
 'slides': fields.List(slideSchema, required=True, serializedValidators=validate.Length(minValue=1, maxValue=MAX_CONFIG_SEQUENCE_SLIDES_COUNT), deserializedValidators=validate.Length(minValue=1, maxValue=MAX_CONFIG_SEQUENCE_SLIDES_COUNT)),
 'views': fields.Integer(required=False, default=0),
 'enabled': fields.Boolean(required=False, default=True),
 'cohorts': fields.List(fields.Enum(SequenceCohorts), required=False, default=SequenceCohorts.getDefaults, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1))}, modelClass=ConfigSequenceModel, checkUnknown=True, deserializedValidators=_validateSequenceLifeTime)
configSchema = schemas.Schema(fields={'enabled': fields.Boolean(required=True),
 'sequences': fields.List(fieldOrSchema=sequenceSchema, required=True, deserializedValidators=validate.Length(minValue=1, maxValue=MAX_CONFIG_SEQUENCES_COUNT))}, modelClass=ConfigModel, checkUnknown=True, deserializedValidators=_validateSequencesNames)

def dumpSequenceModel(model):
    return sequenceSchema.serialize(model, silent=True)


def createSequenceModel(rawData):
    return sequenceSchema.deserialize(rawData, silent=True)


def createConfigModel(rawData):
    return configSchema.deserialize(rawData, silent=True)
