# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_ammunition_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtEventAmmunitionTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WtEventAmmunitionTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getAnimation(self):
        return self._getString(3)

    def setAnimation(self, value):
        self._setString(3, value)

    def getSubtitle(self):
        return self._getString(4)

    def setSubtitle(self, value):
        self._setString(4, value)

    def getText(self):
        return self._getString(5)

    def setText(self, value):
        self._setString(5, value)

    def getAdditionalInfoText(self):
        return self._getString(6)

    def setAdditionalInfoText(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(WtEventAmmunitionTooltipViewModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('animation', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('text', '')
        self._addStringProperty('additionalInfoText', '')
