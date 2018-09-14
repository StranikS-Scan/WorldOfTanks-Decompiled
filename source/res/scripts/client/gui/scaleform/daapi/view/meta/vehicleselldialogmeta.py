# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSellDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleSellDialogMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def setDialogSettings(self, isOpen):
        """
        :param isOpen:
        :return :
        """
        self._printOverrideError('setDialogSettings')

    def sell(self, vehicleData, shells, eqs, optDevices, inventory, isDismissCrew):
        """
        :param vehicleData:
        :param shells:
        :param eqs:
        :param optDevices:
        :param inventory:
        :param isDismissCrew:
        :return :
        """
        self._printOverrideError('sell')

    def setUserInput(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('setUserInput')

    def setResultCredit(self, isGold, value):
        """
        :param isGold:
        :param value:
        :return :
        """
        self._printOverrideError('setResultCredit')

    def checkControlQuestion(self, dismiss):
        """
        :param dismiss:
        :return :
        """
        self._printOverrideError('checkControlQuestion')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_checkGoldS(self, gold):
        """
        :param gold:
        :return :
        """
        return self.flashObject.as_checkGold(gold) if self._isDAAPIInited() else None

    def as_visibleControlBlockS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_visibleControlBlock(value) if self._isDAAPIInited() else None

    def as_enableButtonS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enableButton(value) if self._isDAAPIInited() else None

    def as_setControlQuestionDataS(self, isGold, value, question):
        """
        :param isGold:
        :param value:
        :param question:
        :return :
        """
        return self.flashObject.as_setControlQuestionData(isGold, value, question) if self._isDAAPIInited() else None
