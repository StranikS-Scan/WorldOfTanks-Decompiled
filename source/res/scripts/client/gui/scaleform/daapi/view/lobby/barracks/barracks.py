# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/barracks/Barracks.py
import BigWorld
from AccountCommands import LOCK_REASON
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from account_helpers.AccountSettings import AccountSettings, BARRACKS_FILTER
from CurrentVehicle import g_currentVehicle
from helpers import i18n
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui import SystemMessages
from gui.shared import events, g_itemsCache, REQ_CRITERIA, event_dispatcher as shared_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BarracksMeta import BarracksMeta
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.Tankman import TankmenComparator
from gui.shared.gui_items.processors.common import TankmanBerthsBuyer
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload
from gui.shared.utils import decorators

class Barracks(BarracksMeta, LobbySubView, GlobalListener):

    def __init__(self, ctx = None):
        super(Barracks, self).__init__()
        self.filter = dict(AccountSettings.getFilter(BARRACKS_FILTER))

    def _populate(self):
        super(Barracks, self)._populate()
        self.app.component.wg_inputKeyMode = 1
        self.startGlobalListening()
        g_itemsCache.onSyncCompleted += self.__updateTankmen
        g_clientUpdateManager.addCallbacks({'inventory.8': self.__updateTankmen,
         'stats.berths': self.__updateTankmen})
        self.setTankmenFilter()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_itemsCache.onSyncCompleted -= self.__updateTankmen
        self.stopGlobalListening()
        super(LobbySubView, self)._dispose()

    def openPersonalCase(self, value, tabNumber):
        shared_events.showPersonalCase(int(value), int(tabNumber), EVENT_BUS_SCOPE.LOBBY)

    def closeBarracks(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateTanksList(self):
        self.__updateTanksList()

    def update(self):
        self.__updateTankmen()

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.RECRUIT_WINDOW, ctx={'data': rendererData,
         'menuEnabled': menuEnabled}))

    @decorators.process('buyBerths')
    def buyBerths(self):
        items = g_itemsCache.items
        berthPrice, berthsCount = items.shop.getTankmanBerthPrice(items.stats.tankmenBerthsCount)
        result = yield TankmanBerthsBuyer((0, berthPrice), berthsCount).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __updateTanksList(self):
        data = list()
        modulesAll = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        modulesAll.sort()
        for module in modulesAll:
            if self.filter['nation'] != -1 and self.filter['nation'] != module.descriptor.type.id[0] or self.filter['tankType'] != 'None' and self.filter['tankType'] != -1 and self.filter['tankType'] != module.type:
                continue
            data.append({'data': {'type': module.type,
                      'nationID': module.descriptor.type.id[0],
                      'typeID': module.descriptor.type.id[1]},
             'label': module.descriptor.type.shortUserString})

        self.as_updateTanksListS(data)

    def setTankmenFilter(self):
        self.as_setTankmenFilterS(self.filter['nation'], self.filter['role'], self.filter['tankType'], self.filter['location'], self.filter['nationID'])

    def setFilter(self, nation, role, tankType, location, nationID):
        self.filter['nation'] = nation
        self.filter['role'] = role
        self.filter['tankType'] = tankType
        self.filter['location'] = location
        self.filter['nationID'] = nationID
        AccountSettings.setFilter(BARRACKS_FILTER, self.filter)
        self.__updateTankmen()

    def __updateTankmen(self, *args):
        tankmen = g_itemsCache.items.getTankmen().values()
        slots = g_itemsCache.items.stats.tankmenBerthsCount
        berths = g_itemsCache.items.stats.tankmenBerthsCount
        berthPrice = g_itemsCache.items.shop.getTankmanBerthPrice(berths)
        defaultBerthPrice = g_itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
        tankmenList = list()
        tankmenInBarracks = 0
        action = None
        if berthPrice[0] != defaultBerthPrice[0]:
            action = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'berthsPrices',
             'isBuying': True,
             'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
             'newPrice': (0, berthPrice[0]),
             'oldPrice': (0, defaultBerthPrice[0])}
        tankmenList.append({'buy': True,
         'price': BigWorld.wg_getGoldFormat(berthPrice[0]),
         'actionPriceData': action,
         'count': berthPrice[1]})
        for tankman in sorted(tankmen, TankmenComparator(g_itemsCache.items.getVehicle)):
            if not tankman.isInTank:
                tankmenInBarracks += 1
            slot, vehicleID, vehicleInnationID, vehicle = (None, None, None, None)
            if tankman.isInTank:
                vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
                vehicleID = vehicle.invID
                vehicleInnationID = vehicle.innationID
                if vehicle is None:
                    LOG_ERROR('Cannot find vehicle for tankman: ', tankman, tankman.descriptor.role, tankman.vehicle.name, tankman.firstname, tankman.lastname)
                    continue
                slot = tankman.vehicleSlotIdx
            if self.filter['nation'] != -1 and tankman.nationID != self.filter['nation'] or self.filter['role'] != 'None' and tankman.descriptor.role != self.filter['role'] or self.filter['tankType'] != 'None' and tankman.vehicleNativeType != self.filter['tankType'] or self.filter['location'] == 'tanks' and tankman.isInTank != True or self.filter['location'] == 'barracks' and tankman.isInTank == True or self.filter['nationID'] is not None and (self.filter['location'] != str(vehicleInnationID) or self.filter['nationID'] != str(tankman.nationID)):
                continue
            isLocked, msg = self.getTankmanLockMessage(vehicle) if tankman.isInTank else (False, '')
            tankmanVehicle = g_itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
            isInCurrentTank = tankmanVehicle.invID == g_currentVehicle.invID if tankman.isInTank and g_currentVehicle.isPresent() else False
            tankmenList.append({'firstname': tankman.firstUserName,
             'lastname': tankman.lastUserName,
             'rank': tankman.rankUserName,
             'specializationLevel': tankman.realRoleLevel[0],
             'role': tankman.roleUserName,
             'vehicleType': tankmanVehicle.shortUserName,
             'iconFile': tankman.icon,
             'rankIconFile': tankman.iconRank,
             'roleIconFile': Tankman.getRoleBigIconPath(tankman.descriptor.role),
             'contourIconFile': tankmanVehicle.iconContour,
             'tankmanID': tankman.invID,
             'nationID': tankman.nationID,
             'typeID': tankmanVehicle.innationID,
             'slot': slot,
             'roleType': tankman.descriptor.role,
             'tankType': tankmanVehicle.type,
             'inTank': tankman.isInTank,
             'inCurrentTank': isInCurrentTank,
             'vehicleID': vehicleID,
             'compact': str(tankman.invID),
             'locked': isLocked,
             'lockMessage': msg,
             'vehicleBroken': vehicle.repairCost > 0 if tankman.isInTank else None,
             'isInSelfVehicleClass': vehicle.type == tankmanVehicle.type if tankman.isInTank else True,
             'isInSelfVehicleType': vehicle.shortUserName == tankmanVehicle.shortUserName if tankman.isInTank else True})

        tankmenInSlots = len(tankmenList) - 1
        if tankmenInBarracks < slots:
            tankmenList.insert(1, {'empty': True,
             'freePlaces': slots - tankmenInBarracks})
        self.as_setTankmenS(len(tankmen), tankmenInSlots, slots, tankmenInBarracks, tankmenList)
        return

    @staticmethod
    def getTankmanLockMessage(invVehicle):
        if invVehicle.lock == LOCK_REASON.ON_ARENA:
            return (True, i18n.makeString('#menu:tankmen/lockReason/inbattle'))
        elif invVehicle.repairCost > 0:
            return (False, i18n.makeString('#menu:tankmen/lockReason/broken'))
        else:
            if invVehicle.invID == g_currentVehicle.invID:
                dispatcher = g_prbLoader.getDispatcher()
                if dispatcher is not None:
                    permission = dispatcher.getGUIPermissions()
                    if not permission.canChangeVehicle():
                        return (True, i18n.makeString('#menu:tankmen/lockReason/prebattle'))
            return (False, '')

    @decorators.process('updating')
    def dismissTankman(self, invID):
        tankman = g_itemsCache.items.getTankman(int(invID))
        if tankman is None:
            LOG_ERROR('Attempt to dismiss tankman by invalid invID')
            return
        else:
            result = yield TankmanDismiss(tankman).request()
            if len(result.userMsg):
                SystemMessages.g_instance.pushMessage(result.userMsg, type=result.sysMsgType)
            return

    @decorators.process('unloading')
    def unloadTankman(self, invID):
        tankman = g_itemsCache.items.getTankman(int(invID))
        if tankman is None:
            LOG_ERROR('Attempt to dismiss tankman by invalid invID')
            return
        else:
            tmanVehile = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
            if tmanVehile is None:
                LOG_ERROR("Target tankman's vehicle is not found in inventory", tankman, tankman.vehicleInvID)
                return
            result = yield TankmanUnload(tmanVehile, tankman.vehicleSlotIdx).request()
            if len(result.userMsg):
                SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            return

    def onPrbFunctionalFinished(self):
        self.__updateTankmen()

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updateTankmen()

    def onUnitFunctionalFinished(self):
        self.__updateTankmen()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__updateTankmen()
