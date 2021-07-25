# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_info_animated_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel

class DetachmentInfoAnimatedModel(DetachmentShortInfoModel):
    __slots__ = ()

    def __init__(self, properties=33, commands=1):
        super(DetachmentInfoAnimatedModel, self).__init__(properties=properties, commands=commands)

    def getGainLevels(self):
        return self._getNumber(31)

    def setGainLevels(self, value):
        self._setNumber(31, value)

    def getExperienceOverflow(self):
        return self._getNumber(32)

    def setExperienceOverflow(self, value):
        self._setNumber(32, value)

    def _initialize(self):
        super(DetachmentInfoAnimatedModel, self)._initialize()
        self._addNumberProperty('gainLevels', 0)
        self._addNumberProperty('experienceOverflow', 0)
