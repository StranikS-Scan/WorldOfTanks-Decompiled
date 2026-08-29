# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/battle_queue_provider.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue import RandomQueueProvider
from gui.impl import backport
from gui.impl.gen import R
from soft_exception import SoftException
from white_tiger.gui.Scaleform.daapi.view.lobby import getTypeBigWtIconRPath
from white_tiger.gui.wt_event_helpers import isBoss
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

def _timeLabel(time):
    return '%d:%02d' % divmod(time, 60)


class WhiteTigerQueueProvider(RandomQueueProvider):
    EVENT_TYPES_ORDERED = [WT_VEHICLE_TAGS.BOSS, WT_VEHICLE_TAGS.HUNTER]

    def getIconPath(self, _):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_136x136.white_tiger())

    def getTitle(self, guiType):
        titleRes = R.strings.white_tiger_lobby.loading.battleTypes.wt
        return backport.text(titleRes()) if titleRes.exists() else ''

    def processQueueInfo(self, qInfo):
        bosses = qInfo.get('bosses', 0)
        hunters = qInfo.get('hunters', 0)
        total = bosses + hunters
        self._createCommonPlayerString(total)
        uiData = []
        counts = {WT_VEHICLE_TAGS.BOSS: bosses,
         WT_VEHICLE_TAGS.HUNTER: hunters}
        for vTypeName in self.EVENT_TYPES_ORDERED:
            uiData.append({'type': backport.text(R.strings.white_tiger_lobby.vehicle.tags.dyn(vTypeName).name()),
             'icon': getTypeBigWtIconRPath(vTypeName),
             'count': counts[vTypeName]})

        self._proxy.as_setDPS(uiData)
        vehicle = g_currentVehicle.item
        if not vehicle:
            raise SoftException("Can't get event prebattle vehicle")
        isPlayerBoss = self.__isBossPlayer()
        avgWaitTime = qInfo.get('avgWaitTimeBosses', 0) if isPlayerBoss else qInfo.get('avgWaitTimeHunters', 0)
        self._setAverageWaitingTime(vehicle.userName, avgWaitTime)

    def _setAverageWaitingTime(self, vehicleName, averageWaitingTime):
        avgWaitTimeLabel = backport.text(R.strings.white_tiger_lobby.battleQueue.avgWaitTime.label(), vehName=vehicleName)
        avgWaitTime = _timeLabel(averageWaitingTime)
        self._proxy.as_setAverageTimeS(avgWaitTimeLabel, avgWaitTime)

    def getTankIcon(self, vehicle):
        tag = next((t for t in self.EVENT_TYPES_ORDERED if t in vehicle.tags), '')
        return getTypeBigWtIconRPath(tag)

    def __isBossPlayer(self):
        vehicle = g_currentVehicle.item
        return isBoss(vehicle.tags)
