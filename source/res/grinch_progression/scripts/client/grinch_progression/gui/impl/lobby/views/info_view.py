# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/info_view.py
from functools import partial
from constants import CURRENT_REALM
from frameworks.wulf import ViewFlags, ViewSettings
from grinch_progression.gui.impl.lobby.views.hints_helper import HintsHelper
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.shared.event_dispatcher import showHangar as showDefaultHangar
from grinch.skeletons.battle_controller import IGrinchController
from grinch_progression.gui.shared.event_dispatcher import showAboutGameBoard
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.info_view_model import InfoViewModel
from helpers import getLanguageCode, dependency
from grinch_progression.gui.impl.lobby.grinch_progression_helpers import showInfoVideo
from gui.shared import g_eventBus, events
from shared_utils import nextTick

class InfoView(ViewImpl, LobbyHeaderVisibility):
    _grinchCtrl = dependency.descriptor(IGrinchController)
    _grinchProgressionCtrl = dependency.descriptor(IGrinchProgressionController)

    def __init__(self, layoutID=R.views.grinch_progression.lobby.InfoView(), *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = InfoViewModel()
        super(InfoView, self).__init__(settings)
        self.__hintHelper = HintsHelper()
        self.__isMovingToGameBoard = False

    @property
    def viewModel(self):
        return super(InfoView, self).getViewModel()

    def _getEvents(self):
        return super(InfoView, self)._getEvents() + ((self.viewModel.onVideoClick, self.__onPlayVideo),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onShowAboutEvent, self.__onShowAboutEvent),
         (self._grinchCtrl.onConfigChanged, self.__onConfigChanged))

    def _onLoaded(self, *args, **kwargs):
        self.suspendLobbyHeader(self.uniqueID)
        self.__update()
        self.__onViewLoaded()
        super(InfoView, self)._onLoaded(*args, **kwargs)

    def _finalize(self):
        super(InfoView, self)._finalize()
        if not self.__isMovingToGameBoard:
            nextTick(partial(self.__hintHelper.setFightButtonFlag, False))()
        self.__hintHelper.clear()
        self.resumeLobbyHeader(self.uniqueID)

    def __onClose(self):
        self.__isMovingToGameBoard = True
        self._grinchCtrl.selectMode()

    def __update(self):
        with self.viewModel.transaction() as model:
            lastChapter = len(self._grinchProgressionCtrl.getCurrentSeasonChapters())
            _, clastChapterEnd = self._grinchProgressionCtrl.getChapterDates(lastChapter)
            model.setEventStartDate(self._grinchProgressionCtrl.getStartEventDate())
            model.setEventEndDate(self._grinchProgressionCtrl.getEndEventDate())
            model.setLastChapterEndDate(clastChapterEnd)
            model.region.setRealm(CURRENT_REALM)
            model.region.setLanguage(getLanguageCode())

    @staticmethod
    def __onPlayVideo():
        showInfoVideo()

    @staticmethod
    def __onShowAboutEvent():
        showAboutGameBoard()

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))
        self.__hintHelper.setFightButtonFlag(True)

    def __onConfigChanged(self, _):
        if not self._grinchCtrl.isEnabled() and not self._grinchCtrl.isEventPrbActive():
            showDefaultHangar()
