# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/white_tiger_queue.py
import BigWorld
from helpers import dependency, time_utils, i18n
from soft_exception import SoftException
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import getTypeVPanelIconPath
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider
from skeletons.prebattle_vehicle import IPrebattleVehicle
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.ClientUpdateManager import g_clientUpdateManager
from white_tiger.gui.Scaleform.daapi.view.meta.WTBattleQueueMeta import WTBattleQueueMeta
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLES_CONSTS import WHITE_TIGER_BATTLES_CONSTS
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
from white_tiger.gui.gui_constants import VEHICLE_TAGS, WT_TAGS

def _timeLabel(time):
    return '%d:%02d' % divmod(time, 60)


class WhiteTigerQueueProvider(RandomQueueProvider):
    WT_TYPES_ORDERED = (VEHICLE_TAGS.WT_BOSS, VEHICLE_TAGS.WT_HUNTER)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def start(self):
        super(WhiteTigerQueueProvider, self).start()
        self.__prebattleVehicle.onChanged += self.__onChanged

    def stop(self):
        super(WhiteTigerQueueProvider, self).stop()
        self.__prebattleVehicle.onChanged -= self.__onChanged

    def getVehicle(self):
        return self.__prebattleVehicle.item

    def additionalInfo(self):
        pass

    def getTankIcon(self, vehicle):
        return getTypeBigIconPath(vehicle.eventType) if vehicle else ''

    def getTankName(self, vehicle):
        return vehicle.userName if vehicle else ''

    def getIconPath(self, iconlabel):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_136x136.whiteTiger())

    def processQueueInfo(self, qInfo):
        bosses = qInfo.get('bosses', 0)
        hunters = qInfo.get('hunters', 0)
        avgWaitTime = qInfo.get('avgWaitTime', 0)
        total = bosses + hunters
        self._createCommonPlayerString(total)
        uiData = []
        counts = {VEHICLE_TAGS.WT_BOSS: bosses,
         VEHICLE_TAGS.WT_HUNTER: hunters}
        for vTypeName in self.WT_TYPES_ORDERED:
            uiData.append({'type': backport.text(R.strings.white_tiger.vehicle.tags.dyn(vTypeName).name()),
             'icon': getTypeBigIconPath(vTypeName),
             'count': counts[vTypeName]})

        self._proxy.as_setDPS(uiData)
        vehicle = self.getVehicle()
        if not vehicle:
            raise SoftException("Can't get event prebattle vehicle")
        self._proxy.as_setAverageTimeS(i18n.makeString(backport.text(R.strings.white_tiger.battleQueue.avgWaitTime.label(), vehName=vehicle.userName)), _timeLabel(avgWaitTime))

    def __onChanged(self):
        self._proxy.updateClientState()


class WhiteTigerQueue(WTBattleQueueMeta):
    __eventController = dependency.descriptor(IWhiteTigerController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(WhiteTigerQueue, self).__init__(*args, **kwargs)
        self.__hideQuickStartPanelCallbackID = None
        return

    def onQuickStartPanelAction(self, vehID):
        vehicle = self.__itemsCache.items.getVehicle(vehID)
        if not vehicle:
            raise SoftException("Can' get event vehicle for prebattle selection")
        self.prbEntity.requeue(vehicle)

    def _populate(self):
        super(WhiteTigerQueue, self)._populate()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def _dispose(self):
        super(WhiteTigerQueue, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__cancelHideQuickStartPanelCallback()

    def __onTokensUpdate(self, diff):
        config = self.__eventController.getConfig()
        if config.quickBossTicketToken in diff:
            if self.__eventController.getQuickTicketCount():
                self.__showQuickStartPanel(self.__eventController.getQuickTicketExpiryTime(), self.__packBossQStartPanelData())
            else:
                self.__hideQuickStartPanel(cancelHideQuickStartPanelCallback=True)
        elif config.quickHunterTicketToken in diff:
            if self.__eventController.getQuickHunterTicketCount():
                self.__showQuickStartPanel(self.__eventController.getQuickHunterTicketExpiryTime(), self.__packHunterQStartPanelData())
            else:
                self.__hideQuickStartPanel(cancelHideQuickStartPanelCallback=True)

    def __showQuickStartPanel(self, ticketExpiryTime, panelData):
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        ticketTtl = ticketExpiryTime - currentTime
        if ticketTtl > 0:
            self.as_showQuickStartPanelS(panelData)
            self.__hideQuickStartPanelCallbackID = BigWorld.callback(ticketTtl, self.__hideQuickStartPanel)

    def __hideQuickStartPanel(self, cancelHideQuickStartPanelCallback=False):
        self.as_hideQuickStartPanelS()
        if cancelHideQuickStartPanelCallback:
            self.__cancelHideQuickStartPanelCallback()
        else:
            self.__hideQuickStartPanelCallbackID = None
        return

    def __cancelHideQuickStartPanelCallback(self):
        if self.__hideQuickStartPanelCallbackID is not None:
            BigWorld.cancelCallback(self.__hideQuickStartPanelCallbackID)
            self.__hideQuickStartPanelCallbackID = None
        return

    def __packBossQStartPanelData(self):
        config = self.__eventController.getConfig()
        ticketsToDraw = config.ticketsToDraw if self.__eventController.hasEnoughTickets(False) else 0
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_TAGS.WT_BOSS}) | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({WT_TAGS.WT_SPECIAL_BOSS}))
        if not vehicles:
            raise SoftException("Can't get boss vehicles")
        vehicle = vehicles.values()[0]
        return {'type': WHITE_TIGER_BATTLES_CONSTS.BOSS_QUICK_START_PANEL,
         'ticketsToDraw': ticketsToDraw,
         'vehName': vehicle.userName,
         'vehID': vehicle.invID}

    def __packHunterQStartPanelData(self):
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_TAGS.WT_HUNTER}))
        hunters = []
        for veh in vehicles.values():
            hunters.append({'typeIcon': getTypeVPanelIconPath(veh.eventType),
             'icon': veh.icon,
             'name': veh.userName,
             'vehID': veh.invID,
             'isInBattle': veh.isInBattle})

        return {'type': WHITE_TIGER_BATTLES_CONSTS.HUNTER_QUICK_START_PANEL,
         'hunters': hunters}
