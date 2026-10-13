# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/complexity_level_widget.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from portal.gui.impl.gen.view_models.views.lobby.portal_complexity_level import PortalComplexityLevel

class ComplexityLevelWidget(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ComplexityLevelWidget, self).__init__(properties=properties, commands=commands)

    @property
    def levels(self):
        return self._getViewModel(0)

    @staticmethod
    def getLevelsType():
        return PortalComplexityLevel

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ComplexityLevelWidget, self)._initialize()
        self._addViewModelProperty('levels', UserListModel())
        self._addBoolProperty('isEnabled', True)
