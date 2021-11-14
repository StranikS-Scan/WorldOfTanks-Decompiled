# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/base_wgnp_overlay_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_overlay_view_model import BaseOverlayViewModel

class BaseWgnpOverlayViewModel(BaseOverlayViewModel):
    __slots__ = ('onConfirmClicked', 'onWarningTimer')

    def __init__(self, properties=9, commands=4):
        super(BaseWgnpOverlayViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getSubTitle(self):
        return self._getResource(3)

    def setSubTitle(self, value):
        self._setResource(3, value)

    def getWarningText(self):
        return self._getString(4)

    def setWarningText(self, value):
        self._setString(4, value)

    def getWarningCountdown(self):
        return self._getNumber(5)

    def setWarningCountdown(self, value):
        self._setNumber(5, value)

    def getIsTitleOnly(self):
        return self._getBool(6)

    def setIsTitleOnly(self, value):
        self._setBool(6, value)

    def getIsConfirmEnabled(self):
        return self._getBool(7)

    def setIsConfirmEnabled(self, value):
        self._setBool(7, value)

    def getIsConfirmVisible(self):
        return self._getBool(8)

    def setIsConfirmVisible(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(BaseWgnpOverlayViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addStringProperty('warningText', '')
        self._addNumberProperty('warningCountdown', 0)
        self._addBoolProperty('isTitleOnly', False)
        self._addBoolProperty('isConfirmEnabled', True)
        self._addBoolProperty('isConfirmVisible', True)
        self.onConfirmClicked = self._addCommand('onConfirmClicked')
        self.onWarningTimer = self._addCommand('onWarningTimer')
