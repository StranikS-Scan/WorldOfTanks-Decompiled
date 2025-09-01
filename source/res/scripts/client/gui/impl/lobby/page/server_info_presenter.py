# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/server_info_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.page.footer.server_info_model import ServerInfoModel, PingStatus
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from predefined_hosts import g_preDefinedHosts, PING_STATUSES
from skeletons.connection_mgr import IConnectionManager
_GUI_PING_STATUS = {PING_STATUSES.UNDEFINED: PingStatus.REQUESTED,
 PING_STATUSES.HIGH: PingStatus.HIGH,
 PING_STATUSES.NORM: PingStatus.NORM,
 PING_STATUSES.LOW: PingStatus.LOW,
 PING_STATUSES.REQUESTED: PingStatus.REQUESTED}

class ServerInfoPresenter(ViewComponent[ServerInfoModel]):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(ServerInfoPresenter, self).__init__(model=ServerInfoModel)

    @property
    def viewModel(self):
        return super(ServerInfoPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ServerInfoPresenter, self)._onLoading(*args, **kwargs)
        g_preDefinedHosts.requestPing()
        self.__updateModel()

    def _getEvents(self):
        return ((g_preDefinedHosts.onPingPerformed, self.__onServersUpdate),)

    def __onServersUpdate(self, _):
        self.__updateModel()

    def __updateModel(self):
        pingData = g_preDefinedHosts.getHostPingData(self.__connectionMgr.url)
        with self.viewModel.transaction() as model:
            model.setServerName(self.__connectionMgr.serverUserNameShort)
            pingStatus = _GUI_PING_STATUS[pingData.status]
            model.setStatus(pingStatus)
