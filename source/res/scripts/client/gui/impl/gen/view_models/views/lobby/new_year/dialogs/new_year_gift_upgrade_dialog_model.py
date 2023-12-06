# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/new_year_gift_upgrade_dialog_model.py
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class NewYearGiftUpgradeDialogModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=3):
        super(NewYearGiftUpgradeDialogModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(11)

    def setLevel(self, value):
        self._setNumber(11, value)

    def getCost(self):
        return self._getNumber(12)

    def setCost(self, value):
        self._setNumber(12, value)

    def getShortage(self):
        return self._getNumber(13)

    def setShortage(self, value):
        self._setNumber(13, value)

    def getTokensCount(self):
        return self._getNumber(14)

    def setTokensCount(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(NewYearGiftUpgradeDialogModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('cost', 0)
        self._addNumberProperty('shortage', 0)
        self._addNumberProperty('tokensCount', 0)
