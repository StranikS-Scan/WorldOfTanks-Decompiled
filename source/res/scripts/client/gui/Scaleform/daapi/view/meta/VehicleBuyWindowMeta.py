# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleBuyWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def submit(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('submit')

    def storeSettings(self, expanded):
        """
        :param expanded:
        :return :
        """
        self._printOverrideError('storeSettings')

    def as_setGoldS(self, gold):
        """
        :param gold:
        :return :
        """
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setCreditsS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCredits(value) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setEnabledSubmitBtnS(self, enabled):
        """
        :param enabled:
        :return :
        """
        return self.flashObject.as_setEnabledSubmitBtn(enabled) if self._isDAAPIInited() else None
