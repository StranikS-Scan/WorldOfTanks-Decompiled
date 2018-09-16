# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_map_view.py
import operator
import WWISE
import SoundGroups
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getPersonalMissionAwardsFormatter, getMapRegionTooltipData
from gui.Scaleform.daapi.view.meta.PersonalMissionsMapViewMeta import PersonalMissionsMapViewMeta
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import COMPLETION_TOKENS_SIZES
from gui.server_events.events_dispatcher import showPersonalMissionDetails
from gui.server_events.events_helpers import AwardSheetPresenter
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS
from helpers.i18n import makeString as _ms
from personal_missions import PM_BRANCH
from shared_utils import findFirst, first
_MAIN_AWARD_TEXT = {1: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_ENGINE,
 2: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_HULL,
 3: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_CHASSIS,
 4: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_GUN,
 5: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_RADIO,
 6: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_HULLANDTURRET}
HT_CHAIN_ID = 2
OPERATION_ID_T55A = 3
OPERATION_ID_OBJECT_260 = 4
MAIN_AWARD_TEXT_ID_HULL = 6
_MAIN_AWARD_TEXT_PM2 = {1: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_BLUEPRINTENGINE,
 2: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_BLUEPRINTCHASSIS,
 3: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_BLUEPRINTHULL,
 4: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_BLUEPRINTGUN,
 5: PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD_BLUEPRINTHULLANDTURRET}
ALLIANCE_CHAIN_ID = 3
OPERATION_ID_CHIMERA = 6
OPERATION_ID_OBJECT_279 = 7
MAIN_AWARD_TEXT_PM2_ID_HULL = 5

class PersonalMissionsMapView(PersonalMissionsMapViewMeta, PersonalMissionsNavigation):

    def onRegionClick(self, questID):
        showPersonalMissionDetails(questID)
        SoundGroups.g_instance.playSound2D(SOUNDS.REGION_CLICK)

    def refresh(self):
        chainID = self.getChainID()
        operation = self.getOperation()
        quests = sorted(self.getChain().itervalues(), key=operator.methodcaller('getID'))
        questClassifier = ''
        enabled = False
        if operation.isUnlocked():
            questClassifier = self.getOperation().getChainClassifier(chainID).classificationAttr
            enabled = True
        questsData, awards = self.__getQuestsData(questClassifier, quests)
        self.as_setPlanDataS({'regions': questsData,
         'enabled': enabled,
         'chainID': chainID,
         'operationID': operation.getID(),
         'awardsBlockVO': awards})

    def _populate(self):
        super(PersonalMissionsMapView, self)._populate()
        self.refresh()
        WWISE.WW_setRTCPGlobal(SOUNDS.RTCP_MISSION_BRANCH[self.getBranch()], SOUNDS.BRANCH_SELECTED)

    def _dispose(self):
        WWISE.WW_setRTCPGlobal(SOUNDS.RTCP_MISSION_BRANCH[self.getBranch()], SOUNDS.BRANCH_DEFAULT)
        super(PersonalMissionsMapView, self)._dispose()

    def __getQuestsData(self, chainID, quests):
        questsData = []
        awards = {}
        for quest in quests:
            questsData.append(self.__getQuestStatusData(chainID, quest))
            if quest.isFinal() and not quest.isDisabled():
                awards = self.__getFinalQuestAwardsVO(quest)

        return (questsData, awards)

    def __getQuestStatusData(self, chainID, quest):
        questId = quest.getID()
        state = PERSONAL_MISSIONS_ALIASES.REGION_NOT_COMPLETED
        isFinal = quest.isFinal()
        areTokensPawned = quest.areTokensPawned()
        isUnlocked = quest.isUnlocked()
        isFullCompleted = quest.isFullCompleted()
        isDisabled = quest.isDisabled()
        isOnPause = quest.isOnPause
        if isDisabled:
            state = PERSONAL_MISSIONS_ALIASES.REGION_DISABLED
        elif quest.isInProgress():
            if isOnPause:
                state = PERSONAL_MISSIONS_ALIASES.REGION_ON_PAUSE
            else:
                state = PERSONAL_MISSIONS_ALIASES.REGION_IN_PROGRESS
        elif isFullCompleted:
            state = PERSONAL_MISSIONS_ALIASES.REGION_FULLY_COMPLETED
        elif quest.isMainCompleted():
            state = PERSONAL_MISSIONS_ALIASES.REGION_COMPLETED
        elif not isUnlocked and (not isFinal or not quest.canBePawned()):
            state = PERSONAL_MISSIONS_ALIASES.REGION_NOT_AVAILABLE
        vo = {'id': questId,
         'state': state,
         'isLocked': isFinal and not isUnlocked and not areTokensPawned or isDisabled,
         'isOnPause': isOnPause,
         'tooltipData': getMapRegionTooltipData(state, quest),
         'isTokenPawned': areTokensPawned,
         'isFinal': isFinal,
         'vehType': chainID,
         'sheet': AwardSheetPresenter.getIcon(AwardSheetPresenter.Size.TINY)}
        return vo

    def __getFinalQuestAwardsVO(self, quest):
        tokenAward = findFirst(lambda q: q.getName() == 'completionTokens', quest.getBonuses(isMain=True))
        formatter = getPersonalMissionAwardsFormatter()
        mainAwards = formatter.getFormattedBonuses((tokenAward,), size=COMPLETION_TOKENS_SIZES.HUGE, obtainedImage=RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_OPERATIONS_STATES_COMPLETED, obtainedImageOffset=0)
        chainID = self.getChainID()
        operationID = self.getOperationID()
        mainAwardTextID = chainID
        if self.getBranch() == PM_BRANCH.REGULAR:
            if chainID == HT_CHAIN_ID and (operationID == OPERATION_ID_T55A or operationID == OPERATION_ID_OBJECT_260):
                mainAwardTextID = MAIN_AWARD_TEXT_ID_HULL
            mainAwardText = _ms(_MAIN_AWARD_TEXT[mainAwardTextID])
        else:
            if chainID == ALLIANCE_CHAIN_ID and (operationID == OPERATION_ID_CHIMERA or operationID == OPERATION_ID_OBJECT_279):
                mainAwardTextID = MAIN_AWARD_TEXT_PM2_ID_HULL
            mainAwardText = _ms(_MAIN_AWARD_TEXT_PM2[mainAwardTextID])
        return {'mainAwardText': mainAwardText,
         'mainAward': first(mainAwards)}
