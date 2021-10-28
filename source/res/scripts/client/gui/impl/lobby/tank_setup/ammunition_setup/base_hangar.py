# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/base_hangar.py
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from Event import Event
import adisp
from async import async, await
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_setup_view_model import AmmunitionSetupViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.halloween.tooltips.nitro_tooltip import NitroTooltip
from gui.impl.lobby.tank_setup.ammunition_setup.base import BaseAmmunitionSetupView
from gui.impl.lobby.tank_setup.backports.context_menu import getContextMenuData
from gui.impl.lobby.tank_setup.interactors.base import InteractingItem
from gui.impl.lobby.tank_setup.backports.tooltips import getSlotTooltipData, getShellsPriceDiscountTooltipData, getSlotSpecTooltipData
from gui.impl.lobby.tank_setup.tank_setup_sounds import playEnterTankSetupView, playExitTankSetupView
from gui.prb_control import prbDispatcherProperty
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.events import AmmunitionSetupViewEvent, HangarVehicleEvent, PrbActionEvent
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from post_progression_common import TANK_SETUP_GROUPS, TankSetupGroupsId
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException

class TankSetupCloseConfirmatorsHelper(CloseConfirmatorsHelper):

    def getRestrictedSfViews(self):
        result = super(TankSetupCloseConfirmatorsHelper, self).getRestrictedSfViews()
        result.extend([VIEW_ALIAS.LOBBY_CUSTOMIZATION])
        return result

    def getRestrictedEvents(self):
        result = super(TankSetupCloseConfirmatorsHelper, self).getRestrictedEvents()
        result.remove(PrbActionEvent.LEAVE)
        return result


class BaseHangarAmmunitionSetupView(BaseAmmunitionSetupView):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__blur', '__isClosed', '__closeConfirmatorHelper', 'onClose', 'onAnimationEnd', '__moneyCache')

    def __init__(self, layoutID=R.views.lobby.tanksetup.HangarAmmunitionSetup(), **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = AmmunitionSetupViewModel()
        settings.flags = ViewFlags.COMPONENT
        settings.kwargs = kwargs
        super(BaseHangarAmmunitionSetupView, self).__init__(settings)
        self.__blur = CachedBlur()
        self.__isClosed = False
        self.__closeConfirmatorHelper = TankSetupCloseConfirmatorsHelper()
        self.__moneyCache = self._itemsCache.items.stats.money
        self.onClose = Event()
        self.onAnimationEnd = Event()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def createToolTipContent(self, event, contentID):
        return NitroTooltip() if contentID == R.views.lobby.halloween.tooltips.NitroTooltip() else None

    def sendSlotAction(self, args):
        if self._tankSetup is not None and self._tankSetup.getCurrentSubView() is not None:
            self._tankSetup.getCurrentSubView().onSlotAction(args)
        return

    def setLastSlotAction(self, *args, **kwargs):
        self._onSlotAction(*args, **kwargs)

    def getVehicleItem(self):
        return self._vehItem

    def getSelectedSetup(self):
        return self._tankSetup.getSelectedSetup() if self._tankSetup is not None else None

    def _getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltip')
        if tooltipId == TOOLTIPS_CONSTANTS.PRICE_DISCOUNT:
            return getShellsPriceDiscountTooltipData(event, tooltipId)
        return getSlotSpecTooltipData(event, tooltipId) if tooltipId == TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC else getSlotTooltipData(event, self._vehItem.getItem(), self.viewModel.ammunitionPanel.getSelectedSlot(), self.viewModel.ammunitionPanel.getSelectedSection())

    def _getBackportContextMenuData(self, event):
        return getContextMenuData(event, self.uniqueID, self.getSelectedSetup())

    def _createVehicleItem(self):
        copyVehicle = self.__createCopyVehicle()
        return InteractingItem(copyVehicle)

    def _recreateVehicleItem(self):
        copyVehicle = self.__createCopyVehicle()
        self._vehItem.setItem(copyVehicle)

    def _recreateVehicleSetups(self):
        vehicle = self._vehItem.getItem()
        currentVehicle = g_currentVehicle.item
        for groupID, newIdx in currentVehicle.setupLayouts.groups.iteritems():
            if newIdx != vehicle.setupLayouts.getLayoutIndex(groupID):
                for vehEquip, curVehEquip in self._getEquipmentsPairs(groupID):
                    vehEquip.setInstalled(*curVehEquip.installed)
                    vehEquip.setLayout(*curVehEquip.layout)
                    vehEquip.setupLayouts.setLayoutIndex(newIdx)

        if self.getSelectedSetup() != TankSetupConstants.OPT_DEVICES:
            vehicle.descriptor.installOptDevsSequence(currentVehicle.optDevices.installed.getIntCDs())
        vehicle.setupLayouts.setGroups(currentVehicle.setupLayouts.groups.copy())

    def _getEquipmentsPairs(self, groupID):
        currentVehicle = g_currentVehicle.item
        vehicle = self._vehItem.getItem()
        eqPairs = set()
        if groupID == TankSetupGroupsId.EQUIPMENT_AND_SHELLS:
            eqPairs.add((vehicle.consumables, currentVehicle.consumables))
            eqPairs.add((vehicle.shells, currentVehicle.shells))
        elif groupID == TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS:
            eqPairs.add((vehicle.optDevices, currentVehicle.optDevices))
            eqPairs.add((vehicle.battleBoosters, currentVehicle.battleBoosters))
        else:
            raise SoftException('Vehicle setup group id must match for any type of equipments. groupID {}'.format(groupID))
        return eqPairs

    def _createMainTankSetup(self):
        raise NotImplementedError

    def _createAmmunitionPanel(self):
        raise NotImplementedError

    def _onLoading(self, **kwargs):
        super(BaseHangarAmmunitionSetupView, self)._onLoading(**kwargs)
        fillVehicleInfo(self.viewModel.vehicleInfo, self._vehItem.getItem())
        self.viewModel.setIsEvent(self._vehItem.getItem().isOnlyForEventBattles)

    def _initialize(self, *args, **kwargs):
        super(BaseHangarAmmunitionSetupView, self)._initialize()
        playEnterTankSetupView()
        self.__updateTTC()

    def _finalize(self):
        super(BaseHangarAmmunitionSetupView, self)._finalize()
        self.onClose.clear()
        self.onAnimationEnd.clear()
        if self.__blur is not None:
            self.__blur.fini()
        g_eventBus.handleEvent(HangarVehicleEvent(HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        return

    def _addListeners(self):
        super(BaseHangarAmmunitionSetupView, self)._addListeners()
        self.__closeConfirmatorHelper.start(self.__closeConfirmator)
        self._vehItem.onAcceptComplete += self.__onAcceptComplete
        self._itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.viewModel.onResized += self.__onResized
        self.viewModel.onViewRendered += self.__onViewRendered
        self.viewModel.onAnimationEnd += self.__onAnimationEnd
        self.viewModel.ammunitionPanel.onDragDropSwap += self.__onDragDropSwap
        self.viewModel.ammunitionPanel.onSpecializationSelect += self.__onSpecializationSelect
        g_eventBus.addListener(AmmunitionSetupViewEvent.CLOSE_VIEW, self.__onCloseView, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(BaseHangarAmmunitionSetupView, self)._removeListeners()
        self.__closeConfirmatorHelper.stop()
        self._vehItem.onAcceptComplete -= self.__onAcceptComplete
        self._itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.viewModel.onResized -= self.__onResized
        self.viewModel.onViewRendered -= self.__onViewRendered
        self.viewModel.onAnimationEnd -= self.__onAnimationEnd
        self.viewModel.ammunitionPanel.onDragDropSwap -= self.__onDragDropSwap
        self.viewModel.ammunitionPanel.onSpecializationSelect -= self.__onSpecializationSelect
        g_eventBus.removeListener(AmmunitionSetupViewEvent.CLOSE_VIEW, self.__onCloseView, EVENT_BUS_SCOPE.LOBBY)

    @async
    def _onClose(self):
        quitResult = yield await(self._tankSetup.canQuit())
        if quitResult:
            self.__closeWindow()

    @adisp.process
    def __onSpecializationSelect(self, args=None):
        action = ActionsFactory.getAction(ActionsFactory.SET_EQUIPMENT_SLOT_TYPE, self._vehItem.getItem())
        if action is not None:
            yield action.doAction()
        return

    def _updateAmmunitionPanel(self, sectionName=None):
        super(BaseHangarAmmunitionSetupView, self)._updateAmmunitionPanel(sectionName)
        if sectionName != TankSetupConstants.SHELLS:
            self.__updateTTC()

    def __updateTTC(self):
        currentSubView = self._tankSetup.getCurrentSubView()
        if currentSubView is not None:
            g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.UPDATE_TTC, {'vehicleItem': currentSubView.getInteractor().getVehicleAfterInstall()}), EVENT_BUS_SCOPE.LOBBY)
        return

    def __createCopyVehicle(self):
        currentVehicle = g_currentVehicle.item
        copyVehicle = self._itemsCache.items.getVehicleCopy(currentVehicle)
        copyVehicle.battleAbilities.setInstalled(*currentVehicle.battleAbilities.installed)
        copyVehicle.battleAbilities.setLayout(*currentVehicle.battleAbilities.layout)
        return copyVehicle

    def __onResized(self, args):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.GF_RESIZED, args), EVENT_BUS_SCOPE.LOBBY)

    def __onCloseView(self, event):
        if self.viewModel.getIsReady():
            self._onClose()

    def __onViewRendered(self):
        if not self.viewModel.getIsReady():
            self.viewModel.setShow(True)

    def __onAnimationEnd(self):
        if self.__blur is not None:
            self.__blur.enable()
        g_eventBus.handleEvent(HangarVehicleEvent(HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        if not self.viewModel.getIsReady():
            self.viewModel.setIsReady(True)
        self.onAnimationEnd()
        return

    def __onAcceptComplete(self):
        self.__closeWindow()

    def __onDragDropSwap(self, args):
        actionArgs = {'actionType': BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION}
        dragId = args['dragId']
        dropId = args['dropId']
        if self._tankSetup.getSelectedSetup() == TankSetupConstants.SHELLS:
            actionArgs['leftID'], actionArgs['rightID'] = sorted((dragId, dropId))
        else:
            actionArgs['installedSlotId'] = dragId
            actionArgs['currentSlotId'] = dropId
        self.sendSlotAction(actionArgs)

    def __onSyncCompleted(self, _, diff):
        if not diff and self._itemsCache.items.stats.money == self.__moneyCache:
            return
        else:
            self.__moneyCache = self._itemsCache.items.stats.money
            if g_currentVehicle.isLocked() or not g_currentVehicle.isPresent():
                self.__closeWindow()
                return
            isRentalChange = self._vehItem.getItem().rentalIsOver != g_currentVehicle.isDisabledInRent()
            if self._vehItem.getItem().setupLayouts != g_currentVehicle.item.setupLayouts or isRentalChange:
                needRecreateVehicle = isRentalChange
                if not isRentalChange:
                    changedGroupID = None
                    oldLayouts = self._vehItem.getItem().setupLayouts
                    newLayouts = g_currentVehicle.item.setupLayouts
                    for groupID in TANK_SETUP_GROUPS.iterkeys():
                        if oldLayouts.getLayoutIndex(groupID) != newLayouts.getLayoutIndex(groupID):
                            changedGroupID = groupID
                            break

                    selectedSetup = self._tankSetup.getSelectedSetup()
                    selectedSetupGroup = self._ammunitionPanel.getGroupIdBySection(selectedSetup)
                    needRecreateVehicle = changedGroupID == selectedSetupGroup
                if needRecreateVehicle:
                    self._resetVehicleItem()
                    self._vehItem.getItem().settings = g_currentVehicle.item.settings
                    self._tankSetup.resetVehicle(self._vehItem)
                    self._tankSetup.update(fullUpdate=True)
                else:
                    print '_resetVehicleSetups__________'
                    self._resetVehicleSetups()
                    self._vehItem.getItem().settings = g_currentVehicle.item.settings
                self._ammunitionPanel.updateVehicle(self._vehItem.getItem())
            else:
                self._vehItem.getItem().settings = g_currentVehicle.item.settings
                self._vehItem.getItem().optDevices.dynSlotType = g_currentVehicle.item.optDevices.dynSlotType
                self._tankSetup.currentVehicleUpdated(g_currentVehicle.item)
                self._tankSetup.update(fullUpdate=True)
            self._updateAmmunitionPanel()
            return

    def __closeWindow(self):
        if not self.__isClosed:
            if self.__blur is not None:
                self.__blur.fini()
                self.__blur = None
            self.__isClosed = True
            self.onClose()
            self.viewModel.setShow(False)
            playExitTankSetupView()
        return

    @async
    def __closeConfirmator(self):
        if self.__isClosed:
            raise AsyncReturn(True)
        result = yield await(self._tankSetup.canQuit())
        if result:
            self.__closeWindow()
        raise AsyncReturn(result)
