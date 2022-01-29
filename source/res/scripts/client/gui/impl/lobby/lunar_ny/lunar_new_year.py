# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_new_year.py
import typing
from PlayerEvents import g_playerEvents
from account_helpers import isLongDisconnectedFromCenter
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import MainViewModel, Tab
from gui.impl.lobby.lunar_ny.lunar_main_view_components import MainViewComponents
from gui.impl.pub import ViewImpl
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import updateCharmBonusesModel
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_TAB, SHOW_TAB_EVENT
from lunar_ny.lunar_ny_sounds import LUNAR_NY_MAIN_SOUND_SPACE
from lunar_ny_common.settings_constants import LUNAR_NY_PDATA_KEY
from uilogging.lunar_ny.loggers import LunarSideBarLogger
if typing.TYPE_CHECKING:
    from gui.shared.events import HasCtxEvent

class LunarNYMainView(ViewImpl[MainViewModel]):
    __slots__ = ('__components', '__initCtx')
    __lunarNYController = dependency.descriptor(ILunarNYController)
    _COMMON_SOUND_SPACE = LUNAR_NY_MAIN_SOUND_SPACE

    def __init__(self, layout=R.views.lobby.lunar_ny.LunarNewYear(), initCtx=None):
        settings = ViewSettings(layout)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MainViewModel()
        super(LunarNYMainView, self).__init__(settings)
        self.__initCtx = initCtx if initCtx is not None else {}
        self.__components = MainViewComponents(self.viewModel, self)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return self.__components.createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(LunarNYMainView, self)._onLoading(*args, **kwargs)
        self.viewModel.hold()
        self.__components.onLoading(self.__initCtx)
        if MAIN_VIEW_INIT_CONTEXT_TAB in self.__initCtx:
            self.viewModel.setCurrentTab(self.__initCtx[MAIN_VIEW_INIT_CONTEXT_TAB])
        else:
            self.viewModel.setCurrentTab(Tab.SENDENVELOPES)
        self.viewModel.setIsGiftSystemEnabled(self.__giftSystemActive())
        self.viewModel.setIsLongDisconnectedFromCenter(isLongDisconnectedFromCenter())
        self.__updateCharmBonuses(self.viewModel)
        self.viewModel.commit()

    def _onLoaded(self, *args, **kwargs):
        super(LunarNYMainView, self)._onLoaded(*args, **kwargs)
        self.__components.onLoaded()

    def _initialize(self, *args, **kwargs):
        super(LunarNYMainView, self)._initialize(*args, **kwargs)
        self.__components.initialize()
        self.viewModel.onViewedTab += self.__onViewedTab
        self.viewModel.onClose += self.__exitEvent
        g_clientUpdateManager.addCallback(LUNAR_NY_PDATA_KEY, self.__lunarPDataUpdated)
        self.__lunarNYController.onStatusChange += self.__onEventStatusChange
        self.__lunarNYController.giftSystem.onGiftSystemSettingsUpdated += self.__onGiftSystemSettingsUpdated
        g_eventBus.addListener(SHOW_TAB_EVENT, self.__onShowTabEvent)
        g_playerEvents.onCenterIsLongDisconnected += self.__onCenterIsLongDisconnected

    def _finalize(self):
        g_playerEvents.onCenterIsLongDisconnected += self.__onCenterIsLongDisconnected
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lunarNYController.giftSystem.onGiftSystemSettingsUpdated -= self.__onGiftSystemSettingsUpdated
        self.__lunarNYController.onStatusChange -= self.__onEventStatusChange
        self.viewModel.onClose -= self.__exitEvent
        self.viewModel.onViewedTab -= self.__onViewedTab
        g_eventBus.removeListener(SHOW_TAB_EVENT, self.__onShowTabEvent)
        self.__components.finalize()
        super(LunarNYMainView, self)._finalize()

    def __onViewedTab(self, args):
        receivedTab = Tab(args.get('tab'))
        self.viewModel.setCurrentTab(receivedTab)
        self.__components.onCurrentTabChange(receivedTab)
        if receivedTab == Tab.STOREENVELOPES:
            LunarSideBarLogger().logClick()

    def __updateCharmBonuses(self, model):
        charmBonuses = self.__lunarNYController.charms.getCharmBonuses()
        updateCharmBonusesModel(charmBonuses, model.bonuses)

    def __lunarPDataUpdated(self, _):
        self.__updateCharmBonuses(self.viewModel)

    def __onEventStatusChange(self):
        if not self.__lunarNYController.isActive():
            self.__exitEvent()
        else:
            self.viewModel.setIsGiftSystemEnabled(self.__giftSystemActive())

    def __onShowTabEvent(self, event):
        self.viewModel.setCurrentTab(event.ctx)
        self.__components.onCurrentTabChange(event.ctx)

    def __exitEvent(self, *_):
        showHangar()

    def __onGiftSystemSettingsUpdated(self):
        self.viewModel.setIsGiftSystemEnabled(self.__giftSystemActive())

    def __onCenterIsLongDisconnected(self, isLongDisconnected):
        self.viewModel.setIsLongDisconnectedFromCenter(isLongDisconnected)

    def __giftSystemActive(self):
        return self.__lunarNYController.isGiftSystemEventActive() and not self.__lunarNYController.giftSystem.isAllGiftDisabledForSend()
