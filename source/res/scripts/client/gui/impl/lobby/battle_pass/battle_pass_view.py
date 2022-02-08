# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.meta.MissionsBattlePassViewMeta import MissionsBattlePassViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.battle_pass_progressions_view import BattlePassProgressionsView
from gui.impl.lobby.battle_pass.chapter_choice_view import ChapterChoiceView
from gui.impl.lobby.battle_pass.intro_view import IntroView
from gui.shared.event_dispatcher import showHangar
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
_R_VIEWS = R.views.lobby.battle_pass
_VIEWS = {_R_VIEWS.BattlePassIntroView(): IntroView,
 _R_VIEWS.ChapterChoiceView(): ChapterChoiceView,
 _R_VIEWS.BattlePassProgressionsView(): BattlePassProgressionsView}

class BattlePassViewsHolderComponent(InjectComponentAdaptor, MissionsBattlePassViewMeta, LobbySubView):
    __slots__ = ()
    __battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def updateState(self, *args, **kwargs):
        self.__setDummyVisible(self.__battlePassController.isPaused())
        layoutID = kwargs.get('layoutID', R.invalid())
        if layoutID not in _VIEWS:
            layoutID = self.__getActualViewImplLayoutID()
        chapterID = kwargs.get('chapterID')
        isSameLayout = self._injectView is not None and self._injectView.layoutID == layoutID
        isProgressionView = layoutID == _R_VIEWS.BattlePassProgressionsView()
        if isSameLayout and not isProgressionView:
            return
        else:
            self._destroyInjected()
            self._createInjectView(layoutID, chapterID)
            return

    def markVisited(self):
        self.__safeCallOnInjected('markVisited')

    def dummyClicked(self, eventType):
        if eventType == 'OpenHangar':
            showHangar()

    def _onPopulate(self):
        self.updateState()

    def _makeInjectView(self, layoutID=None, chapterID=0):
        self.as_setWaitingVisibleS(True)
        return _VIEWS[layoutID](chapterID=chapterID)

    def _addInjectContentListeners(self):
        self._injectView.viewModel.onViewLoaded += self.__onViewLoaded

    def _removeInjectContentListeners(self):
        self._injectView.viewModel.onViewLoaded -= self.__onViewLoaded

    def __onViewLoaded(self):
        self.as_showViewS()
        self.as_setWaitingVisibleS(False)

    def __getActualViewImplLayoutID(self):
        if not self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.INTRO_SHOWN):
            return _R_VIEWS.BattlePassIntroView()
        return _R_VIEWS.ChapterChoiceView() if not self.__battlePassController.hasActiveChapter() else _R_VIEWS.BattlePassProgressionsView()

    def __setDummyVisible(self, isVisible):
        if isVisible:
            self.as_setBackgroundS(backport.image(R.images.gui.maps.icons.battlePass.progression.bg()))
            self.as_showDummyS({'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_32X32,
             'htmlText': text_styles.main(backport.text(R.strings.battle_pass.progression.error())),
             'alignCenter': True,
             'btnVisible': True,
             'btnLabel': backport.text(R.strings.battle_pass.progression.errorBtn()),
             'btnTooltip': '',
             'btnEvent': 'OpenHangar',
             'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK})
        else:
            self.as_setBackgroundS('')
            self.as_hideDummyS()

    def __safeCallOnInjected(self, methodName, *args, **kwargs):
        call = getattr(self._injectView, methodName, None)
        if callable(call):
            call(*args, **kwargs)
        return
