# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_short_info_instructor_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel

class DetachmentShortInfoInstructorModel(InstructorBaseModel):
    __slots__ = ()
    HIGHLIGHT_TYPE_NONE = 'none'
    HIGHLIGHT_TYPE_BLUE = 'blue'
    HIGHLIGHT_TYPE_RED = 'red'

    def __init__(self, properties=6, commands=0):
        super(DetachmentShortInfoInstructorModel, self).__init__(properties=properties, commands=commands)

    def getHighlightType(self):
        return self._getString(4)

    def setHighlightType(self, value):
        self._setString(4, value)

    def getHasOvercappedPerk(self):
        return self._getBool(5)

    def setHasOvercappedPerk(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(DetachmentShortInfoInstructorModel, self)._initialize()
        self._addStringProperty('highlightType', 'none')
        self._addBoolProperty('hasOvercappedPerk', False)
