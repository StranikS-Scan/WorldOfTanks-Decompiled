# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/renewable_subscription_common/config.py
import typing
from constants import ARENA_BONUS_TYPE_NAMES
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from ResMgr import DataSection

def readGoldReserveGains(section):
    goldReserveGains = {}
    for value in section.values():
        typeName = value.readString('arenaBonusType').strip()
        arenaType = ARENA_BONUS_TYPE_NAMES.get(typeName, None)
        if arenaType is None:
            raise SoftException("Wrong arena type: '{}'".format(typeName.strip()))
        goldReserveGains[arenaType] = {'win': value.readInt('win'),
         'loss': value.readInt('loss'),
         'draw': value.readInt('draw'),
         'minLevel': value.readInt('minLevel'),
         'minTop': value.readInt('minTop', -1),
         'topType': value.readString('topType', 'fareTeamXPPosition').strip()}

    return goldReserveGains
