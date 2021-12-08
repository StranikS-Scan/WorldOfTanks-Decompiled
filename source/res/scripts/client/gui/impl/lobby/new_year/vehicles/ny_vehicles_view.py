# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/vehicles/ny_vehicles_view.py
import itertools
import typing
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_bonus_info_model import NyBonusInfoModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_vehicle_slot_view_model import NyVehicleSlotViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_vehicles_view_model import NyVehiclesViewModel
from gui.impl.lobby.new_year.dialogs.dialogs import showSetVehicleHint
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED, formatRomanNumber
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.new_year.tooltips.new_year_vehicles_bonus_tooltip import NewYearVehiclesBonusTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.utils import decorators
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils, int2roman
from items.components.ny_constants import VEH_BRANCH_EXTRA_SLOT_TOKEN, NY_BRANCH_MIN_LEVEL, NY_BRANCH_MAX_LEVEL
from new_year.celebrity.celebrity_quests_helpers import getQuestCountForExtraSlot
from new_year.ny_constants import AnchorNames, PERCENT, SyncDataKeys, TANK_SLOT_BONUS_ORDER
from new_year.vehicle_branch import EMPTY_VEH_INV_ID, SetVehicleBranchProcessor, SetVehicleBranchSlotBonusProcessor, getSlotBonusByType, getSlotBonusChoicesConfig
from new_year.vehicle_branch_helpers import getVehicleChangePrice, hasNewVehicleLevel
from ny_common.settings import NYVehBranchConsts, NY_CONFIG_NAME
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyVehiclesInfoLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from new_year.vehicle_branch import VehicleSlot
    from gui.impl.gen.view_models.views.lobby.new_year.views.ny_bonus_dropdown_model import NyBonusDropdownModel

class VehicleCooldownNotifier(SimpleNotifier):
    _MAX_DELTA = time_utils.ONE_MINUTE

    def __init__(self, updateFunc, slots):
        super(VehicleCooldownNotifier, self).__init__(deltaFunc=self.__getNextDelta, updateFunc=updateFunc)
        self.__slots = slots

    def clear(self):
        self.__slots = None
        super(VehicleCooldownNotifier, self).clear()
        return

    def __getNextDelta(self):
        nextDeltaList = []
        for cooldown in (slot.getCooldown() for slot in self.__slots):
            if cooldown is not None:
                nextDeltaList.append(cooldown % self._MAX_DELTA or self._MAX_DELTA)

        return min(nextDeltaList) if nextDeltaList else 0


class NyVehiclesViewPresenter(HistorySubModelPresenter):
    __slots__ = ('__notifier', '__isOwnView')
    _navigationAlias = ViewAliases.VEHICLES_VIEW
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __nyController = dependency.descriptor(INewYearController)
    __infoFlowLogger = NyVehiclesInfoLogger()

    def __init__(self, viewModel, parentView, isOwnView=False):
        self.__notifier = None
        self.__isOwnView = isOwnView
        super(NyVehiclesViewPresenter, self).__init__(viewModel, parentView)
        return

    @property
    def viewModel(self):
        return super(NyVehiclesViewPresenter, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        return NewYearVehiclesBonusTooltip() if ctID == R.views.lobby.new_year.tooltips.new_year_vehicle_bonus.NewYearVehiclesBonus() else super(NyVehiclesViewPresenter, self).createToolTipContent(event, ctID)

    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            alias = VIEW_ALIAS.NY_SELECT_VEHICLE_POPOVER
            slotID = int(event.getArgument('slotID'))
            data = createPopOverData(alias, {'slotID': slotID})
            return BackportPopOverContent(popOverData=data)
        return super(NyVehiclesViewPresenter, self).createPopOverContent(event)

    def initialize(self, *args, **kwargs):
        super(NyVehiclesViewPresenter, self).initialize(*args, **kwargs)
        NewYearSoundsManager.setHangarFilteredState(True)
        self.__subscribe()
        self.__startNotifier()
        levelStr = backport.text(R.strings.ny.vehiclesView.levelsStr(), minLevel=formatRomanNumber(NY_BRANCH_MIN_LEVEL), maxLevel=formatRomanNumber(NY_BRANCH_MAX_LEVEL))
        with self.viewModel.transaction() as tx:
            tx.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
            tx.setIsPostEvent(self.__nyController.isPostEvent())
            tx.setLevelStr(levelStr)
            tx.setCurrentAtmosphereLvl(self.__itemsCache.items.festivity.getMaxLevel())
            self.__createVehiclesList(tx)
            self.__updateIntroStatus(tx)

    def finalize(self):
        self.__stopNotifier()
        self.__unsubscribe()
        NewYearSoundsManager.setHangarFilteredState(False)
        super(NyVehiclesViewPresenter, self).finalize()

    def _getInfoForHistory(self):
        return {}

    def __startNotifier(self):
        self.__notifier = VehicleCooldownNotifier(self.__updateVehicleCooldown, self.__nyController.getVehicleBranch().getVehicleSlots())
        self.__notifier.startNotification()

    def __stopNotifier(self):
        if self.__notifier:
            self.__notifier.stopNotification()
            self.__notifier.clear()

    def __subscribe(self):
        g_clientUpdateManager.addCallbacks({name:callback for name, callback in self.__iterCallbacks()})
        for event, handler in self.__iterEvents():
            event += handler

    def __unsubscribe(self):
        for event, handler in reversed(self.__iterEvents()):
            event -= handler

        g_clientUpdateManager.removeObjectCallbacks(self)

    def __iterEvents(self):
        events = [(self.__nyController.onDataUpdated, self.__onDataUpdated),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.viewModel.onClearBtnClick, self.__onClearBtnClick),
         (self.viewModel.onSwitchSlotBonus, self.__onSwitchSlotBonus),
         (self.viewModel.onGoToChallengeQuests, self.__onGoToChallengeQuests),
         (self.viewModel.onIntroClose, self.__onIntroClose),
         (self.viewModel.onOpenIntro, self.__onOpenIntro)]
        if self.__isOwnView:
            events.append((self.__nyController.onStateChanged, self.__onNyStateUpdated))
        return events

    def __iterCallbacks(self):
        return (('cache.vehsLock', self.__onUnlockChanged), ('tokens', self.__onTokensUpdate))

    def __updateIntroStatus(self, viewModel):
        isPostEvent = self.__nyController.isPostEvent()
        if self.__nyController.isEnabled() and not self.__getSetting(NewYearStorageKeys.NY_VEHICLES_PROGRESS_ENTRY):
            viewModel.setIsIntroOpened(True)
        elif isPostEvent and not self.__getSetting(NewYearStorageKeys.NY_VEHICLES_POST_EVENT_ENTRY):
            viewModel.setIsIntroOpened(True)
        else:
            self.__showLevelUpHintIfNeeded()

    def __showLevelUpHintIfNeeded(self):
        if hasNewVehicleLevel():
            showSetVehicleHint()
            self.__setSetting(NewYearStorageKeys.NY_VEHICLES_LEVEL_UP_ENTRY, self.__itemsCache.items.festivity.getMaxLevel())

    def __updateVehicleCooldown(self):
        self.__updateVehiclesList()

    def __updateVehiclesList(self):
        with self.viewModel.transaction() as tx:
            vehicleSlots = self.__nyController.getVehicleBranch().getVehicleSlots()
            for slot in itertools.chain(tx.getVehicleSlots(), tx.getExtraSlots()):
                self.__updateVehicleSlot(slot, vehicleSlots[slot.getSlotID()])

            tx.getVehicleSlots().invalidate()
            tx.getExtraSlots().invalidate()

    def __createVehiclesList(self, viewModel):
        slots = viewModel.getVehicleSlots()
        extraSlots = viewModel.getExtraSlots()
        slots.clear()
        extraSlots.clear()
        isPostEvent = self.__nyController.isPostEvent()
        for vehicleSlot in self.__nyController.getVehicleBranch().getVehicleSlots():
            if isPostEvent and not vehicleSlot.isAvailable():
                continue
            vehicleSlotModel = self.__makeSlotViewModel(vehicleSlot)
            (extraSlots if vehicleSlotModel.getIsExtraSlot() else slots).addViewModel(vehicleSlotModel)

        self.__updateBonuses(viewModel)

    def __makeSlotViewModel(self, vehicleSlot):
        slotVm = NyVehicleSlotViewModel()
        self.__updateVehicleSlot(slotVm, vehicleSlot)
        slotVm.setSlotID(vehicleSlot.getSlotID())
        slotVm.setLevelStr(vehicleSlot.getLevelStr())
        slotVm.setIsExtraSlot(vehicleSlot.getRestrictionType() == NYVehBranchConsts.TOKEN)
        self.__createSlotDropDown(slotVm.choiceBonusesDropDown)
        self.__updateSlotBonusSelection(slotVm.choiceBonusesDropDown, vehicleSlot)
        return slotVm

    def __updateVehicleSlot(self, slotVm, vehicleSlot):
        slotVm.setChangePrice(0)
        slotVm.setCurrency('')
        vehicle = vehicleSlot.getVehicle()
        if vehicle is not None:
            self.__fillSlotByVehicle(slotVm, vehicle)
        self.__fillSlotState(slotVm, vehicleSlot)
        return

    def __fillSlotByVehicle(self, slotVm, vehicle):
        nation = vehicle.name.split(':')[0]
        slotVm.setVehicleIcon(R.images.gui.maps.shop.vehicles.c_360x270.dyn(replaceHyphenToUnderscore(getNationLessName(vehicle.name)))())
        slotVm.setVehicleName(vehicle.shortUserName)
        slotVm.setNationIcon(R.images.gui.maps.icons.flags.c_362x362.dyn(nation)())
        slotVm.setVehicleLevel(int2roman(vehicle.level))
        slotVm.setVehicleType(vehicle.type)
        slotVm.setVehicleTypeIcon(R.images.gui.maps.icons.vehicleTypes.white.dyn(replaceHyphenToUnderscore(vehicle.type))())
        nySlot = self.__nyController.getVehicleBranch().getSlotForVehicle(vehicle.invID)
        if nySlot is not None:
            bonusType, value = nySlot.getSlotBonus()
            slotVm.bonus.setBonusType(bonusType)
            slotVm.bonus.setBonusValue(value * PERCENT)
        return

    def __fillSlotState(self, slotVm, vehicleSlot):
        vehicle = vehicleSlot.getVehicle()
        cooldown = vehicleSlot.getCooldown()
        slotVm.setCooldown(cooldown if cooldown else 0)
        changePrice, currency = self.__getChangePrice(cooldown is not None)
        slotVm.setChangePrice(changePrice)
        slotVm.setCurrency(currency)
        if vehicle is not None:
            state = NyVehicleSlotViewModel.CHANGE_AVAILABLE
            if vehicle.isInBattle:
                state = NyVehicleSlotViewModel.CHANGE_IN_BATTLE
            elif vehicle.isInUnit:
                state = NyVehicleSlotViewModel.CHANGE_IN_SQUAD
            elif cooldown is not None:
                state = NyVehicleSlotViewModel.CHANGE_TIME_OUT
            slotVm.setSlotState(state)
        elif cooldown is not None:
            slotVm.setSlotState(NyVehicleSlotViewModel.SET_COOLDOWN)
        else:
            slotVm.setSlotState(NyVehicleSlotViewModel.SET_AVAILABLE if vehicleSlot.isAvailable() else NyVehicleSlotViewModel.SLOT_DISABLED)
        restrictionType = vehicleSlot.getRestrictionType()
        if not vehicleSlot.isAvailable():
            if restrictionType == NYVehBranchConsts.LEVEL:
                slotVm.setUnlockSlotAtmosphereLevel(vehicleSlot.getLevel())
            elif restrictionType == NYVehBranchConsts.TOKEN:
                slotVm.setUnlockExtraSlotTaskCount(getQuestCountForExtraSlot())
        return

    def __updateBonuses(self, viewModel):
        bonuses = viewModel.bonuses.getItems()
        bonuses.clear()
        for bonusType in TANK_SLOT_BONUS_ORDER:
            bonusValue = getSlotBonusByType(bonusType)
            if bonusValue:
                bonuses.addViewModel(self.__createBonusViewModel(bonusType, bonusValue))

        bonuses.invalidate()

    @staticmethod
    def __createBonusViewModel(bonusType, bonusValue):
        bonus = NyBonusInfoModel()
        bonus.setBonusType(bonusType)
        bonus.setBonusValue(bonusValue)
        bonus.setLabel(backport.text(R.strings.ny.vehiclesView.bonuses.dyn(bonusType)()))
        return bonus

    @staticmethod
    def __createSlotDropDown(dropDownModel):
        slotBonusesByType = {bonusType:(choiceID, bonusType, bonusValue) for choiceID, (bonusType, bonusValue) in getSlotBonusChoicesConfig().iteritems()}
        dropItems = dropDownModel.getItems()
        for bonusTypeName in TANK_SLOT_BONUS_ORDER:
            if bonusTypeName not in slotBonusesByType:
                continue
            choiceID, bonusType, bonusValue = slotBonusesByType.get(bonusTypeName)
            bonusInfoModel = NyBonusInfoModel()
            bonusInfoModel.setId(choiceID)
            bonusInfoModel.setBonusType(bonusType)
            bonusInfoModel.setBonusValue(int(bonusValue * PERCENT))
            bonusInfoModel.setLabel(backport.text(R.strings.ny.vehiclesView.bonuses.dyn(bonusType)()))
            dropItems.addViewModel(bonusInfoModel)

        dropItems.invalidate()

    @staticmethod
    def __updateSlotBonusSelection(dropDownModel, vehicleSlot):
        selectedIndex = None
        bonusID = vehicleSlot.getBonusChoiceID()
        for index, bonusModel in enumerate(dropDownModel.getItems()):
            if bonusModel.getId() == bonusID:
                selectedIndex = index
                break

        if selectedIndex is not None and dropDownModel.getSelectedIdx() != selectedIndex:
            dropDownModel.setSelectedIdx(selectedIndex)
        return

    def __getChangePrice(self, isCooldown):
        if self.__nyController.isPostEvent() and isCooldown:
            changePrice = getVehicleChangePrice()
            currency = changePrice.getCurrency()
            return (changePrice.get(currency), currency)

    def __onOpenIntro(self):
        if self.__nyController.isPostEvent():
            self.viewModel.setIsIntroOpened(True)
        elif self.__isOwnView:
            self.__infoFlowLogger.logInfoClick()
            NewYearNavigation.showInfoView(previousViewAlias=ViewAliases.VEHICLES_VIEW)
            self.parentView.destroyWindow()
        else:
            self.__infoFlowLogger.logInfoClick()
            NewYearNavigation.showInfoView()

    def __onIntroClose(self):
        self.viewModel.setIsIntroOpened(False)
        if self.__nyController.isPostEvent():
            self.__setSetting(NewYearStorageKeys.NY_VEHICLES_POST_EVENT_ENTRY, True)
        else:
            self.__setSetting(NewYearStorageKeys.NY_VEHICLES_PROGRESS_ENTRY, True)
        self.__showLevelUpHintIfNeeded()

    @decorators.process('newYear/delVehicleBranch')
    def __onClearBtnClick(self, args):
        slotID = int(args['slotID'])
        result = yield SetVehicleBranchProcessor(EMPTY_VEH_INV_ID, slotID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('newYear/changeExtraSlotBonus')
    def __onSwitchSlotBonus(self, args):
        slotID, bonusID = int(args['slotID']), int(args['bonusID'])
        result = yield SetVehicleBranchSlotBonusProcessor(slotID, bonusID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onGoToChallengeQuests(self):
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)
        if self.__isOwnView:
            self.parentView.destroyWindow()

    def __onDataUpdated(self, keys):
        if SyncDataKeys.VEHICLE_BRANCH in keys or SyncDataKeys.VEHICLE_COOLDOWN in keys:
            self.__updateVehiclesList()
            self.__notifier.startNotification()
        if SyncDataKeys.VEHICLE_BONUS_CHOICES in keys:
            with self.viewModel.transaction() as tx:
                vehicleSlots = self.__nyController.getVehicleBranch().getVehicleSlots()
                for slot in itertools.chain(tx.getVehicleSlots(), tx.getExtraSlots()):
                    self.__updateSlotBonusSelection(slot.choiceBonusesDropDown, vehicleSlots[slot.getSlotID()])

                tx.getVehicleSlots().invalidate()
                tx.getExtraSlots().invalidate()

    def __onNyStateUpdated(self):
        if not self.__nyController.isEnabled():
            self.parentView.destroyWindow()

    def __onUnlockChanged(self, *_):
        self.__updateVehiclesList()

    def __onTokensUpdate(self, diff):
        if VEH_BRANCH_EXTRA_SLOT_TOKEN in diff:
            self.__updateVehiclesList()

    def __onServerSettingsChanged(self, diff):
        if NY_CONFIG_NAME in diff and NYVehBranchConsts.CONFIG_NAME in diff[NY_CONFIG_NAME]:
            with self.viewModel.transaction() as tx:
                self.__updateVehiclesList()
                self.__updateBonuses(tx)

    def __setSetting(self, introSetting, value):
        self.__settingsCore.serverSettings.saveInNewYearStorage({introSetting: value})

    def __getSetting(self, introSetting):
        return self.__settingsCore.serverSettings.getNewYearStorage().get(introSetting, None)


class NyVehiclesView(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.NyVehiclesView())
        settings.model = NyVehiclesViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__presenter = None
        self.__backCallback = kwargs.get('backCallback')
        super(NyVehiclesView, self).__init__(settings, *args, **kwargs)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return self.__presenter.createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        return self.__presenter.createPopOverContent(event) or super(NyVehiclesView, self).createPopOverContent(event)

    def _onLoading(self, *args, **kwargs):
        self.__presenter = NyVehiclesViewPresenter(self.getViewModel(), self, isOwnView=True)
        self.__presenter.initialize()
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        if self.__presenter is not None:
            self.__presenter.finalize()
        if self.__backCallback is not None:
            self.__backCallback()
        return

    def __onCloseBtnClick(self):
        self.destroyWindow()


class NyVehiclesWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        flags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(NyVehiclesWindow, self).__init__(flags, content=NyVehiclesView(*args, **kwargs), layer=WindowLayer.TOP_WINDOW)
