# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/post_progression_widget_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.components.component_base_model import ComponentBaseModel

class PostProgressionWidgetModel(ComponentBaseModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=5, commands=1):
        super(PostProgressionWidgetModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getProgressCurrent(self):
        return self._getNumber(2)

    def setProgressCurrent(self, value):
        self._setNumber(2, value)

    def getProgressMax(self):
        return self._getNumber(3)

    def setProgressMax(self, value):
        self._setNumber(3, value)

    def getHasWarning(self):
        return self._getBool(4)

    def setHasWarning(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(PostProgressionWidgetModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('progressCurrent', 0)
        self._addNumberProperty('progressMax', 0)
        self._addBoolProperty('hasWarning', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
