# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/controller.py
from BWUtil import AsyncReturn
import BigWorld
from gui.impl.dialogs.dialogs import showSkillsTrainingConfirmDialog
from gui.impl.lobby.container_views.base.controllers import InteractionController
from gui.impl.lobby.crew.container_vews.skills_training.events import SkillsTrainingComponentViewEvents
from gui.impl.pub.dialog_window import SingleDialogResult
from gui.shared.event_dispatcher import showChangeCrewMember
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.shared.gui_items.items_actions import factory
from items.components import skills_constants
from items.tankmen import MAX_SKILL_LEVEL
from wg_async import wg_async, wg_await

class SkillsTrainingInteractionController(InteractionController):

    def _getEventsProvider(self):
        return SkillsTrainingComponentViewEvents()

    def _getEvents(self):
        return [(self.eventsProvider.onSkillHover, self._onSkillHover),
         (self.eventsProvider.onSkillOut, self._onSkillOut),
         (self.eventsProvider.onSkillClick, self._onSkillClick),
         (self.eventsProvider.onTrain, self._onTrain),
         (self.eventsProvider.onCancel, self._onCancel),
         (self.eventsProvider.onClose, self._onClose)]

    @wg_async
    def onChangeTankman(self, tankmanInvID, slotIdx):
        if self.context.isAnySkillSelected:
            busy, result = yield wg_await(self.__showConfirm())
            if busy:
                return
            if not result:
                self.view.crewWidget.updateTankmanId(self.context.tankman.invID)
                return
        if tankmanInvID == NO_TANKMAN:
            showChangeCrewMember(slotIdx, self.context.tankmanCurrentVehicle.invID)
            self.view.destroyWindow()
        else:
            self.context.update(tankmanInvID, True)
            self.__clearSelection()
            self.refresh()

    def _onSkillHover(self, skillId):
        self.context.updateHoveredSkill(skillId)
        highlightedSkills = []
        if any((skill.name == skillId and skill.level == MAX_SKILL_LEVEL for skill in self.context.tankman.skills)):
            highlightedSkills.append(skillId)
        for _, bonusSkills in self.context.tankman.bonusSkills.iteritems():
            if any((skill.name == skillId and skill.level == MAX_SKILL_LEVEL for skill in bonusSkills if skill)):
                highlightedSkills.append(skillId)

        if skillId not in self.context.selectedSkills:
            self.view.paramsView.updateForSkill(self.context.activeSkillsForTTC, highlightedSkills)

    def _onSkillOut(self, skillId):
        self.context.updateHoveredSkill(None)
        if skillId not in self.context.selectedSkills:
            self.view.paramsView.updateForSkill(self.context.activeSkillsForTTC)
        return

    def _onSkillClick(self, skillId):
        self.context.updateSelectedSkills(skillId)
        if skillId != self.context.hoveredSkill:
            self.view.paramsView.updateForSkill(self.context.activeSkillsForTTC)
        self.view.crewWidget.updateSelectedSkills(self.context.tankman, self.context.selectedSkills, self.context.role)
        self.refresh()

    def _onTrain(self):
        self.__train()
        self.view.destroyWindow()

    def _onCancel(self):
        self.__clearSelection()
        self.refresh()

    @wg_async
    def _onClose(self):
        if self.context.isAnySkillSelected:
            busy, result = yield wg_await(self.__showConfirm())
            if busy or not result:
                return
        self.view.destroyWindow()

    @wg_async
    def __showConfirm(self):
        busy, result = yield wg_await(showSkillsTrainingConfirmDialog(self.context.tankman, self.context.selectedSkills, self.context.availableSkillsData))
        if busy:
            raise AsyncReturn(SingleDialogResult(True, False))
        confirmResult, isClosed = result
        if isClosed:
            raise AsyncReturn(SingleDialogResult(False, False))
        if confirmResult:
            self.__train()
        else:
            self.__clearSelection()
        raise AsyncReturn(SingleDialogResult(False, True))

    def __train(self):
        factory.doAction(factory.ADD_SKILLS_TANKMAN, self.context.tankman.invID, skills_constants.SkillUtilization.MAJOR_SKILL if self.context.isMajorQualification else skills_constants.SkillUtilization.BONUS_SKILL, self.context.selectedSkills)
        BigWorld.player().crewAccountController.setLearnedSkillsAnimanion(self.context.tankman.invID, self.context.selectedSkills)
        self.__clearSelection()

    def __clearSelection(self):
        self.context.clearSelection()
        self.view.paramsView.updateForSkill(self.context.activeSkillsForTTC)
        self.view.crewWidget.updateSelectedSkills(self.context.tankman, self.context.selectedSkills, self.context.role)
