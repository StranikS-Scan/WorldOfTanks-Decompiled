# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/extended_node_state_flags.py
from frameworks.wulf import ViewModel

class ExtendedNodeStateFlags(ViewModel):
    __slots__ = ()
    DEFAULT = 1
    RESET_FINISHED_PARAGONS = 2
    LOCKED_BY_PARAGONS = 4

    def __init__(self, properties=0, commands=0):
        super(ExtendedNodeStateFlags, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ExtendedNodeStateFlags, self)._initialize()
