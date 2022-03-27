# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MissionsBattlePassViewMeta import MissionsBattlePassViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_pass.battle_pass_helpers import getExtraIntroVideoURL, getIntroVideoURL
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.battle_pass_progressions_view import BattlePassProgressionsView
from gui.impl.lobby.battle_pass.chapter_choice_view import ChapterChoiceView
from gui.impl.lobby.battle_pass.extra_intro_view import ExtraIntroView
from gui.impl.lobby.battle_pass.intro_view import IntroView
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar
from gui.shared.formatters import text_styles
from helpers import dependency
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
_R_VIEWS = R.views.lobby.battle_pass
_VIEWS = {_R_VIEWS.BattlePassIntroView(): IntroView,
 _R_VIEWS.ExtraIntroView(): ExtraIntroView,
 _R_VIEWS.ChapterChoiceView(): ChapterChoiceView,
 _R_VIEWS.BattlePassProgressionsView(): BattlePassProgressionsView}
_INTRO_VIDEO_SHOWN = BattlePassStorageKeys.INTRO_VIDEO_SHOWN
_EXTRA_VIDEO_SHOWN = BattlePassStorageKeys.EXTRA_CHAPTER_VIDEO_SHOWN
_INTRO_SHOWN = BattlePassStorageKeys.INTRO_SHOWN

class BattlePassViewsHolderComponent(InjectComponentAdaptor, MissionsBattlePassViewMeta):
    __slots__ = ('__isDummyVisible', '__isIntroVideoShown', '__isIntroVideoIsShowing')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(BattlePassViewsHolderComponent, self).__init__()
        self.__isDummyVisible = False
        self.__isIntroVideoShown = False
        self.__isIntroVideoIsShowing = False

    @nextTick
    def updateState(self, *args, **kwargs):
        self.__setDummyVisible(self.__battlePassController.isPaused())
        layoutID = kwargs.get('layoutID', R.invalid())
        chapterID = kwargs.get('chapterID', 0)
        if self.__needTakeDefault(layoutID, chapterID):
            layoutID = self.__getActualViewImplLayoutID(chapterID)
        if not self.__needReload(layoutID):
            return
        self.__showIntroVideoIfNeeded()
        self._destroyInjected()
        self._createInjectView(layoutID, chapterID)

    def markVisited(self):
        self.__safeCallOnInjected('markVisited')

    def dummyClicked(self, eventType):
        if eventType == 'OpenHangar':
            showHangar()

    def _onPopulate(self):
        self.updateState()

    def _populate(self):
        super(BattlePassViewsHolderComponent, self)._populate()
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChanged

    def _dispose(self):
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChanged
        super(BattlePassViewsHolderComponent, self)._dispose()

    def _addInjectContentListeners(self):
        self._injectView.viewModel.onViewLoaded += self.__onViewLoaded

    def _removeInjectContentListeners(self):
        self._injectView.viewModel.onViewLoaded -= self.__onViewLoaded

    def _makeInjectView(self, layoutID=None, chapterID=0):
        self.as_setWaitingVisibleS(True)
        return _VIEWS[layoutID](chapterID=chapterID)

    def __needTakeDefault(self, layoutID, chapterID):
        return layoutID not in _VIEWS or layoutID == _R_VIEWS.BattlePassProgressionsView() and chapterID and not self.__battlePassController.isChapterExists(chapterID)

    def __needReload(self, layoutID):
        return self._injectView is None or self._injectView.layoutID != layoutID or self._injectView.layoutID == _R_VIEWS.BattlePassProgressionsView()

    def __onViewLoaded(self):
        self.as_showViewS()
        self.as_setWaitingVisibleS(False)

    def __onSettingsChanged(self, *_):
        if self.__isDummyVisible:
            self.updateState()

    def __getActualViewImplLayoutID(self, chapterID):
        ctrl = self.__battlePassController

        def isExtraActiveFirstTime():
            return ctrl.hasExtra() and not self.__hasTrueInBPStorage(_EXTRA_VIDEO_SHOWN)

        if not self.__hasTrueInBPStorage(_INTRO_SHOWN):
            return _R_VIEWS.BattlePassIntroView()
        return _R_VIEWS.BattlePassProgressionsView() if not isExtraActiveFirstTime() and (ctrl.hasActiveChapter() or ctrl.isChapterExists(chapterID)) else _R_VIEWS.ChapterChoiceView()

    def __setDummyVisible(self, isVisible):
        self.__isDummyVisible = isVisible
        if self.__isDummyVisible:
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

    def __showIntroVideoIfNeeded(self):
        if not self.__hasTrueInBPStorage(_INTRO_VIDEO_SHOWN):
            _showOverlayVideo(getIntroVideoURL(), self.__showExtraVideoIfNeeded)
            self.__setTrueToBPStorage(_INTRO_VIDEO_SHOWN)
            self.__isIntroVideoShown = True
            self.__isIntroVideoIsShowing = True
        elif not self.__isIntroVideoIsShowing:
            self.__showExtraVideoIfNeeded()

    def __showExtraVideoIfNeeded(self):
        if not self.__hasTrueInBPStorage(_EXTRA_VIDEO_SHOWN) and self.__battlePassController.hasExtra():
            _showOverlayVideo(getExtraIntroVideoURL())
            self.__setTrueToBPStorage(_EXTRA_VIDEO_SHOWN)
            if not self.__isIntroVideoShown:
                showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())

    def __hasTrueInBPStorage(self, storageSettingName):
        return self.__settingsCore.serverSettings.getBPStorage().get(storageSettingName)

    def __setTrueToBPStorage(self, storageSettingName):
        self.__settingsCore.serverSettings.saveInBPStorage({storageSettingName: True})

    def __safeCallOnInjected(self, methodName, *args, **kwargs):
        call = getattr(self._injectView, methodName, None)
        if callable(call):
            call(*args, **kwargs)
        return


def _showOverlayVideo(url, exitCallback=None):
    showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY, callbackOnClose=exitCallback)
