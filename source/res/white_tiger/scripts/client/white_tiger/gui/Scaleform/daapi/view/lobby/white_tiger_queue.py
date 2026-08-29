# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/white_tiger_queue.py
import BigWorld
from helpers import dependency, time_utils, i18n
from soft_exception import SoftException
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getTypeVPanelIconPath
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider
from skeletons.prebattle_vehicle import IPrebattleVehicle
from white_tiger.gui.Scaleform.daapi.view.meta.WTBattleQueueMeta import WTBattleQueueMeta
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLES_CONSTS import WHITE_TIGER_BATTLES_CONSTS
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
from wt_settings import g_wt_config
import logging
_logger = logging.getLogger(__name__)

def _timeLabel(time):
    return '%d:%02d' % divmod(time, 60)


class WhiteTigerQueueProvider(RandomQueueProvider):
    WT_TYPES_ORDERED = ('boss', 'hunter')
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __wtController = dependency.descriptor(IWhiteTigerController)

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
        if vehicle:
            vehData = g_wt_config.getVehicleData(vehicle.intCD)
            return backport.image(R.images.gui.maps.icons.vehicleTypes.big.dyn(vehData.type)())

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
        counts = {'boss': bosses,
         'hunter': hunters}
        for vTypeName in self.WT_TYPES_ORDERED:
            uiData.append({'type': backport.text(R.strings.white_tiger.vehicle.tags.dyn(vTypeName).name()),
             'icon': backport.image(R.images.gui.maps.icons.vehicleTypes.big.dyn(vTypeName)()),
             'count': counts[vTypeName]})

        self._proxy.as_setDPS(uiData)
        vehicle = self.getVehicle() or self.__wtController.getCurrentVehicle()
        if not vehicle:
            return
        vehicleData = g_wt_config.getVehicleData(vehicle.intCD)
        self._proxy.as_setAverageTimeS(i18n.makeString(backport.text(R.strings.white_tiger.battleQueue.avgWaitTime.label(), vehName=backport.text(R.strings.white_tiger.vehicle.tags.dyn(vehicleData.type).name()))), _timeLabel(avgWaitTime))

    def __onChanged(self):
        self._proxy.updateClientState()


class WhiteTigerQueue(WTBattleQueueMeta):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(WhiteTigerQueue, self).__init__(*args, **kwargs)
        self.__hideQuickStartPanelCallbackID = None
        return

    def onQuickStartPanelAction(self, vehCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        if not vehicle:
            raise SoftException("Can't get event vehicle for prebattle selection")
        self.prbEntity.requeue(vehicle)

    def _populate(self):
        super(WhiteTigerQueue, self)._populate()
        g_wt_config.onQuickTokenUpdate += self.__onQuickTokenUpdate

    def _dispose(self):
        super(WhiteTigerQueue, self)._dispose()
        self.__cancelHideQuickStartPanelCallback()
        g_wt_config.onQuickTokenUpdate -= self.__onQuickTokenUpdate

    def __onQuickTokenUpdate(self, keys, _):
        config = g_wt_config.getConfig()
        for key in keys:
            if key in (config.quickBossTicketToken, config.quickHunterTicketToken):
                if key == config.quickBossTicketToken:
                    panelData = self.__packBossQStartPanelData
                else:
                    panelData = self.__packHunterQStartPanelData
                data = g_wt_config.getTokenDataByName(key)
                if data['currentCount'] > 0:
                    self.__showQuickStartPanel(g_wt_config.getTokenExpiryTime(key), panelData())
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
        vehicles = g_wt_config.getBossVehiclesData()
        if not vehicles:
            raise SoftException("Can't get boss vehicles")
        ticketsToDraw = 0
        tokenData = g_wt_config.getTokenDataByName('wtevent:ticket')
        if tokenData['currentCount'] > 0:
            ticketsToDraw = tokenData['tokenDraw']
        vehicle = next(vehicles.itervalues()).vehicle
        return {'type': WHITE_TIGER_BATTLES_CONSTS.BOSS_QUICK_START_PANEL,
         'ticketsToDraw': ticketsToDraw,
         'vehName': vehicle.userName,
         'vehID': vehicle.intCD}

    def __packHunterQStartPanelData(self):
        vehicles = g_wt_config.getHunterVehiclesData()
        hunters = []
        for vehCD, vehData in vehicles.iteritems():
            hunters.append({'typeIcon': getTypeVPanelIconPath(vehData.type),
             'icon': vehData.vehicle.icon,
             'name': vehData.vehicle.userName,
             'vehID': vehCD,
             'isInBattle': vehData.vehicle.isInBattle})

        return {'type': WHITE_TIGER_BATTLES_CONSTS.HUNTER_QUICK_START_PANEL,
         'hunters': hunters}
