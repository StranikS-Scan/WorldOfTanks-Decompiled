# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/barracks/Barracks.py
import logging
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, BARRACKS_FILTER, RECRUIT_NOTIFICATIONS
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.BarracksMeta import BarracksMeta
from gui.Scaleform.daapi.view.lobby.barracks.sound_constants import BARRACKS_SOUND_SPACE
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.ingame_shop import showBuyGoldForBerth
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared import events, event_dispatcher as shared_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons, moneyWithIcon
from gui.shared.gui_items import Tankman, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmenComparator
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload, TankmanRestore
from gui.shared.money import Currency
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.tankman import getRecoveryStatusText, formatRecoveryLeftValue
from gui.shared.utils import decorators, flashObject2Dict
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.ambients import LobbySubViewEnv
from gui.server_events import recruit_helper
from helpers import i18n, time_utils, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
_COUNTERS_MAP = {RECRUIT_NOTIFICATIONS: ('locationButtonBar', 5)}

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _packTankmanData(tankman, itemsCache=None):
    tankmanVehicle = itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
    if tankman.isInTank:
        vehicle = itemsCache.items.getVehicle(tankman.vehicleInvID)
        if vehicle is None:
            _logger.error('Cannot find vehicle for tankman: %r %r %r %r %r', tankman, tankman.descriptor.role, tankman.vehicle.name, tankman.firstname, tankman.lastname)
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
     'isInSelfVehicleType': isInSelfVehicle,
     'notRecruited': False}
    return data


def _packNotRecruitedTankman(recruitInfo):
    expiryTime = recruitInfo.getExpiryTime()
    recruitBeforeStr = _ms(MENU.BARRACKS_NOTRECRUITEDACTIVATEBEFORE, date=expiryTime) if expiryTime else ''
    availableRoles = recruitInfo.getRoles()
    roleType = availableRoles[0] if len(availableRoles) == 1 else ''
    result = {'firstName': i18n.convert(recruitInfo.getFirstName()),
     'lastName': i18n.convert(recruitInfo.getLastName()),
     'rank': recruitBeforeStr,
     'specializationLevel': recruitInfo.getRoleLevel(),
     'role': text_styles.counter(recruitInfo.getLabel()),
     'vehicleType': '',
     'iconFile': recruitInfo.getBarracksIcon(),
     'roleIconFile': Tankman.getRoleBigIconPath(roleType) if roleType else '',
     'rankIconFile': '',
     'contourIconFile': '',
     'tankmanID': -1,
     'nationID': -1,
     'typeID': -1,
     'roleType': roleType,
     'tankType': '',
     'inTank': False,
     'compact': '',
     'lastSkillLevel': recruitInfo.getLastSkillLevel(),
     'actionBtnEnabled': True,
     'inCurrentTank': False,
     'vehicleID': None,
     'slot': None,
     'locked': False,
     'lockMessage': '',
     'isInSelfVehicleClass': True,
     'isInSelfVehicleType': True,
     'notRecruited': True,
     'isRankNameVisible': True,
     'recoveryPeriodText': None,
     'actionBtnLabel': MENU.BARRACKS_BTNRECRUITNOTRECRUITED,
     'actionBtnTooltip': TOOLTIPS.BARRACKS_TANKMEN_RECRUIT,
     'skills': [],
     'isSkillsVisible': False,
     'recruitID': str(recruitInfo.getRecruitID())}
    return result


def _getTankmanLockMessage(invVehicle):
    if invVehicle.isInBattle:
        return (True, i18n.makeString('#menu:tankmen/lockReason/inbattle'))
    if invVehicle.isBroken:
        return (True, i18n.makeString('#menu:tankmen/lockReason/broken'))
    return (True, i18n.makeString('#menu:tankmen/lockReason/prebattle')) if invVehicle.invID == g_currentVehicle.invID and (g_currentVehicle.isInPrebattle() or g_currentVehicle.isInBattle()) else (False, '')


def _packCounterVO(componentId, count, selectedIdx=0):
    return {'componentId': componentId,
     'count': count,
     'selectedIdx': selectedIdx}


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
     'price': BigWorld.wg_getGoldFormat(berthPrice.getSignValue(Currency.GOLD)),
     'enoughGold': enoughGold or isIngameShopEnabled(),
     'actionPriceData': action,
     'count': berthCount}


def _makeRecoveryPeriodText(restoreInfo):
    price, timeLeft = restoreInfo
    timeStr = formatRecoveryLeftValue(timeLeft)
    if not price.isDefined():
        textStyle = text_styles.main
    elif price.getCurrency() == Currency.GOLD:
        textStyle = text_styles.gold
    else:
        textStyle = text_styles.credits
    return textStyle(timeStr)


class Barracks(BarracksMeta, LobbySubView, IGlobalListener):
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, ctx=None):
        super(Barracks, self).__init__()
        self.filter = dict(AccountSettings.getFilter(BARRACKS_FILTER))
        self.__updateLocationFilter(ctx)
        self.__notRecruitedTankmen = []

    def openPersonalCase(self, tankmanInvID, tabNumber):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            return
        tmanInvID = int(tankmanInvID)
        tankman = self.itemsCache.items.getTankman(tmanInvID)
        if tankman and not tankman.isDismissed:
            shared_events.showPersonalCase(tmanInvID, int(tabNumber), EVENT_BUS_SCOPE.LOBBY)

    def closeBarracks(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateTanksList(self):
        self.__updateTanksList()

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        if rendererData is not None and rendererData.notRecruited:
            showRecruitWindow(rendererData.recruitID)
        else:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.RECRUIT_WINDOW, ctx={'data': rendererData,
             'menuEnabled': menuEnabled}))
        return

    def buyBerths(self):
        price, _ = self.itemsCache.items.shop.getTankmanBerthPrice(self.itemsCache.items.stats.tankmenBerthsCount)
        availableMoney = self.itemsCache.items.stats.money
        if price and availableMoney.gold < price.gold and isIngameShopEnabled():
            showBuyGoldForBerth(price.gold)
        else:
            ActionsFactory.doAction(ActionsFactory.BUY_BERTHS)

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
        if self.filter['location'] != BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            tankman = self.itemsCache.items.getTankman(int(invID))
            if tankman is None:
                _logger.error('Attempt to dismiss tankman by invalid invID: %r', invID)
                return
            if tankman.isDismissed:
                result = yield TankmanRestore(tankman).request()
            elif tankman.isInTank:
                tmanVehile = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
                if tmanVehile is None:
                    _logger.error("Target tankman's vehicle is not found in inventory %r %r", tankman, tankman.vehicleInvID)
                    return
                result = yield TankmanUnload(tmanVehile, tankman.vehicleSlotIdx).request()
            else:
                result = yield TankmanDismiss(tankman).request()
            if result.userMsg:
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

    def onCountersVisited(self, counters):
        for counterGfxData in counters:
            counterData = flashObject2Dict(counterGfxData)
            valToSearch = (counterData['componentId'], counterData['selectedIdx'])
            prefName = _COUNTERS_MAP.keys()[_COUNTERS_MAP.values().index(valToSearch)]
            self.__setCountersData(prefName, counter=0)
            self.__setVisited(prefName)

    def _populate(self):
        super(Barracks, self)._populate()
        self.app.component.wg_inputKeyMode = 1
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self.__updateTankmen
        g_clientUpdateManager.addCallbacks({'inventory.8': self.__updateTankmen,
         'stats.berths': self.__updateTankmen,
         'recycleBin.tankmen': self.__updateTankmen})
        self.eventsCache.onProgressUpdated += self.__updateNotRecruitedTankmen
        self.restore.onTankmenBufferUpdated += self.__updateDismissedTankmen
        self.__updateNotRecruitedTankmen()
        self.setTankmenFilter()

    def _invalidate(self, ctx=None):
        super(Barracks, self)._invalidate(ctx)
        self.__updateLocationFilter(ctx)
        self.setTankmenFilter()

    def _dispose(self):
        self.eventsCache.onProgressUpdated -= self.__updateNotRecruitedTankmen
        self.restore.onTankmenBufferUpdated -= self.__updateDismissedTankmen
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.itemsCache.onSyncCompleted -= self.__updateTankmen
        self.stopGlobalListening()
        super(LobbySubView, self)._dispose()

    def __updateLocationFilter(self, ctx):
        if ctx is not None:
            location = ctx.get('location', None)
            if location is not None:
                self.filter['location'] = location
        return

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
        isNotRecruited = self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED
        self.__switchTankmanFiltersEnable(not isNotRecruited)
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED:
            self.__showDismissedTankmen(self.__buildCriteria())
        elif isNotRecruited:
            self.__showNotRecruitedTankmen()
        else:
            self.__showActiveTankmen(self.__buildCriteria())

    def __showActiveTankmen(self, criteria):
        tankmen = self.itemsCache.items.getTankmen().values()
        tankmenInBarracks = 0
        tankmenList = [_packBuyBerthsSlot()]
        for tankman in sorted(tankmen, cmp=TankmenComparator(self.itemsCache.items.getVehicle)):
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
        self.as_setTankmenS({'tankmenCount': self.__getTankmenCountStr(tankmenInSlots=tankmenInSlots, totalCount=len(tankmen)),
         'placesCount': self.__getPlaceCountStr(free=max(slots - tankmenInBarracks, 0), totalCount=slots),
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

        placeCount = self.restore.getMaxTankmenBufferLength()
        hasNoInfoData, noInfoData = self.__getNoInfoData(totalCount=len(tankmen), filteredCount=len(tankmenList))
        self.as_setTankmenS({'tankmenCount': self.__getTankmenCountStr(tankmenInSlots=len(tankmenList), totalCount=len(tankmen)),
         'placesCount': self.__getPlaceCountStr(free=icons.info(), totalCount=placeCount),
         'placesCountTooltip': self.__getPlacesCountTooltip(placeCount=placeCount),
         'tankmenData': tankmenList,
         'hasNoInfoData': hasNoInfoData,
         'noInfoData': noInfoData})

    def __updateNotRecruitedTankmen(self, *args):
        self.__notRecruitedTankmen = []
        for recruitInfo in recruit_helper.getAllRecruitsInfo(sortByExpireTime=True):
            self.__notRecruitedTankmen.append(_packNotRecruitedTankman(recruitInfo))

        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            self.__updateTankmen()
            recruit_helper.setNewRecruitsVisited()
        else:
            self.__updateRecruitNotification()

    def __showNotRecruitedTankmen(self):
        count = len(self.__notRecruitedTankmen)
        hasNoInfoData, noInfoData = self.__getNoInfoData(totalCount=count, filteredCount=count)
        self.as_setTankmenS({'tankmenCount': self.__getTankmenCountStr(totalCount=count),
         'placesCount': '',
         'placesCountTooltip': None,
         'tankmenData': self.__notRecruitedTankmen,
         'hasNoInfoData': hasNoInfoData,
         'noInfoData': noInfoData})
        return

    def __getNoInfoData(self, totalCount=0, filteredCount=0):
        hasNoInfoData = filteredCount < 1
        noInfoData = None
        if hasNoInfoData:
            if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED:
                if totalCount < 1:
                    tankmenRestoreConfig = self.itemsCache.items.shop.tankmenRestoreConfig
                    freeDays = tankmenRestoreConfig.freeDuration / time_utils.ONE_DAY
                    billableDays = tankmenRestoreConfig.billableDuration / time_utils.ONE_DAY - freeDays
                    noInfoData = {'title': text_styles.highTitle(MENU.BARRACKS_NORECOVERYTANKMEN_TITLE),
                     'message': text_styles.main(_ms(MENU.BARRACKS_NORECOVERYTANKMEN_MESSAGE, price=moneyWithIcon(tankmenRestoreConfig.cost), totalDays=freeDays + billableDays, freeDays=freeDays, paidDays=billableDays))}
                else:
                    noInfoData = {'message': text_styles.main(MENU.BARRACKS_NOFILTEREDRECOVERYTANKMEN_MESSAGE)}
            elif self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
                noInfoData = {'title': text_styles.highTitle(MENU.BARRACKS_NONOTRECRUITEDTANKMEN_TITLE),
                 'message': text_styles.main(MENU.BARRACKS_NONOTRECRUITEDTANKMEN_MESSAGE)}
        return (hasNoInfoData, noInfoData)

    def __getPlaceCountStr(self, free=0, totalCount=0):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED:
            result = _ms(MENU.BARRACKS_RECOVERYCOUNT, info=free, total=totalCount)
        elif self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            result = ''
        else:
            result = _ms(MENU.BARRACKS_PLACESCOUNT, free=free, total=totalCount)
        return text_styles.playerOnline(result) if result else ''

    def __getPlacesCountTooltip(self, placeCount):
        return makeTooltip(TOOLTIPS.BARRACKS_PLACESCOUNT_DISMISS_HEADER, _ms(TOOLTIPS.BARRACKS_PLACESCOUNT_DISMISS_BODY, placeCount=placeCount)) if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED else None

    def __getTankmenCountStr(self, tankmenInSlots=0, totalCount=0):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED:
            result = _ms(MENU.BARRACKS_DISMISSEDTANKMENCOUNT, curValue=tankmenInSlots, total=totalCount)
        elif self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            result = _ms(MENU.BARRACKS_NOTRECRUITEDCOUNT, total=totalCount)
        else:
            result = _ms(MENU.BARRACKS_TANKMENCOUNT, curValue=tankmenInSlots, total=totalCount)
        return text_styles.playerOnline(result)

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

    def __switchTankmanFiltersEnable(self, value):
        self.as_switchFilterEnableS(nationEnable=value, roleEnable=value, typeEnable=value)

    def __updateRecruitNotification(self):
        counter = recruit_helper.getNewRecruitsCounter()
        self.__setCountersData(RECRUIT_NOTIFICATIONS, counter)

    def __setCountersData(self, preferenceName, counter):
        counters = [_packCounterVO(componentId=_COUNTERS_MAP[preferenceName][0], count=str(counter) if counter else '', selectedIdx=_COUNTERS_MAP[preferenceName][1])]
        self.as_setCountersDataS(countersData=counters)

    def __setVisited(self, preferenceName):
        if preferenceName == RECRUIT_NOTIFICATIONS:
            recruit_helper.setNewRecruitsVisited()
