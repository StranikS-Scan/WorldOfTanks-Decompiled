# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/meta_widget_view.py
import logging
from Event import Event
from gui.impl.gen.view_models.views.lobby.rts.meta_widget_view_model import MetaWidgetViewModel
from gui.impl.lobby.rts.tooltips.widget_tooltip_view import WidgetTooltipView
from helpers import dependency
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from frameworks.wulf.gui_constants import ViewFlags
from skeletons.gui.game_control import IRTSBattlesController
from account_helpers.AccountSettings import AccountSettings, RTS_LAST_COLLECTION_SEEN
from skeletons.gui.game_control import IRTSProgressionController
_logger = logging.getLogger(__name__)

class MetaWidgetView(ViewImpl):
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __progressionCtrl = dependency.descriptor(IRTSProgressionController)
    __slots__ = ('onNewElementChanged',)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.rts.MetaWidgetView(), model=MetaWidgetViewModel(), flags=ViewFlags.COMPONENT)
        self.onNewElementChanged = Event()
        super(MetaWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    @staticmethod
    def handleClick():
        from gui.shared.event_dispatcher import showRTSMetaRootWindow
        showRTSMetaRootWindow()

    def _initialize(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.onClick += self.handleClick
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        self.__progressionCtrl.onProgressUpdated += self.__onProgressUpdated

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel()

    def _onLoaded(self, *args, **kwargs):
        self.onNewElementChanged(self.__hasNewElement())

    def _updateViewModel(self):
        with self.viewModel.transaction() as model:
            model.setCurrentCollectionCount(self.__progressionCtrl.getCollectionProgress())
            model.setTotalCollectionCount(self.__progressionCtrl.getCollectionSize())

    def _finalize(self):
        with self.viewModel.transaction() as model:
            model.onClick -= self.handleClick
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        self.__progressionCtrl.onProgressUpdated -= self.__onProgressUpdated

    def createToolTipContent(self, event, contentID):
        return WidgetTooltipView() if contentID == R.views.lobby.rts.tooltips.WidgetTooltipView() else None

    def __onAccountSettingsChanging(self, key, _):
        if key == RTS_LAST_COLLECTION_SEEN:
            self._updateViewModel()

    def __onProgressUpdated(self):
        self.onNewElementChanged(self.__hasNewElement())
        self._updateViewModel()

    def __hasNewElement(self):
        previousProgress = AccountSettings.getSettings(RTS_LAST_COLLECTION_SEEN)
        currentProgress = self.__progressionCtrl.getCollectionProgress()
        return previousProgress != currentProgress
