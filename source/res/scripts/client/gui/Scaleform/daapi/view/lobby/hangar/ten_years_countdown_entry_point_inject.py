# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ten_years_countdown_entry_point_inject.py
from account_helpers.settings_core.settings_constants import GRAPHICS
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.TenYearsCountdownEntryPointMeta import TenYearsCountdownEntryPointMeta
from gui.impl.lobby.ten_years_countdown.ten_years_countdown_entry_point import TenYearsCountdownEntryPoint
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_EXTENDED_RENDER_PIPELINE_SETTING = 0

class TenYearsCountdownEntryPointInject(TenYearsCountdownEntryPointMeta):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(TenYearsCountdownEntryPointInject, self).__init__()
        self.__isAnimationEnabled = True

    def _populate(self):
        super(TenYearsCountdownEntryPointInject, self)._populate()
        renderPipelineSetting = self._settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        isAnimationEnabled = renderPipelineSetting == _EXTENDED_RENDER_PIPELINE_SETTING
        self.as_setAnimationEnabledS(isAnimationEnabled)
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged

    def _dispose(self):
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(TenYearsCountdownEntryPointInject, self)._dispose()

    def _makeInjectView(self):
        return TenYearsCountdownEntryPoint(flags=ViewFlags.COMPONENT, updateAnimationMethod=self.as_updateActivityS)

    def __onSettingsChanged(self, diff):
        if GRAPHICS.RENDER_PIPELINE in diff:
            isAnimationEnabled = diff.get(GRAPHICS.RENDER_PIPELINE)
            self.as_setAnimationEnabledS(isAnimationEnabled)
