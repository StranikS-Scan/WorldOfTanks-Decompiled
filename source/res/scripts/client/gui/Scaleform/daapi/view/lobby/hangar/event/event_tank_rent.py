# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_tank_rent.py
import logging
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.meta.EventTankRentMeta import EventTankRentMeta
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl import backport
from gui.shop import showBuyGoldForBundle
from gui.server_events.bonuses import BattleTokensBonus
from gui.server_events.events_dispatcher import showEventMissions
from gui.server_events.awards_formatters import AWARDS_SIZES, getEventShopConfirmFormatter, formatShopConfirmBonus
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from helpers import dependency
from items import vehicles
from items.components.c11n_constants import SeasonType
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_GIFT_BONUS_NAME = 'battleToken'

class EventTankRent(EventTankRentMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    _PROMOTION_DELAY = 0.5

    def __init__(self):
        super(EventTankRent, self).__init__()
        self._vehTypeCompDescr = None
        self.__isNavigationEnabled = True
        self.__promotePreviewVehicleCallback = None
        self.__selectedVehicleEntityId = None
        return

    def onToQuestsClick(self):
        forceSelectedQuestID = None
        unlockToken = self.gameEventController.getVehiclesController().getUnlockTokenFor(self._vehTypeCompDescr)
        if unlockToken:
            item = self.gameEventController.getMissionsController().getItemWithBonusToken(unlockToken)
            if item is not None:
                forceSelectedQuestID = item.getQuest().getID()
        showEventMissions(forceSelectedQuestID=forceSelectedQuestID)
        return

    def onEventRentClick(self):
        vehTypeCompDescr = self._vehTypeCompDescr
        currency, price = self._getRentPrice(vehTypeCompDescr)
        if price is None:
            return
        else:
            stats = self.itemsCache.items.stats
            curAmount = stats.money.get(currency, 0)
            isGold = currency == CURRENCIES_CONSTANTS.GOLD
            notEnough = curAmount < price and isGold
            if notEnough:
                showBuyGoldForBundle(price, {})
                return
            bonuses = self.__getQuestBonuses(vehTypeCompDescr)
            if not bonuses:
                return
            _, nationIdx, innationIdx = vehicles.parseIntCompactDescr(vehTypeCompDescr)
            vehName = vehicles.VehicleDescr(typeID=(nationIdx, innationIdx)).type.userString
            formattedBonuses = getEventShopConfirmFormatter().format(bonuses)
            rewards = [ formatShopConfirmBonus(bonus) for bonus in formattedBonuses ]
            unlockToken = self.gameEventController.getVehiclesController().getUnlockTokenFor(vehTypeCompDescr)
            giftBonus = BattleTokensBonus(unlockToken, {unlockToken: {}})
            formattedGiftBonus = getEventShopConfirmFormatter().format([giftBonus])
            gift = formatShopConfirmBonus(formattedGiftBonus[0])
            gift['label'] = vehName
            conversionDate = backport.getShortDateFormat(self.eventsCache.getEventFinishTime())
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_RENT_CONFIRMATION), ctx={'title': backport.text(R.strings.event.shop.rentTank.title()),
             'descr': backport.text(R.strings.event.shop.rentTank.descr()),
             'rewards': rewards,
             'giftTitle': backport.text(R.strings.event.shop.rentTank.giftTitle(), vehName=vehName),
             'giftDescr': backport.text(R.strings.event.shop.rentTank.giftDescr(), date=conversionDate, vehName=vehName),
             'gift': gift,
             'currency': currency,
             'price': price,
             'vehTypeCompDescr': vehTypeCompDescr}), EVENT_BUS_SCOPE.LOBBY)
            return

    def _populate(self):
        super(EventTankRent, self)._populate()
        self.__updateVehicle()
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)

    def _dispose(self):
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onInventoryChanged
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        if self.__promotePreviewVehicleCallback is not None:
            BigWorld.cancelCallback(self.__promotePreviewVehicleCallback)
            self.__promotePreviewVehicleCallback = None
        super(EventTankRent, self)._dispose()
        return

    def _getRentPrice(self, vehTypeCompDescr):
        vehiclesForRent = self.gameEventController.getVehiclesController().getVehiclesForRent()
        info = vehiclesForRent.get(vehTypeCompDescr, {})
        return (info.get('currency', None), info.get('price', None))

    def __updateVehicle(self):
        if not g_currentPreviewVehicle.isPresent():
            self.as_setVisibleS(False)
            return
        else:
            vehTypeCompDescr = g_currentPreviewVehicle.item.intCD
            vehicle = self.itemsCache.items.getItemByCD(vehTypeCompDescr)
            if vehicle.isInInventory and vehicle.isOnlyForEventBattles:
                g_currentVehicle.selectEventVehicle(vehicle.invID)
                self.as_setVisibleS(False)
                return
            price = self._getRentPrice(vehTypeCompDescr)
            if price is None:
                self.as_setVisibleS(False)
                return
            data = {'description': backport.text(R.strings.event.hangar.eventTankRent.description()),
             'cost': str(price[1]),
             'specialArgs': [vehTypeCompDescr, str(price[1])],
             'specialAlias': TOOLTIPS_CONSTANTS.EVENT_TANK_RENT_INFO,
             'isSpecial': True,
             'rewardText': backport.text(R.strings.event.hangar.eventTankRent.bonuses.label())}
            self.as_setVisibleS(True)
            self.as_setRentDataS(data)
            self._vehTypeCompDescr = vehTypeCompDescr
            vEntity = g_currentPreviewVehicle.hangarSpace.getVehicleEntity()
            self.__selectedVehicleEntityId = vEntity.id if vEntity is not None else None
            return

    def __promotePreviewVehicleToCurrent(self):
        self.__promotePreviewVehicleCallback = None
        if not g_currentPreviewVehicle.isPresent():
            return
        else:
            vehTypeCompDescr = g_currentPreviewVehicle.item.intCD
            vehicle = self.itemsCache.items.getItemByCD(vehTypeCompDescr)
            if vehicle.isInInventory and vehicle.isOnlyForEventBattles:
                g_currentVehicle.selectEventVehicle(vehicle.invID)
            return

    def __onVehicleChanged(self):
        self.__updateVehicle()

    def __onInventoryChanged(self):
        if self.__promotePreviewVehicleCallback is None:
            self.__promotePreviewVehicleCallback = BigWorld.callback(self._PROMOTION_DELAY, self.__promotePreviewVehicleToCurrent)
        return

    def __getShortBonusesData(self, formattedBonuses):
        bonuses = []
        for bonus in formattedBonuses:
            shortData = {'name': bonus.userName,
             'label': bonus.getFormattedLabel(),
             'imgSource': bonus.getImage(AWARDS_SIZES.SMALL)}
            bonuses.append(shortData)

        return bonuses

    def __getQuestBonuses(self, vehTypeCompDescr):
        quest = self.gameEventController.getVehiclesController().getRentBonusQuest(vehTypeCompDescr)
        return quest.getBonuses() if quest else None

    def __onVehicleLoading(self, ctxEvent):
        isVehicleLoadingStarted = ctxEvent.ctx['started']
        if isVehicleLoadingStarted:
            _logger.warning('Too early VEHICLE_LOADING handler call.')
            return
        elif self._vehTypeCompDescr is None or ctxEvent.ctx['intCD'] != self._vehTypeCompDescr:
            return
        elif self.__selectedVehicleEntityId is None or ctxEvent.ctx['vEntityId'] != self.__selectedVehicleEntityId:
            return
        else:
            self.__onVehicleLoaded()
            return

    def __onVehicleLoaded(self):
        if not g_currentPreviewVehicle.item:
            return
        outfit = g_currentPreviewVehicle.item.getOutfit(SeasonType.EVENT)
        g_currentPreviewVehicle.hangarSpace.updateVehicleOutfit(outfit)
