# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_map_view.py
import operator
import SoundGroups
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getPersonalMissionAwardsFormatter
from gui.Scaleform.daapi.view.meta.PersonalMissionsMapViewMeta import PersonalMissionsMapViewMeta
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_dispatcher import showPersonalMissionDetails
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.functions import makeTooltip
PLAN_LINKAGES = {1: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PLAN_LT_LINKAGE,
 3: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PLAN_MT_LINKAGE,
 2: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PLAN_HT_LINKAGE,
 4: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PLAN_AT_SPG_LINKAGE,
 5: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PLAN_SPG_LINKAGE}

class PersonalMissionsMapView(PersonalMissionsMapViewMeta, PersonalMissionsNavigation):

    def onRegionClick(self, questID):
        showPersonalMissionDetails(questID)
        SoundGroups.g_instance.playSound2D(SOUNDS.REGION_CLICK)

    def refresh(self):
        chainID = self.getChainID()
        operation = self.getOperation()
        quests = sorted(self.getChain().itervalues(), key=operator.methodcaller('getID'))
        vehType = ''
        enabled = False
        if operation.isUnlocked():
            vehType = self.getOperation().getChainVehicleClass(chainID)
            enabled = True
        questsData, awards = self.__getQuestsData(vehType, quests)
        self.as_setPlanDataS({'planLinkage': PLAN_LINKAGES[chainID],
         'regions': questsData,
         'enabled': enabled,
         'vehTypeID': chainID,
         'operationID': operation.getID(),
         'awardsBlockVO': awards})

    def _populate(self):
        super(PersonalMissionsMapView, self)._populate()
        self.refresh()

    def __getQuestsData(self, vehType, quests):
        questsData = []
        awards = {}
        for quest in quests:
            questsData.append(self.__getQuestStatusData(vehType, quest))
            if quest.isFinal():
                awards = self.__getFinalQuestAwardsVO(quest)

        return (questsData, awards)

    def __getQuestStatusData(self, vehType, quest):
        questId = quest.getID()
        state = PERSONAL_MISSIONS_ALIASES.REGION_NOT_COMPLETED
        if quest.isInProgress():
            state = PERSONAL_MISSIONS_ALIASES.REGION_IN_PROGRESS
        elif quest.isFullCompleted():
            state = PERSONAL_MISSIONS_ALIASES.REGION_FULLY_COMPLETED
        elif quest.isMainCompleted():
            state = PERSONAL_MISSIONS_ALIASES.REGION_COMPLETED
        elif not quest.isUnlocked():
            state = PERSONAL_MISSIONS_ALIASES.REGION_NOT_AVAILABLE
        if quest.isFullCompleted():
            tooltipData = {'tooltip': makeTooltip(header=quest.getUserName(), body=_ms(TOOLTIPS.PERSONALMISSIONS_MAPREGION_DESCR_EXCELLENTDONE)),
             'isSpecial': False,
             'specialArgs': []}
        else:
            tooltipData = {'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_MAP_REGION,
             'isSpecial': True,
             'specialArgs': [questId, state]}
        vo = {'id': questId,
         'state': state,
         'tooltipData': tooltipData,
         'isTokenPawned': quest.areTokensPawned(),
         'vehType': vehType}
        return vo

    def __getFinalQuestAwardsVO(self, quest):
        mainQuestAwards = quest.getBonuses(isMain=True)
        isMainObtained = quest.isMainCompleted()
        formatter = getPersonalMissionAwardsFormatter()
        mainAwards = formatter.getFormattedBonuses(mainQuestAwards, size=AWARDS_SIZES.BIG, isObtained=isMainObtained, obtainedImage=RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_OPERATIONS_STATES_COMPLETED, obtainedImageOffset=0)
        mainAwardsSmall = formatter.getFormattedBonuses(mainQuestAwards, size=AWARDS_SIZES.SMALL, isObtained=isMainObtained, obtainedImage=RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_OPERATIONS_STATES_COMPLETED, obtainedImageOffset=2)
        additionalQuestAwards = quest.getBonuses(isMain=False)
        isAdditionalObtained = quest.isFullCompleted()
        additionalAwards = formatter.getFormattedBonuses(additionalQuestAwards, size=AWARDS_SIZES.SMALL, isObtained=isAdditionalObtained, obtainedImage=RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_OPERATIONS_STATES_COMPLETED, obtainedImageOffset=2)
        return {'mainAwardsText': PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_MAINAWARD,
         'additionalAwardsText': PERSONAL_MISSIONS.PERSONALMISSIONSPLANREGION_ADDITIONALAWARD,
         'mainAwards': mainAwards,
         'mainAwardsSmall': mainAwardsSmall,
         'additionalAwards': additionalAwards}
