# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/hints_common/battle/manager.py
import typing
import logging
from dict2model import exceptions
from hints_common.common.manager import BaseHintsModelsManager
from hints_common.battle.schemas.base import HMCType, CommonHintSchema
_logger = logging.getLogger(__name__)
_g_manager = None
DEFAULT_XML = 'scripts/item_defs/hints/battle_hints.xml'

class CommonBattleHintsModelsManager(BaseHintsModelsManager, typing.Generic[HMCType]):
    __slots__ = ('_hints', '_hintsBySchemas')

    def __init__(self, schemaTag, defaultSchema):
        self._hints = {}
        self._hintsBySchemas = {}
        super(CommonBattleHintsModelsManager, self).__init__(DEFAULT_XML, defaultSchema, schemaTag=schemaTag)

    def get(self, uniqueName):
        return self._hints.get(uniqueName)

    def getAll(self):
        return self._hints.values()

    def getBySchema(self, schema):
        return self._hintsBySchemas.get(schema, [])

    def _addToStorage(self, schema, hint):
        if hint.uniqueName in self._hints:
            raise exceptions.ValidationError('{} already exist.'.format(hint.uniqueName))
        hint.prepare(schema)
        self._hints[hint.uniqueName] = hint
        self._hintsBySchemas.setdefault(schema, []).append(hint)

    def _checkSchemaType(self, schema):
        if not isinstance(schema, CommonHintSchema):
            raise exceptions.ValidationError('Schema type must be {} or inherited.'.format(CommonHintSchema))


def init(schemaTag, defaultSchema):
    global _g_manager
    if _g_manager is None:
        _g_manager = CommonBattleHintsModelsManager(schemaTag=schemaTag, defaultSchema=defaultSchema)
        _logger.debug('Battle hints models manager created from: %s.', DEFAULT_XML)
    return


def get():
    if _g_manager is None:
        _logger.error('Battle hints models manager not initialized.')
    return _g_manager
