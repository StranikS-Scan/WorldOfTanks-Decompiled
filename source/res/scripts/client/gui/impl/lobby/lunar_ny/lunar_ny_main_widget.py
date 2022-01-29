# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_main_widget.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import updateCharmBonusesModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.lunar_ny_main_widget_model import LunarNyMainWidgetModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showLunarNYMainView
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_TAB
from lunar_ny_common.settings_constants import LUNAR_NY_PDATA_KEY
from uilogging.lunar_ny.loggers import LunarWidgetLogger
from gui.impl.lobby.lunar_ny.tooltips.widget_tooltip_new_envelopes import WidgetTooltipNewEnvelopes
from gui.impl.lobby.lunar_ny.tooltips.widget_tooltip import WidgetTooltip

class LunarNYMainWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return LunarNYMainWidget()


class LunarNYMainWidget(ViewImpl, IGlobalListener):
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.lunar_ny.LunarNYMainWidget())
        settings.flags = ViewFlags.COMPONENT
        settings.model = LunarNyMainWidgetModel()
        super(LunarNYMainWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.lunar_ny.tooltips.WidgetTooltip():
            return WidgetTooltip(contentID)
        else:
            return WidgetTooltipNewEnvelopes(contentID) if contentID == R.views.lobby.lunar_ny.tooltips.WidgetTooltipNewEnvelopes() else None

    def onPrbEntitySwitched(self):
        self.__updateBonusesVisibility()

    def _initialize(self):
        super(LunarNYMainWidget, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.viewModel.onEnvelopeClick += self.__onEnvelopeClick

    def _onLoading(self, *args, **kwargs):
        super(LunarNYMainWidget, self)._onLoading()
        with self.viewModel.transaction() as model:
            self.__updateCharmBonuses(model)
            self.__updateProgressionLevel(model=model)
            self.__updateEnvelopesCount(model=model)
            self.__updateBonusesVisibility(model=model)
        self.__lunarNYController.progression.onProgressionUpdated += self.__updateProgressionLevel
        g_clientUpdateManager.addCallback(LUNAR_NY_PDATA_KEY, self.__onClientUpdated)
        self.__lunarNYController.receivedEnvelopes.onReceivedEnvelopesUpdated += self.__updateEnvelopesCount
        self.startGlobalListening()

    def _finalize(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lunarNYController.receivedEnvelopes.onReceivedEnvelopesUpdated -= self.__updateEnvelopesCount
        self.__lunarNYController.progression.onProgressionUpdated -= self.__updateProgressionLevel
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.viewModel.onEnvelopeClick -= self.__onEnvelopeClick
        super(LunarNYMainWidget, self)._finalize()

    def __onWidgetClick(self, *_):
        showLunarNYMainView()
        LunarWidgetLogger().logClick()

    def __onEnvelopeClick(self, *_):
        showLunarNYMainView(initCtx={MAIN_VIEW_INIT_CONTEXT_TAB: Tab.STOREENVELOPES})

    def __onClientUpdated(self, _):
        with self.viewModel.transaction() as model:
            self.__updateCharmBonuses(model)

    def __updateCharmBonuses(self, model):
        charmBonuses = self.__lunarNYController.charms.getCharmBonuses()
        updateCharmBonusesModel(charmBonuses, model.bonuses)

    @replaceNoneKwargsModel
    def __updateEnvelopesCount(self, model=None):
        model.setNewCount(self.__lunarNYController.receivedEnvelopes.getCountNewEnvelopes())

    @replaceNoneKwargsModel
    def __updateProgressionLevel(self, model=None):
        level = self.__lunarNYController.progression.getCurrentProgressionLevel()
        model.setCurrentProgressionLevel(level.getLevel() if level is not None else 0)
        return

    @replaceNoneKwargsModel
    def __updateBonusesVisibility(self, model=None):
        model.setBonusesSupported(self.prbEntity is not None and bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANDOM))
        return
