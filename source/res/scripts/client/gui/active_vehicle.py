# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/active_vehicle.py
from typing import TYPE_CHECKING
import logging
import BigWorld
import AccountCommands
from items.components.c11n_constants import SeasonType
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import Any as TAny
_logger = logging.getLogger(__name__)

class ActiveVehicleSeasonType(object):

    def __init__(self):
        self._vehTypeDescrToSeason = {'historical': {}}

    def get(self, vehTypeDescr, defaultSeasonType):
        season = self._vehTypeDescrToSeason.get(vehTypeDescr, defaultSeasonType)
        return defaultSeasonType if season == SeasonType.UNDEFINED else season

    def __setitem__(self, vehTypeDescr, seasonType):
        if seasonType not in SeasonType.RANGE and seasonType != SeasonType.UNDEFINED:
            raise SoftException("Invalid SeasonType '{}'".format(seasonType))
        if self.get(vehTypeDescr, SeasonType.UNDEFINED) != seasonType:
            self._vehTypeDescrToSeason[vehTypeDescr] = seasonType
            self.__updateServer(vehTypeDescr, seasonType)

    def __getitem__(self, vehTypeDescr):
        return self._vehTypeDescrToSeason[vehTypeDescr]

    def __contains__(self, vehTypeDescr):
        return vehTypeDescr in self._vehTypeDescrToSeason

    def __updateServer(self, vehTypeDescr, seasonType):
        player = BigWorld.player()
        if player is not None and hasattr(player, '_doCmdInt2'):
            player._doCmdInt2(AccountCommands.CMD_SET_ACTIVE_VEH_SEASON, vehTypeDescr, seasonType, self.__onSetActiveVehSeason)
        return

    def __onSetActiveVehSeason(self, requestID, resultID, errorStr, ext=None):
        logFunc = _logger.debug
        if isinstance(ext, dict) and ext.get('exception_message'):
            logFunc = _logger.error
        logFunc('__onSetActiveVehSeason requestID=%s resultID=%s, errorStr=%s, ext=%s', requestID, resultID, errorStr, ext)
