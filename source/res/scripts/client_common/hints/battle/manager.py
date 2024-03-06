# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/hints/battle/manager.py
import typing
from hints_common.battle import manager
from hints.battle.schemas.base import clientHintSchema
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import CHMType
SCHEMA_TAG = 'clientSchema'

def init():
    manager.init(schemaTag=SCHEMA_TAG, defaultSchema=clientHintSchema)


def get():
    return manager.get()
