# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/gen/view_models/views/lobby/attachments_preview_model.py
from frameworks.wulf import Array, ViewModel
from open_bundle.gui.impl.gen.view_models.views.lobby.bonus_model import BonusModel

class AttachmentsPreviewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AttachmentsPreviewModel, self).__init__(properties=properties, commands=commands)

    def getBundleType(self):
        return self._getString(0)

    def setBundleType(self, value):
        self._setString(0, value)

    def getAttachments(self):
        return self._getArray(1)

    def setAttachments(self, value):
        self._setArray(1, value)

    @staticmethod
    def getAttachmentsType():
        return BonusModel

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(AttachmentsPreviewModel, self)._initialize()
        self._addStringProperty('bundleType', '')
        self._addArrayProperty('attachments', Array())
        self._addStringProperty('name', '')
