# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/game_params_configs.py
import typing
from schema_manager import getSchemaManager
import hints_common.prebattle.newbie.schemas
import hints_common.prebattle.schemas
import hints_common.battle.schemas.newbie
if typing.TYPE_CHECKING:
    from schema_manager import SchemaManager

def init():
    schemaManager = getSchemaManager()
    _registerSchemas(schemaManager)


def _registerSchemas(schemaManager):
    schemaManager.registerClientServerSchema(hints_common.prebattle.newbie.schemas.configSchema)
    schemaManager.registerClientServerSchema(hints_common.prebattle.schemas.configSchema)
    schemaManager.registerClientServerSchema(hints_common.battle.schemas.newbie.configSchema)
