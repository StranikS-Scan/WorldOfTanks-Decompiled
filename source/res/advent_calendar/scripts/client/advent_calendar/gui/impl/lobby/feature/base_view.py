# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/base_view.py
import BigWorld
from gui.Scaleform.Waiting import Waiting
from gui.impl.pub import ViewImpl

class BaseView(ViewImpl):
    WAITING_TIMEOUT = 0.3
    WAITING_NAME = 'loadContent'

    def _finalize(self):
        if Waiting.getWaiting(self.WAITING_NAME) is not None:
            Waiting.hide(self.WAITING_NAME)
        super(BaseView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        Waiting.show(self.WAITING_NAME, softStart=True, showBg=False)
        super(BaseView, self)._onLoading(args, kwargs)

    def _onShown(self):
        BigWorld.callback(self.WAITING_TIMEOUT, self._hideWaiting)
        super(BaseView, self)._onShown()

    def _hideWaiting(self):
        Waiting.hide(self.WAITING_NAME)
