# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_select_charm_view.py
from adisp import process
from gui.impl.pub import WindowImpl
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
from gui.impl.gen.view_models.views.lobby.lunar_ny.select_charm_view_model import SelectCharmViewModel
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import updateCharmModel, updateCharmBonusesModel
from gui.impl.lobby.lunar_ny.tooltips.charm_tooltip import CharmTooltip
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import SHOW_TAB_EVENT
from lunar_ny.lunar_ny_processor import FillAlbumSlotProcessor
from lunar_ny_common.settings_constants import LUNAR_NY_PDATA_KEY
from skeletons.gui.shared import IItemsCache
from gui.shared import g_eventBus
from gui.shared.events import HasCtxEvent

class LunarNYSelectCharmView(ViewImpl[SelectCharmViewModel]):
    __slots__ = ('__slotIdx', '__blur')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lunarController = dependency.descriptor(ILunarNYController)

    def __init__(self, layout, slotIdx):
        settings = ViewSettings(layout)
        settings.flags = ViewFlags.VIEW
        settings.model = SelectCharmViewModel()
        super(LunarNYSelectCharmView, self).__init__(settings)
        self.__slotIdx = slotIdx

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LunarNYSelectCharmView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        with self.viewModel.transaction() as model:
            self.__updateCharmBonuses(model=model)
            self.__updateCharms(model=model)

    def _finalize(self):
        self.__removeListeners()
        super(LunarNYSelectCharmView, self)._finalize()

    def createToolTipContent(self, event, contentID):
        return CharmTooltip(charmID=event.getArgument('charmID')) if contentID == R.views.lobby.lunar_ny.CharmTooltip() else super(LunarNYSelectCharmView, self).createToolTipContent(event, contentID)

    def __addListeners(self):
        self.viewModel.onSelectCharm += self.__doSelectCharm
        self.viewModel.goToSendEnvelopes += self.__goToSendEnvelopes
        g_clientUpdateManager.addCallback(LUNAR_NY_PDATA_KEY, self.__onClientUpdated)

    def __removeListeners(self):
        self.viewModel.onSelectCharm -= self.__doSelectCharm
        self.viewModel.goToSendEnvelopes -= self.__goToSendEnvelopes
        g_clientUpdateManager.removeObjectCallbacks(self)

    @process
    def __doSelectCharm(self, args=None):
        charmID = args.get('charmID')
        result = yield FillAlbumSlotProcessor(charmID, self.__slotIdx).request()
        if result.success:
            self.destroyWindow()

    def __goToSendEnvelopes(self):
        g_eventBus.handleEvent(HasCtxEvent(SHOW_TAB_EVENT, Tab.SENDENVELOPES))
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __updateCharmBonuses(self, model=None):
        charmBonuses = self.__lunarController.charms.getCharmBonuses()
        updateCharmBonusesModel(charmBonuses, model.bonuses)

    @replaceNoneKwargsModel
    def __updateCharms(self, model=None):
        charms = self.__itemsCache.items.lunarNY.getCharms()
        charmsArray = model.getCharms()
        charmsArray.clear()
        for charm in charms.values():
            if charm.getCountInStorage() > 0:
                charmModel = CharmModel()
                updateCharmModel(charm, charmModel)
                charmsArray.addViewModel(charmModel)

        charmsArray.invalidate()

    def __onClientUpdated(self, _):
        with self.viewModel.transaction() as model:
            self.__updateCharmBonuses(model=model)
            self.__updateCharms(model=model)


class LunarNYSelectCharmWindow(WindowImpl):

    def __init__(self, slotIdx, parent=None):
        super(LunarNYSelectCharmWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LunarNYSelectCharmView(R.views.lobby.lunar_ny.SelectCharmView(), slotIdx), layer=WindowLayer.OVERLAY, parent=parent)
