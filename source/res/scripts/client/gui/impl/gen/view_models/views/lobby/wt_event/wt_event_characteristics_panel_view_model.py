# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_characteristics_panel_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.property_model import PropertyModel

class WtEventCharacteristicsPanelViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WtEventCharacteristicsPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def pros(self):
        return self._getViewModel(0)

    @property
    def cons(self):
        return self._getViewModel(1)

    def getSpecialInfo(self):
        return self._getResource(2)

    def setSpecialInfo(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(WtEventCharacteristicsPanelViewModel, self)._initialize()
        self._addViewModelProperty('pros', UserListModel())
        self._addViewModelProperty('cons', UserListModel())
        self._addResourceProperty('specialInfo', R.invalid())
