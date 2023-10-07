# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/document_change_dialog_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

class DocumentChangeDialogModel(DialogTemplateViewModel):
    __slots__ = ('onChangeFirstName', 'onChangeLastName')

    def __init__(self, properties=10, commands=4):
        super(DocumentChangeDialogModel, self).__init__(properties=properties, commands=commands)

    def getFirstNameIndex(self):
        return self._getNumber(6)

    def setFirstNameIndex(self, value):
        self._setNumber(6, value)

    def getLastNameIndex(self):
        return self._getNumber(7)

    def setLastNameIndex(self, value):
        self._setNumber(7, value)

    def getFirstNameList(self):
        return self._getArray(8)

    def setFirstNameList(self, value):
        self._setArray(8, value)

    @staticmethod
    def getFirstNameListType():
        return unicode

    def getLastNameList(self):
        return self._getArray(9)

    def setLastNameList(self, value):
        self._setArray(9, value)

    @staticmethod
    def getLastNameListType():
        return unicode

    def _initialize(self):
        super(DocumentChangeDialogModel, self)._initialize()
        self._addNumberProperty('firstNameIndex', 0)
        self._addNumberProperty('lastNameIndex', 0)
        self._addArrayProperty('firstNameList', Array())
        self._addArrayProperty('lastNameList', Array())
        self.onChangeFirstName = self._addCommand('onChangeFirstName')
        self.onChangeLastName = self._addCommand('onChangeLastName')
