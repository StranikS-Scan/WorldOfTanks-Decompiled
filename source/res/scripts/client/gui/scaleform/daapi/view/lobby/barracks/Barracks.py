# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/barracks/Barracks.py
import logging
from account_helpers.AccountSettings import AccountSettings, BARRACKS_FILTER, RECRUIT_NOTIFICATIONS
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.barracks.barracks_data_provider import BarracksDataProvider
from gui.Scaleform.daapi.view.lobby.barracks.sound_constants import BARRACKS_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.BarracksMeta import BarracksMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import recruit_helper
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showPersonalCase
from gui.shared.formatters import icons, moneyWithIcon, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmenComparator
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanRestore, TankmanUnload
from gui.shared.utils import decorators, flashObject2Dict
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import showBuyGoldForBerth
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency, time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRestoreController, IWalletController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_COUNTERS_MAP = {RECRUIT_NOTIFICATIONS: ('locationButtonBar', 5)}

def _packCounterVO(componentId, count, selectedIdx=0):
    return {'componentId': componentId,
     'count': count,
     'selectedIdx': selectedIdx}


class Barracks(BarracksMeta, LobbySubView, IGlobalListener):
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    restore = dependency.descriptor(IRestoreController)
    wallet = dependency.descriptor(IWalletController)

    def __init__(self, ctx=None):
        super(Barracks, self).__init__()
        self.filter = dict(AccountSettings.getFilter(BARRACKS_FILTER))
        self.__ctx = ctx
        self.__updateLocationFilter()
        self.__sortedCachedTankmen = None
        self.__notRecruitedTankmen = []
        self.__dataProvider = BarracksDataProvider()
        return

    @property
    def dataProvider(self):
        return self.__dataProvider

    def openPersonalCase(self, tankmanInvID, tabID):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            return
        tmanInvID = int(tankmanInvID)
        tankman = self.itemsCache.items.getTankman(tmanInvID)
        if tankman and not tankman.isDismissed:
            showPersonalCase(tmanInvID, previousViewID=R.views.lobby.crew.BarracksView())

    def closeBarracks(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateTanksList(self):
        self.__updateTanksList()

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        if rendererData is not None and rendererData.notRecruited:
            showRecruitWindow(rendererData.recruitID)
        return

    def buyBerths(self):
        price, _ = self.itemsCache.items.shop.getTankmanBerthPrice(self.itemsCache.items.stats.tankmenBerthsCount)
        availableMoney = self.itemsCache.items.stats.money
        if price and self.wallet.isAvailable and availableMoney.gold < price.gold:
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

    @decorators.adisp_process('updating')
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
                result = yield TankmanUnload(tmanVehile.invID, tankman.vehicleSlotIdx).request()
            else:
                result = yield TankmanDismiss(tankman).request()
            SystemMessages.pushMessagesFromResult(result)
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
        self.app.component.wg_inputKeyMode = InputKeyMode.IGNORE_RESULT
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self.__updateCachedTankmenList
        self.eventsCache.onProgressUpdated += self.__updateNotRecruitedTankmen
        self.restore.onTankmenBufferUpdated += self.__updateDismissedTankmen
        self.__dataProvider.setFlashObject(self.as_getDataProviderS())
        self.__updateNotRecruitedTankmen()
        self.setTankmenFilter()

    def _invalidate(self, ctx=None):
        super(Barracks, self)._invalidate(ctx)
        self.__ctx = ctx
        self.__updateLocationFilter()
        self.setTankmenFilter()

    def _dispose(self):
        self.eventsCache.onProgressUpdated -= self.__updateNotRecruitedTankmen
        self.restore.onTankmenBufferUpdated -= self.__updateDismissedTankmen
        self.itemsCache.onSyncCompleted -= self.__updateCachedTankmenList
        self.stopGlobalListening()
        self.__sortedCachedTankmen = None
        self.__notRecruitedTankmen = None
        if self.__dataProvider is not None:
            self.__dataProvider.clear()
            self.__dataProvider.destroy()
            self.__dataProvider = None
        super(LobbySubView, self)._dispose()
        return

    def __updateLocationFilter(self):
        data = self.__ctx or {}
        location = data.get('location')
        if location is not None:
            self.filter['location'] = location
        nationID = data.get('nationID')
        if nationID is not None:
            self.filter['nationID'] = nationID
        tankType = data.get('tankType')
        if tankType is not None:
            self.filter['tankType'] = tankType
        role = data.get('role')
        if role is not None:
            self.filter['role'] = role
        return

    def __updateTanksList(self):
        data = list()
        criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.IS_CREW_HIDDEN
        criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.MAPS_TRAINING
        criteria |= ~REQ_CRITERIA.VEHICLE.HIDDEN_IN_HANGAR
        modulesAll = self.itemsCache.items.getVehicles(criteria).values()
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

    def __updateCachedTankmenList(self, *args):
        self.__updateTankmen()

    def __getSortedTankmen(self):
        return sorted(self.itemsCache.items.getTankmen().itervalues(), cmp=TankmenComparator(self.itemsCache.items.getVehicle))

    def __showActiveTankmen(self, criteria):
        self.__dataProvider.showActiveTankmen(criteria)
        self.as_setTankmenS({'tankmenCount': self.__getTankmenCountStr(self.__dataProvider.filteredCount, totalCount=self.__dataProvider.totalCount),
         'placesCount': self.__getPlaceCountStr(free=self.__dataProvider.placeCount, totalCount=self.itemsCache.items.stats.tankmenBerthsCount),
         'placesCountTooltip': None,
         'hasNoInfoData': False})
        return

    def __showDismissedTankmen(self, criteria):
        self.__dataProvider.showDismissedTankmen(criteria)
        placeCount = self.__dataProvider.placeCount
        filteredCount = self.__dataProvider.filteredCount
        totalCount = self.__dataProvider.totalCount
        hasNoInfoData, noInfoData = self.__getNoInfoData(totalCount=totalCount, filteredCount=filteredCount)
        self.as_setTankmenS({'tankmenCount': self.__getTankmenCountStr(tankmenInSlots=filteredCount, totalCount=totalCount),
         'placesCount': self.__getPlaceCountStr(free=icons.info(), totalCount=placeCount),
         'placesCountTooltip': self.__getPlacesCountTooltip(placeCount=placeCount),
         'hasNoInfoData': hasNoInfoData,
         'noInfoData': noInfoData})

    def __updateNotRecruitedTankmen(self, *args):
        if self.filter['location'] == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED:
            self.__updateTankmen()
            recruit_helper.setNewRecruitsVisited()
        else:
            self.__updateRecruitNotification()

    def __showNotRecruitedTankmen(self):
        self.__dataProvider.showNotRecruitedTankmen()
        count = self.__dataProvider.totalCount
        hasNoInfoData, noInfoData = self.__getNoInfoData(totalCount=count, filteredCount=count)
        self.as_setTankmenS({'tankmenCount': self.__getTankmenCountStr(totalCount=count),
         'placesCount': '',
         'placesCountTooltip': None,
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
