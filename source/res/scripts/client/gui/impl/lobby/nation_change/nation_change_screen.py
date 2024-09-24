# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/nation_change/nation_change_screen.py
import SoundGroups
import WWISE
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED, AccountSettings
from frameworks.wulf import ViewSettings
from frameworks.wulf import ViewStatus
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_device_model import NationChangeDeviceModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_screen_model import NationChangeScreenModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_shell_model import NationChangeShellModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_supply_model import NationChangeSupplyModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_tankman_model import NationChangeTankmanModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_tank_setup_model import NationChangeTankSetupModel
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName, sortCrew
from gui.shared.gui_items.processors.common import VehicleChangeNation
from gui.shared.utils import decorators
from gui.shared.utils.functions import getVehTypeIconName
from helpers import int2roman
from helpers.dependency import descriptor
from helpers.i18n import convert
from helpers.server_settings import serverSettingsChangeListener
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.tankmen import getSkillsConfig
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from post_progression_common import SERVER_SETTINGS_KEY, SWITCH_LAYOUT_CAPACITY
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class NationChangeScreen(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __appLoader = descriptor(IAppLoader)
    _DOG_SOUND = 'rudy'
    _HANGAR_SOUND_FILTERED_STATE_NAME = 'STATE_hangar_filtered'
    _HANGAR_SOUND_FILTERED_STATE_ON = 'STATE_hangar_filtered_on'
    _HANGAR_SOUND_FILTERED_STATE_OFF = 'STATE_hangar_filtered_off'
    __LAYOUTS_IN_SETUP = 4
    __slots__ = ('__currentVehicle', '__targetVehicle', '__icons')

    def __init__(self, viewKey, ctx=None):
        settings = ViewSettings(viewKey)
        settings.model = NationChangeScreenModel()
        super(NationChangeScreen, self).__init__(settings)
        vehicle = self.__itemsCache.items.getItemByCD(ctx.get('vehicleCD', None))
        if vehicle.activeInNationGroup:
            self.__currentVehicle = vehicle
            self.__targetVehicle = self.__itemsCache.items.getItemByCD(iterVehTypeCDsInNationGroup(vehicle.intCD).next())
        else:
            self.__currentVehicle = self.__itemsCache.items.getItemByCD(iterVehTypeCDsInNationGroup(vehicle.intCD).next())
            self.__targetVehicle = vehicle
        self.__icons = R.images.gui.maps.icons
        return

    @property
    def viewModel(self):
        return super(NationChangeScreen, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if not tooltipId:
                return
            if tooltipId == TOOLTIPS_CONSTANTS.TANKMAN:
                toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
                args = (int(event.getArgument('intCD')),)
                toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.TANKMAN, args, event.mouse.positionX, event.mouse.positionY, self.getParentWindow())
                return TOOLTIPS_CONSTANTS.TANKMAN
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            return window
        else:
            return super(NationChangeScreen, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(NationChangeScreen, self)._initialize()
        with self.viewModel.transaction() as vm:
            vm.setCurrentTankLvl(int2roman(self.__currentVehicle.level))
            vm.setTargetTankLvl(int2roman(self.__targetVehicle.level))
            vm.setCurrentTankType(getVehTypeIconName(self.__currentVehicle.type, self.__currentVehicle.isElite))
            vm.setTargetTankType(getVehTypeIconName(self.__targetVehicle.type, self.__targetVehicle.isElite))
            vm.setCurrenTankName(self.__currentVehicle.userName)
            vm.setTargetTankName(self.__targetVehicle.userName)
            vm.setCurrentNation(getIconResourceName(self.__currentVehicle.nationName))
            vm.setTargetNation(getIconResourceName(self.__targetVehicle.nationName))
            vm.setCurrentTankTooltipHeader(self.__currentVehicle.longUserName)
            vm.setCurrentTankTooltipBody(self.__currentVehicle.fullDescription)
            currentVehicle = self.__currentVehicle
            targetVehicle = self.__targetVehicle
            currentVehNumSetups = self.__updateTankSlot(vm.currentNation, currentVehicle)
            vm.setCurrentTankSetupsNumber(currentVehNumSetups)
            targetVehNumSetups = self.__updateTankSlot(vm.targetNation, targetVehicle)
            vm.setTargetTankSetupsNumber(targetVehNumSetups)
        self.__addListeners()
        self.__setViewed()
        WWISE.WW_setState(self._HANGAR_SOUND_FILTERED_STATE_NAME, self._HANGAR_SOUND_FILTERED_STATE_ON)

    def _finalize(self):
        WWISE.WW_setState(self._HANGAR_SOUND_FILTERED_STATE_NAME, self._HANGAR_SOUND_FILTERED_STATE_OFF)
        self.__removeListeners()
        super(NationChangeScreen, self)._finalize()

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        vehicleIntCD = int(event.getArgument('vehicleIntCD'))
        if tooltipId == TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE:
            args = [vehicleIntCD]
        elif tooltipId == TOOLTIPS_CONSTANTS.NATION_CHANGE_BATTLE_BOOSTER:
            args = [vehicleIntCD, int(event.getArgument('intCD')), int(event.getArgument('layoutIDx'))]
        else:
            args = [vehicleIntCD, int(event.getArgument('intCD'))]
        return TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=args)

    def __updateTankSlot(self, tankSlotVM, vehicle):
        tankSlotVM.setTankImage(R.images.gui.maps.shop.vehicles.c_600x450.dyn(getIconResourceName(getNationLessName(vehicle.name)))())
        tankSlotVM.setTankNation(getIconResourceName(vehicle.nationName))
        tankSlotVM.setVehicleIntCD(vehicle.intCD)
        self.__setCrewViewModelData(tankSlotVM, vehicle)
        tankSetups = tankSlotVM.getSetups()
        tankSetups.clear()
        if not vehicle.postProgressionAvailability().result:
            setupsIndexes = [(vehicle.battleBoosters.setupLayouts.layoutIndex,
              vehicle.consumables.setupLayouts.layoutIndex,
              vehicle.optDevices.setupLayouts.layoutIndex,
              vehicle.shells.setupLayouts.layoutIndex)]
        else:
            setupsIndexes = [ [layoutID] * self.__LAYOUTS_IN_SETUP for layoutID in range(SWITCH_LAYOUT_CAPACITY) ]
        numSetups = 0
        for setupIndexes in setupsIndexes:
            setupModel = NationChangeTankSetupModel()
            hasEquipment = self.__setSetupData(setupModel, vehicle, setupIndexes)
            if hasEquipment:
                tankSetups.addViewModel(setupModel)
                numSetups += 1

        tankSetups.invalidate()
        tankSlotVM.setNoEquipment(numSetups == 0)
        return numSetups

    def __setSetupData(self, setupModel, guiVh, layoutIndexes):
        instructionsIdx, consumablesIdx, devicesIdx, shellsIdx = layoutIndexes
        hasEquipment = self.__setEquipmentViewModelData(setupModel.getSupplyList(), guiVh, consumablesIdx)
        hasDevices = self.__setDevicesViewModelData(setupModel.getEquipmentList(), guiVh, devicesIdx)
        hasShells = self.__setShellsViewModelData(setupModel.getShellList(), guiVh, shellsIdx)
        hasInstructions = self.__setInstructionViewModelData(setupModel.instructionSlot, guiVh, instructionsIdx)
        return hasEquipment or hasDevices or hasShells or hasInstructions

    def __setCrewViewModelData(self, tankSlotVM, guiVh):
        crewListVM = tankSlotVM.getCrewList()
        crewListVM.clear()
        roles = guiVh.descriptor.type.crewRoles
        crew = sortCrew(guiVh.crew, roles)
        skillsConfig = getSkillsConfig()
        isDogInCrew = 'dog' in guiVh.tags
        iconsSmall = self.__icons.tankmen.icons.barracks
        for slotIdx, tankman in crew:
            tankmanVM = NationChangeTankmanModel()
            if tankman is not None:
                if tankman.skinID != NO_CREW_SKIN_ID:
                    skinItem = self.__itemsCache.items.getCrewSkin(tankman.skinID)
                    tankmanVM.setImage(iconsSmall.crewSkins.dyn(skinItem.getIconName())())
                else:
                    tankmanVM.setImage(iconsSmall.dyn(getIconResourceName(tankman.extensionLessIcon))())
                tankmanVM.setInvID(tankman.invID)
            else:
                role = roles[slotIdx][0]
                tankmanVM.setImage(self.__icons.tankmen.icons.barracks.silhouette_mask())
                tankmanVM.setIsSimpleTooltip(True)
                tankmanVM.setSimpleTooltipHeader(convert(skillsConfig.getSkill(role).userString))
                tankmanVM.setSimpleTooltipBody(guiVh.longUserName)
            R.strings.multinational_vehicles.changeScreen.title.header()
            crewListVM.addViewModel(tankmanVM)

        if isDogInCrew:
            tankmanVM = NationChangeTankmanModel()
            dogTooltip = R.strings.tooltips.hangar.crew.rudy.dog.dyn(guiVh.nationName)
            tankmanVM.setImage(self.__icons.tankmen.icons.barracks.ussr_dog_1())
            tankmanVM.setIsSimpleTooltip(True)
            tankmanVM.setSimpleTooltipHeader(backport.text(dogTooltip.header()))
            tankmanVM.setSimpleTooltipBody(backport.text(dogTooltip.body()))
            tankmanVM.setIsDog(True)
            crewListVM.addViewModel(tankmanVM)
        if any((tankman[1] is not None for tankman in guiVh.crew)) or isDogInCrew:
            tankSlotVM.setNoCrew(False)
        return

    def __setEquipmentViewModelData(self, slotVM, guiVh, layoutIdx):
        slotVM.clear()
        setup = guiVh.consumables.setupLayouts.setupByIndex(layoutIdx)
        installedEquipment = setup.getItems() if setup is not None else ()
        hasEquipment = False
        for equipment in installedEquipment:
            if equipment is not None:
                supplyModel = NationChangeSupplyModel()
                supplyModel.setImage(self.__icons.artefact.dyn(getIconResourceName(equipment.descriptor.iconName))())
                supplyModel.setIntCD(equipment.intCD)
                slotVM.addViewModel(supplyModel)
                hasEquipment = True

        slotVM.invalidate()
        return hasEquipment

    def __setDevicesViewModelData(self, slotVM, guiVh, layoutIdx):
        slotVM.clear()
        setup = guiVh.optDevices.setupLayouts.setupByIndex(layoutIdx)
        installedOptDevices = setup.getItems() if setup is not None else ()
        hasDevices = False
        for device in installedOptDevices:
            deviceModel = NationChangeDeviceModel()
            deviceModel.setImage(self.__icons.artefact.dyn(getIconResourceName(device.descriptor.iconName))())
            deviceModel.setIsImproved(device.isDeluxe)
            deviceModel.setIsTrophyBasic(device.isUpgradable)
            deviceModel.setIsTrophyUpgraded(device.isUpgraded)
            deviceModel.setIsModernized(device.isModernized)
            deviceModel.setLevel(device.level)
            deviceModel.setIntCD(device.intCD)
            slotVM.addViewModel(deviceModel)
            hasDevices = True

        slotVM.invalidate()
        return hasDevices

    def __setShellsViewModelData(self, slotVM, guiVh, layoutIdx):
        slotVM.clear()
        setup = guiVh.shells.setupLayouts.setupByIndex(layoutIdx)
        installedShells = setup.getItems() if setup is not None else ()
        hasShells = False
        for shell in installedShells:
            if shell.count > 0:
                shellModel = NationChangeShellModel()
                shellModel.setImage(self.__icons.shell.small.dyn(getIconResourceName(shell.descriptor.iconName))())
                shellModel.setIntCD(shell.intCD)
                slotVM.addViewModel(shellModel)
                hasShells = True

        slotVM.invalidate()
        return hasShells

    def __setInstructionViewModelData(self, slotVM, guiVh, layoutIdx):
        setup = guiVh.battleBoosters.setupLayouts.setupByIndex(layoutIdx)
        booster = setup.getItems() if setup is not None else ()
        instruction = next(iter(booster or []), None)
        if instruction is not None:
            slotVM.setImage(self.__icons.artefact.dyn(getIconResourceName(instruction.descriptor.iconName))())
            slotVM.setIsActive(instruction.isAffectsOnVehicle(guiVh, layoutIdx))
            slotVM.setIsPerkReplace(instruction.isCrewBooster() and not instruction.isAffectedSkillLearnt(guiVh))
            slotVM.setIsInstalled(True)
            slotVM.setIntCD(instruction.intCD)
            slotVM.setLayoutIDx(layoutIdx)
            return True
        else:
            return False

    def __playAnimation(self):
        if self.viewStatus != ViewStatus.LOADED:
            return
        self.viewModel.setIsSlotAnimPlaying(True)

    def __setViewed(self):
        if not AccountSettings.getSettings(NATION_CHANGE_VIEWED):
            AccountSettings.setSettings(NATION_CHANGE_VIEWED, True)

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        g_clientUpdateManager.addCallbacks({'inventory.1.compDescr': self.__onVehiclesInInventoryUpdate})
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onSwitchBtnClick += self.__onSwitchBtnClick
        self.viewModel.onCancelBtnClick += self.__onCancelBtnClick
        self.viewModel.onHangarBtnClick += self.__onHangarBtnClick
        self.viewModel.onDogClick += self.__onDogClick

    def __removeListeners(self):
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onSwitchBtnClick -= self.__onSwitchBtnClick
        self.viewModel.onCancelBtnClick -= self.__onCancelBtnClick
        self.viewModel.onHangarBtnClick -= self.__onHangarBtnClick
        self.viewModel.onDogClick -= self.__onDogClick
        g_clientUpdateManager.removeCallback('inventory.1.compDescr', self.__onVehiclesInInventoryUpdate)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    @serverSettingsChangeListener('isNationChangeEnabled', SERVER_SETTINGS_KEY)
    def __onServerSettingsChange(self, diff):
        if not self.__lobbyContext.getServerSettings().isNationChangeEnabled():
            self.__onWindowClose()
            return
        with self.viewModel.transaction() as vm:
            self.__updateTankSlot(vm.currentNation, self.__currentVehicle)
            self.__updateTankSlot(vm.targetNation, self.__targetVehicle)

    def __onVehiclesInInventoryUpdate(self, diff):
        if self.__currentVehicle.invID in diff and diff[self.__currentVehicle.invID] is None:
            self.__onWindowClose()
        return

    def __onWindowClose(self):
        if g_currentVehicle.item == self.__currentVehicle and not self.__itemsCache.items.getItemByCD(self.__currentVehicle.intCD).activeInNationGroup:
            event_dispatcher.selectVehicleInHangar(self.__targetVehicle.intCD)
        self.destroyWindow()

    def __onHangarBtnClick(self):
        event_dispatcher.selectVehicleInHangar(self.__targetVehicle.intCD)
        self.__onWindowClose()

    def __onDogClick(self):
        SoundGroups.g_instance.playSound2D(self._DOG_SOUND)

    @decorators.adisp_process('updating')
    def __onSwitchBtnClick(self):
        processor = VehicleChangeNation(self.__currentVehicle, self.__targetVehicle)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__playAnimation()

    def __onCancelBtnClick(self):
        self.__onWindowClose()
