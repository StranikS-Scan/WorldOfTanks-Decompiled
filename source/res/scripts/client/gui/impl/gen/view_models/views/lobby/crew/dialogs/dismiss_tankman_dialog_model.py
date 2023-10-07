# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dismiss_tankman_dialog_model.py
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel

class DismissTankmanDialogModel(DialogTemplateViewModel):
    __slots__ = ('onInputChanged',)

    def __init__(self, properties=14, commands=3):
        super(DismissTankmanDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankman(self):
        return self._getViewModel(6)

    @staticmethod
    def getTankmanType():
        return TankmanModel

    @property
    def replacedTankman(self):
        return self._getViewModel(7)

    @staticmethod
    def getReplacedTankmanType():
        return TankmanModel

    def getIsRecoveryPossible(self):
        return self._getBool(8)

    def setIsRecoveryPossible(self, value):
        self._setBool(8, value)

    def getIsLimitReached(self):
        return self._getBool(9)

    def setIsLimitReached(self, value):
        self._setBool(9, value)

    def getDismissPeriod(self):
        return self._getNumber(10)

    def setDismissPeriod(self, value):
        self._setNumber(10, value)

    def getPerkName(self):
        return self._getString(11)

    def setPerkName(self, value):
        self._setString(11, value)

    def getPerkLevel(self):
        return self._getNumber(12)

    def setPerkLevel(self, value):
        self._setNumber(12, value)

    def getTrainingLevel(self):
        return self._getNumber(13)

    def setTrainingLevel(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(DismissTankmanDialogModel, self)._initialize()
        self._addViewModelProperty('tankman', TankmanModel())
        self._addViewModelProperty('replacedTankman', TankmanModel())
        self._addBoolProperty('isRecoveryPossible', False)
        self._addBoolProperty('isLimitReached', False)
        self._addNumberProperty('dismissPeriod', 0)
        self._addStringProperty('perkName', '')
        self._addNumberProperty('perkLevel', 0)
        self._addNumberProperty('trainingLevel', 0)
        self.onInputChanged = self._addCommand('onInputChanged')
