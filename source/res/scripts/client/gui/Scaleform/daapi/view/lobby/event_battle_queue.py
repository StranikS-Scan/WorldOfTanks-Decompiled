# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_battle_queue.py
import typing
import BigWorld
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.EventBattleQueueMeta import EventBattleQueueMeta
from constants import WT_TAGS
from gui.Scaleform.genConsts.EVENT_BATTLES_CONSTS import EVENT_BATTLES_CONSTS
from gui.shared.gui_items.Vehicle import getTypeVPanelIconPath
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.prebattle_vehicle import IPrebattleVehicle
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class EventBattleQueue(EventBattleQueueMeta):
    __eventController = dependency.descriptor(IEventBattlesController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(EventBattleQueue, self).__init__(*args, **kwargs)
        self.__hideQuickStartPanelCallbackID = None
        return

    def onQuickStartPanelAction(self, vehID):
        vehicle = self.__itemsCache.items.getVehicle(vehID)
        if not vehicle:
            raise SoftException("Can' get event vehicle for prebattle selection")
        self.prbEntity.requeue(vehicle)

    def _populate(self):
        super(EventBattleQueue, self)._populate()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__playBattleQueueSound()

    def _dispose(self):
        super(EventBattleQueue, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__cancelHideQuickStartPanelCallback()

    def __playBattleQueueSound(self):
        vehicleName = self.__prebattleVehicle.item.name
        self.__eventController.getBattleQueueSoundMgr().playSound(vehicleName)

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
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_TAGS.BOSS}) | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({WT_TAGS.PRIORITY_BOSS}))
        if not vehicles:
            raise SoftException("Can't get boss vehicles")
        vehicle = vehicles.values()[0]
        return {'type': EVENT_BATTLES_CONSTS.BOSS_QUICK_START_PANEL,
         'ticketsToDraw': ticketsToDraw,
         'vehName': vehicle.userName,
         'vehID': vehicle.invID}

    def __packHunterQStartPanelData(self):
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_TAGS.HUNTER}))
        hunters = []
        for veh in vehicles.values():
            hunters.append({'typeIcon': getTypeVPanelIconPath(veh.eventType),
             'icon': veh.icon,
             'name': veh.userName,
             'vehID': veh.invID,
             'isInBattle': veh.isInBattle})

        return {'type': EVENT_BATTLES_CONSTS.HUNTER_QUICK_START_PANEL,
         'hunters': hunters}
