# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: newbie_start_page/scripts/client/newbie_start_page/gui/impl/lobby/newbie_start_page/newbie_start_page_view.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from helpers import dependency
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags
from gui.Scaleform.Waiting import Waiting
from gui.game_loading import loading
from gui.impl.gen import R
from newbie_start_page.gui.impl.gen.view_models.views.lobby.newbie_start_page.newbie_start_page_view_model import ExperienceChoice, NewbieStartPageViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from skeletons.gui.game_control import INewbieEntryPointController
_logger = logging.getLogger(__name__)

class NewbieStartPageView(ViewImpl):
    _newbieEntryPointController = dependency.descriptor(INewbieEntryPointController)

    def __init__(self, guiCtx):
        settings = ViewSettings(layoutID=R.views.newbie_start_page.lobby.newbie_start_page.NewbieStartPageView(), flags=ViewFlags.VIEW, model=NewbieStartPageViewModel())
        self._guiCtx = guiCtx
        super(NewbieStartPageView, self).__init__(settings)

    def _onLoaded(self, *args, **kwargs):
        super(NewbieStartPageView, self)._onLoaded(*args, **kwargs)
        Waiting.close()
        loading.getLoader().idl()

    @property
    def viewModel(self):
        return super(NewbieStartPageView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onSelect, self.__onSelect), (g_playerEvents.onDisconnected, self.destroyWindow))

    def _onLoading(self, *args, **kwargs):
        super(NewbieStartPageView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            levels = model.getLevels()
            levels.clear()
            for level in [ExperienceChoice.NEWBIE, ExperienceChoice.INEXPERIENCED, ExperienceChoice.EXPERIENCED]:
                levels.addNumber(level)

            levels.invalidate()

    def __onSelect(self, args):
        expLevel = ExperienceChoice(args.get(NewbieStartPageViewModel.ON_SELECT_ARG_NAME))
        self._newbieEntryPointController.setExperienceLevel(expLevel)
        if expLevel in [ExperienceChoice.INEXPERIENCED, ExperienceChoice.EXPERIENCED]:
            self._guiCtx.update({'canSkipOnboarding': True})
        if self._newbieEntryPointController.isStoryModeEnabled():
            self._newbieEntryPointController.goToStoryModeQueue(self._guiCtx)
        else:
            self._newbieEntryPointController.goToHangar(self._guiCtx)
            loading.getLoader().playerLoading(True)
        self.viewModel.onSelect -= self.__onSelect
        BigWorld.callback(2.5, self.destroyWindow)


class NewbieStartPageViewWindow(WindowImpl):

    def __init__(self, guiCtx):
        super(NewbieStartPageViewWindow, self).__init__(content=NewbieStartPageView(guiCtx), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
