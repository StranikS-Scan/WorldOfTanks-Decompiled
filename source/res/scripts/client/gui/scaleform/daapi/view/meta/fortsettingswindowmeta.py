# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortSettingsWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def activateDefencePeriod(self):
        """
        :return :
        """
        self._printOverrideError('activateDefencePeriod')

    def disableDefencePeriod(self):
        """
        :return :
        """
        self._printOverrideError('disableDefencePeriod')

    def cancelDisableDefencePeriod(self):
        """
        :return :
        """
        self._printOverrideError('cancelDisableDefencePeriod')

    def as_setFortClanInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setFortClanInfo(data) if self._isDAAPIInited() else None

    def as_setMainStatusS(self, title, msg, toolTip):
        """
        :param title:
        :param msg:
        :param toolTip:
        :return :
        """
        return self.flashObject.as_setMainStatus(title, msg, toolTip) if self._isDAAPIInited() else None

    def as_setViewS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setView(value) if self._isDAAPIInited() else None

    def as_setDataForActivatedS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setDataForActivated(data) if self._isDAAPIInited() else None

    def as_setCanDisableDefencePeriodS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCanDisableDefencePeriod(value) if self._isDAAPIInited() else None

    def as_setDataForNotActivatedS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setDataForNotActivated(data) if self._isDAAPIInited() else None
