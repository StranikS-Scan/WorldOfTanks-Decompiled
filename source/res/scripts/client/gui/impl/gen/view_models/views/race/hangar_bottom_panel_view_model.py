# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/hangar_bottom_panel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class HangarBottomPanelViewModel(ViewModel):
    __slots__ = ()

    @property
    def equipment(self):
        return self._getViewModel(0)

    def getHasShortPanel(self):
        return self._getBool(1)

    def setHasShortPanel(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(HangarBottomPanelViewModel, self)._initialize()
        self._addViewModelProperty('equipment', ListModel())
        self._addBoolProperty('hasShortPanel', False)
