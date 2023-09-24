# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/enlarge_barracks_dialog_model.py
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.stepper_view_model import StepperViewModel

class EnlargeBarracksDialogModel(DialogTemplateViewModel):
    __slots__ = ('onBunksCountChange',)

    def __init__(self, properties=10, commands=3):
        super(EnlargeBarracksDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def stepper(self):
        return self._getViewModel(6)

    @staticmethod
    def getStepperType():
        return StepperViewModel

    @property
    def currency(self):
        return self._getViewModel(7)

    @staticmethod
    def getCurrencyType():
        return CurrencyViewModel

    def getFreeBunksCount(self):
        return self._getNumber(8)

    def setFreeBunksCount(self, value):
        self._setNumber(8, value)

    def getAllBunksCount(self):
        return self._getNumber(9)

    def setAllBunksCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(EnlargeBarracksDialogModel, self)._initialize()
        self._addViewModelProperty('stepper', StepperViewModel())
        self._addViewModelProperty('currency', CurrencyViewModel())
        self._addNumberProperty('freeBunksCount', 0)
        self._addNumberProperty('allBunksCount', 0)
        self.onBunksCountChange = self._addCommand('onBunksCountChange')
