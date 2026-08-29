# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_ammunition_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WtAmmunitionTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(WtAmmunitionTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(0)

    def setIconName(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getSubtitle(self):
        return self._getString(3)

    def setSubtitle(self, value):
        self._setString(3, value)

    def getText(self):
        return self._getString(4)

    def setText(self, value):
        self._setString(4, value)

    def getAdditionalInfoText(self):
        return self._getString(5)

    def setAdditionalInfoText(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(WtAmmunitionTooltipViewModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('text', '')
        self._addStringProperty('additionalInfoText', '')
