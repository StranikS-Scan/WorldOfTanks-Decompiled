# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import itertools
import logging
import weakref
from collections import namedtuple
import BigWorld
from frameworks.wulf import ViewFlags
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import LootBoxBonusComposer
from gui.Scaleform.locale.LOOTBOXES import LOOTBOXES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_model import LootBoxCompensationTooltipModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_renderer_types import LootRendererTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_video_renderer_model import LootVehicleVideoRendererModel
from gui.impl.auxiliary.rewards_helper import LootVehicleRewardPresenter, VehicleCompensationModelPresenter, LootNewYearToyPresenter, LootNewYearFragmentsPresenter, NY_VIDEO, getVehByStyleCD, isSpecialStyle, LootVideoWithCongratsRewardPresenter, getVehicleStrID
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter
from gui.impl.lobby.loot_box.tooltips.compensation_tooltip import CompensationTooltipContent
from gui.impl.lobby.loot_box.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxViewEvents, playSound
from gui.impl.new_year.tooltips.toy_content import ToyContent
from gui.server_events.awards_formatters import getLootboxesAwardsPacker, getLootboxesAutoOpenAwardsPacker
from gui.server_events.bonuses import getNonQuestBonuses
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showVehiclePreview, showHangar
from gui.shared.events import GameEvent
from gui.shared.gui_items import Vehicle
from gui.shared.money import Currency, Money, ZERO_MONEY
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from helpers.i18n import makeString as _ms
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
MAX_BOXES_TO_OPEN = 5
ADDITIONAL_AWARDS_COUNT = 6
LOOT_BOX_REWARDS = 'lootBoxRewards'
_AUTO_MAX_COUNT = 99999
_logger = logging.getLogger(__name__)
_BONUSES_ORDER = ('ny19ToyFragments',
 'ny19Toys',
 Currency.CREDITS,
 'premium',
 Currency.GOLD,
 Currency.CRYSTAL,
 'vehicles',
 'freeXP',
 'freeXPFactor',
 'creditsFactor',
 'tankmen',
 'items',
 'slots',
 'berths',
 'dossier',
 'customizations',
 'tokens',
 'goodies')
_AUTO_OPEN_BONUSES_ORDER = ('ny19ToyFragments',
 'customizations',
 'vehicles',
 Currency.GOLD,
 Currency.CREDITS,
 'premium',
 'tmanToken')
SpecialRewardData = namedtuple('SpecialRewardData', ('sourceName', 'congratsType', 'congratsSourceId', 'vehicleName', 'vehicleLvl', 'vehicleIsElite', 'vehicleType'))

def getMergedLootBoxBonuses(bonusesList):
    result = {}
    for bonuses in bonusesList:
        for bonusName, bonusValue in bonuses.iteritems():
            BONUS_MERGERS[bonusName](result, bonusName, bonusValue, False, 1, None)

    return result


def _isVideoVehicle(vehicle):
    return True if NY_VIDEO in vehicle.tags else False


class LootBoxShowHideCloseHandler(object):
    __slots__ = ('__target',)

    def __init__(self):
        self.__target = None
        return

    def startListen(self, target):
        self.__target = weakref.proxy(target)
        g_eventBus.addListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.addListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.addListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)

    def stopListen(self):
        self.__target = None
        g_eventBus.removeListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.removeListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.removeListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)
        return

    def __onHideLBWindow(self, _=None):
        if self.__target:
            self.__target.hide()

    def __onShowLBWindow(self, _=None):
        if self.__target:
            self.__target.show()
            fireSpecialRewardsClosed()

    def __onCloseLBWindow(self, _=None):
        if self.__target:
            self.__target.destroy()


class _LootVehicleVideoRewardPresenter(LootVehicleRewardPresenter):
    __slots__ = ('__videoStrID',)

    def __init__(self):
        super(_LootVehicleVideoRewardPresenter, self).__init__()
        self.__videoStrID = None
        return

    def _setReward(self, reward):
        super(_LootVehicleVideoRewardPresenter, self)._setReward(reward)
        self.__videoStrID = None
        if self._vehicle is not None and _isVideoVehicle(self._vehicle):
            self.__videoStrID = Vehicle.getIconResourceName(getVehicleStrID(self._vehicle.name))
        return

    def _createModel(self):
        return LootVehicleVideoRendererModel() if self.__isVideoVehicle() else LootDefRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE_VIDEO if self.__isVideoVehicle() else LootRendererTypes.DEF

    def _formatVehicle(self, vehicle, model):
        if self.__isVideoVehicle():
            super(_LootVehicleVideoRewardPresenter, self)._formatVehicle(vehicle, model)
            model.setVideoSrc(self.__videoStrID or '')

    def __isVideoVehicle(self):
        return self.__videoStrID is not None


_COMPENSATION_PRESENTERS = {'vehicles': VehicleCompensationModelPresenter()}
_MODEL_PRESENTERS = {'vehicles': _LootVehicleVideoRewardPresenter(),
 'tmanToken': LootVideoWithCongratsRewardPresenter(LootCongratsTypes.CONGRAT_TYPE_TANKMAN),
 'customizations': LootVideoWithCongratsRewardPresenter(LootCongratsTypes.CONGRAT_TYPE_STYLE),
 'ny19Toys': LootNewYearToyPresenter(),
 'ny19ToyFragments': LootNewYearFragmentsPresenter()}

def getLootboxRendererModelPresenter(reward):
    return getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, _COMPENSATION_PRESENTERS)


def showLootBoxMultyOpen(lootBoxItem, rewards):
    from gui.impl.lobby.loot_box.loot_box_multi_open_view import LootBoxMultiOpenWindow
    window = LootBoxMultiOpenWindow(lootBoxItem, rewards)
    window.load()


def showLootBoxReward(lootBoxItem, rewards):
    from gui.impl.lobby.loot_box.loot_box_reward_view import LootBoxRewardWrapperWindow
    window = LootBoxRewardWrapperWindow(lootBoxItem, rewards)
    window.load()


def fireHideRewardView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireCloseToHangar():
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    _closeLootBoxWindows()


def fireHideMultiOpenView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireSpecialRewardsClosed():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def showLootBoxSpecialReward(responseDict):
    from gui.impl.lobby.loot_box.loot_box_special_reward_view import LootBoxSpecialRewardWindow
    congratsType = responseDict.get('congratsType')
    congratsSourceId = responseDict.get('congratsSourceId')
    sourceName = responseDict.get('sourceName')
    if sourceName and congratsSourceId is not None and congratsType is not None:
        specialRewardData = SpecialRewardData(sourceName=sourceName, congratsType=congratsType, congratsSourceId=int(congratsSourceId), vehicleName=responseDict.get('vehicleName'), vehicleIsElite=responseDict.get('vehicleIsElite'), vehicleLvl=responseDict.get('vehicleLvl'), vehicleType=responseDict.get('vehicleType'))
        window = LootBoxSpecialRewardWindow(specialRewardData)
        window.load()
    return


def getRewardTooltipContent(event):
    if event.contentID == R.views.lootBoxCompensationTooltipContent:
        tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
         'labelBefore': event.getArgument('labelBefore', ''),
         'iconAfter': event.getArgument('iconAfter', ''),
         'labelAfter': event.getArgument('labelAfter', ''),
         'bonusName': event.getArgument('bonusName', '')}
        return CompensationTooltipContent(content=R.views.lootBoxCompensationTooltipContent, viewFlag=ViewFlags.VIEW, model=LootBoxCompensationTooltipModel, **tooltipData)
    elif event.contentID == R.views.lootBoxVehicleCompensationTooltipContent:
        tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
         'labelBefore': event.getArgument('labelBefore', ''),
         'iconAfter': event.getArgument('iconAfter', ''),
         'labelAfter': event.getArgument('labelAfter', ''),
         'bonusName': event.getArgument('bonusName', ''),
         'vehicleName': event.getArgument('vehicleName', ''),
         'vehicleType': event.getArgument('vehicleType', ''),
         'isElite': event.getArgument('isElite', True),
         'vehicleLvl': event.getArgument('vehicleLvl', '')}
        return VehicleCompensationTooltipContent(**tooltipData)
    elif event.contentID == R.views.newYearToyTooltipContent:
        toyID = event.getArgument('toyID')
        return ToyContent(toyID)
    else:
        return None


def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=_ms(LOOTBOXES.RESTRICTEDMESSAGE_BODY), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': _ms(LOOTBOXES.RESTRICTEDMESSAGE_HEADER)})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


def preparationRewardsCurrency(rewards):
    money = _getCompensationMoney(rewards)
    for currency in Currency.ALL:
        if currency in rewards:
            rewards[currency] -= money.get(currency, 0)
            if rewards[currency] <= 0:
                del rewards[currency]


def getAutoOpenLootboxBonuses(rewards, size='big'):
    preparationRewardsCurrency(rewards)
    formatter = LootBoxBonusComposer(_AUTO_MAX_COUNT, getLootboxesAutoOpenAwardsPacker())
    bonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'premium':
                splitDays = _splitPremiumDays(bonusValue)
                for day in splitDays:
                    bonus = getNonQuestBonuses(bonusType, day)
                    bonuses.extend(bonus)

            if bonusType == 'vehicles' and isinstance(bonusValue, list):
                for vehicleData in bonusValue:
                    bonus = getNonQuestBonuses(bonusType, vehicleData)
                    bonuses.extend(bonus)

            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

    bonuses.sort(key=_autoOpenKeySortOrder)
    return formatter.getFormattedBonuses(bonuses, size)


def getLootboxBonuses(rewards, size='big', maxAwardCount=ADDITIONAL_AWARDS_COUNT):
    preparationRewardsCurrency(rewards)
    specialRewardType = ''
    formatter = LootBoxBonusComposer(maxAwardCount, getLootboxesAwardsPacker())
    bonuses = []
    alwaysVisibleBonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'vehicles' and isinstance(bonusValue, list):
                for vehicleData in bonusValue:
                    bonus = getNonQuestBonuses(bonusType, vehicleData)
                    if _checkAndFillVehicles(bonus, alwaysVisibleBonuses, bonuses):
                        specialRewardType = LootCongratsTypes.CONGRAT_TYPE_VEHICLE

            if bonusType == 'customizations':
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                if _checkAndFillCustomizations(bonus, alwaysVisibleBonuses, bonuses):
                    specialRewardType = LootCongratsTypes.CONGRAT_TYPE_STYLE
            if bonusType == 'tokens':
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                if _checkAndFillTokens(bonus, alwaysVisibleBonuses, bonuses):
                    specialRewardType = LootCongratsTypes.CONGRAT_TYPE_TANKMAN
            if bonusType == 'premium':
                splitDays = _splitPremiumDays(bonusValue)
                for day in splitDays:
                    bonus = getNonQuestBonuses(bonusType, day)
                    bonuses.extend(bonus)

            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        bonuses.sort(key=_keySortOrder)
    formattedBonuses = formatter.getVisibleFormattedBonuses(bonuses, alwaysVisibleBonuses, size)
    return (formattedBonuses, specialRewardType)


def _getCompensationMoney(bonuses):
    money = ZERO_MONEY
    for bonusName, bonusValue in bonuses.iteritems():
        if bonusName == 'vehicles':
            vehicles = itertools.chain.from_iterable([ vehBonus.itervalues() for vehBonus in bonusValue ])
            for vehData in vehicles:
                if 'customCompensation' in vehData:
                    money += Money.makeFromMoneyTuple(vehData['customCompensation'])

    return money


class _ExitCallback(object):

    def __init__(self, exitCallback, destroyCallback):
        self.__exitCallback = exitCallback
        self.__destroyCallback = destroyCallback
        self.__wasCalled = False

    def __call__(self, fromDestroy=False):
        if not self.__wasCalled:
            if fromDestroy:
                self.__destroyCallback()
            else:
                self.__exitCallback()
            self.__wasCalled = True
            self.__exitCallback = None
            self.__destroyCallback = None
        return


@dependency.replace_none_kwargs(itemsCache=IItemsCache, c11nService=ICustomizationService)
def showStyledVehicleByStyleCD(styleIntCD, itemsCache=None, c11nService=None):
    vehicle = getVehByStyleCD(styleIntCD)
    if vehicle.isInInventory:
        style = itemsCache.items.getItemByCD(styleIntCD)
        callback = lambda : c11nService.getCtx().previewStyle(style, exitCallback=_ExitCallback(_showLootBoxWindows, _closeLootBoxWindows))
        c11nService.showCustomization(vehicle.invID, callback)
    else:
        showVehiclePreview(vehicle.intCD, previewAlias=LOOT_BOX_REWARDS, vehParams={'styleCD': styleIntCD}, previewBackCb=_ExitCallback(_goHangarAndRestoreLootboxWindows, _closeLootBoxWindows))
    _hideLootBoxWindows()


def _goHangarAndRestoreLootboxWindows():
    showHangar()
    _showLootBoxWindows()


def _showLootBoxWindows():
    playSound(LootBoxViewEvents.ENTRY_VIEW_ENTER)
    g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_LOOT_BOX_WINDOWS))


def _hideLootBoxWindows():
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_LOOT_BOX_WINDOWS))


def _closeLootBoxWindows():
    g_eventBus.handleEvent(GameEvent(GameEvent.CLOSE_LOOT_BOX_WINDOWS))


def _keySortOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _autoOpenKeySortOrder(bonus):
    if bonus.getName() in _AUTO_OPEN_BONUSES_ORDER:
        return _AUTO_OPEN_BONUSES_ORDER.index(bonus.getName())
    addIndex = 1 if bonus.getName() == 'ny19Toys' else 0
    return len(_AUTO_OPEN_BONUSES_ORDER) + addIndex


def _checkAndFillVehicles(bonus, alwaysVisibleBonuses, bonuses):
    hasVehicle = False
    for vehBonus in bonus:
        for vehicle, _ in vehBonus.getVehicles():
            if _isVideoVehicle(vehicle):
                hasVehicle = True
                break

        if hasVehicle:
            alwaysVisibleBonuses.append(vehBonus)
        bonuses.append(vehBonus)

    return hasVehicle


def _checkAndFillCustomizations(bonus, alwaysVisibleBonuses, bonuses):
    hasStyle = False
    for customBonus in bonus:
        for bonusData in customBonus.getCustomizations():
            bonusType = bonusData.get('custType')
            bonusValue = bonusData.get('value')
            item = customBonus.getC11nItem(bonusData)
            if bonusType and bonusValue and bonusType == 'style' and isSpecialStyle(item.intCD):
                hasStyle = True
                break

        if hasStyle:
            alwaysVisibleBonuses.append(customBonus)
        bonuses.append(customBonus)

    return hasStyle


def _checkAndFillTokens(bonus, alwaysVisibleBonuses, bonuses):
    hasTman = False
    for tokenBonus in bonus:
        allTokens = tokenBonus.getTokens()
        for tID, _ in allTokens.iteritems():
            if getRecruitInfo(tID):
                hasTman = True
                break

        if hasTman:
            alwaysVisibleBonuses.append(tokenBonus)
        bonuses.append(tokenBonus)

    return hasTman


def _splitPremiumDays(days):
    available = (360, 180, 90, 30, 14, 7, 3, 2, 1)

    def nearest(array, value):
        index = 0
        for idx, i in enumerate(array):
            index = idx
            if value >= i:
                break

        return array[index]

    result = []
    while days > 0:
        near = nearest(available, days)
        days -= near
        result.append(near)

    return result
