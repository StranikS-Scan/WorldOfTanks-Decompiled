# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_header_widget_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EVENT_LAST_STAMPS_SEEN
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from white_tiger.gui.shared.event_dispatcher import showEventProgressionWindow
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_header_widget_view_model import WtHeaderWidgetViewModel
from white_tiger.gui.impl.lobby.tooltips.wt_event_header_widget_tooltip_view import WtEventHeaderWidgetTooltipView
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache

class WTEventHeaderWidgetComponent(InjectComponentAdaptor):

    def __init__(self):
        super(WTEventHeaderWidgetComponent, self).__init__()
        self.__view = None
        return

    def _dispose(self):
        self.__view = None
        super(WTEventHeaderWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = WTEventHeaderWidgetView(flags=ViewFlags.VIEW)
        return self.__view


class WTEventHeaderWidgetView(ViewImpl):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.white_tiger.lobby.ProgressionEntryPoint())
        settings.flags = flags
        settings.model = WtHeaderWidgetViewModel()
        super(WTEventHeaderWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtEventHeaderWidgetTooltipView()

    def _onLoading(self, *args, **kwargs):
        super(WTEventHeaderWidgetView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventHeaderWidgetView, self)._finalize()

    def __addListeners(self):
        self.viewModel.onClick += self.__onClick
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted

    def __removeListeners(self):
        self.viewModel.onClick -= self.__onClick
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted

    def __onSyncCompleted(self, _, __):
        self.__updateViewModel()

    def __onAccountSettingsChanging(self, key, _):
        if key == EVENT_LAST_STAMPS_SEEN:
            self.__updateIsNewItems()

    def __onClick(self):
        showEventProgressionWindow()

    def __updateViewModel(self):
        totalProgress = self.__gameEventCtrl.getTotalLevelsCount()
        currentProgress = self.__gameEventCtrl.getFinishedLevelsCount()
        tooltip = R.views.white_tiger.lobby.tooltips.ProgressionEntryPointTooltip()
        with self.viewModel.transaction() as model:
            model.setTooltipID(tooltip)
            model.setCurrentProgression(currentProgress)
            model.setTotalProgression(totalProgress)
            model.setAllCollected(currentProgress == totalProgress)
            self.__updateIsNewItems()

    def __updateIsNewItems(self):
        with self.viewModel.transaction() as model:
            previous = AccountSettings.getSettings(EVENT_LAST_STAMPS_SEEN)
            current = self.__gameEventCtrl.getCurrentStampsCount()
            model.setIsNewItem(current > previous)
