# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/story_choice.py
from __future__ import absolute_import
import logging
from halloween.gui.impl.gen.view_models.views.lobby.story_choice_view_model import StoryChoiceViewModel
from halloween.gui.impl.lobby.base_view import BaseView
from halloween.gui.shared.event_dispatcher import showStoryChoiceDialog, showAwardCongratsWindow
from halloween.gui.shared.gui_items.processors.processors import ChoiceProcessor
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import STORY_CHOICE_WINDOW_EXIT, STORY_CHOICE_WINDOW_ENTER
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from frameworks.wulf import ViewSettings, WindowFlags
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.utils import decorators
from gui.shared.utils.decorators import adisp_async
from helpers import dependency
from halloween.gui.impl.lobby.hw_helpers import getEndingToken
from halloween_common.halloween_constants import HWStoryChoiceSettings
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await

class StoryChoiceView(BaseView):
    __slots__ = ()
    layoutID = R.views.halloween.mono.lobby.story_choice()
    _hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, model=StoryChoiceViewModel())
        super(StoryChoiceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(StoryChoiceView, self).getViewModel()

    def _subscribe(self):
        super(StoryChoiceView, self)._subscribe()
        self.viewModel.onClose += self.__onClose
        self.viewModel.onSelectSide += self.__onSelectSide

    def _unsubscribe(self):
        super(StoryChoiceView, self)._unsubscribe()
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onSelectSide -= self.__onSelectSide

    def _initialize(self, *args, **kwargs):
        super(StoryChoiceView, self)._initialize()
        playSound(STORY_CHOICE_WINDOW_ENTER)

    def _finalize(self):
        playSound(STORY_CHOICE_WINDOW_EXIT)
        super(StoryChoiceView, self)._finalize()

    def __onClose(self):
        self._hwArtifactsCtrl.setChoice(HWStoryChoiceSettings.OPTION_SKIP)
        self.destroyWindow()

    @adisp_async
    @decorators.adisp_process('updating')
    def __acrualArtefact(self, artefactID):
        yield self._hwArtifactsCtrl.openArtefact(artefactID, False)

    @wg_async
    def __onSelectSide(self, args):
        if args is None:
            return
        else:
            choice = args.get('sideId', '')
            result = yield wg_await(showStoryChoiceDialog(choice))
            if result.result:
                logging.info('result = %s', choice)
                self.__acrualChoice(choice)
            return

    @adisp_async
    @decorators.adisp_process('updating')
    def __acrualChoice(self, choiceID):
        if self._hwArtifactsCtrl.getChoiceID() == HWStoryChoiceSettings.OPTION_SKIP:
            showAwardCongratsWindow(choiceID)
        self._hwArtifactsCtrl.setChoice(choiceID)
        result = yield ChoiceProcessor(getEndingToken(choiceID)).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        self.destroyWindow()


class StoryChoiceWindow(LobbyNotificationWindow):

    def __init__(self, layoutID, parent=None):
        super(StoryChoiceWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=StoryChoiceView(layoutID=layoutID), parent=parent)
        self._args = (layoutID,)

    def isParamsEqual(self, *args):
        return self._args == args
