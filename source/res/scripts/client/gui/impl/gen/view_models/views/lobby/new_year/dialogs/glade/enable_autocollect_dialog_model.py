# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/glade/enable_autocollect_dialog_model.py
from frameworks.wulf import ViewModel

class EnableAutocollectDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=5, commands=2):
        super(EnableAutocollectDialogModel, self).__init__(properties=properties, commands=commands)

    def getIsManualCollectAvailable(self):
        return self._getBool(0)

    def setIsManualCollectAvailable(self, value):
        self._setBool(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getCredits(self):
        return self._getNumber(2)

    def setCredits(self, value):
        self._setNumber(2, value)

    def getDayStartTime(self):
        return self._getNumber(3)

    def setDayStartTime(self, value):
        self._setNumber(3, value)

    def getSecondCollectCooldown(self):
        return self._getNumber(4)

    def setSecondCollectCooldown(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(EnableAutocollectDialogModel, self)._initialize()
        self._addBoolProperty('isManualCollectAvailable', True)
        self._addNumberProperty('price', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('dayStartTime', 0)
        self._addNumberProperty('secondCollectCooldown', 0)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
