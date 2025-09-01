# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/dialog_template_param_view_model.py
from frameworks.wulf import ViewModel

class DialogTemplateParamViewModel(ViewModel):
    __slots__ = ('onAction', 'onClose')

    def __init__(self, properties=2, commands=2):
        super(DialogTemplateParamViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getParams(self):
        return self._getString(1)

    def setParams(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(DialogTemplateParamViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('params', '{}')
        self.onAction = self._addCommand('onAction')
        self.onClose = self._addCommand('onClose')
