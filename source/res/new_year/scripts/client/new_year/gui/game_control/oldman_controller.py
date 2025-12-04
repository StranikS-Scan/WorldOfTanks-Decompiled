# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/oldman_controller.py
import CGF
import Math
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.app_loader.settings import APP_NAME_SPACE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from new_year.cgf.oldman_manager import OldManActivationZoneComponent
from new_year.gui.impl.new_year.sounds import NewYearSoundEvents
from new_year.skeletons.new_year import IOldManController, ITamagotchiDataProvider
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
_SOUND_MAP = {'food': NewYearSoundEvents.OLDMAN_NOTIFICATION_HUNGRY,
 'fun': NewYearSoundEvents.OLDMAN_NOTIFICATION_ENERGY,
 'activity': NewYearSoundEvents.OLDMAN_NOTIFICATION_HYGIENE}
_OLD_MAN_SHOW_TIMEOUT = 15

class OldManController(IOldManController):
    __slots__ = ('__callbackDelayer', '_wasInBattle', '_oldManWasShown')
    __appLoader = dependency.descriptor(IAppLoader)
    __dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args, **kwargs):
        super(OldManController, self).__init__(*args, **kwargs)
        self.__callbackDelayer = CallbackDelayer()
        self._oldManWasShown = False
        self._wasInBattle = False

    def onDisconnected(self):
        self.__callbackDelayer.clearCallbacks()
        self._wasInBattle = False
        self._oldManWasShown = False

    def onAvatarBecomePlayer(self):
        self._wasInBattle = True
        self.__callbackDelayer.clearCallbacks()

    def tryShowOldMan(self):
        self.__callbackDelayer.delayCallback(_OLD_MAN_SHOW_TIMEOUT, self.showOldMan)

    def showOldMan(self):
        if not self.__shouldShowOldMan() or not self.__hangarSpace.spaceID:
            return
        for go, oldManZoneGO in CGF.Query(self.__hangarSpace.spaceID, (CGF.GameObject, OldManActivationZoneComponent)):
            CGF.loadGameObjectIntoHierarchy(oldManZoneGO.prefabPath, go, Math.Vector3(0, 0, 0))
            self._oldManWasShown = True

    def getSoundEvent(self):
        lowStats = self.__getLowStats()
        if not lowStats:
            return ''
        return NewYearSoundEvents.OLDMAN_NOTIFICATION_GENERAL if len(lowStats) > 1 else _SOUND_MAP.get(lowStats[0], '')

    def __shouldShowOldMan(self):
        return not self._oldManWasShown and self.__isHangarViewLoaded and self._wasInBattle and self.__getLowStats() and self.__dataProvider.raccoonState

    def __getLowStats(self):
        indicatorStates = self.__dataProvider.getIndicatorStates()
        return [ stat for stat, level in indicatorStates.iteritems() if level <= 1 ]

    @property
    def __isHangarViewLoaded(self):
        app = self.__appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        return app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR)) is not None if app and app.containerManager else False
