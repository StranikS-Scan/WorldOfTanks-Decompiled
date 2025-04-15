# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/notification_base.py
from gui.impl.pub import ViewImpl
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.lobby.gf_notifications.cache import getCache
from gui.prb_control.entities.base.listener import IPrbListener

class NotificationBase(ViewImpl, IPrbListener):
    __slots__ = ('_isPopUp', '_linkageData')

    def __init__(self, resId, model, *args, **kwargs):
        settings = ViewSettings(resId)
        settings.model = model
        settings.flags = ViewFlags.VIEW
        self._isPopUp = args[0]
        self._linkageData = args[1]
        super(NotificationBase, self).__init__(settings)

    @property
    def linkageData(self):
        return self._linkageData

    def _onLoading(self, *args, **kwargs):
        super(NotificationBase, self)._onLoading(*args, **kwargs)
        self._update()

    def _update(self):
        raise NotImplementedError

    def _getEvents(self):
        events = super(NotificationBase, self)._getEvents()
        return events + ((g_playerEvents.onEnqueued, self.__updatePrebattleControls), (g_playerEvents.onDequeued, self.__updatePrebattleControls))

    def _finalize(self):
        self._isPopUp = None
        self._linkageData = None
        super(NotificationBase, self)._finalize()
        return

    def _getPayload(self):
        data = self._linkageData.toDict()
        return getCache().getPayload(data['gfDataID'])

    def _canNavigate(self):
        prbDispatcher = self.prbDispatcher
        return False if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled() else True

    def __updatePrebattleControls(self, *_):
        self._update()
