# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_vehicles_selection_view.py
from typing import TYPE_CHECKING, Tuple
from collections import OrderedDict
from functools import partial
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui import GUI_NATIONS_ORDER_INDEX, GUI_NATIONS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.server_events.events_dispatcher import showBattleMattersMainView
from gui.shared.event_dispatcher import showOfferGiftVehiclePreview, showVehiclePreview
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from helpers import dependency
from nations import NONE_INDEX
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.game_control import ITankAcademyController, IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_vehicles_selection_tabs_model import TankAcademyVehiclesSelectionTabsModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_view_model import QuestViewModel, State
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy import tank_academy_vehicles_selection_view_model as ta_vm
from tank_academy.gui.impl.lobby.tank_academy.tank_academy_filter_popover_view import TankAcademyFilterPopoverView
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.popovers.filter_control_view_model import FilterControlViewModel
from tank_academy.gui.selectable_reward.selectable_reward_manager import TankAcademySelectableRewardManager
from tank_academy.gui.shared.event_dispatcher import showTankAcademyDelayedConfirmationDialog, showTankAcademyVehicleSelection
from sound_gui_manager import CommonSoundSpaceSettings
from tank_academy.gui.shared.bonus_packers import TankAcademyVehiclesBonusUIPacker
if TYPE_CHECKING:
    from account_helpers.offers.events_data import OfferEventData
_NATIONS_KEY_NAME = 'Nations'
_TYPES_KEY_NAME = 'Types'
_TYPES_ORDER = ('heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG')
_TYPES_ORDER_INDEX = dict(((vehicleType, index) for index, vehicleType in enumerate(_TYPES_ORDER)))

class Sounds(CONST_CONTAINER):
    SOUND_PLACE_HANGAR = 'STATE_hangar_place'
    STATE_TASKS_PREVIEW = 'STATE_hangar_place_tasks_preview'


PREVIEW_VEHICLE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SOUND_PLACE_HANGAR, entranceStates={Sounds.SOUND_PLACE_HANGAR: Sounds.STATE_TASKS_PREVIEW}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

def _getVehicleItem(vehicleDict):
    return vehicleDict['vehicle'].displayedItem


def _sortByNation(vehicleTuple):
    _, vehicleDict = vehicleTuple
    nation = _getVehicleItem(vehicleDict).nationName
    return GUI_NATIONS_ORDER_INDEX.get(nation, NONE_INDEX)


def _sortByType(vehicleTuple):
    _, vehicleDict = vehicleTuple
    vehicleType = _getVehicleItem(vehicleDict).type
    return _TYPES_ORDER_INDEX.get(vehicleType, len(_TYPES_ORDER_INDEX))


def _sortByName(vehicleTuple):
    _, vehicleDict = vehicleTuple
    return _getVehicleItem(vehicleDict).userName


def _isVehicleAlreadyAvailable(vehicle, unlocked):
    return vehicle.isInInventory if vehicle.isPremium else vehicle.intCD in unlocked


def _sortVehicles(vehicles):
    return sorted(vehicles.iteritems(), key=lambda item: (_sortByNation(item), _sortByType(item), _sortByName(item)))


class TankAcademyVehiclesSelectionView(ViewImpl):
    __slots__ = ('__selectableBonus', '__vehiclesByTabKey', '__filters', '__filterPopover', '__offerToken', '__offersByTabKey', '__selectedTabKey', '__questsByOfferToken')
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __itemsCache = dependency.descriptor(IItemsCache)
    __selectableRewardMgr = TankAcademySelectableRewardManager

    def __init__(self, offerToken):
        settings = ViewSettings(R.views.tank_academy.lobby.tank_academy.TankAcademyVehiclesSelectionView(), flags=ViewFlags.VIEW, model=ta_vm.TankAcademyVehiclesSelectionViewModel())
        self.__offerToken = offerToken
        self.__selectableBonus = None
        self.__offersByTabKey = OrderedDict()
        self.__vehiclesByTabKey = OrderedDict()
        self.__selectedTabKey = None
        self.__questsByOfferToken = {}
        self.__filterPopover = None
        self.__filters = {}
        self.__resetFilters(True)
        super(TankAcademyVehiclesSelectionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(TankAcademyVehiclesSelectionView, self).getViewModel()

    def createPopOverContent(self, event):
        if event.contentID == R.views.tank_academy.lobby.tank_academy.popovers.TankAcademyFilterPopoverView():
            self.__filterPopover = TankAcademyFilterPopoverView(self.__filters, self.onUpdateFilter)
            return self.__filterPopover
        return super(TankAcademyVehiclesSelectionView, self).createPopOverContent(event)

    @args2params(int)
    def onCompareVehicle(self, vehCD):
        self.__comparisonBasket.addVehicle(vehCD)

    @args2params(int)
    def onShowVehicle(self, vehCD):
        offer = self.__getSelectedOffer()
        vehicleDict = self.__getVehicles().get(vehCD)
        if offer is None or vehicleDict is None:
            return
        elif self.__selectableBonus is None:
            showVehiclePreview(vehCD, previewBackCb=partial(showTankAcademyVehicleSelection, self.__offerToken), previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW, isFromVehicleView=True, soundSpace=PREVIEW_VEHICLE_SOUND_SPACE, bottomPanelTextData={'uniqueVehicleTitle': text_styles.tutorial(backport.text(R.strings.tank_academy.vehiclesSelection.vehiclePreview.uniqueVehicleTitle())),
             'hideBuyBlock': True}, backBtnLabel=VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_BATTLEMATTERS, showCloseBtn=False)
            return
        else:
            giftID = vehicleDict['giftID']
            offerToken = offer.token
            vehiclesLevel = self.__getOfferTabKey(offer)[0]
            onConfirm = partial(showTankAcademyDelayedConfirmationDialog, vehicleDict['vehicle'].displayedItem, vehiclesLevel, partial(self.__onDialogConfirm, bonus=self.__selectableBonus, giftID=giftID, offerToken=offerToken))
            showOfferGiftVehiclePreview(offer.id, giftID, onConfirm, VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_BATTLEMATTERS, soundSpace=PREVIEW_VEHICLE_SOUND_SPACE, customCallbacks={'previewBackCb': partial(showTankAcademyVehicleSelection, self.__offerToken),
             'offerEndedCb': lambda : None}, showCloseBtn=False)
            return

    def onResetFilter(self):
        self.__resetFilters()

    def onUpdateFilter(self, filters=None):
        if filters:
            self.__filters = filters
        with self.viewModel.transaction() as tx:
            self.__updateFilterControls(tx.getTypes(), self.__filters[_TYPES_KEY_NAME])
            self.__updateFilterControls(tx.getNations(), self.__filters[_NATIONS_KEY_NAME])

    def _onLoading(self, *args, **kwargs):
        super(TankAcademyVehiclesSelectionView, self)._onLoading(*args, **kwargs)
        self._update()

    def _finalize(self):
        self.__filters = None
        self.__filterPopover = None
        self.__vehiclesByTabKey = None
        self.__offersByTabKey = None
        self.__selectedTabKey = None
        self.__questsByOfferToken = None
        self.__offerToken = None
        super(TankAcademyVehiclesSelectionView, self)._finalize()
        return

    def _update(self):
        self.__updateOffersData()
        expires = self.__tankAcademyController.getDelayedRewardExpirationTime()
        with self.viewModel.transaction() as tx:
            if self.__tankAcademyController.isFinished():
                tx.setEndDate(expires)
            vehicles = self.__getVehicles()
            tx.setTotalVehiclesCount(len(vehicles))
            self.__updateTabs(tx.getTabs())
            self.__updateFilterControls(tx.getTypes(), self.__filters[_TYPES_KEY_NAME])
            self.__updateFilterControls(tx.getNations(), self.__filters[_NATIONS_KEY_NAME])
            vehiclesVM = tx.getVehicles()
            self._updateVehicles(vehiclesVM)

    def _updateVehicles(self, vm):
        vm.clear()
        for _, vehicleDict in self.__getVehicles().iteritems():
            vehicleModel = TankAcademyVehiclesBonusUIPacker.pack(vehicleDict['vehicle'])[0]
            vm.addViewModel(vehicleModel)

        vm.invalidate()

    def _getEvents(self):
        return ((self.__tankAcademyController.onStateChanged, showBattleMattersMainView),
         (self.viewModel.onGoBack, showBattleMattersMainView),
         (self.viewModel.onCompareVehicle, self.onCompareVehicle),
         (self.viewModel.onShowVehicle, self.onShowVehicle),
         (self.viewModel.onResetFilter, self.onResetFilter),
         (self.viewModel.onSelectTab, self.__onSelectTab),
         (self.__offersProvider.onOffersUpdated, self._update))

    def __getVehicles(self):
        return self.__vehiclesByTabKey.get(self.__selectedTabKey, OrderedDict())

    @staticmethod
    def __updateFilterControls(arrayVM, values):
        arrayVM.clear()
        for filterName, filterValue in values.iteritems():
            currentControl = FilterControlViewModel()
            currentControl.setName(filterName)
            currentControl.setIsSelected(filterValue)
            arrayVM.addViewModel(currentControl)

        arrayVM.invalidate()

    def __resetFilters(self, init=False):
        self.__filters = {_NATIONS_KEY_NAME: OrderedDict(((nation, False) for nation in GUI_NATIONS)),
         _TYPES_KEY_NAME: OrderedDict(((t, False) for t in VEHICLE_TYPES_ORDER))}
        if self.__filterPopover and self.__filterPopover.viewStatus == ViewStatus.LOADED:
            self.__filterPopover.updateFilterFromOutside(self.__filters)
        elif not init:
            self.onUpdateFilter()

    def __onDialogConfirm(self, result, bonus, giftID, offerToken):
        if result and bonus is not None:
            self.__selectableRewardMgr.chooseReward(bonus, giftID=giftID, callback=partial(self.__showAwardView, offerToken=offerToken))
        return

    def __showAwardView(self, result, offerToken):
        if result and result.auxData:
            showTankAcademyVehicleSelection(offerToken, forceCreate=True)
            self.__tankAcademyController.showAwardView(questsData=None, clientCtx=result.auxData)
        return

    def __updateOffersData(self):
        self.__offersByTabKey = OrderedDict()
        self.__vehiclesByTabKey = OrderedDict()
        offers = [ offer for offer in self.__offersProvider.getAllOffers() if self.__tankAcademyController.isTAOfferToken(offer.token) ]
        offers.sort(key=self.__getOfferSortKey)
        unlocked = self.__itemsCache.items.stats.unlocks
        for offer in offers:
            tabKey = self.__getOfferTabKey(offer)
            level = tabKey[0]
            if not level:
                continue
            self.__offersByTabKey.setdefault(tabKey, []).append(offer)
            vehicles = self.__vehiclesByTabKey.setdefault(tabKey, OrderedDict())
            for gift in offer.getAllGifts():
                vehicleBonus = gift.bonus
                vehicle = vehicleBonus.displayedItem
                if _isVehicleAlreadyAvailable(vehicle, unlocked):
                    continue
                if vehicle.intCD in vehicles:
                    continue
                vehicles[vehicle.intCD] = {'vehicle': vehicleBonus,
                 'giftID': gift.id}

        for tabKey, vehicles in self.__vehiclesByTabKey.iteritems():
            self.__vehiclesByTabKey[tabKey] = OrderedDict(_sortVehicles(vehicles))

        self.__questsByOfferToken = self.__getQuestsByOfferToken()
        self.__selectedTabKey = self.__getInitialSelectedTabKey()
        selectedOffer = self.__getSelectedOffer()
        if selectedOffer is None or selectedOffer.token != self.__offerToken:
            self.__offerToken = self.__getSelectedOfferToken()
        self.__selectableBonus = self.__getSelectableBonusByOfferToken(self.__offerToken)
        if self.__selectableBonus is None:
            self.__offerToken = self.__getSelectedOfferToken()
            self.__selectableBonus = self.__getSelectableBonusByOfferToken(self.__offerToken)
        return

    def __getInitialSelectedTabKey(self):
        if self.__selectedTabKey in self.__offersByTabKey:
            return self.__selectedTabKey
        else:
            tabKey = self.__getTabKeyByOfferToken(self.__offerToken)
            if tabKey is not None:
                return tabKey
            tabKey = self.__getRecommendedInitialTabKey()
            return tabKey if tabKey is not None else first(self.__offersByTabKey.iterkeys())

    def __getTabKeyByOfferToken(self, offerToken):
        if offerToken is None:
            return
        else:
            for tabKey, offers in self.__offersByTabKey.iteritems():
                if any((offer.token == offerToken for offer in offers)):
                    return tabKey

            return

    def __getRecommendedInitialTabKey(self):
        if not self.__getObtainedTabKeys():
            return first(self.__offersByTabKey.iterkeys())
        else:
            tabKey = self.__getHighestUnobtainedTabKey()
            return tabKey if tabKey is not None else self.__getNextTabKeyAfterHighestObtained()

    def __getHighestUnobtainedTabKey(self):
        offerTokens = self.__tankAcademyController.getVehicleOfferTokensWithUnobtainedGifts()
        if not offerTokens:
            return None
        else:
            tabKeys = [ tabKey for tabKey, offers in self.__offersByTabKey.iteritems() if any((offer.token in offerTokens for offer in offers)) ]
            return max(tabKeys) if tabKeys else None

    def __getNextTabKeyAfterHighestObtained(self):
        tabKeys = self.__offersByTabKey.keys()
        if not tabKeys:
            return None
        else:
            obtainedTabKeys = self.__getObtainedTabKeys()
            if not obtainedTabKeys:
                return first(tabKeys)
            highestObtainedTabKey = max(obtainedTabKeys)
            return first((tabKey for tabKey in tabKeys if tabKey > highestObtainedTabKey), highestObtainedTabKey)

    def __getObtainedTabKeys(self):
        return [ tabKey for tabKey, offers in self.__offersByTabKey.iteritems() if any((self.__tankAcademyController.isOfferRewardObtained(offer.token) for offer in offers)) ]

    def __getSelectedOffer(self):
        offers = self.__offersByTabKey.get(self.__selectedTabKey, ())
        if self.__offerToken is not None:
            for offer in offers:
                if offer.token == self.__offerToken:
                    return offer

        return first(offers)

    def __getSelectedOfferToken(self):
        offers = self.__offersByTabKey.get(self.__selectedTabKey, [])
        for offer in offers:
            if self.__getSelectableBonusByOffer(offer) is not None:
                return offer.token

        offer = first(offers)
        return offer.token if offer is not None else None

    @classmethod
    def __getOfferTabKey(cls, offer):
        return (int(offer.properties.get('giftVehiclesLevel', 0)), cls.__isPremiumOffer(offer))

    @classmethod
    def __getOfferSortKey(cls, offer):
        level, isPremium = cls.__getOfferTabKey(offer)
        return (level, isPremium, offer.token)

    @staticmethod
    def __isPremiumOffer(offer):
        for gift in offer.getAllGifts():
            vehicle = gift.bonus.displayedItem
            if vehicle.isPremium:
                return True

        return False

    def __getSelectableBonusByOfferToken(self, offerToken):
        return None if offerToken is None else first(self.__selectableRewardMgr.getAvailableSelectableBonuses(lambda tokenID: tokenID == offerToken))

    def __getSelectableBonusByOffer(self, offer):
        return self.__getSelectableBonusByOfferToken(offer.token)

    def __isTabDone(self, offers):
        return all((self.__tankAcademyController.isOfferRewardObtained(offer.token) for offer in offers))

    def __getTabTokensCount(self, offers):
        result = 0
        for offer in offers:
            bonus = self.__getSelectableBonusByOffer(offer)
            if bonus is not None:
                result += self.__selectableRewardMgr.getRemainedChoices(bonus)

        return result

    def __updateTabs(self, vm):
        vm.clear()
        for tabKey, offers in self.__offersByTabKey.iteritems():
            level, isPremium = tabKey
            tab = TankAcademyVehiclesSelectionTabsModel()
            tab.setLevel(level)
            tab.setIsSelected(tabKey == self.__selectedTabKey)
            tab.setIsDone(self.__isTabDone(offers))
            tab.setIsPremium(isPremium)
            tab.setTokensCount(self.__getTabTokensCount(offers))
            self.__updateTabTasks(tab.getTasks(), offers)
            vm.addViewModel(tab)

        vm.invalidate()

    def __updateTabTasks(self, vm, offers):
        vm.clear()
        currentQuest = self.__tankAcademyController.getCurrentQuest()
        currentQuestNumber = currentQuest.getOrder() if currentQuest else None
        quests = OrderedDict()
        for offer in offers:
            for quest in self.__questsByOfferToken.get(offer.token, []):
                quests[quest.getOrder()] = quest

        for _, quest in quests.iteritems():
            vm.addViewModel(self.__createQuestViewModel(quest, currentQuestNumber))

        vm.invalidate()
        return

    def __getQuestsByOfferToken(self):
        result = {}
        for quest in self.__tankAcademyController.getTankAcademyQuests():
            for offerToken in quest.getVehicleOfferTokens():
                result.setdefault(offerToken, []).append(quest)

        return result

    def __createQuestViewModel(self, quest, currentQuestNumber):
        questModel = QuestViewModel()
        number = quest.getOrder()
        questModel.setNumber(number)
        questState = State.UNAVAILABLE
        if quest.isCompleted() and (currentQuestNumber is None or number < currentQuestNumber):
            questState = State.DONE
        elif number == currentQuestNumber:
            questState = State.INPROGRESS
        questModel.setState(questState)
        return questModel

    @args2params(int, bool)
    def __onSelectTab(self, level, isPremium):
        tabKey = (level, isPremium)
        if tabKey not in self.__offersByTabKey:
            return
        self.__selectedTabKey = tabKey
        self.__offerToken = self.__getSelectedOfferToken()
        self.__selectableBonus = self.__getSelectableBonusByOfferToken(self.__offerToken)
        self.__resetFilters(True)
        with self.viewModel.transaction() as tx:
            tx.setTotalVehiclesCount(len(self.__getVehicles()))
            self.__updateTabs(tx.getTabs())
            self.__updateFilterControls(tx.getTypes(), self.__filters[_TYPES_KEY_NAME])
            self.__updateFilterControls(tx.getNations(), self.__filters[_NATIONS_KEY_NAME])
            self._updateVehicles(tx.getVehicles())
