# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/conditions_formatters/tooltips.py
from constants import EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters import packText, getSeparator, intersperse, requirements
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters.requirements import prepareAccountConditionsGroup
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.cond_formatters.formatters import ConditionFormatter, ConditionsFormatter
from gui.server_events.conditions import GROUP_TYPE
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache

def reqStyle(_):
    return text_styles.main


class MissionsAccountRequirementsFormatter(ConditionsFormatter):
    """ Formatter for the account requirements block in the detailed quest window.
    """

    def __init__(self):
        super(MissionsAccountRequirementsFormatter, self).__init__({'token': _TokenRequirementFormatter(),
         'premiumAccount': requirements.PremiumAccountFormatter(),
         'inClan': requirements.InClanRequirementFormatter(),
         'igrType': requirements.IgrTypeRequirementFormatter(),
         'GR': requirements.GlobalRatingRequirementFormatter(),
         'accountDossier': requirements.AccountDossierRequirementFormatter(),
         'vehiclesUnlocked': requirements.VehiclesRequirementFormatter(),
         'vehiclesOwned': requirements.VehiclesRequirementFormatter(),
         'hasReceivedMultipliedXP': requirements.HasReceivedMultipliedXPFormatter()})

    def format(self, conditions, event):
        if event.isGuiDisabled():
            return {}
        group = prepareAccountConditionsGroup(conditions, event)
        requirements = self._format(group, event)
        return requirements

    def _format(self, group, event, isNested=False):
        """ Recursive format method that should be called for each condition group.
        """
        result = []
        separator = getSeparator(group.getName())
        for condition in group.getSortedItems():
            branch = []
            if not condition.isAvailable():
                conditionName = condition.getName()
                if conditionName in GROUP_TYPE.ALL():
                    branch = self._format(condition, event, isNested=True)
                else:
                    fmt = self.getConditionFormatter(conditionName)
                    if fmt:
                        branch = fmt.format(condition, event, reqStyle)
                result.extend(branch)
                if not isNested and branch:
                    branch[0].update(bullet=TOOLTIPS.QUESTS_UNAVAILABLE_BULLET)

        if separator:
            result = intersperse(result, packText(text_styles.standard(separator)))
        return result


class _TokenRequirementFormatter(ConditionFormatter):
    eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def format(cls, condition, event, styler=reqStyle):
        style = styler(condition.isAvailable())
        result = []
        if event.getType() not in EVENT_TYPE.LIKE_BATTLE_QUESTS + EVENT_TYPE.LIKE_TOKEN_QUESTS:
            return result
        tokensNeedCount = condition.getNeededCount()
        return [packText(style(_ms(TOOLTIPS.QUESTS_UNAVAILABLE_TOKEN, tokenName=text_styles.neutral(condition.getUserName()), count=tokensNeedCount)))]
