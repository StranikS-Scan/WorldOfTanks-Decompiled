# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/easy_tank_equip/loggers.py
import json
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalType
from uilogging.base.logger import MetricsLogger
from uilogging.easy_tank_equip.constants import FEATURE, EasyTankEquipLogActions, EasyTankEquipLogItems, EasyTankEquipSwapInitiators
if TYPE_CHECKING:
    from typing import List
LOGGING_ITEMS_MAP = {ProposalType.CREW: EasyTankEquipLogItems.CREW,
 ProposalType.OPT_DEVICES: EasyTankEquipLogItems.OPT_DEVICES,
 ProposalType.SHELLS: EasyTankEquipLogItems.SHELLS,
 ProposalType.CONSUMABLES: EasyTankEquipLogItems.CONSUMABLES,
 ProposalType.STYLES: EasyTankEquipLogItems.STYLES}

class EasyTankEquipLogger(MetricsLogger):
    STATUS_KEY = 'status'
    PRESET_NUMBER_KEY = 'preset_number'
    IDS_KEY = 'ids'

    def __init__(self):
        super(EasyTankEquipLogger, self).__init__(FEATURE)

    def createCardInfo(self, status, presetNumber, ids):
        return {self.STATUS_KEY: status,
         self.PRESET_NUMBER_KEY: presetNumber,
         self.IDS_KEY: ids}

    def onViewOpen(self, info):
        self.log(action=EasyTankEquipLogActions.OPEN, item=EasyTankEquipLogItems.MAIN_VIEW, info=json.dumps(info))

    def onViewClose(self, isApplyBtnClicked, info):
        if isApplyBtnClicked:
            self.log(action=EasyTankEquipLogActions.CLICK, item=EasyTankEquipLogItems.APPLY_BUTTON, parentScreen=EasyTankEquipLogItems.MAIN_VIEW, info=json.dumps(info))
        else:
            self.log(action=EasyTankEquipLogActions.CLOSE, item=EasyTankEquipLogItems.MAIN_VIEW, info=json.dumps(info))

    def onCancel(self):
        self.log(action=EasyTankEquipLogActions.CLICK, item=EasyTankEquipLogItems.CANCEL_BUTTON, parentScreen=EasyTankEquipLogItems.MAIN_VIEW)

    def onSwitchPreset(self, proposalType, fromPresetNumber, toPresetNumber):
        self.log(action=EasyTankEquipLogActions.SWITCH_PRESET, item=LOGGING_ITEMS_MAP[proposalType], parentScreen=EasyTankEquipLogItems.MAIN_VIEW, info='{}:{}'.format(fromPresetNumber, toPresetNumber))

    def onSwapSlots(self, proposalType, isDndUsed, firstSlotNumber, secondSlotNumber):
        initiator = EasyTankEquipSwapInitiators.DRAG_AND_DROP if isDndUsed else EasyTankEquipSwapInitiators.SWAP_BUTTON
        self.log(action=EasyTankEquipLogActions.SWAP_SLOTS, item=LOGGING_ITEMS_MAP[proposalType], parentScreen=EasyTankEquipLogItems.MAIN_VIEW, info='{}:{}:{}'.format(initiator, firstSlotNumber, secondSlotNumber))
