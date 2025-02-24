# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/quick_training/tips_list_component_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import InfoTipModel
from gui.impl.gen.view_models.views.lobby.crew.components.component_base_model import ComponentBaseModel

class TipsListComponentModel(ComponentBaseModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TipsListComponentModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(1)

    def setItems(self, value):
        self._setArray(1, value)

    @staticmethod
    def getItemsType():
        return InfoTipModel

    def _initialize(self):
        super(TipsListComponentModel, self)._initialize()
        self._addArrayProperty('items', Array())
