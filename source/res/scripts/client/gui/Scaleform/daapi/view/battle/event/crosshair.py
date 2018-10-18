# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/crosshair.py
from account_helpers.settings_core.settings_constants import AIM
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin, CrosshairPlugin, ShotResultIndicatorPlugin
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
_SETTINGS_KEY_TO_VIEW_ID = {AIM.ARCADE: CROSSHAIR_VIEW_ID.ARCADE,
 AIM.SNIPER: CROSSHAIR_VIEW_ID.SNIPER}
_SETTINGS_KEYS = set(_SETTINGS_KEY_TO_VIEW_ID.keys())

class PveAmmoPlugin(AmmoPlugin):

    def _setup(self, ctrl, hideAmmoCounter=False, isReplayPlaying=False):
        super(PveAmmoPlugin, self)._setup(ctrl, hideAmmoCounter=True, isReplayPlaying=True)


class PveSettingsPlugin(CrosshairPlugin):

    def start(self):
        self._parentObj.setSettings(self._makeSettingsVO())

    def _makeSettingsVO(self):
        data = {}
        for mode in _SETTINGS_KEYS:
            _settings = self.settingsCore.getSetting(mode)
            if _settings is not None:
                data[_SETTINGS_KEY_TO_VIEW_ID[mode]] = {'centerType': 14,
                 'mixingType': 8,
                 'netColor': 2,
                 'centerAlphaValue': 0,
                 'gunTagType': 9,
                 'netType': 3,
                 'netAlphaValue': 1}

        return data


class PveShotResultIndicatorPlugin(ShotResultIndicatorPlugin):

    def __init__(self, parentObj):
        super(PveShotResultIndicatorPlugin, self).__init__(parentObj)
        self._shotResultTypes = GUN_MARKER_VIEW_CONSTANTS.GUN_TAG_SHOT_RESULT_TYPES_EVENT
