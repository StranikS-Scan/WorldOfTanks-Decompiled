# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/constants/base_format_constants.py
from frameworks.wulf import ViewModel

class BaseFormatConstants(ViewModel):
    __slots__ = ()
    ALIGN_LEFT = 0
    ALIGN_RIGHT = 1
    ALIGN_CENTER = 4
    ALIGN_TOP = 0
    ALIGN_MIDDLE = 8
    ALIGN_BOTTOM = 2

    def __init__(self, properties=0, commands=0):
        super(BaseFormatConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(BaseFormatConstants, self)._initialize()
