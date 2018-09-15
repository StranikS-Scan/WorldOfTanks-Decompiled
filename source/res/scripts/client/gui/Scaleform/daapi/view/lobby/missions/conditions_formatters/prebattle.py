# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/conditions_formatters/prebattle.py
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters import MissionsBattleConditionsFormatter
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import formatters
from gui.server_events.cond_formatters.formatters import ConditionFormatter
from gui.shared.formatters import icons, text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
from items.vehicles import CAMOUFLAGE_KINDS
from shared_utils import findFirst
ICON_SIZE = 24
VERTICAL_SPACE = -9

class MissionsPreBattleConditionsFormatter(MissionsBattleConditionsFormatter):
    """
    Conditions formatter for 'prebattle' conditions section.
    Prebattle conditions shows requirements for battle.
    Displayed in detailed card view under main conditions and upper awards ribbon.
    Has slim visual representation which has icon and description
    """

    def __init__(self):
        super(MissionsPreBattleConditionsFormatter, self).__init__({'bonusTypes': _BattleBonusTypeFormatter(),
         'isSquad': _BattleSquadFormatter(),
         'clanMembership': _BattleClanMembershipFormatter(),
         'camouflageKind': _BattleCamouflageFormatter(),
         'geometryNames': _BattleMapFormatter()})

    def format(self, conditions, event):
        result = []
        condition = conditions.getConditions()
        groupFormatter = self.getConditionFormatter(condition.getName())
        if groupFormatter:
            groupResult = groupFormatter.format(condition, event)
            for condList in groupResult:
                result.extend(condList)

        return result


class _BattleBonusTypeFormatter(ConditionFormatter):
    """
    Formatter for BattleBonusType condition.
    Shows battle types in which player can complete quest.
    """

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            bonusTypes = condition.getValue()
            labelKey = QUESTS.MISSIONDETAILS_CONDITIONS_BATTLEBONUSTYPE
            data = formatters.packMissionBonusTypeElements(bonusTypes)
            icons = ''.join([ iconData.icon for iconData in data ])
            if len(bonusTypes) == 1 and findFirst(None, bonusTypes) in (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.RANKED, ARENA_BONUS_TYPE.EPIC_RANDOM):
                label = text_styles.main(data[0].iconLabel)
            else:
                label = text_styles.main(labelKey)
            bTypes = ', '.join([ iconData.iconLabel for iconData in data ])
            tooltipBody = i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLEBONUSTYPE_BODY, battleBonusTypes=bTypes)
            result.append(formatters.packMissionPrebattleCondition(label, icons, makeTooltip(labelKey, tooltipBody)))
        return result


class _BattleSquadFormatter(ConditionFormatter):
    """
    Formatter for BattleSquad condition.
    Shows ability to complete quest in squad.
    """

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            if condition.getValue():
                labelKey = QUESTS.MISSIONDETAILS_CONDITIONS_FORMATION_SQUAD
                label = text_styles.main(labelKey)
                iconData = formatters.packMissionFormationElement('squad')
                result.append(formatters.packMissionPrebattleCondition(label, iconData.icon, makeTooltip(labelKey, iconData.iconLabel)))
            else:
                result.append(formatters.packMissionPrebattleCondition(text_styles.main(QUESTS.DETAILS_CONDITIONS_NOTSQUAD)))
        return result


class _BattleClanMembershipFormatter(ConditionFormatter):
    """
    Formatter for BattleClanMembership condition.
    Shows ability to complete quest if player is a clanMember.
    """

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            label = '#quests:missionDetails/conditions/clanMembership/%s' % condition.getValue()
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_QUESTS_PREBATTLECONDITIONS_CLAN, width=ICON_SIZE, height=ICON_SIZE, vSpace=VERTICAL_SPACE)
            tooltip = makeTooltip(label, '#quests:details/conditions/clanMembership/%s/%s' % (condition.getValue(), condition.getArenaBonusType()))
            result.append(formatters.packMissionPrebattleCondition(text_styles.main(label), icon, tooltip=tooltip))
        return result


class _BattleCamouflageFormatter(ConditionFormatter):
    """
    Formatter for BattleCamouflage condition.
    Shows maps types in which player can complete quest.
    """

    def _format(self, condition, event):
        result = []
        if event is None or not event.isGuiDisabled():
            camos = []
            for camoTypeName, camoID in CAMOUFLAGE_KINDS.iteritems():
                if camoID in condition.getValue():
                    camos.append(formatters.packMissionCamoElement(camoTypeName))

            if camos:
                mapsTypesStr = i18n.makeString('#quests:details/conditions/mapsType')
                mapsTypeLabels = [ iconData.iconLabel for iconData in camos ]
                maps = ', '.join(mapsTypeLabels)
                tooltipBody = i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_MAPSTYPE_BODY, maps=maps)
                tooltip = makeTooltip(mapsTypesStr, tooltipBody)
                if len(camos) > 1:
                    label = text_styles.main('#quests:missionDetails/conditions/mapsType')
                    icons = ''.join([ iconData.icon for iconData in camos ])
                else:
                    iconData = findFirst(None, camos)
                    label = text_styles.main(iconData.iconLabel)
                    icons = iconData.icon
                result.append(formatters.packMissionPrebattleCondition(label, icons=icons, tooltip=tooltip))
        return result


class _BattleMapFormatter(ConditionFormatter):
    """
    Formatter for BattleMap condition.
    Shows maps names in which player can complete quest.
    """

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            mapsLabels = set()
            for atID in condition.getMaps():
                iconData = formatters.packMissionkMapElement(atID)
                if iconData is not None:
                    mapsLabels.add(iconData.iconLabel)

            if len(mapsLabels) > 1:
                labelKey = '#quests:missionDetails/conditions/maps'
                tooltipHeaderKey = '#quests:details/conditions/maps'
                if condition.isNegative():
                    tooltipHeaderKey = '#quests:missionDetails/conditions/maps/not'
                    labelKey = '#quests:details/conditions/maps/not'
            else:
                labelKey = findFirst(None, mapsLabels)
                tooltipHeaderKey = '#quests:details/conditions/map'
                if condition.isNegative():
                    tooltipHeaderKey = '#quests:details/conditions/maps/not'
                    labelKey = '#quests:missionDetails/conditions/maps/not'
            tooltipHeader = i18n.makeString(tooltipHeaderKey)
            tooltipBody = ', '.join(mapsLabels)
            tooltip = makeTooltip(tooltipHeader, tooltipBody)
            result.append(formatters.packMissionPrebattleCondition(text_styles.main(labelKey), icons=icons.makeImageTag(RES_ICONS.MAPS_ICONS_QUESTS_PREBATTLECONDITIONS_MAPS, width=ICON_SIZE, height=ICON_SIZE, vSpace=VERTICAL_SPACE), tooltip=tooltip))
        return result
