# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/player_format.py
import logging
import BigWorld
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.arena_info.player_format import PlayerFullNameFormatter
from helpers import dependency
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class BattleRoyalePlayerFullNameFormatter(PlayerFullNameFormatter):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def format(self, vInfoVO, playerName=None):
        if isSpawnedBot(vInfoVO.vehicleType.tags):
            botVehID = vInfoVO.vehicleID
            botVehicle = BigWorld.entities.get(botVehID)
            if botVehicle:
                masterVehId = botVehicle.masterVehID
                for vI in self.__sessionProvider.getArenaDP().getVehiclesInfoIterator():
                    if vI.vehicleID == masterVehId:
                        vInfoVO = vI
                        break
                else:
                    defBotName = ' '
                    _logger.warning('The Master vehicle of a bot (id=%s) has not been found, use default name %s', botVehID, defBotName)
                    vInfoVO = VehicleArenaInfoVO(botVehID)
                    return super(BattleRoyalePlayerFullNameFormatter, self).format(vInfoVO, playerName=defBotName)

            else:
                defBotName = ' '
                _logger.warning('Bot vehicle (id=%s) has not been found, use default name %s', botVehID, defBotName)
                vInfoVO = VehicleArenaInfoVO(botVehID)
                return super(BattleRoyalePlayerFullNameFormatter, self).format(vInfoVO, playerName=defBotName)
        selfFormat = super(BattleRoyalePlayerFullNameFormatter, self).format(vInfoVO, playerName)
        return selfFormat
