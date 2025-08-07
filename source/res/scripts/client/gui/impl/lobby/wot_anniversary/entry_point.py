# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/entry_point.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.entry_point_model import EntryPointModel, State
from gui.impl.lobby.wot_anniversary.wot_anniversary_helpers import showWotAnniversaryMainView
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController

class EntryPointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return EntryPointWidget()


class EntryPointWidget(ViewImpl):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wot_anniversary.EntryPoint(), flags=ViewFlags.VIEW, model=EntryPointModel())
        super(EntryPointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointWidget, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onEnterEventLobby, self.__onEnterEventLobby),
         (self.__wotAnniversaryController.onSettingsChanged, self.__onSettingsChanged),
         (self.__wotAnniversaryController.onStartDateReached, self.__onActionByDate),
         (self.__wotAnniversaryController.onNextEnvelopeArrived, self.__onActionByDate),
         (self.__wotAnniversaryController.onEndDateReached, self.__onActionByDate))

    def _getCallbacks(self):
        return (('tokens', self.__onTokenReceived),)

    def _onLoaded(self, *args, **kwargs):
        super(EntryPointWidget, self)._onLoaded(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        availableEnvelops = self.__wotAnniversaryController.getAvailableEnvelops()
        if self.__wotAnniversaryController.getDayTokenCount() == len(self.__wotAnniversaryController.config.days):
            state = State.COMPLETED
        elif availableEnvelops == 0:
            state = State.IDLE
        else:
            state = State.AVAILABLE
        with self.viewModel.transaction() as tx:
            tx.setState(state)
            tx.setEnvelopesCount(availableEnvelops)

    def __onSettingsChanged(self):
        self.__updateModel()

    def __onActionByDate(self):
        self.__updateModel()

    def __onTokenReceived(self, diff):
        if self.__wotAnniversaryController.config.dayToken in diff:
            self.__updateModel()

    def __onEnterEventLobby(self):
        showWotAnniversaryMainView()
