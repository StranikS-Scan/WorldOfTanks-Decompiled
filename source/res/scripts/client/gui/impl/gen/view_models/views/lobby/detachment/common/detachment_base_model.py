# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_base_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_model import RoseModel

class DetachmentBaseModel(DetachmentShortInfoModel):
    __slots__ = ()

    def __init__(self, properties=33, commands=1):
        super(DetachmentBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def roseModel(self):
        return self._getViewModel(31)

    def getLocation(self):
        return self._getString(32)

    def setLocation(self, value):
        self._setString(32, value)

    def _initialize(self):
        super(DetachmentBaseModel, self)._initialize()
        self._addViewModelProperty('roseModel', RoseModel())
        self._addStringProperty('location', '')
