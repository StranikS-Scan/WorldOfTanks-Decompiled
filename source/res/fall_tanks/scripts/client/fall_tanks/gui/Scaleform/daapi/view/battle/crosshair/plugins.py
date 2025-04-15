# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/crosshair/plugins.py
from account_helpers.settings_core.options import AimSetting
from account_helpers.settings_core.settings_constants import AIM
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import SettingsPlugin, ShotResultIndicatorPlugin
_OVERRIDE_AIM_SETTINGS_KEYS = {AIM.ARCADE, AIM.SNIPER}
_GUN_TAG_TYPE = AimSetting.OPTIONS.GUN_TAG_TYPE
_GUN_TAG_TYPE_OVERRIDES = {0: 2,
 3: 5,
 6: 8,
 9: 11,
 12: 14}

def _overrideAimSettings(settings):
    if _GUN_TAG_TYPE in settings:
        settings[_GUN_TAG_TYPE] = _GUN_TAG_TYPE_OVERRIDES.get(settings[_GUN_TAG_TYPE], settings[_GUN_TAG_TYPE])
    return settings


class FunRandomSettingsPlugin(SettingsPlugin):

    def _getSettings(self, key):
        settings = super(FunRandomSettingsPlugin, self)._getSettings(key)
        return _overrideAimSettings(settings) if settings and key in _OVERRIDE_AIM_SETTINGS_KEYS else settings


class FunRandomShotResultIndicatorPlugin(ShotResultIndicatorPlugin):

    def _getSettings(self, key):
        settings = super(FunRandomShotResultIndicatorPlugin, self)._getSettings(key)
        return _overrideAimSettings(settings) if settings and key in _OVERRIDE_AIM_SETTINGS_KEYS else settings


def updatePlugins(plugins):
    plugins['settings'] = FunRandomSettingsPlugin
    plugins['shotResultIndicator'] = FunRandomShotResultIndicatorPlugin
    return plugins
