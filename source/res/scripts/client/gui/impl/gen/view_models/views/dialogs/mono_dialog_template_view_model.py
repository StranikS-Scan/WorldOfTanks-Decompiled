# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/mono_dialog_template_view_model.py
from frameworks.wulf import Array, Map, ViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import MonoDialogTemplateButtonModel

class MonoDialogTemplateViewModel(ViewModel):
    __slots__ = ('onAction',)
    ACTION_ESCAPE = 'escape'
    ACTION_CLOSE = 'close'
    ACTION_SPACE = 'space'
    ACTION_CONFIRM = 'confirm'
    ACTION_CANCEL = 'cancel'
    ACTION_SECONDARY = 'secondary'

    def __init__(self, properties=5, commands=1):
        super(MonoDialogTemplateViewModel, self).__init__(properties=properties, commands=commands)

    def getButtons(self):
        return self._getArray(0)

    def setButtons(self, value):
        self._setArray(0, value)

    @staticmethod
    def getButtonsType():
        return MonoDialogTemplateButtonModel

    def getContent(self):
        return self._getMap(1)

    def setContent(self, value):
        self._setMap(1, value)

    @staticmethod
    def getContentType():
        return (unicode, unicode)

    def getResources(self):
        return self._getMap(2)

    def setResources(self, value):
        self._setMap(2, value)

    @staticmethod
    def getResourcesType():
        return (unicode, unicode)

    def getBackgroundImage(self):
        return self._getResource(3)

    def setBackgroundImage(self, value):
        self._setResource(3, value)

    def getDimmerAlpha(self):
        return self._getReal(4)

    def setDimmerAlpha(self, value):
        self._setReal(4, value)

    def _initialize(self):
        super(MonoDialogTemplateViewModel, self)._initialize()
        self._addArrayProperty('buttons', Array())
        self._addMapProperty('content', Map(unicode, unicode))
        self._addMapProperty('resources', Map(unicode, unicode))
        self._addResourceProperty('backgroundImage', R.invalid())
        self._addRealProperty('dimmerAlpha', 0.0)
        self.onAction = self._addCommand('onAction')
