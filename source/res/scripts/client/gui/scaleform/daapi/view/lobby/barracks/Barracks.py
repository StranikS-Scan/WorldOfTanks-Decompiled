# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/barracks/Barracks.py
import BigWorld
from AccountCommands import LOCK_REASON
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, BARRACKS_FILTER
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BarracksMeta import BarracksMeta
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events, event_dispatcher as shared_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons, moneyWithIcon
from gui.shared.gui_items import Tankman, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmenComparator
from gui.shared.gui_items.processors.common import TankmanBerthsBuyer
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload, TankmanRestore
from gui.shared.money import ZERO_MONEY, Currency
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.tankman import getRecoveryStatusText, formatRecoveryLeftValue
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.ambients import LobbySubViewEnv
from helpers import i18n, time_utils, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _packTankmanData(tankman, itemsCache=None):
    tankmanVehicle = itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
    if tankman.isInTank:
        vehicle = itemsCache.items.getVehicle(tankman.vehicleInvID)
        if vehicle is None:
            LOG_ERROR('Cannot find vehicle for tankman: ', tankman, tankman.descriptor.role, tankman.vehicle.name, tankman.firstname, tankman.lastname)
            return
        vehicleID = vehicle.invID
        slot = tankman.vehicleSlotIdx
        isLocked, msg = _getTankmanLockMessage(vehicle)
        actionBtnEnabled = not isLocked
        isInCurrentTank = g_currentVehicle.isPresent() and tankmanVehicle.invID == g_currentVehicle.invID
        isInSelfVehicle = vehicle.shortUserName == tankmanVehicle.shortUserName
        isInSelfVehicleType = vehicle.type == tankmanVehicle.type
    else:
        isLocked, msg = False, ''
        actionBtnEnabled = True
        isInCurrentTank = False
        vehicleID = None
        slot = None
        isInSelfVehicle = True
        isInSelfVehicleType = True
    data = {'firstName': tankman.firstUserName,
     'lastName': tankman.lastUserName,
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
     'roleType': tankman.descriptor.role,
     'tankType': tankmanVehicle.type,
     'inTank': tankman.isInTank,
     'compact': str(tankman.invID),
     'lastSkillLevel': tankman.descriptor.lastSkillLevel,
     'actionBtnEnabled': actionBtnEnabled,
     'inCurrentTank': isInCurrentTank,
     'vehicleID': vehicleID,
     'slot': slot,
     'locked': isLocked,
     'lockMessage': msg,
     'isInSelfVehicleClass': isInSelfVehicleType,
     'isInSelfVehicleType': isInSelfVehicle}
    return data


def _getTankmanLockMessage(invVehicle):
    if invVehicle.lock == LOCK_REASON.ON_ARENA:
        return (True, i18n.makeString('#menu:tankmen/lockReason/inbattle'))
    elif invVehicle.repairCost > 0:
        return (True, i18n.makeString('#menu:tankmen/lockReason/broken'))
    elif invVehicle.invID == g_currentVehicle.invID and (g_currentVehicle.isInPrebattle() or g_currentVehicle.isInBattle()):
        return (True, i18n.makeString('#menu:tankmen/lockReason/prebattle'))
    else:
        return (False, '')


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _packBuyBerthsSlot(itemsCache=None):
    berths = itemsCache.items.stats.tankmenBerthsCount
    berthPrice, berthCount = itemsCache.items.shop.getTankmanBerthPrice(berths)
    defaultBerthPrice, _ = itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
    gold = itemsCache.items.stats.money.gold
    action = None
    if berthPrice != defaultBerthPrice:
        action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'berthsPrices', True, berthPrice, defaultBerthPrice)
    enoughGold = berthPrice.gold <= gold
    return {'buy': True,
     'price': BigWorld.wg_getGoldFormat(berthPrice.gold),
     'enoughGold': enoughGold,
     'actionPriceData': action,
     'count': berthCount}


def _makeRecoveryPeriodText(restoreInfo):
    price, timeLeft = restoreInfo
    timeStr = formatRecoveryLeftValue(timeLeft)
    if price == ZERO_MONEY:
        textStyle = text_styles.main
    elif price.getCurrency() == Currency.GOLD:
        textStyle = text_styles.gold
    else:
        textStyle = text_styles.credits
    return textStyle(timeStr)


class Barracks(BarracksMeta, LobbySubView, IGlobalListener):
    __sound_env__ = LobbySubViewEnv
    itemsCache = dependency.descriptor(IItemsCache)
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, ctx=None):
        super(Barracks, self).__init__()
        self.filter = dict(AccountSettings.getFilter(BARRACKS_FILTER))

    def openPersonalCase(self, tankmanInvID, tabNumber):
        tmanInvID = int(tankmanInvID)
        tankman = self.itemsCache.items.getTankman(tmanInvID)
        if tankman and not tankman.isDismissed:
            shared_events.showPersonalCase(tmanInvID, int(tabNumber), EVENT_BUS_SCOPE.LOBBY)

    def closeBarracks(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateTanksList(self):
        self.__updateTanksList()

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.RECRUIT_WINDOW, ctx={'data': rendererData,
         'menuEnabled': menuEnabled}))

    @decorators.process('buyBerths')
    def buyBerths(self):
        items = self.itemsCache.items
        berthPrice, berthsCount = items.shop.getTankmanBerthPrice(items.stats.tankmenBerthsCount)
        result = yield TankmanBerthsBuyer(berthPrice, berthsCount).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

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

    @decorators.process('updating')
    def actTankman(self, invID):
        tankman = self.itemsCache.items.getTankman(int(invID))
        if tankman is None:
            LOG_ERROR('Attempt to dismiss tankman by invalid invID:', invID)
            return
        else:
            if tankman.isDismissed:
                result = yield TankmanRestore(tankman).request()
            elif tankman.isInTank:
                tmanVehile = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
                if tmanVehile is None:
                    LOG_ERROR("Target tankman's vehicle is not found in inventory", tankman, tankman.vehicleInvID)
                    return
                result = yield TankmanUnload(tmanVehile, tankman.vehicleSlotIdx).request()
            else:
                result = yield TankmanDismiss(tankman).request()
            if len(result.userMsg):
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            return

    def update(self):
        self.__updateTankmen()

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

    def _populate(self):
        super(Barracks, self)._populate()
        self.app.component.wg_inputKeyMode = 1
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self.__updateTankmen
        g_clientUpdateManager.addCallbacks({'inventory.8': self.__updateTankmen,
         'stats.berths': self.__updateTankmen,
         'recycleBin.tankmen': self.__updateTankmen})
        self.restore.onTankmenBufferUpdated += self.__updateDismissedTankmen
        self.setTankmenFilter()

    def _dispose(self):
        self.restore.onTankmenBufferUpdated -= self.__updateDismissedTankmen
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.itemsCache.onSyncCompleted -= self.__updateTankmen
        self.stopGlobalListening()
        super(LobbySubView, self)._dispose()

    def __updateTanksList(self):
        data = list()
        modulesAll = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        modulesAll.sort()
        for module in modulesAll:
            if self.filter['nation'] != -1 and self.filter['nation'] != module.descriptor.type.id[0] or self.filter['tankType'] != 'None' and self.filter['tankType'] != -1 and self.filter['tankType'] != module.type:
                continue
            data.append({'data': {'type': module.type,
                      'nationID': module.descriptor.type.id[0],
                      'typeID': module.descriptor.type.id[1]},
             'label': module.descriptor.type.shortUserString})

        self.as_updateTanksListS(data)

    def __updateTankmen(self, *args):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED:
            self.__showDismissedTankmen(self.__buildCriteria())
        else:
            self.__showActiveTankmen(self.__buildCriteria())

    def __showActiveTankmen(self, criteria):
        tankmen = self.itemsCache.items.getTankmen().values()
        tankmenInBarracks = 0
        tankmenList = [_packBuyBerthsSlot()]
        for tankman in sorted(tankmen, TankmenComparator(self.itemsCache.items.getVehicle)):
            if not tankman.isInTank:
                tankmenInBarracks += 1
            if not criteria(tankman):
                continue
            tankmanData = _packTankmanData(tankman)
            if tankmanData is not None:
                if tankman.isInTank:
                    actionBtnLabel = MENU.BARRACKS_BTNUNLOAD
                    actionBtnTooltip = TOOLTIPS.BARRACKS_TANKMEN_UNLOAD
                else:
                    actionBtnLabel = MENU.BARRACKS_BTNDISSMISS
                    actionBtnTooltip = TOOLTIPS.BARRACKS_TANKMEN_DISMISS
                tankmanData.update({'isRankNameVisible': True,
                 'recoveryPeriodText': None,
                 'actionBtnLabel': actionBtnLabel,
                 'actionBtnTooltip': actionBtnTooltip,
                 'skills': None,
                 'isSkillsVisible': False})
                tankmenList.append(tankmanData)

        tankmenInSlots = len(tankmenList) - 1
        slots = self.itemsCache.items.stats.tankmenBerthsCount
        if tankmenInBarracks < slots:
            tankmenList.insert(1, {'empty': True,
             'freePlaces': slots - tankmenInBarracks})
        tankmenCountStr = _ms(MENU.BARRACKS_TANKMENCOUNT, curValue=tankmenInSlots, total=len(tankmen))
        placeCountStr = _ms(MENU.BARRACKS_PLACESCOUNT, free=max(slots - tankmenInBarracks, 0), total=slots)
        self.as_setTankmenS({'tankmenCount': text_styles.playerOnline(tankmenCountStr),
         'placesCount': text_styles.playerOnline(placeCountStr),
         'placesCountTooltip': None,
         'tankmenData': tankmenList,
         'hasNoInfoData': False})
        return

    def __showDismissedTankmen(self, criteria):
        tankmen = self.restore.getDismissedTankmen()
        tankmenList = list()
        for tankman in tankmen:
            if not criteria(tankman):
                continue
            skillsList = []
            for skill in tankman.skills:
                skillsList.append({'tankmanID': tankman.invID,
                 'id': str(tankman.skills.index(skill)),
                 'name': skill.userName,
                 'desc': skill.description,
                 'icon': skill.icon,
                 'level': skill.level,
                 'active': skill.isEnable and skill.isActive})

            newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
            if newSkillsCount > 0:
                skillsList.append({'buy': True,
                 'buyCount': newSkillsCount - 1,
                 'tankmanID': tankman.invID,
                 'level': lastNewSkillLvl})
            restoreInfo = getTankmenRestoreInfo(tankman)
            actionBtnTooltip = makeTooltip(TOOLTIPS.BARRACKS_TANKMEN_RECOVERYBTN_HEADER, getRecoveryStatusText(restoreInfo))
            tankmanData = _packTankmanData(tankman)
            tankmanData.update({'isRankNameVisible': False,
             'recoveryPeriodText': _makeRecoveryPeriodText(restoreInfo),
             'actionBtnLabel': MENU.BARRACKS_BTNRECOVERY,
             'actionBtnTooltip': actionBtnTooltip,
             'skills': skillsList,
             'isSkillsVisible': True})
            tankmenList.append(tankmanData)

        tankmenCountStr = _ms(MENU.BARRACKS_DISMISSEDTANKMENCOUNT, curValue=len(tankmenList), total=len(tankmen))
        placeCount = self.restore.getMaxTankmenBufferLength()
        placeCountStr = _ms(MENU.BARRACKS_RECOVERYCOUNT, total=placeCount, info=icons.info())
        noInfoData = None
        hasNoInfoData = len(tankmenList) == 0
        if hasNoInfoData:
            if len(tankmen) == 0:
                tankmenRestoreConfig = self.itemsCache.items.shop.tankmenRestoreConfig
                freeDays = tankmenRestoreConfig.freeDuration / time_utils.ONE_DAY
                billableDays = tankmenRestoreConfig.billableDuration / time_utils.ONE_DAY - freeDays
                noInfoData = {'title': text_styles.highTitle(MENU.BARRACKS_NORECOVERYTANKMEN_TITLE),
                 'message': text_styles.main(_ms(MENU.BARRACKS_NORECOVERYTANKMEN_MESSAGE, price=moneyWithIcon(tankmenRestoreConfig.cost), totalDays=freeDays + billableDays, freeDays=freeDays, paidDays=billableDays))}
            else:
                noInfoData = {'message': text_styles.main(MENU.BARRACKS_NOFILTEREDRECOVERYTANKMEN_MESSAGE)}
        placesCountTooltip = makeTooltip(TOOLTIPS.BARRACKS_PLACESCOUNT_DISMISS_HEADER, _ms(TOOLTIPS.BARRACKS_PLACESCOUNT_DISMISS_BODY, placeCount=placeCount))
        self.as_setTankmenS({'tankmenCount': text_styles.playerOnline(tankmenCountStr),
         'placesCount': text_styles.playerOnline(placeCountStr),
         'placesCountTooltip': placesCountTooltip,
         'tankmenData': tankmenList,
         'hasNoInfoData': hasNoInfoData,
         'noInfoData': noInfoData})
        return

    def __buildCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        if self.filter['nation'] != -1:
            criteria |= REQ_CRITERIA.NATIONS([self.filter['nation']])
        if self.filter['role'] != 'None':
            criteria |= REQ_CRITERIA.TANKMAN.ROLES(self.filter['role'])
        if self.filter['tankType'] != 'None':
            criteria |= REQ_CRITERIA.CUSTOM(lambda tankman: tankman.vehicleNativeType == self.filter['tankType'])
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_TANKS or self.filter['location'] == '':
            criteria |= REQ_CRITERIA.TANKMAN.IN_TANK
        elif self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_BARRACKS:
            criteria |= ~REQ_CRITERIA.TANKMAN.IN_TANK
        if self.filter['nationID'] is not None:
            vehicle = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, int(self.filter['nationID']), int(self.filter['location']))
            criteria |= REQ_CRITERIA.TANKMAN.NATIVE_TANKS([vehicle.intCD])
        return criteria

    def __updateDismissedTankmen(self):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED:
            self.__showDismissedTankmen(self.__buildCriteria())
