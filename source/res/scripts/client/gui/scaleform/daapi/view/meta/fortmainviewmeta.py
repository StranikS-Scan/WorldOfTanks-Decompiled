# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortMainViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortMainViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onClanProfileClick(self):
        """
        :return :
        """
        self._printOverrideError('onClanProfileClick')

    def onStatsClick(self):
        """
        :return :
        """
        self._printOverrideError('onStatsClick')

    def onClanClick(self):
        """
        :return :
        """
        self._printOverrideError('onClanClick')

    def onCalendarClick(self):
        """
        :return :
        """
        self._printOverrideError('onCalendarClick')

    def onSettingClick(self):
        """
        :return :
        """
        self._printOverrideError('onSettingClick')

    def onCreateDirectionClick(self, dirId):
        """
        :param dirId:
        :return :
        """
        self._printOverrideError('onCreateDirectionClick')

    def onEnterBuildDirectionClick(self):
        """
        :return :
        """
        self._printOverrideError('onEnterBuildDirectionClick')

    def onLeaveBuildDirectionClick(self):
        """
        :return :
        """
        self._printOverrideError('onLeaveBuildDirectionClick')

    def onEnterTransportingClick(self):
        """
        :return :
        """
        self._printOverrideError('onEnterTransportingClick')

    def onLeaveTransportingClick(self):
        """
        :return :
        """
        self._printOverrideError('onLeaveTransportingClick')

    def onIntelligenceClick(self):
        """
        :return :
        """
        self._printOverrideError('onIntelligenceClick')

    def onSortieClick(self):
        """
        :return :
        """
        self._printOverrideError('onSortieClick')

    def onFirstTransportingStep(self):
        """
        :return :
        """
        self._printOverrideError('onFirstTransportingStep')

    def onNextTransportingStep(self):
        """
        :return :
        """
        self._printOverrideError('onNextTransportingStep')

    def onViewReady(self):
        """
        :return :
        """
        self._printOverrideError('onViewReady')

    def onSelectOrderSelector(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('onSelectOrderSelector')

    def as_switchModeS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_switchMode(data) if self._isDAAPIInited() else None

    def as_toggleCommanderHelpS(self, show):
        """
        :param show:
        :return :
        """
        return self.flashObject.as_toggleCommanderHelp(show) if self._isDAAPIInited() else None

    def as_setMainDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setMainData(data) if self._isDAAPIInited() else None

    def as_setClanIconIdS(self, clanIconId):
        """
        :param clanIconId:
        :return :
        """
        return self.flashObject.as_setClanIconId(clanIconId) if self._isDAAPIInited() else None

    def as_setHeaderMessageS(self, message, isWrongLocalTime):
        """
        :param message:
        :param isWrongLocalTime:
        :return :
        """
        return self.flashObject.as_setHeaderMessage(message, isWrongLocalTime) if self._isDAAPIInited() else None

    def as_setBattlesDirectionDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setBattlesDirectionData(data) if self._isDAAPIInited() else None

    def as_setTutorialArrowVisibilityS(self, arrowAlias, isVisible):
        """
        :param arrowAlias:
        :param isVisible:
        :return :
        """
        return self.flashObject.as_setTutorialArrowVisibility(arrowAlias, isVisible) if self._isDAAPIInited() else None
