# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/battle_queue.py
import logging
import BigWorld
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from white_tiger.gui.Scaleform.daapi.view.lobby import getTypeWhiteWtIconRPath
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerBattleQueueMeta import WhiteTigerBattleQueueMeta
from white_tiger.gui.Scaleform.genConsts.BATTLES_CONSTS import BATTLES_CONSTS
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from white_tiger.gui.sounds.sound_constants import WT_BATTLE_QUEUE_VIEW_SOUND_SPACE
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class BattleQueue(WhiteTigerBattleQueueMeta):
    __eventController = dependency.descriptor(IWhiteTigerController)
    __economicsController = dependency.descriptor(IEconomicsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __sound_env__ = None
    _COMMON_SOUND_SPACE = WT_BATTLE_QUEUE_VIEW_SOUND_SPACE

    def __init__(self, **kwargs):
        super(BattleQueue, self).__init__(**kwargs)
        self.__hideQuickStartPanelCallbackID = None
        return

    def onQuickStartPanelAction(self, vehID):
        vehicle = self.__itemsCache.items.getVehicle(vehID)
        if not vehicle:
            raise SoftException("Can' get event vehicle for prebattle selection")
        self.prbEntity.requeue(vehicle)

    def _populate(self):
        super(BattleQueue, self)._populate()
        self.as_showQuickStartPanelS({'type': BATTLES_CONSTS.HUNTER_QUICK_START_PANEL,
         'hunters': []})
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def _dispose(self):
        super(BattleQueue, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__cancelHideQuickStartPanelCallback()

    def __onTokensUpdate(self, diff):
        if self.__economicsController.getQuickTicketTokenName() in diff:
            if self.__economicsController.getQuickTicketCount():
                self.__showQuickStartPanel(self.__economicsController.getQuickBossTicketExpiryTime(), self.__packBossQStartPanelData())
            else:
                self.__hideQuickStartPanel(cancelHideQuickStartPanelCallback=True)
        elif self.__economicsController.getQuickHunterTicketTokenName() in diff:
            if self.__economicsController.getQuickHunterTicketCount():
                self.__showQuickStartPanel(self.__economicsController.getQuickHunterTicketExpiryTime(), self.__packHunterQStartPanelData())
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
        config = self.__economicsController.getConfig()
        ticketsToDraw = config.get('ticketsToDraw', 0)
        ticketsToDraw = ticketsToDraw if self.__economicsController.getTicketCount() >= ticketsToDraw else 0
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_VEHICLE_TAGS.BOSS}) | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({WT_VEHICLE_TAGS.PRIORITY_BOSS}))
        if not vehicles:
            raise SoftException("Can't get boss vehicles")
        if len(vehicles) > 1:
            _logger.warning('There were more than 1 vehicles found: %s', ','.join([ v.userName for v in vehicles ]))
        vehicle = vehicles.values()[0]
        return {'type': BATTLES_CONSTS.BOSS_QUICK_START_PANEL,
         'ticketsToDraw': ticketsToDraw,
         'vehName': vehicle.userName,
         'vehID': vehicle.invID}

    def __packHunterQStartPanelData(self):
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_VEHICLE_TAGS.HUNTER}))
        hunters = []
        for veh in vehicles.values():
            hunters.append({'typeIcon': getTypeWhiteWtIconRPath(WT_VEHICLE_TAGS.HUNTER),
             'icon': veh.icon,
             'name': veh.userName,
             'vehID': veh.invID,
             'isInBattle': veh.isInBattle})

        return {'type': BATTLES_CONSTS.HUNTER_QUICK_START_PANEL,
         'hunters': hunters}
