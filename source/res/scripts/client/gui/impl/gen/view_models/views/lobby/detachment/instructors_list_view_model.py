# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructors_list_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_right_panel_model import DetachmentRightPanelModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_view_base_model import InstructorsViewBaseModel

class InstructorsListViewModel(InstructorsViewBaseModel):
    __slots__ = ('onInstructorHover', 'onInstructorOut')

    def __init__(self, properties=12, commands=8):
        super(InstructorsListViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(9)

    @property
    def rightPanelModel(self):
        return self._getViewModel(10)

    def getDetachmentNation(self):
        return self._getString(11)

    def setDetachmentNation(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(InstructorsListViewModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentShortInfoModel())
        self._addViewModelProperty('rightPanelModel', DetachmentRightPanelModel())
        self._addStringProperty('detachmentNation', '')
        self.onInstructorHover = self._addCommand('onInstructorHover')
        self.onInstructorOut = self._addCommand('onInstructorOut')
