# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/app_loader/observers.py
import typing
from gui.Scaleform.framework.entities.View import ViewKey
from gui.app_loader.observers import BattleLoadingObserver, registerBattleObserverOverrideHandler, SwitchToBattleObserver, BattlePageObserver, SwitchToLobbyObserver
from helpers import dependency
from skeletons.gameplay import GameplayStateID
from skeletons.gui.app_loader import IAppLoader
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS, IS_ONBOARDING_SEAMLESS_MISSION_CHANGING_ON
from story_mode.skeletons.story_mode_controller import IStoryModeController
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry
    from story_mode.gui.scaleform.daapi.view.battle.page_base import StoryModeBattlePageBase

def getStoryModeBattle():
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    if app is None:
        return
    else:
        containerManager = app.containerManager
        return None if containerManager is None else containerManager.getViewByKey(ViewKey(VIEW_ALIAS.ONBOARDING_BATTLE_PAGE)) or containerManager.getViewByKey(ViewKey(VIEW_ALIAS.STORY_MODE_BATTLE_PAGE))


def isInStoryModeBattle():
    return getStoryModeBattle() is not None


class StoryModeSwitchToBattleObserver(SwitchToBattleObserver):
    __slots__ = ()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def _destroyLobby(self):
        if not self._storyModeCtrl.isOnboarding or self._proxy.getDefLobbyApp() is not None:
            super(StoryModeSwitchToBattleObserver, self)._destroyLobby()
        return

    def _createBattle(self, arenaGuiType):
        if not self._storyModeCtrl.isOnboarding or self._proxy.getDefBattleApp() is None:
            super(StoryModeSwitchToBattleObserver, self)._createBattle(arenaGuiType)
        return


class StoryModeBattlePageObserver(BattlePageObserver):
    __slots__ = ()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def onExitState(self, event=None):
        if not self._storyModeCtrl.isOnboarding or self._storyModeCtrl.isQuittingBattle:
            super(StoryModeBattlePageObserver, self).onExitState(event)
        else:
            battlePage = getStoryModeBattle()
            if battlePage is not None:
                battlePage.hideAndStop()
        return


class StoryModeSwitchToLobbyObserver(SwitchToLobbyObserver):
    __slots__ = ()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def _createLobby(self):
        if not self._storyModeCtrl.isOnboarding or self._storyModeCtrl.isQuittingBattle:
            super(StoryModeSwitchToLobbyObserver, self)._createLobby()


class StoryModeObserverPredicate(object):
    __slots__ = ()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __call__(self, *_, **__):
        return self._storyModeCtrl.isEnabled() and isInStoryModeBattle()


def registerObservers(proxy):
    return (StoryModeObserverPredicate(), (StoryModeSwitchToBattleObserver(GameplayStateID.AVATAR_ENTERING, proxy),
      BattleLoadingObserver(GameplayStateID.AVATAR_ARENA_INFO, proxy),
      BattleLoadingObserver(GameplayStateID.AVATAR_SHOW_GUI, proxy),
      StoryModeBattlePageObserver(GameplayStateID.AVATAR_ARENA_LOADED, proxy),
      StoryModeSwitchToLobbyObserver(GameplayStateID.ACCOUNT_ENTERING, GameplayStateID.AVATAR_EXITING, proxy)))


def preInit():
    if IS_ONBOARDING_SEAMLESS_MISSION_CHANGING_ON:
        registerBattleObserverOverrideHandler(registerObservers)
