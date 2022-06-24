# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/tankman_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_icon_model import TankmanTooltipViewIconModel

class TankmanTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(TankmanTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def icons(self):
        return self._getViewModel(0)

    @staticmethod
    def getIconsType():
        return TankmanTooltipViewIconModel

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getSubtitle(self):
        return self._getString(2)

    def setSubtitle(self, value):
        self._setString(2, value)

    def getMainIcon(self):
        return self._getString(3)

    def setMainIcon(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getIconsTitle(self):
        return self._getString(5)

    def setIconsTitle(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(TankmanTooltipViewModel, self)._initialize()
        self._addViewModelProperty('icons', UserListModel())
        self._addStringProperty('title', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('mainIcon', '')
        self._addStringProperty('description', '')
        self._addStringProperty('iconsTitle', '')
