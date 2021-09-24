# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/prebattle.py
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import formatters
from gui.server_events.cond_formatters import packSimpleTitle, packDescriptionField
from gui.server_events.cond_formatters.formatters import ConditionFormatter, MissionsBattleConditionsFormatter, SimpleMissionsFormatter
from gui.shared.formatters import icons, text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
from items.vehicles import CAMOUFLAGE_KINDS
from personal_missions_constants import CONDITION_ICON
from shared_utils import findFirst
from soft_exception import SoftException
ICON_SIZE = 32
VERTICAL_SPACE = -11

class MissionsPreBattleConditionsFormatter(MissionsBattleConditionsFormatter):

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

    def _packCondition(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def _getFormattedField(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def _packConditions(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')


class _BattleBonusTypeFormatter(ConditionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            bonusTypes = condition.getValue()
            labelKey = QUESTS.MISSIONDETAILS_CONDITIONS_BATTLEBONUSTYPE
            data = formatters.packMissionBonusTypeElements(bonusTypes)
            iconsList = ''.join([ iconData.icon for iconData in data ])
            if len(bonusTypes) == 1 and findFirst(None, bonusTypes) in (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.RANKED) or ARENA_BONUS_TYPE.EVENT_BATTLES in bonusTypes:
                label = text_styles.main(data[0].iconLabel)
            else:
                label = text_styles.main(labelKey)
            bTypes = ', '.join([ iconData.iconLabel for iconData in data ])
            tooltipBody = i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLEBONUSTYPE_BODY, battleBonusTypes=bTypes)
            result.append(formatters.packMissionPrebattleCondition(label, iconsList, makeTooltip(labelKey, tooltipBody)))
        return result


class _BattleSquadFormatter(ConditionFormatter):

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

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            label = '#quests:missionDetails/conditions/clanMembership/%s' % condition.getValue()
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_QUESTS_PREBATTLECONDITIONS_CLAN, width=ICON_SIZE, height=ICON_SIZE, vSpace=VERTICAL_SPACE)
            tooltip = makeTooltip(label, '#quests:details/conditions/clanMembership/%s/%s' % (condition.getValue(), condition.getArenaBonusType()))
            result.append(formatters.packMissionPrebattleCondition(text_styles.main(label), icon, tooltip=tooltip))
        return result


class _BattleCamouflageFormatter(ConditionFormatter):

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
                    iconsData = ''.join([ iconData.icon for iconData in camos ])
                else:
                    iconData = findFirst(None, camos)
                    label = text_styles.main(iconData.iconLabel)
                    iconsData = iconData.icon
                result.append(formatters.packMissionPrebattleCondition(label, icons=iconsData, tooltip=tooltip))
        return result


class _BattleMapFormatter(ConditionFormatter):

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


class _InstalledModulesGroupFormatter(ConditionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            installedItemsConditionFormatter = _InstalledItemsConditionFormatter()
            for c in condition.getModulesConditions():
                result.extend(installedItemsConditionFormatter.format(c, event))

        return result


class _InstalledItemsConditionFormatter(SimpleMissionsFormatter):

    @classmethod
    def _getTitle(cls, condition):
        return packSimpleTitle(QUESTS.DETAILS_CONDITIONS_INSTALLEDMODULE_TITLE)

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.PREPARATION

    def _getDescription(self, condition):
        key = '#quests:details/conditions/installedModule/%s' % condition.getItemType()
        moduleNames = ', '.join([ item.userName for item in condition.getItemsList() ])
        if condition.isNegative():
            key = '%s/not' % key
        return packDescriptionField(i18n.makeString(key, moduleNames=moduleNames))


class _CorrespondedCamouflageFormatter(SimpleMissionsFormatter):

    def _getDescription(self, condition):
        key = 'installedCamouflage' if condition.getValue() else 'noInstalledCamouflage'
        return packDescriptionField(i18n.makeString('#quests:details/conditions/%s' % key))

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.PREPARATION

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return packSimpleTitle(QUESTS.DETAILS_CONDITIONS_INSTALLEDCAMOUFLAGE_TITLE)
