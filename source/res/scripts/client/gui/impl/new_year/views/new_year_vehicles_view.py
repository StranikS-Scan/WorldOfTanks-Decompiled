# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_vehicles_view.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GAME
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_bonus_header_model import NewYearBonusHeaderModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_vehicle_slot_view_model import NewYearVehicleSlotViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_vehicles_view_model import NewYearVehiclesViewModel
from gui.impl.pub import ViewImpl
from gui.shared.formatters.icons import creditsBig, goldBig
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import int2roman, dependency, time_utils
from new_year.ny_constants import SyncDataKeys
from new_year.vehicle_branch import SetVehicleBranchProcessor, getBonusByVehicle, getVehicleBonusConfig, EMPTY_VEH_INV_ID, getInEventCooldown
from ny_common.settings import NY_CONFIG_NAME, NYVehBranchConsts
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from gui.impl.new_year.tooltips.new_year_vehicles_bonus_tooltip import NewYearVehiclesBonusTooltip
from gui.impl.new_year.sounds import NewYearSoundsManager
_PERCENT = 100
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


class NewYearVehiclesView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    __slots__ = ('__notifier', '__backCtx')

    def __init__(self, layoutID, backCtx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.TOP_WINDOW_VIEW
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

    def _initialize(self):
        super(NewYearVehiclesView, self)._initialize()
        NewYearSoundsManager.setHangarFilteredState(True)
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onUnlockChanged})
        self._nyController.onDataUpdated += self.__onDataUpdated
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onClearBtnClick += self.__onClearBtnClick
        with self.viewModel.transaction() as tx:
            self.__createVehiclesList(tx)
            self.__updateIntroStatus(tx)
        self.__notifier = VehicleCooldownNotifier(self.__updateVehicleCooldown, self._nyController.getVehicleBranch().getVehicleSlots())
        self.__notifier.startNotification()

    def _finalize(self):
        NewYearSoundsManager.setHangarFilteredState(False)
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onClearBtnClick -= self.__onClearBtnClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._lobbyCtx.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
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
        return "<img src='{0}'/>".format(backPortImage.replace('../', 'img://gui/'))

    def __createVehiclesList(self, model):
        slots = model.vehicleSlots.getItems()
        for vehicleSlot in self._nyController.getVehicleBranch().getVehicleSlots():
            slots.addViewModel(self.__makeSlotViewModel(vehicleSlot))

        self.__updateBonuses(model)

    def __updateBonuses(self, model):
        bonuses = model.bonuses.getItems()
        bonuses.clear()
        for bonusType in _BONUS_ORDER:
            vehTypes = []
            vehBonusValues = []
            for vehType, (vehBonusType, vehBonusValue) in getVehicleBonusConfig().iteritems():
                if vehBonusType == bonusType:
                    vehTypes.append(replaceHyphenToUnderscore(vehType))
                    vehBonusValues.append(vehBonusValue)

            bonuses.addViewModel(self.__makeBonusViewModel(min(vehBonusValues), bonusType, vehTypes))

        bonuses.invalidate()

    def __updateVehiclesList(self):
        with self.viewModel.transaction() as tx:
            vehicleSlots = self._nyController.getVehicleBranch().getVehicleSlots()
            for slot in tx.vehicleSlots.getItems():
                self.__updateVehicleSlot(slot, vehicleSlots[slot.getSlotID()])

    def __updateVehicleCooldown(self):
        self.__updateVehiclesList()

    def __makeBonusViewModel(self, value, bonusType, vehicleTypes):
        bonus = NewYearBonusHeaderModel()
        bonus.setBonusType(bonusType)
        bonus.setBonusValue(value * _PERCENT)
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
        slot.setLevelStr(int2roman(vehicleSlot.getVehicleLvl()))
        return slot

    def __updateVehicleSlot(self, slot, vehicleSlot):
        vehicle = vehicleSlot.getVehicle()
        slot.setChangePriceString('')
        slot.setVehicleIcon(R.invalid())
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
        slot.setVehicleTypeIcon(R.images.gui.maps.icons.new_year.vehicles_view.icons.dyn(replaceHyphenToUnderscore(vehicle.type))())
        bonusType, value = getBonusByVehicle(vehicle)
        slot.bonus.setBonusType(bonusType)
        slot.bonus.setBonusValue(value * _PERCENT)

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
        model.setIntroCooldown(getInEventCooldown())
        if self._nyController.isEnabled() and not self.__getIntroSetting(GAME.NY_VEHICLES_PROGRESS_ENTRY):
            model.setIsInProgressIntro(True)
            self.__setIntroSetting(GAME.NY_VEHICLES_PROGRESS_ENTRY)
        model.setIsPostEventIntro(self._nyController.isPostEvent())
        if self._nyController.isPostEvent() and not self.__getIntroSetting(GAME.NY_VEHICLES_POST_EVENT_ENTRY):
            model.setIsInProgressIntro(True)
            self.__setIntroSetting(GAME.NY_VEHICLES_POST_EVENT_ENTRY)

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

    def __onCloseBtnClick(self, *_):
        self.__onClose()

    @decorators.process('newYear/delVehicleBranch')
    def __onClearBtnClick(self, args):
        slotID = int(args['slotID'])
        result = yield SetVehicleBranchProcessor(EMPTY_VEH_INV_ID, slotID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onClose(self):
        if self.__backCtx:
            self.__backCtx()
        self.destroyWindow()

    def __onDataUpdated(self, keys):
        if SyncDataKeys.VEHICLE_BRANCH in keys or SyncDataKeys.VEHICLE_COOLDOWN in keys:
            self.__updateVehiclesList()
            self.__notifier.startNotification()

    def __onUnlockChanged(self, *_):
        self.__updateVehiclesList()

    def __onServerSettingsChanged(self, diff):
        if NY_CONFIG_NAME in diff and NYVehBranchConsts.CONFIG_NAME in diff[NY_CONFIG_NAME]:
            with self.viewModel.transaction() as tx:
                self.__updateVehiclesList()
                self.__updateBonuses(tx)
