# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/common/request_status_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class RequestStatus(IntEnum):
    INITIAL = 0
    INPROCESS = 1
    SUCCESS = 2
    FAILED = 3


class RequestStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RequestStatusModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return RequestStatus(self._getNumber(0))

    def setStatus(self, value):
        self._setNumber(0, value.value)

    def _initialize(self):
        super(RequestStatusModel, self)._initialize()
        self._addNumberProperty('status', RequestStatus.INITIAL.value)
