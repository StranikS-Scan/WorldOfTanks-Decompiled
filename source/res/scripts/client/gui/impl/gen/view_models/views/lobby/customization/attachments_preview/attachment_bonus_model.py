# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/attachments_preview/attachment_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class AttachmentBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(AttachmentBonusModel, self).__init__(properties=properties, commands=commands)

    def getOverlayType(self):
        return self._getString(9)

    def setOverlayType(self, value):
        self._setString(9, value)

    def getId(self):
        return self._getNumber(10)

    def setId(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(AttachmentBonusModel, self)._initialize()
        self._addStringProperty('overlayType', '')
        self._addNumberProperty('id', 0)
