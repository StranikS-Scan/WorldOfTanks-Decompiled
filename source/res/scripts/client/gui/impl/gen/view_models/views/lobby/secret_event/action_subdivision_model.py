# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_subdivision_model.py
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.subdivision_model import SubdivisionModel

class ActionSubdivisionModel(ActionMenuModel):
    __slots__ = ('onBuyClick',)

    def __init__(self, properties=6, commands=4):
        super(ActionSubdivisionModel, self).__init__(properties=properties, commands=commands)

    @property
    def generals(self):
        return self._getViewModel(4)

    def getRevision(self):
        return self._getNumber(5)

    def setRevision(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ActionSubdivisionModel, self)._initialize()
        self._addViewModelProperty('generals', ListModel())
        self._addNumberProperty('revision', 0)
        self.onBuyClick = self._addCommand('onBuyClick')
