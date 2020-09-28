# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_helpers.py
import itertools
import typing
import BigWorld
from frameworks.wulf import Array
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_tooltip_view import WtEventCarouselTooltipView
from gui.periodic_battles.models import CalendarStatusVO
from gui.ranked_battles.constants import PrimeTimeStatus, AlertTypes
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import checkForTags
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IGameEventController, IWalletController
from skeletons.gui.game_control import IEventLootBoxesController
from gui.ranked_battles.ranked_helpers import _AlertMessage
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, VehiclesBonus, GoodiesBonus
LOWER_LIMIT_OF_MEDIUM_LVL = 6
LOWER_LIMIT_OF_HIGH_LVL = 9
VEH_COMP_R_ID = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()
COLLECTION_COLOR_FORMATTER = {'colorTagOpen': '<font color="#CBAC77">',
 'colorTagClose': '</font>'}
HUNTER_ELEMENT_NAME = 'hunter_collection'
BOSS_ELEMENT_NAME = 'boss_collection'
TOOLTIP_VEHICLE_TYPES = {VEHICLE_EVENT_TYPE.EVENT_HUNTER: 'Hunter',
 VEHICLE_EVENT_TYPE.EVENT_BOSS: 'CommonBoss',
 VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS: 'specialBoss'}

def getTooltipVehicleType(intCD):
    itemsCache = dependency.instance(IItemsCache)
    vehicle = itemsCache.items.getItemByCD(intCD)
    return TOOLTIP_VEHICLE_TYPES.get(vehicle.eventType, '')


def getInfoPageURL():
    return GUI_SETTINGS.wtEvent.get('infoPage')


def getIntroVideoURL():
    return GUI_SETTINGS.wtEvent.get('introVideo')


def hasEnoughTickets():
    gameEventController = dependency.instance(IGameEventController)
    return gameEventController.hasEnoughTickets()


def getTicketName():
    gameEventController = dependency.instance(IGameEventController)
    return gameEventController.getWtEventTokenName()


def getTicketCount():
    gameEventController = dependency.instance(IGameEventController)
    return gameEventController.getWtEventTokensCount()


def getHunterFullUserName(role):
    return backport.text(R.strings.wt_event.tankman.hunter.dyn(role)())


def isBossVehicle(vehicle):
    return vehicle.eventType == VEHICLE_EVENT_TYPE.EVENT_BOSS


def getHunterDescr():
    gameEventController = dependency.instance(IGameEventController)
    return gameEventController.getHunterCD()


def getVehicleEquipmentsIDs(vehicleDescr):
    gameEventController = dependency.instance(IGameEventController)
    return gameEventController.getVehicleEquipmentIDs(vehicleDescr)


def isBossByDescr(vehicleDescr):
    return isBossByTags(vehicleDescr.type.tags)


def isBossByTags(tags):
    return checkForTags(tags, VEHICLE_EVENT_TYPE.EVENT_BOSS)


def isPlayerBoss():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    info = sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
    return isBossByTags(info.vehicleType.tags) if info and info.vehicleType else False


def isSpecialBossVehicle(vehicle):
    return vehicle.eventType == VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS


def isBossAndNotSpecialBossVehicle(vehicle):
    return vehicle.eventType == VEHICLE_EVENT_TYPE.EVENT_BOSS and not vehicle.eventType == VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def isBossCollectionElement(bonus, gameEventController=None):
    if bonus.getName() != 'groups':
        return None
    value = bonus.getValue()
    if not value or 'oneof' not in value[0]:
        return None
    bonusesCount = len(value[0]['oneof'][1])
    bossSize = gameEventController.getBossCollectionSize()
    hunterSize = gameEventController.getHunterCollectionSize()
    if bonusesCount == bossSize:
        return True
    else:
        return False if bonusesCount == hunterSize else None


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def getDaysLeftFormatted(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    if season is None:
        return ''
    else:
        currentCycleEnd = season.getCycleEndDate()
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))
        return backport.text(R.strings.wt_event.status.timeLeft.lessHour()) if timeLeft < time_utils.ONE_HOUR else backport.getTillTimeStringByRClass(timeLeft, R.strings.wt_event.status.timeLeft)


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def getLootBoxRewardTooltipData(rewardType, boxId, gameEventController=None):
    rTooltips = R.strings.wt_event.storageBoxes.tooltips
    if rewardType == 'vehicles':
        vehiclesList = _getVehiclesNames(boxId, gameEventController=gameEventController)
        return backport.createTooltipData(isWulfTooltip=True, specialArgs=[vehiclesList], specialAlias=TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX_VEHICLES)
    if rewardType == 'gold':
        goldAmount = _getGoldAmount(boxId, gameEventController=gameEventController)
        header = text_styles.gold(goldAmount) + icons.gold()
        body = backport.text(rTooltips.gold.body())
    else:
        header = text_styles.middleTitle(backport.text(rTooltips.dyn(rewardType).header()))
        innerText = ''
        if rewardType == 'collection':
            innerText = backport.text(rTooltips.collection.dyn(boxId)())
        elif rewardType == 'random':
            bonusesList = _getRandomBonusesNames(boxId, gameEventController=gameEventController)
            innerText = ', '.join(bonusesList)
        body = backport.text(rTooltips.dyn(rewardType).body(), innerText=text_styles.stats(innerText))
    return backport.createTooltipData(makeTooltip(header=header, body=body))


def getLootBoxButtonTooltipData():
    text = backport.text(R.strings.wt_event.storageBoxes.tooltips.button.unavailable())
    return backport.createTooltipData(makeTooltip(body=text))


def getNoLootBoxButtonTooltipData():
    text = backport.text(R.strings.wt_event.storageBoxes.tooltips.button.noBoxes())
    return backport.createTooltipData(makeTooltip(body=text))


def getLootBoxTypeByID(lootBoxID=None):
    lootBoxController = dependency.instance(IEventLootBoxesController)
    return lootBoxController.getLootBoxTypeByID(lootBoxID)


def hasWtEventQuest(completedQuestIDs):
    gameEventController = dependency.instance(IGameEventController)
    questPrefix = gameEventController.getWtEventQuestPrefix()
    for questId in completedQuestIDs:
        if questId.startswith(questPrefix):
            return True

    return False


def isWtEventQuest(questId):
    gameEventController = dependency.instance(IGameEventController)
    questPrefix = gameEventController.getWtEventQuestPrefix()
    return questId.startswith(questPrefix)


def getAlertStatusVO():
    alertMessage = _getAlertMessage()
    buttonLabelResID = R.strings.ranked_battles.alertMessage.button.moreInfo()
    if alertMessage.alertType == AlertTypes.PRIME:
        buttonLabelResID = R.strings.ranked_battles.alertMessage.button.changeServer()
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if alertMessage.alertType != AlertTypes.SEASON else None, buttonIcon='', buttonLabel=backport.text(buttonLabelResID), buttonVisible=alertMessage.buttonVisible, buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(alertMessage.alertStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=alertMessage.alertType != AlertTypes.SEASON, tooltip=TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO if alertMessage.alertType != AlertTypes.VEHICLE else None)


def backportTooltipDecorator(tooltipItemsName='_tooltipItems'):

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = _getTooltipDataByEvent(event, getattr(self, tooltipItemsName, {}))
                if tooltipData is None:
                    return
                if tooltipData.specialAlias == TOOLTIPS_CONSTANTS.WT_EVENT_BOSS_TICKET:
                    eventController = dependency.instance(IGameEventController)
                    ticketsCount = eventController.getWtEventTokensCount()
                    window = DecoratedTooltipWindow(WtEventCarouselTooltipView(ticketsCount), parent=self.getParentWindow(), useDecorator=False)
                    window.move(event.mouse.positionX, event.mouse.positionY)
                else:
                    window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def vehCompCreateToolTipContentDecorator(tooltipItemsName='_tooltipItems'):

    def decorator(func):

        def wrapper(self, event, contentID):
            if contentID == VEH_COMP_R_ID:
                tooltipData = _getTooltipDataByEvent(event, getattr(self, tooltipItemsName, {}))
                if tooltipData is None or tooltipData.specialAlias != VEH_COMP_R_ID:
                    return
                return VehicleCompensationTooltipContent(VEH_COMP_R_ID, viewModelClazz=LootBoxVehicleCompensationTooltipModel, **tooltipData.specialArgs)
            else:
                return func(self, event, contentID)

        return wrapper

    return decorator


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def fillLootBoxRewards(model, boxType, addIcons=False, gameEventController=None):
    model.setBoxType(boxType)
    rewards = gameEventController.getLootBoxRewards(boxType)
    for reward in rewards:
        if reward.startswith('gold'):
            _, amount = reward.split('_')
            model.setGold(int(amount))
        if reward == 'collection':
            model.setHasCollectionItem(True)
        if reward == 'vehicles':
            vehiclesList = _getVehiclesNames(boxType, gameEventController=gameEventController)
            model.setVehicles(', '.join(vehiclesList))
        if reward == 'random':
            bonuses = Array()
            if not addIcons:
                items = _getRandomBonusesTypes(boxType, gameEventController=gameEventController)
            else:
                items = _getRandomBonusesIcons(boxType, gameEventController=gameEventController)
            for item in items:
                if item is not None:
                    if addIcons and item.startswith('../maps/icons'):
                        bonuses.addString('img://gui' + item[2:])
                    else:
                        bonuses.addString(item)

            model.setRewards(bonuses)

    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache, wallet=IWalletController)
def fillStatsModel(statsModel, itemsCache=None, wallet=None):
    with statsModel.transaction() as model:
        model.setIsWalletAvailable(wallet.isAvailable)
        model.setGold(itemsCache.items.stats.gold)
        model.setCredits(itemsCache.items.stats.credits)
        model.setCrystal(itemsCache.items.stats.crystal)
        model.setFreeXP(itemsCache.items.stats.freeXP)
        model.setExchangeRate(itemsCache.items.shop.exchangeRate)


def stripLootBoxFromRewards(rewards, boxID, needToCheckCompensation=False):
    from gui.impl.auxiliary.rewards_helper import preparationRewardsCurrency
    preparationRewardsCurrency(rewards)
    if 'tokens' in rewards:
        tokenToRemoveName = 'lootBox:' + str(boxID)
        if tokenToRemoveName in rewards['tokens'].keys():
            rewards['tokens'].pop(tokenToRemoveName)
        if not rewards.get('tokens'):
            rewards.pop('tokens')
    if needToCheckCompensation:
        _addVehicleCompensationInRewards(rewards)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _addVehicleCompensationInRewards(rewards, itemsCache=None):
    if 'vehicles' not in rewards:
        return
    vehicles = rewards['vehicles']
    if isinstance(vehicles, list):
        vehiclesIter = itertools.chain.from_iterable((vehBonus.iteritems() for vehBonus in vehicles))
    else:
        vehiclesIter = vehicles.iteritems()
    for vehIntCD, vehBonus in vehiclesIter:
        vehicle = itemsCache.items.getItemByCD(vehIntCD)
        if vehicle.isInInventory:
            vehBonus['compensatedNumber'] = 1
            if 'customCompensation' in vehBonus:
                continue
            defaultPrice = vehicle.getBuyPrice().defPrice
            vehBonus['customCompensation'] = (defaultPrice.credits, defaultPrice.gold)


def _getTooltipDataByEvent(event, tooltipItems):
    tooltipId = event.getArgument('tooltipId')
    if tooltipId is None:
        return
    else:
        tooltipData = tooltipItems.get(tooltipId)
        return None if tooltipData is None else tooltipData


def _getAlertMessage():
    rAlertMessage = R.strings.wt_event.alertMessage
    eventController = dependency.instance(IGameEventController)
    connectionMgr = dependency.instance(IConnectionManager)
    hasAvailableServers = eventController.hasAvailablePrimeTimeServers()
    hasConfiguredServers = eventController.hasConfiguredPrimeTimeServers()
    status, _, _ = eventController.getPrimeTimeStatus()
    if hasAvailableServers:
        if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
            alertStr = backport.text(rAlertMessage.unsuitablePeriphery(), serverName=connectionMgr.serverUserNameShort)
            return _AlertMessage(AlertTypes.PRIME, alertStr, True)
        alertStr = backport.text(rAlertMessage.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
        return _AlertMessage(AlertTypes.PRIME, alertStr, True)
    currSeason = eventController.getCurrentSeason()
    if currSeason:
        if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
            alertStr = backport.text(rAlertMessage.unsuitablePeriphery(), serverName=connectionMgr.serverUserNameShort)
            return _AlertMessage(AlertTypes.PRIME, alertStr, hasConfiguredServers)
        timeLeft = eventController.getTimer()
        timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.ranked_battles.status.timeLeft)
        alertStr = backport.text(rAlertMessage.singleModeHalt() if connectionMgr.isStandalone() else rAlertMessage.allPeripheriesHalt(), time=timeLeftStr)
        return _AlertMessage(AlertTypes.PRIME, alertStr, False)
    return _AlertMessage(AlertTypes.SEASON, '', False)


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def _getGoldAmount(boxId, gameEventController=None):
    rewards = gameEventController.getLootBoxRewards(boxId)
    for reward in rewards:
        if reward.startswith('gold'):
            _, amount = reward.split('_')
            return amount


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def _getVehiclesNames(boxId, gameEventController=None):
    rewards = gameEventController.getLootBoxDetailedRewards(boxId)
    vehicleBonuses = rewards.get('vehicles', [])
    vehicles = []
    for vehicle in vehicleBonuses:
        for item, _ in vehicle.getVehicles():
            vehicles.append(item.shortUserName)

    return sorted(vehicles)


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def _getRandomBonusesNames(boxId, gameEventController=None):
    bonusesNames = []
    for bonusType in _getRandomBonusesTypes(boxId, gameEventController=gameEventController):
        rKey = R.strings.wt_event.storageBoxes.bonuses.dyn(bonusType)
        if rKey.exists():
            bonusesNames.append(backport.text(rKey()))

    return sorted(bonusesNames)


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def _getRandomBonusesTypes(boxId, gameEventController=None):
    rewards = gameEventController.getLootBoxDetailedRewards(boxId)
    randomBonuses = rewards.get('random', [])
    bonuses = set()
    for bonus in randomBonuses:
        bonusName = bonus.getName()
        bonuses.add(bonusName)
        if bonusName == 'goodies':
            if bonus.getDemountKits():
                bonuses.add('demountKit')

    if 'vehicles' in rewards and 'slots' in bonuses:
        bonuses.remove('slots')
    return bonuses


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def _getRandomBonusesIcons(boxId, gameEventController=None):
    rewards = gameEventController.getLootBoxDetailedRewards(boxId)
    randomBonuses = rewards.get('random', [])
    bonusesIcons = []
    for bonus in randomBonuses:
        bonusName = bonus.getName()
        if 'vehicles' in rewards and bonusName == 'slots':
            continue
        if bonusName in ('goodies', 'items', 'crewBooks'):
            for icon in bonus.getIconsList():
                bonusesIcons.append(icon)

        if bonusName == 'premium_plus':
            bonusesIcons.append(bonus.getDefaultIconBySize('small'))
        bonusesIcons.append(bonus.getIconBySize('small'))

    return set(bonusesIcons)


class VignetteHolder(object):
    __slots__ = ('__defaultIntensity',)
    _VIGNETTE_INTENSITY = 0.85

    def __init__(self):
        vignetteSettings = BigWorld.WGRenderSettings().getVignetteSettings()
        self.__defaultIntensity = vignetteSettings.w
        vignetteSettings.w = self._VIGNETTE_INTENSITY
        BigWorld.WGRenderSettings().setVignetteSettings(vignetteSettings)

    def __del__(self):
        vignetteSettings = BigWorld.WGRenderSettings().getVignetteSettings()
        vignetteSettings.w = self.__defaultIntensity
        BigWorld.WGRenderSettings().setVignetteSettings(vignetteSettings)
