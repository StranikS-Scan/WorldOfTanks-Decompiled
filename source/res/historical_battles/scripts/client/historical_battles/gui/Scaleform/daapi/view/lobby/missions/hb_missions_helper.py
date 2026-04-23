# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/missions/hb_missions_helper.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.server_events.events_helpers import MISSIONS_STATES
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import _MissionInfo, _DetailedMissionInfo, getBonusLimitTooltip
from historical_battles.gui.server_events.hb_awards_formatter import getHBQuestsAwardFormatter
from historical_battles.gui.server_events.cond_formatters.hb_requirements import HBRequirementsFormatter
CARD_AWARDS_COUNT = 6
_cardAwardsFormatter = CurtailingAwardsComposer(CARD_AWARDS_COUNT, getHBQuestsAwardFormatter())
_reqsFormatter = HBRequirementsFormatter()

class HBMissionInfo(_MissionInfo):

    def _getUIDecoration(self):
        return backport.image(R.images.historical_battles.gui.maps.icons.quests.missionItem_se22())

    def _getAwards(self, mainQuest=None):
        if self._formattedBonuses is None:
            self._formattedBonuses = _cardAwardsFormatter.getFormattedBonuses(self._substituteBonuses(mainQuest))
        return {'awards': self._formattedBonuses}

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        flagIcon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.inProgressIcon()), 16, 16, -2, 8)
        statusText = backport.text(R.strings.quests.personalMission.status.inProgress())
        statusLabel = text_styles.concatStylesWithSpace(flagIcon, text_styles.neutral(statusText))
        statusTooltipData = getBonusLimitTooltip(bonusCount, bonusLimit, False, False)
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.NONE,
         'statusTooltipData': statusTooltipData}

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        rLibrary = R.images.gui.maps.icons.library
        clockIcon = icons.makeImageTag(backport.image(rLibrary.timerIcon()), 16, 16, -2, 0)
        tickIcon = icons.makeImageTag(backport.image(rLibrary.ConfirmIcon_1()), 16, 16, -2, 0)
        statusText = backport.text(R.strings.quests.quests.status.done())
        statusLabel = text_styles.concatStylesToSingleLine(clockIcon, tickIcon, text_styles.bonusAppliedText(statusText))
        header = backport.text(R.strings.tooltips.quests.unavailable.time.statusTooltip())
        body = self._getCompleteDailyStatus(R.strings.quests.missionDetails.status.completed.daily())
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.COMPLETED,
         'statusTooltipData': {'tooltip': makeTooltip(header=header, body=body),
                               'isSpecial': False,
                               'specialArgs': []}}

    def _getDisabledRequirementTooltip(self):
        return {'tooltip': TOOLTIPS_CONSTANTS.HB_UNAVAILABLE_QUEST,
         'isSpecial': True,
         'specialArgs': [self.event.getID()],
         'specialAlias': TOOLTIPS_CONSTANTS.HB_UNAVAILABLE_QUEST}


class HBDetailedMissionInfo(_DetailedMissionInfo):

    def _getUIDecoration(self):
        return backport.image(R.images.historical_battles.gui.maps.icons.quests.default_se22())

    def _getAwards(self, mainQuest=None):
        if self._formattedBonuses is None:
            self._formattedBonuses = _cardAwardsFormatter.getFormattedBonuses(self._substituteBonuses(mainQuest), AWARDS_SIZES.BIG)
        return {'awards': self._formattedBonuses}

    def _getAccountRequirements(self):
        return _reqsFormatter.format(self.event.accountReqs, self.event)

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusFields = super(HBDetailedMissionInfo, self)._getCompleteStatusFields(isLimited, bonusCount, bonusLimit)
        statusFields['status'] = MISSIONS_STATES.COMPLETED
        return statusFields

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        if isLimited and not self.event.bonusCond.isDaily() and not self.event.bonusCond.isWeekly():
            flagIcon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.inProgressIcon()), 16, 16, -2, 8)
            statusText = backport.text(R.strings.quests.personalMission.status.inProgress())
            statusLabel = text_styles.concatStylesWithSpace(flagIcon, text_styles.neutral(statusText))
            statusTooltipData = getBonusLimitTooltip(bonusCount, bonusLimit, False, False)
            return {'statusLabel': statusLabel,
             'status': MISSIONS_STATES.NONE,
             'statusTooltipData': statusTooltipData,
             'dateLabel': self._getActiveTimeDateLabel()}
        return super(HBDetailedMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
