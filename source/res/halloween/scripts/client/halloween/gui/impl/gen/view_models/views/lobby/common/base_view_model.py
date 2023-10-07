# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/base_view_model.py
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.phase_item_model import PhaseItemModel

class BaseViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(BaseViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def phase(self):
        return self._getViewModel(0)

    @staticmethod
    def getPhaseType():
        return PhaseItemModel

    def getSelectedPhase(self):
        return self._getNumber(1)

    def setSelectedPhase(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BaseViewModel, self)._initialize()
        self._addViewModelProperty('phase', PhaseItemModel())
        self._addNumberProperty('selectedPhase', 0)
        self.onClose = self._addCommand('onClose')
