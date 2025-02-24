# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/easy_tank_equip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.consumables_preset_model import ConsumablesPresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.crew_preset_model import CrewPresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.opt_devices_preset_model import OptDevicesPresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.shells_preset_model import ShellsPresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.style_preset_model import StylePresetModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import DealPanelModel

class EasyTankEquipViewModel(ViewModel):
    __slots__ = ('onClose', 'onEnableBlur', 'onSelectProposal', 'onSwitchPreset', 'onSwapSlots')

    def __init__(self, properties=7, commands=5):
        super(EasyTankEquipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def dealPanel(self):
        return self._getViewModel(1)

    @staticmethod
    def getDealPanelType():
        return DealPanelModel

    @property
    def crewProposal(self):
        return self._getViewModel(2)

    @staticmethod
    def getCrewProposalType():
        return CrewPresetModel

    @property
    def optDevicesProposal(self):
        return self._getViewModel(3)

    @staticmethod
    def getOptDevicesProposalType():
        return OptDevicesPresetModel

    @property
    def shellsProposal(self):
        return self._getViewModel(4)

    @staticmethod
    def getShellsProposalType():
        return ShellsPresetModel

    @property
    def consumablesProposal(self):
        return self._getViewModel(5)

    @staticmethod
    def getConsumablesProposalType():
        return ConsumablesPresetModel

    @property
    def styleProposal(self):
        return self._getViewModel(6)

    @staticmethod
    def getStyleProposalType():
        return StylePresetModel

    def _initialize(self):
        super(EasyTankEquipViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('dealPanel', DealPanelModel())
        self._addViewModelProperty('crewProposal', ProposalModel())
        self._addViewModelProperty('optDevicesProposal', ProposalModel())
        self._addViewModelProperty('shellsProposal', ProposalModel())
        self._addViewModelProperty('consumablesProposal', ProposalModel())
        self._addViewModelProperty('styleProposal', ProposalModel())
        self.onClose = self._addCommand('onClose')
        self.onEnableBlur = self._addCommand('onEnableBlur')
        self.onSelectProposal = self._addCommand('onSelectProposal')
        self.onSwitchPreset = self._addCommand('onSwitchPreset')
        self.onSwapSlots = self._addCommand('onSwapSlots')
