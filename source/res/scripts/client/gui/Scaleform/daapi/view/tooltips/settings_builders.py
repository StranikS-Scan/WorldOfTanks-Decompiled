# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/settings_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import common
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DefaultFormatBuilder(TOOLTIPS_CONSTANTS.SETTINGS_CONTROL, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.SettingsControlTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON_UI, common.SettingsButtonTooltipData(contexts.HangarServerStatusContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_MINIMAP_CIRCLES, TOOLTIPS_CONSTANTS.SETTINGS_MINIMAP_CIRCLES_UI, common.SettingsMinimapCircles(contexts.SettingsMinimapContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_FOLLOW_ME, TOOLTIPS_CONSTANTS.SETTINGS_KEY_FOLLOW_ME_UI, common.SettingsKeyFollowMe(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_TURN_BACK, TOOLTIPS_CONSTANTS.SETTINGS_KEY_TURN_BACK_UI, common.SettingsKeyTurnBack(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_NEED_HELP, TOOLTIPS_CONSTANTS.SETTINGS_KEY_NEED_HELP_UI, common.SettingsKeyNeedHelp(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_RELOAD, TOOLTIPS_CONSTANTS.SETTINGS_KEY_RELOAD_UI, common.SettingsKeyReload(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SETTINGS_KEY_SWITCH_MODE, TOOLTIPS_CONSTANTS.SETTINGS_KEY_SWITCH_MODE_UI, common.SettingKeySwitchMode(contexts.ToolTipContext(None))))
