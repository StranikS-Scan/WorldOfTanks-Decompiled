# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/AbstractPopOverView.py
from gui.Scaleform.daapi.view.meta.PopOverViewMeta import PopOverViewMeta
from gui.shared.events import HidePopoverEvent

class AbstractPopOverView(PopOverViewMeta):

    def __init__(self, ctx=None):
        super(AbstractPopOverView, self).__init__()

    def _populate(self):
        super(AbstractPopOverView, self)._populate()
        self.addListener(HidePopoverEvent.HIDE_POPOVER, self._handlerHidePopover)

    def _handlerHidePopover(self, event):
        self.destroy()

    def _dispose(self):
        self.removeListener(HidePopoverEvent.HIDE_POPOVER, self._handlerHidePopover)
        super(AbstractPopOverView, self)._dispose()
        self.fireEvent(HidePopoverEvent(HidePopoverEvent.POPOVER_DESTROYED))
