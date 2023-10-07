# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/ammunition_panel.py
import wg_async as future_async
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.Waiting import Waiting
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.vehicle_compare_ammunition_panel_model import VehicleCompareAmmunitionPanelModel
from gui.impl.lobby.tank_setup.backports.tooltips import getSlotSpecTooltipData
from gui.impl.lobby.tank_setup.tank_setup_helper import setLastSlotAction, NONE_ID
from gui.impl.lobby.vehicle_compare.panel import CompareAmmunitionPanel
from gui.impl.lobby.vehicle_compare.select_slot_spec_compare_dialog import showDialog
from gui.impl.lobby.vehicle_compare.tooltips import getCmpSlotTooltipData
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showCompareAmmunitionSelectorView

class CompareAmmunitionPanelView(ViewImpl):
    __slots__ = ('__ammunitionPanel', '__vehItem')

    def __init__(self):
        settings = ViewSettings(R.views.lobby.tanksetup.VehicleCompareAmmunitionPanel())
        settings.flags = ViewFlags.VIEW
        settings.model = VehicleCompareAmmunitionPanelModel()
        super(CompareAmmunitionPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CompareAmmunitionPanelView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltip')
            if tooltipId == TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC:
                tooltipData = getSlotSpecTooltipData(event, tooltipId)
            else:
                tooltipData = getCmpSlotTooltipData(event, self.__vehItem.getItem())
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(CompareAmmunitionPanelView, self).createToolTip(event)

    def update(self):
        self.__ammunitionPanel.update(self.__vehItem.getItem())

    def updateSection(self, sectionName):
        self.__ammunitionPanel.updateSection(sectionName)

    def _onLoading(self, *args, **kwargs):
        super(CompareAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.__vehItem = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicleItem()
        ctx = {'specializationClickable': True}
        self.__ammunitionPanel = CompareAmmunitionPanel(self.viewModel.ammunitionPanel, self.__vehItem.getItem(), ctx=ctx)
        self.__ammunitionPanel.onLoading()

    def _initialize(self, *args, **kwargs):
        super(CompareAmmunitionPanelView, self)._initialize(*args, **kwargs)
        self.__addListeners()
        self.__ammunitionPanel.initialize()

    def _finalize(self):
        self.__removeListeners()
        self.__ammunitionPanel.finalize()
        self.__ammunitionPanel = None
        self.__vehItem = None
        super(CompareAmmunitionPanelView, self)._finalize()
        return

    def __addListeners(self):
        self.viewModel.ammunitionPanel.onSlotClear += self.__onPanelSlotClear
        self.viewModel.ammunitionPanel.onSectionSelect += self.__onPanelSectionSelected
        self.viewModel.ammunitionPanel.onSpecializationSelect += self.__onSpecializationSelect
        self.viewModel.ammunitionPanel.onDragDropSwap += self.__onDragDropSwap
        self.viewModel.onClose += self.__onClose
        self.__vehItem.onSlotAction += self.__onSlotAction

    def __removeListeners(self):
        self.viewModel.ammunitionPanel.onSlotClear -= self.__onPanelSlotClear
        self.viewModel.ammunitionPanel.onSectionSelect -= self.__onPanelSectionSelected
        self.viewModel.ammunitionPanel.onSpecializationSelect -= self.__onSpecializationSelect
        self.viewModel.ammunitionPanel.onDragDropSwap -= self.__onDragDropSwap
        self.viewModel.onClose -= self.__onClose
        self.__vehItem.onSlotAction -= self.__onSlotAction

    def __onPanelSlotClear(self, args):
        slotID = int(args.get('slotId'))
        sectionName = args.get('sectionType')
        if sectionName == TankSetupConstants.OPT_DEVICES:
            cmp_helpers.getCmpConfiguratorMainView().removeOptionalDevice(slotID)
        elif sectionName == TankSetupConstants.CONSUMABLES:
            cmp_helpers.getCmpConfiguratorMainView().removeEquipment(slotID)
        elif sectionName == TankSetupConstants.BATTLE_BOOSTERS:
            cmp_helpers.getCmpConfiguratorMainView().removeBattleBooster()
        self.__onSlotAction(setupName=sectionName, actionType=BaseSetupModel.REVERT_SLOT_ACTION, slotID=slotID)

    @staticmethod
    def __onPanelSectionSelected(args):
        selectedSection = args.get('selectedSection')
        if selectedSection == TankSetupConstants.TOGGLE_SHELLS:
            selectedSlot = int(args['selectedSlot'])
            cmp_helpers.getCmpConfiguratorMainView().selectShell(selectedSlot)
        elif selectedSection == TankSetupConstants.TOGGLE_CAMOUFLAGE:
            cmpMainView = cmp_helpers.getCmpConfiguratorMainView()
            cmpMainView.selectCamouflage(not cmpMainView.isCamouflageSet())
        else:
            showCompareAmmunitionSelectorView(**args)

    @staticmethod
    def __onClose():
        cmp_helpers.getCmpConfiguratorMainView().closeView()

    def __onSlotAction(self, *args, **kwargs):
        setLastSlotAction(self.viewModel, self.__vehItem.getItem(), *args, **kwargs)

    def __onDragDropSwap(self, args):
        sectionName = args['sectionType']
        leftID, rightID = sorted((int(args['dragId']), int(args['dropId'])))
        if sectionName == TankSetupConstants.OPT_DEVICES:
            cmp_helpers.getCmpConfiguratorMainView().swapOptionalDevice(leftID, rightID)
            self.__sendDragAndDropSlotAction(sectionName, self.__vehItem.getItem().optDevices.layout, leftID, rightID)
        elif sectionName == TankSetupConstants.CONSUMABLES:
            cmp_helpers.getCmpConfiguratorMainView().swapEquipment(leftID, rightID)
            self.__sendDragAndDropSlotAction(sectionName, self.__vehItem.getItem().consumables.layout, leftID, rightID)

    @future_async.wg_async
    def __onSpecializationSelect(self, *_):
        Waiting.show('loadModalWindow', softStart=True)
        cmpConfiguratorView = cmp_helpers.getCmpConfiguratorMainView()
        result = yield future_async.wg_await(showDialog(cmpConfiguratorView.getCurrentVehicle()))
        if result.result[0]:
            cmpConfiguratorView.changeDynRoleSlot(result.result[1])

    def __sendDragAndDropSlotAction(self, sectionName, currentLayout, leftID, rightID):
        leftItem, rightItem = currentLayout[leftID], currentLayout[rightID]
        self.__onSlotAction(setupName=sectionName, actionType=BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION, leftID=leftID, rightID=rightID, leftIntCD=leftItem.intCD if leftItem else NONE_ID, rightIntCD=rightItem.intCD if rightItem else NONE_ID)
