# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/components/tips_list_component.py
import typing
import SoundGroups
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import TipType
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.utils import TRAINING_TIPS, getTip
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.quick_training_view_model import QuickTrainingViewModel
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.tips_list_component_model import TipsListComponentModel

class TipsListComponent(ComponentBase):

    def _getViewModel(self, vm):
        return vm.tips

    def _fillViewModel(self, vm):
        tips = vm.getItems()
        playErrorSound = True
        for tip in tips:
            if tip.getType() == TipType.ERROR:
                playErrorSound = False

        tips.clear()
        self.__fillErrorTips(tips, playErrorSound)
        tips.invalidate()

    def __fillErrorTips(self, tips, playSound):
        if self.context.isAllCrewMaxTrained and not self.context.hasCrewLowTrainedTman:
            tips.addViewModel(getTip(TRAINING_TIPS.ALL_FULL_TRAINED, TipType.ERROR))
            return
        if self.context.hasCrewMaxedTman:
            if self.context.alreadyMaxedTankmanName:
                tips.addViewModel(getTip(TRAINING_TIPS.FULL_TRAINED_PERSONAL, TipType.ERROR, tankman=self.context.alreadyMaxedTankmanName))
            else:
                tips.addViewModel(getTip(TRAINING_TIPS.FULL_TRAINED_FEW_MEMBERS, TipType.ERROR))
        if self.context.selection.hasCommonBook:
            if self.context.willAllTmenGainMaxXp:
                tips.addViewModel(getTip(TRAINING_TIPS.WILL_FULL_TRAINED_CREW, TipType.ERROR))
            elif self.context.willAnyTmanBeMaxed and not self.context.possibleMaxedTankmanName:
                tips.addViewModel(getTip(TRAINING_TIPS.WILL_FULL_TRAINED_FEW_MEMBERS, TipType.ERROR))
        if self.context.selection.hasAnyBook and self.context.possibleMaxedTankmanName:
            tips.addViewModel(getTip(TRAINING_TIPS.WILL_FULL_TRAINED_PERSONAL, TipType.ERROR, tankman=self.context.possibleMaxedTankmanName))
        if self.context.selection.hasPersonalBook and not self.context.tankman.isMaxSkillEfficiency:
            tips.addViewModel(getTip(TRAINING_TIPS.LOW_PE_TIPS_PERSONAL, TipType.ERROR, tankman=self.context.tankman.getFullUserNameWithSkin()))
        else:
            crewStateTip = self.context.crewTip
            if crewStateTip:
                tips.addViewModel(getTip(crewStateTip, TipType.ERROR))
        if playSound:
            SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TIPS_ERROR)
