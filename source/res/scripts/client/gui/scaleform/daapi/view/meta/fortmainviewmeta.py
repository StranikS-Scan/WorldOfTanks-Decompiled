# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortMainViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortMainViewMeta(BaseDAAPIComponent):

    def onClanProfileClick(self):
        self._printOverrideError('onClanProfileClick')

    def onStatsClick(self):
        self._printOverrideError('onStatsClick')

    def onClanClick(self):
        self._printOverrideError('onClanClick')

    def onCalendarClick(self):
        self._printOverrideError('onCalendarClick')

    def onSettingClick(self):
        self._printOverrideError('onSettingClick')

    def onCreateDirectionClick(self, dirId):
        self._printOverrideError('onCreateDirectionClick')

    def onEnterBuildDirectionClick(self):
        self._printOverrideError('onEnterBuildDirectionClick')

    def onLeaveBuildDirectionClick(self):
        self._printOverrideError('onLeaveBuildDirectionClick')

    def onEnterTransportingClick(self):
        self._printOverrideError('onEnterTransportingClick')

    def onLeaveTransportingClick(self):
        self._printOverrideError('onLeaveTransportingClick')

    def onIntelligenceClick(self):
        self._printOverrideError('onIntelligenceClick')

    def onSortieClick(self):
        self._printOverrideError('onSortieClick')

    def onFirstTransportingStep(self):
        self._printOverrideError('onFirstTransportingStep')

    def onNextTransportingStep(self):
        self._printOverrideError('onNextTransportingStep')

    def onViewReady(self):
        self._printOverrideError('onViewReady')

    def onSelectOrderSelector(self, value):
        self._printOverrideError('onSelectOrderSelector')

    def as_switchModeS(self, data):
        return self.flashObject.as_switchMode(data) if self._isDAAPIInited() else None

    def as_toggleCommanderHelpS(self, show):
        return self.flashObject.as_toggleCommanderHelp(show) if self._isDAAPIInited() else None

    def as_setMainDataS(self, data):
        return self.flashObject.as_setMainData(data) if self._isDAAPIInited() else None

    def as_setClanIconIdS(self, clanIconId):
        return self.flashObject.as_setClanIconId(clanIconId) if self._isDAAPIInited() else None

    def as_setHeaderMessageS(self, message, isWrongLocalTime):
        return self.flashObject.as_setHeaderMessage(message, isWrongLocalTime) if self._isDAAPIInited() else None

    def as_setBattlesDirectionDataS(self, data):
        return self.flashObject.as_setBattlesDirectionData(data) if self._isDAAPIInited() else None

    def as_setTutorialArrowVisibilityS(self, arrowAlias, isVisible):
        return self.flashObject.as_setTutorialArrowVisibility(arrowAlias, isVisible) if self._isDAAPIInited() else None
