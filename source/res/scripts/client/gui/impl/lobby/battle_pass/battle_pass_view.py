# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewStatus
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
from gui.impl.lobby.battle_pass.intro_view import IntroView
from gui.impl.lobby.battle_pass.post_progression_view import PostProgressionView
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar
from gui.shared.formatters import text_styles
from helpers import dependency
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.impl import IGuiLoader
_R_VIEWS = R.views.lobby.battle_pass
_VIEWS = {_R_VIEWS.BattlePassIntroView(): IntroView,
 _R_VIEWS.ChapterChoiceView(): ChapterChoiceView,
 _R_VIEWS.BattlePassProgressionsView(): BattlePassProgressionsView,
 _R_VIEWS.PostProgressionView(): PostProgressionView}
_INTRO_VIDEO_SHOWN = BattlePassStorageKeys.INTRO_VIDEO_SHOWN
_EXTRA_VIDEO_SHOWN = BattlePassStorageKeys.EXTRA_CHAPTER_VIDEO_SHOWN
_INTRO_SHOWN = BattlePassStorageKeys.INTRO_SHOWN

class _IntroVideoManager(object):
    __battlePass = dependency.descriptor(IBattlePassController)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self.__isIntroVideoShown = False

    @property
    def isIntroVideoShown(self):
        return _hasTrueInBPStorage(_INTRO_VIDEO_SHOWN)

    @property
    def isExtraVideoShown(self):
        return _hasTrueInBPStorage(_EXTRA_VIDEO_SHOWN)

    def init(self):
        g_eventBus.addListener(events.BattlePassEvent.VIDEO_SHOWN, self.showIntroVideoIfNeeded, EVENT_BUS_SCOPE.LOBBY)

    def fini(self):
        g_eventBus.removeListener(events.BattlePassEvent.VIDEO_SHOWN, self.showIntroVideoIfNeeded, EVENT_BUS_SCOPE.LOBBY)

    def showIntroVideoIfNeeded(self, *_):
        if not self.isIntroVideoShown:
            _showOverlayVideo(getIntroVideoURL())
            _setTrueToBPStorage(_INTRO_VIDEO_SHOWN)
            self.__isIntroVideoShown = True
        else:

            def isVideoView(window):
                return window.content is not None and getattr(window.content, 'alias', None) == VIEW_ALIAS.BATTLE_PASS_VIDEO_BROWSER_VIEW

            if not self.__guiLoader.windowsManager.findWindows(isVideoView):
                self.__showExtraVideoIfNeeded()

    @nextTick
    def __showExtraVideoIfNeeded(self):
        if not self.isExtraVideoShown and self.__battlePass.hasExtra():
            _showOverlayVideo(getExtraIntroVideoURL())
            _setTrueToBPStorage(_EXTRA_VIDEO_SHOWN)
            if not self.__isIntroVideoShown:
                showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())
        g_eventBus.removeListener(events.BattlePassEvent.VIDEO_SHOWN, self.showIntroVideoIfNeeded, EVENT_BUS_SCOPE.LOBBY)


class BattlePassViewsHolderComponent(InjectComponentAdaptor, MissionsBattlePassViewMeta):
    __slots__ = ('__isDummyVisible', '__introVideoManager')
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        super(BattlePassViewsHolderComponent, self).__init__()
        self.__isDummyVisible = False
        self.__introVideoManager = _IntroVideoManager()

    def finalize(self):
        self._dispose()

    @nextTick
    def updateState(self, *args, **kwargs):
        self.__setDummyVisible(self.__battlePass.isPaused())
        layoutID = kwargs.get('layoutID', R.invalid())
        chapterID = kwargs.get('chapterID', 0)
        if self.__needTakeDefault(layoutID, chapterID):
            layoutID = self.__getActualViewImplLayoutID(chapterID)
        if not self.__needReload(layoutID) or not self.__battlePass.isActive():
            return
        else:
            if self.__battlePass.isActive():
                self.__introVideoManager.showIntroVideoIfNeeded()
            isProgressionView = self._injectView is not None and self._injectView.layoutID == layoutID and layoutID == _R_VIEWS.BattlePassProgressionsView()
            if isProgressionView:
                self._injectView.setChapter(chapterID)
            else:
                self._destroyInjected()
                self._createInjectView(layoutID, chapterID)
            return

    def dummyClicked(self, eventType):
        if eventType == 'OpenHangar':
            showHangar()

    def markVisited(self):
        pass

    def start(self):
        if self._injectView is not None:
            self.__safeCall(self._injectView, 'activate')
        return

    def stop(self):
        if self._injectView is not None:
            self.__safeCall(self._injectView, 'deactivate')
        return

    def _onPopulate(self):
        pass

    def _populate(self):
        super(BattlePassViewsHolderComponent, self)._populate()
        self.__battlePass.onBattlePassSettingsChange += self.__onSettingsChanged
        self.__introVideoManager.init()

    def _dispose(self):
        if self.__introVideoManager is not None:
            self.__introVideoManager.fini()
        self.__battlePass.onBattlePassSettingsChange -= self.__onSettingsChanged
        self.stop()
        super(BattlePassViewsHolderComponent, self)._dispose()
        return

    def _addInjectContentListeners(self):
        self._injectView.onStatusChanged += self.__onViewLoaded

    def _removeInjectContentListeners(self):
        self._injectView.onStatusChanged -= self.__onViewLoaded

    def _makeInjectView(self, layoutID=None, chapterID=0):
        self.as_setWaitingVisibleS(True)
        return _VIEWS[layoutID](chapterID=chapterID)

    def __needTakeDefault(self, layoutID, chapterID):
        return layoutID not in _VIEWS or not _hasTrueInBPStorage(_INTRO_SHOWN) or layoutID == _R_VIEWS.BattlePassProgressionsView() and chapterID and not self.__battlePass.isChapterExists(chapterID)

    def __needReload(self, layoutID):
        return self._injectView is None or self._injectView.layoutID != layoutID or self._injectView.layoutID == _R_VIEWS.BattlePassProgressionsView()

    def __onViewLoaded(self, state):
        if state == ViewStatus.LOADED:
            self.as_showViewS()
            self.as_setWaitingVisibleS(False)

    def __onSettingsChanged(self, *_):
        isPaused = self.__battlePass.isPaused()
        if self.__isDummyVisible and not isPaused:
            self.updateState()
        self.__setDummyVisible(isPaused)

    def __getActualViewImplLayoutID(self, chapterID):
        ctrl = self.__battlePass

        def isExtraActiveFirstTime():
            return ctrl.hasExtra() and not self.__introVideoManager.isExtraVideoShown

        if not _hasTrueInBPStorage(_INTRO_SHOWN):
            return _R_VIEWS.BattlePassIntroView()
        if not isExtraActiveFirstTime() and (ctrl.hasActiveChapter() or ctrl.isChapterExists(chapterID)):
            return _R_VIEWS.BattlePassProgressionsView()
        return _R_VIEWS.PostProgressionView() if ctrl.isHoliday() and self.__battlePass.isCompleted() else _R_VIEWS.ChapterChoiceView()

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
            self._destroyInjected()
        else:
            self.as_setBackgroundS('')
            self.as_hideDummyS()

    @staticmethod
    def __safeCall(obj, attrName, *args, **kwargs):
        return getattr(obj, attrName, lambda *__, **_: None)(*args, **kwargs)


def _showOverlayVideo(url):
    showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_VIDEO_BROWSER_VIEW)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def _hasTrueInBPStorage(storageSettingName, settingsCore=None):
    return settingsCore.serverSettings.getBPStorage().get(storageSettingName)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def _setTrueToBPStorage(storageSettingName, settingsCore=None):
    settingsCore.serverSettings.saveInBPStorage({storageSettingName: True})
