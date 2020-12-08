# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_vehicles_view.py
import itertools
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GAME, OnceOnlyHints
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_bonus_header_model import NewYearBonusHeaderModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_vehicle_slot_view_model import NewYearVehicleSlotViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_vehicles_view_model import NewYearVehiclesViewModel
from gui.impl.lobby.new_year.new_year_extra_slot_level_up_view import NewYearExtraSlotLevelUpWindow
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_helper import BONUS_ICONS, hasNewExtraSlotLevel, IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.formatters.icons import creditsBig, goldBig
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from items.components.ny_constants import VEH_BRANCH_EXTRA_SLOT_TOKEN
from new_year.ny_constants import SyncDataKeys, PERCENT, AnchorNames
from new_year.vehicle_branch import SetVehicleBranchProcessor, getRegularSlotBonusConfig, EMPTY_VEH_INV_ID, getInEventCooldown, getExtraSlotBonusesConfig, SetVehicleBranchSlotBonusProcessor
from ny_common.settings import NY_CONFIG_NAME, NYVehBranchConsts
from ny_common.VehBranchConfig import BRANCH_SLOT_TYPE
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from gui.impl.new_year.tooltips.new_year_vehicles_bonus_tooltip import NewYearVehiclesBonusTooltip
from gui.impl.new_year.sounds import NewYearSoundsManager
from uilogging.decorators import simpleLog, loggerTarget, loggerEntry
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
_BONUS_ORDER = ['xpFactor', 'freeXPFactor', 'tankmenXPFactor']

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


@loggerTarget(loggerCls=NYLogger, logKey=NY_LOG_KEYS.NY_VEHICLE_WINDOW)
class NewYearVehiclesView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, backCtx=None):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_vehicles_view.NewYearVehiclesView())
        settings.model = NewYearVehiclesViewModel()
        super(NewYearVehiclesView, self).__init__(settings)
        self.__backCtx = backCtx
        self.__notifier = None
        return

    @property
    def viewModel(self):
        return super(NewYearVehiclesView, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        return NewYearVehiclesBonusTooltip() if ctID == R.views.lobby.new_year.tooltips.new_year_vehicle_bonus.NewYearVehiclesBonus() else super(NewYearVehiclesView, self).createToolTipContent(event, ctID)

    @loggerEntry
    def _initialize(self):
        super(NewYearVehiclesView, self)._initialize()
        NewYearSoundsManager.setHangarFilteredState(True)
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onUnlockChanged,
         'tokens': self.__onTokensUpdate})
        self._nyController.onDataUpdated += self.__onDataUpdated
        self._nyController.onStateChanged += self.__onStateChanged
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onClearBtnClick += self.__onClearBtnClick
        self.viewModel.onSwitchExtraSlotBonus += self.__onSwitchExtraSlotBonus
        self.viewModel.onGoToChallengeQuests += self.__onGoToChallengeQuests
        self.viewModel.onSetIntroInProgress += self.__onSetIntroInProgress
        self.viewModel.onReadyToShow += self.__onReadyToShow
        with self.viewModel.transaction() as tx:
            self.__createVehiclesList(tx)
            self.__updateIntroStatus(tx)
            tx.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        self.__notifier = VehicleCooldownNotifier(self.__updateVehicleCooldown, self._nyController.getVehicleBranch().getVehicleSlots())
        self.__notifier.startNotification()

    def _finalize(self):
        NewYearSoundsManager.setHangarFilteredState(False)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onClearBtnClick -= self.__onClearBtnClick
        self.viewModel.onSwitchExtraSlotBonus -= self.__onSwitchExtraSlotBonus
        self.viewModel.onGoToChallengeQuests -= self.__onGoToChallengeQuests
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._nyController.onStateChanged -= self.__onStateChanged
        self._lobbyCtx.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.viewModel.onSetIntroInProgress -= self.__onSetIntroInProgress
        self.viewModel.onReadyToShow -= self.__onReadyToShow
        if self.__notifier:
            self.__notifier.stopNotification()
            self.__notifier.clear()
        self.__backCtx = None
        return

    @staticmethod
    def _tankNameToRClassName(name):
        return replaceHyphenToUnderscore(name.lower())

    @staticmethod
    def _getVehicleIcon(vehicleType):
        backPortImage = backport.image(R.images.gui.maps.icons.new_year.vehicles_view.icons.dyn(vehicleType)())
        return "<img src='{0}' vspace='-3'/>".format(backPortImage.replace('../', 'img://gui/'))

    def __createVehiclesList(self, model):
        slots = model.vehicleSlots.getItems()
        extraSlots = model.extraSlots.getItems()
        for vehicleSlot in self._nyController.getVehicleBranch().getVehicleSlots():
            vehicleSlotModel = self.__makeSlotViewModel(vehicleSlot)
            if vehicleSlotModel.getIsExtraSlot():
                extraSlots.addViewModel(vehicleSlotModel)
            slots.addViewModel(vehicleSlotModel)

        self.__updateBonuses(model)

    def __updateBonuses(self, model):
        bonuses = model.bonuses.getItems()
        bonuses.clear()
        for bonusType in _BONUS_ORDER:
            vehTypes = []
            vehBonusValues = []
            for vehType, (vehBonusType, vehBonusValue) in getRegularSlotBonusConfig().iteritems():
                if vehBonusType == bonusType:
                    vehTypes.append(replaceHyphenToUnderscore(vehType))
                    vehBonusValues.append(vehBonusValue)

            bonuses.addViewModel(self.__makeBonusViewModel(min(vehBonusValues), bonusType, vehTypes))

        bonuses.invalidate()

    def __updateVehiclesList(self):
        with self.viewModel.transaction() as tx:
            vehicleSlots = self._nyController.getVehicleBranch().getVehicleSlots()
            for slot in itertools.chain(tx.vehicleSlots.getItems(), tx.extraSlots.getItems()):
                self.__updateVehicleSlot(slot, vehicleSlots[slot.getSlotID()])

    def __updateVehicleCooldown(self):
        self.__updateVehiclesList()

    def __makeBonusViewModel(self, value, bonusType, vehicleTypes):
        bonus = NewYearBonusHeaderModel()
        bonus.setBonusType(bonusType)
        bonus.setBonusValue(value * PERCENT)
        if vehicleTypes:
            args = {}
            for vehicleType in vehicleTypes:
                if vehicleType is not None:
                    args[vehicleType] = self._getVehicleIcon(vehicleType)

            bonus.setDescription(backport.text(R.strings.ny.vehiclesView.bonuses.dyn(bonusType)(), **args))
        return bonus

    def __makeSlotViewModel(self, vehicleSlot):
        slot = NewYearVehicleSlotViewModel()
        self.__updateVehicleSlot(slot, vehicleSlot)
        slot.setSlotID(vehicleSlot.getSlotID())
        slot.setLevelStr(vehicleSlot.getLevelStr())
        if vehicleSlot.getSlotType() == BRANCH_SLOT_TYPE.EXTRA:
            slot.setIsExtraSlot(True)
            self.__createExtraSlotDropDown(slot.choiceBonusesDropDown)
            self.__updateExtraSlotBonusSelection(slot.choiceBonusesDropDown, vehicleSlot)
        return slot

    def __updateVehicleSlot(self, slot, vehicleSlot):
        vehicle = vehicleSlot.getVehicle()
        slot.setChangePriceString('')
        if vehicle is not None:
            self.__fillSlotByVehicle(slot, vehicle)
        slot.setIsPostEvent(self._nyController.isPostEvent())
        self.__fillSlotState(slot, vehicleSlot)
        return

    def __fillSlotByVehicle(self, slot, vehicle):
        nation = vehicle.name.split(':')[0]
        slot.setVehicleIcon(R.images.gui.maps.shop.vehicles.c_360x270.dyn(replaceHyphenToUnderscore(getNationLessName(vehicle.name)))())
        slot.setVehicleName(vehicle.shortUserName)
        slot.setNationIcon(R.images.gui.maps.icons.flags.c_362x362.dyn(nation)())
        slot.setSlotState(NewYearVehicleSlotViewModel.CHANGE_AVAILABLE)
        slot.setVehicleCD(vehicle.intCD)
        slot.setLevelIcon(R.images.gui.maps.icons.levels.dyn('tank_level_big_' + str(vehicle.level))())
        slot.setVehicleTypeIcon(R.images.gui.maps.icons.vehicleTypes.white.dyn(replaceHyphenToUnderscore(vehicle.type))())
        nySlot = self._nyController.getVehicleBranch().getSlotForVehicle(vehicle.invID)
        if nySlot is not None:
            bonusType, value = nySlot.getSlotBonus()
            slot.bonus.setBonusType(bonusType)
            slot.bonus.setBonusValue(value * PERCENT)
        return

    def __fillSlotState(self, slot, vehicleSlot):
        vehicle = vehicleSlot.getVehicle()
        cooldown = vehicleSlot.getCooldown()
        slot.setCooldown(cooldown if cooldown else 0)
        slot.setChangePriceString(self.__getChangePriceString(vehicleSlot, cooldown is not None))
        if vehicle is not None:
            state = NewYearVehicleSlotViewModel.CHANGE_AVAILABLE
            if vehicle.isInBattle:
                state = NewYearVehicleSlotViewModel.CHANGE_IN_BATTLE
            elif vehicle.isInUnit:
                state = NewYearVehicleSlotViewModel.CHANGE_IN_SQUAD
            elif cooldown is not None:
                state = NewYearVehicleSlotViewModel.CHANGE_TIME_OUT
            slot.setSlotState(state)
        elif cooldown is not None:
            slot.setSlotState(NewYearVehicleSlotViewModel.SET_COOLDOWN)
        else:
            slot.setSlotState(NewYearVehicleSlotViewModel.SET_AVAILABLE if vehicleSlot.isAvailable() else NewYearVehicleSlotViewModel.SLOT_DISABLED)
        return

    def __updateIntroStatus(self, model):
        cooldowns = getInEventCooldown()
        model.setIntroRegularCooldown(cooldowns[BRANCH_SLOT_TYPE.REGULAR])
        model.setIntroExtraCooldown(cooldowns[BRANCH_SLOT_TYPE.EXTRA])
        if self._nyController.isEnabled() and not self.__getIntroSetting(GAME.NY_VEHICLES_PROGRESS_ENTRY):
            model.setIsInProgressIntro(True)
            self.__setIntroSetting(GAME.NY_VEHICLES_PROGRESS_ENTRY)
        model.setIsPostEventIntro(self._nyController.isPostEvent())
        if self._nyController.isPostEvent() and not self.__getIntroSetting(GAME.NY_VEHICLES_POST_EVENT_ENTRY):
            model.setIsInProgressIntro(True)
            self.__setIntroSetting(GAME.NY_VEHICLES_POST_EVENT_ENTRY)

    @staticmethod
    def __createExtraSlotDropDown(dropDownModel):
        extraSlotBonusesByType = {bonusType:(choiceID, bonusType, bonusValue) for choiceID, (bonusType, bonusValue) in getExtraSlotBonusesConfig().iteritems()}
        for bonusTypeName in _BONUS_ORDER:
            if bonusTypeName not in extraSlotBonusesByType:
                continue
            choiceID, bonusType, bonusValue = extraSlotBonusesByType.get(bonusTypeName)
            dropDownModel.addItem(actionID=choiceID, labelStr=backport.text(R.strings.ny.totalBonusWidget.pbBonus()).format(int(bonusValue * PERCENT)), icon=BONUS_ICONS[bonusType])

    @staticmethod
    def __updateExtraSlotBonusSelection(dropDownModel, vehicleSlot):
        selectedIndex = None
        bonusID = vehicleSlot.getBonusChoiceID()
        for index, bonusModel in enumerate(dropDownModel.getItems()):
            if bonusModel.getId() == bonusID:
                selectedIndex = index
                break

        selectedIndices = dropDownModel.getSelectedIndices()
        if selectedIndex is not None and (not selectedIndices or selectedIndices[0] != selectedIndex):
            dropDownModel.getSelectedIndices().clear()
            dropDownModel.addSelectedIndex(selectedIndex)
        return

    def __getChangePriceString(self, vehicleSlot, isCooldown):
        if self._nyController.isPostEvent():
            if not isCooldown:
                changePriceString = backport.text(R.strings.ny.vehiclesView.vehicleSlot.changeForFree())
            else:
                if vehicleSlot.getVehicle() is not None:
                    changeText = R.strings.ny.vehiclesView.vehicleSlot.changeFor()
                else:
                    changeText = R.strings.ny.vehiclesView.vehicleSlot.setFor()
                changePrice = vehicleSlot.getChangePrice()
                currency = changePrice.getCurrency()
                if currency == Currency.CREDITS:
                    currencyImg = creditsBig()
                else:
                    currencyImg = goldBig()
                changePriceString = backport.text(changeText, price=' '.join([self.gui.systemLocale.getNumberFormat(changePrice.get(currency)), currencyImg]))
        else:
            changePriceString = backport.text(R.strings.ny.vehiclesView.vehicleSlot.change())
        return changePriceString

    def __setIntroSetting(self, introSetting):
        self._settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, {introSetting: True})

    def __getIntroSetting(self, introSetting):
        return self._settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, introSetting)

    def __onReadyToShow(self, _=None):
        if hasNewExtraSlotLevel():
            levelUpWindow = NewYearExtraSlotLevelUpWindow(parent=self.getParentWindow())
            levelUpWindow.load()

    @simpleLog(action=NY_LOG_ACTIONS.NY_VEHICLE_WINDOW_CLOSED)
    def __onCloseBtnClick(self, *_):
        self.__onClose()

    @decorators.process('newYear/delVehicleBranch')
    @simpleLog(action=NY_LOG_ACTIONS.NY_VEHICLE_WINDOW_DROP_VEHICLE)
    def __onClearBtnClick(self, args):
        slotID = int(args['slotID'])
        vehicleSlot = self._nyController.getVehicleBranch().getVehicleSlots()[slotID]
        if vehicleSlot.getSlotType() == BRANCH_SLOT_TYPE.EXTRA:
            self.__saveExtraSlotBonusHint()
        result = yield SetVehicleBranchProcessor(EMPTY_VEH_INV_ID, slotID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onClose(self):
        if self.__backCtx:
            self.__backCtx()
        self.destroyWindow()

    @decorators.process('newYear/changeExtraSlotBonus')
    def __onSwitchExtraSlotBonus(self, args):
        slotID, bonusID = int(args['slotID']), int(args['bonusID'])
        result = yield SetVehicleBranchSlotBonusProcessor(slotID, bonusID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onGoToChallengeQuests(self, _=None):
        self.__onClose()
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)

    def __onDataUpdated(self, keys):
        if SyncDataKeys.VEHICLE_BRANCH in keys or SyncDataKeys.VEHICLE_COOLDOWN in keys:
            self.__updateVehiclesList()
            self.__notifier.startNotification()
        if SyncDataKeys.VEHICLE_BONUS_CHOICES in keys:
            vehicleSlots = self._nyController.getVehicleBranch().getVehicleSlots()
            for slot in self.viewModel.extraSlots.getItems():
                self.__updateExtraSlotBonusSelection(slot.choiceBonusesDropDown, vehicleSlots[slot.getSlotID()])

    def __onStateChanged(self):
        if not self._nyController.isEnabled():
            self.destroyWindow()

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

    @simpleLog(action=NY_LOG_ACTIONS.NY_INTRO_VIEW_OPEN)
    def __onSetIntroInProgress(self):
        self.viewModel.setIsInProgressIntro(True)
        self.__saveExtraSlotBonusHint()

    def __saveExtraSlotBonusHint(self):
        self._settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.NY_VEHICLES_EXTRA_SLOT_BONUS_HINT: True})


class NewYearVehiclesWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, **kwargs):
        flags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(NewYearVehiclesWindow, self).__init__(flags, content=NewYearVehiclesView(**kwargs), layer=WindowLayer.TOP_WINDOW)
