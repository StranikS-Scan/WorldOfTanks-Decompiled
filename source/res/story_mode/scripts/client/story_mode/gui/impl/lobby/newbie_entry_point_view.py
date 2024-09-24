# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/newbie_entry_point_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from story_mode.gui.impl.gen.view_models.views.lobby.entry_point_view_model import EntryPointViewModel
from story_mode.gui.impl.lobby.consts import EntryPointStates
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.loggers import NewbieEntryPointLogger
from story_mode_common.configs.story_mode_settings import settingsSchema
_BG_FOLDER_NAME = 'entryPoint'

class NewbieEntryPointView(ViewImpl):
    __controller = dependency.descriptor(IStoryModeController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.story_mode.lobby.NewbieEntryPointView())
        settings.flags = flags
        settings.model = EntryPointViewModel()
        super(NewbieEntryPointView, self).__init__(settings)
        self.__state = EntryPointStates.UNKNOWN
        self.__newRemoved = False
        self.__uiLogger = NewbieEntryPointLogger()

    def _getEvents(self):
        return [(self.getViewModel().onClick, self.__onClick),
         (g_playerEvents.onConfigModelUpdated, self.__configChangeHandler),
         (self.getViewModel().onHoverForSetTime, self.__onHover),
         (self.getViewModel().onLeaveAfterSetTime, self.__onUnhover)]

    def _onLoading(self, *args, **kwargs):
        super(NewbieEntryPointView, self)._onLoading(*args, **kwargs)
        viewModel = self.getViewModel()
        viewModel.setTitle(backport.text(R.strings.sm_lobby.newbieEntryPoint.title.newStorie()))
        viewModel.setSubtitle(backport.text(R.strings.sm_lobby.newbieEntryPoint.subtitle.newStorie()))
        viewModel.setBgFolderName(_BG_FOLDER_NAME)
        with viewModel.transaction() as vm:
            self.__fillViewModel(vm)

    def __configChangeHandler(self, _):
        with self.getViewModel().transaction() as vm:
            self.__fillViewModel(vm)

    def __fillViewModel(self, vm):
        settings = settingsSchema.getModel()
        if settings and settings.newbieBannerEnabled and self.__controller.isNewNeededForNewbies():
            self.__state = EntryPointStates.NEW_EVENT
            vm.setIsNew(True)

    def __onClick(self):
        self.__uiLogger.logClick(self.__state)
        if self.__controller.isNewNeededForNewbies():
            self.__controller.setNewForNewbiesSeen()
        self.__controller.switchPrb()

    def __onHover(self):
        view = self.getViewModel()
        if view.getIsNew():
            self.__newRemoved = True
            view.setIsNew(False)
            self.__controller.setNewForNewbiesSeen()

    def __onUnhover(self):
        if self.__newRemoved:
            self.__newRemoved = False
