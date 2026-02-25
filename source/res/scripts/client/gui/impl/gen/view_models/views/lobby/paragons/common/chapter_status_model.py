# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/common/chapter_status_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StatusList(Enum):
    DEFAULT = 'default'
    DISABLED = 'disabled'
    ACTIVE = 'active'
    FINISHED = 'finished'
    ANNOUNCEMENT = 'announcement'
    PAUSED = 'paused'


class ChapterStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ChapterStatusModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return StatusList(self._getString(0))

    def setStatus(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(ChapterStatusModel, self)._initialize()
        self._addStringProperty('status', StatusList.DEFAULT.value)
