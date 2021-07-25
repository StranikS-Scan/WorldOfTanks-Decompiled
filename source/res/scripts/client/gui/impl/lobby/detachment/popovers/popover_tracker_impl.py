# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/popover_tracker_impl.py
from gui.impl.pub import PopOverViewImpl

class PopoverTrackerImpl(PopOverViewImpl):
    __slots__ = ('__onLifecycleChange',)

    def __init__(self, settings, onLifecycleChange, *args, **kwargs):
        super(PopoverTrackerImpl, self).__init__(settings)
        self.__onLifecycleChange = onLifecycleChange

    def _initialize(self, *args):
        super(PopoverTrackerImpl, self)._initialize()
        self.__onLifecycleChange(True)

    def _finalize(self):
        self.__onLifecycleChange(False)
        super(PopoverTrackerImpl, self)._finalize()
