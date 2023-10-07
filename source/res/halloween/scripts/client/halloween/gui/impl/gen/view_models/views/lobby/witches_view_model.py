# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/witches_view_model.py
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
from halloween.gui.impl.gen.view_models.views.lobby.witches_model import WitchesModel

class WitchesViewModel(BaseViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=2):
        super(WitchesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def witchesWidget(self):
        return self._getViewModel(2)

    @staticmethod
    def getWitchesWidgetType():
        return WitchesModel

    def _initialize(self):
        super(WitchesViewModel, self)._initialize()
        self._addViewModelProperty('witchesWidget', WitchesModel())
        self.onClick = self._addCommand('onClick')
