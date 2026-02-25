# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/settings_builders.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_model import PerkType
from gui.Scaleform.daapi.view.tooltips.tankman_builders import CrewPerkTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import common
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder, TooltipWindowBuilder
__all__ = ('getTooltipBuilders',)

class SituationalPerkTooltipData(CrewPerkTooltipData):

    def __init__(self, context):
        super(SituationalPerkTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.SETTINGS_SITUATIONAL_PERK)

    def getDisplayableData(self, skillName, *args, **kwargs):
        return super(SituationalPerkTooltipData, self).getDisplayableData(skillName, None, tankmanId=None, showAdditionalInfo=False, showDetailedTooltip=True, isAdvancedTooltipEnable=False, customSkillType=PerkType.EMPTY, *args, **kwargs)


def getTooltipBuilders():
    return (DefaultFormatBuilder(TOOLTIPS_CONSTANTS.SETTINGS_CONTROL, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.SettingsControlTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON_UI, common.SettingsButtonTooltipData(contexts.HangarServerStatusContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SERVERS_INFO, TOOLTIPS_CONSTANTS.SERVERS_INFO_UI, common.ServersInfoTooltipData(contexts.HangarServerStatusContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_MINIMAP_CIRCLES, TOOLTIPS_CONSTANTS.SETTINGS_MINIMAP_CIRCLES_UI, common.SettingsMinimapCircles(contexts.SettingsMinimapContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_SWITCH_MODE, TOOLTIPS_CONSTANTS.SETTINGS_KEY_SWITCH_MODE_UI, common.SettingKeySwitchMode(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_SPECIAL_ABILITY, TOOLTIPS_CONSTANTS.SETTINGS_KEY_SPECIAL_ABILITY_UI, common.SettingKeySpecialAbility(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_HIGHLIGHTLOCATION, TOOLTIPS_CONSTANTS.SETTINGS_KEY_HIGHLIGHTLOCATION_UI, common.SettingsKeyHighlightLocation(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_HIGHLIGHTTARGET, TOOLTIPS_CONSTANTS.SETTINGS_KEY_HIGHLIGHTTARGET_UI, common.SettingsKeyHighlightTarget(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_SHOWRADIALMENU, TOOLTIPS_CONSTANTS.SETTINGS_KEY_SHOWRADIALMENU_UI, common.SettingsKeyShowRadialMenu(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_SHOW_LOCATION_MARKERS, TOOLTIPS_CONSTANTS.SETTINGS_SHOW_LOCATION_MARKERS_UI, common.SettingsShowLocationMarkers(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_CHARGE_FIRE, TOOLTIPS_CONSTANTS.SETTINGS_KEY_CHARGE_FIRE_UI, common.SettingsKeyChargeFire(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_SWITCH_EQUIPMENT, TOOLTIPS_CONSTANTS.SETTINGS_SWITCH_EQUIPMENT_UI, common.SettingsSwitchEquipment(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.SETTINGS_SITUATIONAL_PERK, None, SituationalPerkTooltipData(contexts.ToolTipContext(None))))
