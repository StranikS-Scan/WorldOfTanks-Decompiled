# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_hints.py
from typing import TYPE_CHECKING
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.impl.gen import R
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.impl import IGuiLoader
from constants import NEW_PERK_SYSTEM as NPS
from tutorial.hints_manager import HINT_SHOWN_STATUS
if TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.impl.lobby.crew.container_vews.skills_training.skills_training_view import SkillsTrainingView
    from gui.impl.lobby.crew.container_vews.skills_training.context import SkillsTrainingViewContext
    from gui.impl.lobby.crew.container_vews.personal_file.personal_file_view import PersonalFileView
    from gui.impl.lobby.crew.container_vews.personal_file.context import PersonalFileViewContext

@replace_none_kwargs(wotPlusCtrl=IWotPlusController)
def isTankmanWotPlusAssistCandidate(tman, vehicle=None, wotPlusCtrl=None):
    if not tman:
        return False
    vehicle = vehicle or g_currentVehicle.item
    if not vehicle:
        return False
    if not tman.isInNativeTank:
        return False
    common, legend = wotPlusCtrl.hasCrewAssistOrderSets(vehicle, tman.role)
    return True if common or legend else False


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def updateCrewWidgetWotPlusAssistCandidateHint(vehicle, settingsCore=None):
    hintID = OnceOnlyHints.WOTPLUS_CREW_WIDGET_TANKMAN_ASSIST_HINT
    hintShown = bool(settingsCore.serverSettings.getOnceOnlyHintsSetting(hintID))
    if not hintShown:
        if findTankmanInCrewForWotPlusAssistCandidate(vehicle) > 0:
            settingsCore.serverSettings.setOnceOnlyHintsSettings({hintID: HINT_SHOWN_STATUS})


def findTankmanInCrewForWotPlusAssistCandidate(vehicle=None):
    vehicle = vehicle or g_currentVehicle.item
    if not vehicle:
        return 0

    def __hasUntrainedBonusSkill(tankman):
        for bSkillList in tankman.bonusSkills.itervalues():
            for bSkill in bSkillList:
                if not bSkill:
                    return True

        return False

    candidateTmanId = 0
    candidateWithAllTrainedSkills = 0
    for _, tman in vehicle.crew:
        if isTankmanWotPlusAssistCandidate(tman, vehicle):
            emptyMajorSkillsCount = max(0, NPS.MAX_MAJOR_PERKS - tman.earnedSkillsCount - tman.freeSkillsCount)
            if emptyMajorSkillsCount:
                candidateTmanId = tman.invID
                break
            if __hasUntrainedBonusSkill(tman):
                candidateTmanId = tman.invID
                break
            if not candidateWithAllTrainedSkills:
                candidateWithAllTrainedSkills = tman.invID

    return candidateTmanId if candidateTmanId else candidateWithAllTrainedSkills


class WotPlusCrewWidgetTankmanAssistChecker(object):

    def check(self, _):
        wotPlusCtrl = dependency.instance(IWotPlusController)
        if not wotPlusCtrl.isCrewAssistEnabled():
            return False
        vehicle = g_currentVehicle.item
        if not vehicle:
            return False
        for _, tankman in vehicle.crew:
            if isTankmanWotPlusAssistCandidate(tankman):
                return True

        return False


class WotPlusCrewSkillTrainingDropDownAssistChecker(object):

    def check(self, _):
        uiLoader = dependency.instance(IGuiLoader)
        skillTrainingView = uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.crew.SkillsTrainingView())
        if skillTrainingView:
            ctx = skillTrainingView.context
            if isTankmanWotPlusAssistCandidate(ctx.tankman, ctx.tankman.getVehicle()):
                return True
        return False


class WotPlusCrewContainerTankmanSkillAssistChecker(object):

    def check(self, _):
        uiLoader = dependency.instance(IGuiLoader)
        personalFileView = uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.crew.personal_case.PersonalFileView())
        if personalFileView:
            ctx = personalFileView.context
            if isTankmanWotPlusAssistCandidate(ctx.tankman, ctx.tankman.getVehicle()):
                return True
        return False
