# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_hangar_header_helper.py
from operator import attrgetter
from account_helpers.AccountSettings import EarlyAccess, AccountSettings
from early_access_common import EARLY_ACCESS_POSTPR_KEY
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_entry_point_view_model import ExtendedStates
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from helpers import time_utils, dependency, int2roman
from skeletons.gui.game_control import IEarlyAccessController

@dependency.replace_none_kwargs(ctrl=IEarlyAccessController)
def getFlagData(ctrl=None):

    def getEarlyAccessCurrentActiveCycleID():
        currTime = time_utils.getServerUTCTime()
        currentSeason = ctrl.getCurrentSeason()
        if currentSeason:
            currCycle = currentSeason.getLastActiveCycleInfo(currTime)
            return str(currCycle.ID)

    state = ctrl.getState()
    currentTime = time_utils.getServerUTCTime()
    _, currFinishTime = ctrl.getCycleProgressionTimes()
    if not ctrl.isQuestActive():
        state = ExtendedStates.DISABLED
    elif state == State.ACTIVE:
        remainProgrQuestsCount = __getEarlyAccessTotalIncompleteQuestCount()
        currentCycleID = getEarlyAccessCurrentActiveCycleID()
        remainPostProgrQuestsCount = __getEarlyAccessIncompleteQuestCountInCycle(EARLY_ACCESS_POSTPR_KEY)
        remainCurrCycleQuestsCount = __getEarlyAccessIncompleteQuestCountInCycle(currentCycleID)
        if not remainProgrQuestsCount and remainPostProgrQuestsCount:
            state = State.POSTPROGRESSION
        elif not remainCurrCycleQuestsCount and currentTime < currFinishTime:
            state = ExtendedStates.WAITFORNEXTCHAPTER
    elif state == State.BUY:
        state = State.POSTPROGRESSION
    stateIcon = ''
    label = ''
    isEnabled = state != ExtendedStates.DISABLED
    if state == State.POSTPROGRESSION:
        mainIcon = backport.image(R.images.gui.maps.icons.early_access.entry_point.postProgression())
    else:
        if isEnabled:
            mainIcon = backport.image(R.images.gui.maps.icons.early_access.entry_point.progression())
        else:
            mainIcon = backport.image(R.images.gui.maps.icons.early_access.entry_point.disabled_token())
        if state == State.ACTIVE:
            label = int2roman(__calculateEarlyAccessProgressionLevel() + 1)
        else:
            stateIcon = backport.image(R.images.gui.maps.icons.early_access.entry_point.dyn(state.value)())
    if AccountSettings.getEarlyAccess(EarlyAccess.INTRO_SEEN):
        if isEnabled:
            tooltip = TOOLTIPS_CONSTANTS.EARLY_ACCESS_ENTRY_POINT
        else:
            tooltip = TOOLTIPS_CONSTANTS.EARLY_ACCESS_PAUSED
    else:
        tooltip = TOOLTIPS_CONSTANTS.EARLY_ACCESS_COMMON_INFO
    return (isEnabled,
     label,
     mainIcon,
     stateIcon,
     tooltip)


@dependency.replace_none_kwargs(earlyAccessCtrl=IEarlyAccessController)
def __getEarlyAccessTotalIncompleteQuestCount(earlyAccessCtrl=None):
    return sum((__getEarlyAccessIncompleteQuestCountInCycle(cycleID) for cycleID, _ in earlyAccessCtrl.iterAllCycles()))


@dependency.replace_none_kwargs(earlyAccessCtrl=IEarlyAccessController)
def __calculateEarlyAccessProgressionLevel(earlyAccessCtrl=None):
    currentSeason = earlyAccessCtrl.getCurrentSeason()
    cycles = sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID'))
    return next((i for i, cycle in enumerate(cycles) if __getEarlyAccessIncompleteQuestCountInCycle(str(cycle.ID)) > 0), None)


@dependency.replace_none_kwargs(earlyAccessCtrl=IEarlyAccessController)
def __getEarlyAccessIncompleteQuestCountInCycle(cycleID, earlyAccessCtrl=None):
    return sum(((not quest.isCompleted() if quest else False) for quest in earlyAccessCtrl.iterCycleProgressionQuests(cycleID)))
