# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/surprise_gift_entrypoint_view/surprise_gift_entrypoint_view.py
from frameworks.wulf import ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.pub import ViewImpl
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.surprise_gift_entrypoint_model import SurpriseGiftEntrypointModel
from gui.server_events.event_items import Quest
from gui.shared.event_dispatcher import showSurpriseGiftWindow
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbacksSetByID
from new_year.ny_helper import getNYGeneralConfig
from ny_common.settings import NY_CONFIG_NAME, NYGeneralConsts
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearController
_UPDATE_ID = 1

class SurpriseGiftEntrypointView(ViewImpl):
    __slots__ = ('__surpriseToken', '__delayer')
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.SurpriseGiftEntrypointView())
        settings.model = SurpriseGiftEntrypointModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__delayer = CallbacksSetByID()
        self.__surpriseToken = getNYGeneralConfig().getSurpriseToken()
        super(SurpriseGiftEntrypointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SurpriseGiftEntrypointView, self).getViewModel()

    def _getEvents(self):
        events = super(SurpriseGiftEntrypointView, self)._getEvents()
        return events + ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged),
         (self.__eventsCache.onSyncCompleted, self._update),
         (self.__nyController.onStateChanged, self._update),
         (self.viewModel.onClick, self.__openSurpriseWindow))

    def _onLoading(self, *args, **kwargs):
        super(SurpriseGiftEntrypointView, self)._onLoading(*args, **kwargs)
        self._update()

    def _update(self):
        surpriseTokenQuest = self.__getSurpriseTokenQuest()
        if surpriseTokenQuest is not None and self.__nyController.isEnabled():
            timeStamp = surpriseTokenQuest.getFinishTime() if surpriseTokenQuest.isAvailable().isValid else surpriseTokenQuest.getStartTime()
            remainingTime = timeStamp - time_utils.getServerUTCTime()
            self.__delayer.delayCallback(_UPDATE_ID, remainingTime, self._update)
            with self.viewModel.transaction() as model:
                model.setRemainingTime(remainingTime)
                model.setIsAvailable(surpriseTokenQuest.isAvailable().isValid)
        return

    def _finalize(self):
        self.__surpriseToken = None
        self.__delayer.clear()
        super(SurpriseGiftEntrypointView, self)._finalize()
        return

    def __onServerSettingChanged(self, diff):
        if diff.get(NY_CONFIG_NAME, {}).get(NYGeneralConsts.CONFIG_NAME) is None:
            return
        else:
            newSurpriseToken = getNYGeneralConfig().getSurpriseToken()
            if self.__surpriseToken != newSurpriseToken:
                self.__surpriseToken = newSurpriseToken
                self._update()
            return

    def __isSurpriseQuest(self, quest):
        questId = quest if isinstance(quest, str) else quest.getID()
        return questId.startswith(self.__surpriseToken)

    def __getSurpriseTokenQuest(self):
        quests = self.__eventsCache.getAllQuests(self.__isSurpriseQuest)
        return quests.get(self.__surpriseToken)

    def __openSurpriseWindow(self):
        showSurpriseGiftWindow()


class NyGiftWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return SurpriseGiftEntrypointView()
