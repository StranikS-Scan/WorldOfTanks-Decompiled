# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/attachments_preview/attachments_preview_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.customization.attachments_preview.attachment_bonus_model import AttachmentBonusModel

class AttachmentsPreviewFeature(Enum):
    CHALLENGES = 'challenges'
    OPEN_BUNDLE = 'open_bundle'
    BATTLE_PASS = 'battle_pass'


class AttachmentsPreviewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AttachmentsPreviewModel, self).__init__(properties=properties, commands=commands)

    def getAttachmentSetID(self):
        return self._getString(0)

    def setAttachmentSetID(self, value):
        self._setString(0, value)

    def getFeature(self):
        return self._getString(1)

    def setFeature(self, value):
        self._setString(1, value)

    def getAttachments(self):
        return self._getArray(2)

    def setAttachments(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAttachmentsType():
        return AttachmentBonusModel

    def _initialize(self):
        super(AttachmentsPreviewModel, self)._initialize()
        self._addStringProperty('attachmentSetID', '')
        self._addStringProperty('feature', '')
        self._addArrayProperty('attachments', Array())
