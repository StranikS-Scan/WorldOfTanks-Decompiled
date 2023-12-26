# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/base/notification_base.py
from gui.impl.pub import ViewImpl
from gui.prb_control import prbDispatcherProperty
from frameworks.wulf import ViewFlags, ViewSettings

class NotificationBase(ViewImpl):
    __slots__ = ('_isPopUp', '_linkageData')

    def __init__(self, resId, model, *args, **kwargs):
        settings = ViewSettings(resId)
        settings.model = model
        settings.flags = ViewFlags.VIEW
        self._isPopUp = args[0]
        self._linkageData = args[1]
        super(NotificationBase, self).__init__(settings)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @property
    def linkageData(self):
        return self._linkageData

    def _finalize(self):
        self._isPopUp = None
        self._linkageData = None
        super(NotificationBase, self)._finalize()
        return

    def _canNavigate(self):
        prbDispatcher = self.prbDispatcher
        return False if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled() else True
