# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/ambients.py
from collections import defaultdict
import MusicControllerWWISE as _MC
from Event import Event
from constants import ARENA_PERIOD as _PERIOD
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import sf_lobby
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from gui.battle_control.battle_constants import WinStatus
from gui.shared import g_eventBus, events
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable
from gui.sounds import filters as snd_filters
from gui.sounds.sound_constants import SoundFilters, PLAYING_SOUND_CHECK_PERIOD
from gui.sounds.sound_utils import SOUND_DEBUG
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.utils import IHangarSpace

def _getViewSoundEnv(view):
    if hasattr(view, 'getDynamicSoundEnv'):
        return getattr(view, 'getDynamicSoundEnv')()
    elif hasattr(view, '__sound_env__'):
        return getattr(view, '__sound_env__')
    else:
        return ModalWindowEnv if isinstance(view, WindowViewMeta) and view.isViewModal() else None


def _getGFViewSoundEnv(viewImplAdaptor):
    viewImpl = getattr(viewImplAdaptor, 'view', None)
    return getattr(viewImpl, '__sound_env__', None) if viewImpl is not None else None


class SoundEvent(Notifiable):

    def __init__(self, soundEventID, params=None, checkFinish=False):
        super(SoundEvent, self).__init__()
        self._soundEventID = soundEventID
        self._params = params or {}
        self._checkFinish = checkFinish
        self._isStarted = False
        self.onStarted = Event()
        self.onFinished = Event()

    def __del__(self):
        self.clearNotification()

    def getID(self):
        return self._soundEventID

    def isEmpty(self):
        return self._soundEventID is None

    def clearParams(self):
        self._params.clear()

    def start(self):
        if not self.isPlaying():
            SOUND_DEBUG('Start playing sound event', self._soundEventID, self._params)
            _MC.g_musicController.play(self._soundEventID, self._params)
            if self._checkFinish:
                self._isStarted = True
                self.addNotificators(PeriodicNotifier(self._getNotificationDelta, self._onCheckAmbientNotification, (PLAYING_SOUND_CHECK_PERIOD,)))
                self.startNotification()
                self.onStarted()
        else:
            SOUND_DEBUG('Sound is already playing', self._soundEventID, self._params)

    def stop(self):
        if self.isPlaying():
            SOUND_DEBUG('Stop sound event playing', self._soundEventID)
            _MC.g_musicController.stopEvent(self._soundEventID)
            self._doStop(notify=True)
        else:
            self._doStop(notify=False)
            SOUND_DEBUG('Skip stopping, sound is already stopped', self._soundEventID)

    def clear(self):
        self._doStop(notify=False)

    def isPlaying(self):
        return _MC.g_musicController.isPlaying(self._soundEventID)

    def isCompleted(self):
        return _MC.g_musicController.isCompleted(self._soundEventID)

    def setParam(self, paramName, value):
        self._params[paramName] = value
        _MC.g_musicController.setEventParam(paramName, int(value))

    def _getNotificationDelta(self):
        return PLAYING_SOUND_CHECK_PERIOD if self._isStarted else 0

    def _onCheckAmbientNotification(self):
        SOUND_DEBUG('Current ambient playing check: is playing now', self, self.isPlaying())
        if not self.isPlaying():
            self._isStarted = False
            self.clearNotification()
            self.onFinished(self.isCompleted())

    def _doStop(self, notify=True):
        if self._checkFinish:
            self._isStarted = False
            self.clearNotification()
            if notify:
                self.onFinished()

    def __repr__(self):
        return '%s(id = %d, params = %s)' % (self.__class__.__name__, self._soundEventID, self._params)


class EmptySound(SoundEvent):

    def __init__(self):
        super(EmptySound, self).__init__(soundEventID=None)
        return

    def start(self):
        pass

    def stop(self):
        pass

    def setParam(self, paramName, value):
        pass

    def isPlaying(self):
        return False

    def __repr__(self):
        pass


class NoMusic(EmptySound):

    def start(self):
        self.stop()

    def stop(self):
        SOUND_DEBUG('Stopping music sound event')
        _MC.g_musicController.stopMusic()

    def isEmpty(self):
        return False

    def __repr__(self):
        pass


class NoAmbient(EmptySound):

    def start(self):
        self.stop()

    def stop(self):
        SOUND_DEBUG('Stopping ambient sound event')
        _MC.g_musicController.stopAmbient()

    def isEmpty(self):
        return False

    def __repr__(self):
        pass


class SoundEnv(object):

    def __init__(self, soundsCtrl, envId, music=None, ambient=None, filters=None):
        self._soundsCtrl = soundsCtrl
        self._music = music or EmptySound()
        self._ambient = ambient or EmptySound()
        self._filters = filters or []
        self.__envID = envId
        self.onChanged = Event()

    def start(self):
        self._soundsCtrl.system.onEnvStart(self.__envID)

    def stop(self):
        self.onChanged.clear()
        self._soundsCtrl.system.onEnvStop(self.__envID)
        self._ambient.clear()
        self._music.clear()

    def getMusicEvent(self):
        return self._music

    def getAmbientEvent(self):
        return self._ambient

    def getFilters(self):
        return self._filters

    def _onChanged(self):
        self.onChanged(self)

    def _setAmbientParam(self, paramName, value):
        SOUND_DEBUG('Change ambient parameter', paramName, value)
        self._ambient.setParam(paramName, value)

    def _setMusicParam(self, paramName, value):
        SOUND_DEBUG('Change music parameter', paramName, value)
        self._music.setParam(paramName, value)

    def __repr__(self):
        return '%s(music = %s, ambient = %s, filters = %d)' % (self.__class__.__name__,
         self._music,
         self._ambient,
         len(self._filters))


class EmptySpaceEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(EmptySpaceEnv, self).__init__(soundsCtrl, 'empty')


class LoginSpaceEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(LoginSpaceEnv, self).__init__(soundsCtrl, 'login', music=NoMusic(), ambient=NoAmbient())


class LobbySpaceEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(LobbySpaceEnv, self).__init__(soundsCtrl, 'lobby', music=SoundEvent(_MC.MUSIC_EVENT_LOBBY, checkFinish=True), ambient=SoundEvent(_MC.AMBIENT_EVENT_LOBBY))
        self._music.onFinished += self._onMusicFinished

    def stop(self):
        self._music.onFinished -= self._onMusicFinished
        super(LobbySpaceEnv, self).stop()

    def _onMusicFinished(self, isCompleted=False):
        if isCompleted:
            self._music.onFinished -= self._onMusicFinished
            self._music = EmptySound()


class BattleLoadingSpaceEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(BattleLoadingSpaceEnv, self).__init__(soundsCtrl, 'battleLoading', music=SoundEvent(_MC.MUSIC_EVENT_COMBAT_LOADING), ambient=NoAmbient())


class BattleSpaceEnv(SoundEnv, IArenaPeriodController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, soundsCtrl):
        super(BattleSpaceEnv, self).__init__(soundsCtrl, 'battle', music=SoundEvent(_MC.MUSIC_EVENT_COMBAT_LOADING), ambient=SoundEvent(_MC.AMBIENT_EVENT_COMBAT))

    def start(self):
        super(BattleSpaceEnv, self).start()
        self.sessionProvider.addArenaCtrl(self)
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if periodCtrl is not None:
            self._updateBattleAmbient(periodCtrl.getPeriod())
        return

    def stop(self):
        self.sessionProvider.removeArenaCtrl(self)
        super(BattleSpaceEnv, self).stop()

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self._updateBattleAmbient(period)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self._updateBattleAmbient(period)

    def _updateBattleAmbient(self, period):
        if period in (_PERIOD.BATTLE,):
            self._setBattleAmbient()
        elif period in (_PERIOD.AFTERBATTLE,):
            self._setAfterBattleAmbient()

    def _setBattleAmbient(self):
        SOUND_DEBUG('Change battle music event in the battle period')
        self._music = SoundEvent(_MC.MUSIC_EVENT_COMBAT)
        self._onChanged()

    def _setAfterBattleAmbient(self):
        SOUND_DEBUG('Stop battle ambient sounds in the afterbattle period')
        self._music = NoMusic()
        self._onChanged()


class LobbySubViewEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(LobbySubViewEnv, self).__init__(soundsCtrl, 'lobbySubView', filters=(SoundFilters.FILTERED_HANGAR,))


class BattleQueueEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(BattleQueueEnv, self).__init__(soundsCtrl, 'queue', filters=(SoundFilters.FILTERED_HANGAR,))


class ShopEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(ShopEnv, self).__init__(soundsCtrl, 'shop', ambient=SoundEvent(_MC.AMBIENT_EVENT_SHOP), filters=(SoundFilters.FILTERED_HANGAR,))


class ModalWindowEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(ModalWindowEnv, self).__init__(soundsCtrl, 'modal', filters=(SoundFilters.FILTERED_HANGAR,))


class StrongholdEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(StrongholdEnv, self).__init__(soundsCtrl, 'stronghold', filters=(SoundFilters.FILTERED_HANGAR,))


class BattleResultsEnv(SoundEnv):
    _sounds = {WinStatus.WIN: SoundEvent(_MC.MUSIC_EVENT_COMBAT_VICTORY, checkFinish=True),
     WinStatus.DRAW: SoundEvent(_MC.MUSIC_EVENT_COMBAT_DRAW, checkFinish=True),
     WinStatus.LOSE: SoundEvent(_MC.MUSIC_EVENT_COMBAT_LOSE, checkFinish=True)}
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, soundsCtrl):
        super(BattleResultsEnv, self).__init__(soundsCtrl, 'battleResults')

    def start(self):
        super(BattleResultsEnv, self).start()
        lastWinStatus = self.sessionProvider.getCtx().extractLastArenaWinStatus()
        if lastWinStatus is not None:
            SOUND_DEBUG('There is last arena win status need to be processed', lastWinStatus)
            self._music = self._sounds.get(lastWinStatus.getStatus(), EmptySound())
            self._music.onFinished += self._onMusicFinished
        return

    def stop(self):
        self._clearMusicEvent()
        super(BattleResultsEnv, self).stop()

    def _clearMusicEvent(self):
        self._music.onFinished -= self._onMusicFinished
        self._music = EmptySound()

    def _onMusicFinished(self, isCompleted=False):
        self._clearMusicEvent()
        self._onChanged()


class BattlePassSoundEnv(SoundEnv):

    def __init__(self, soundsCtrl):
        super(BattlePassSoundEnv, self).__init__(soundsCtrl, 'battlePass', filters=(SoundFilters.BATTLE_PASS_FILTER,))


class GuiAmbientsCtrl(object):
    _spaces = {GuiGlobalSpaceID.LOGIN: LoginSpaceEnv,
     GuiGlobalSpaceID.LOBBY: LobbySpaceEnv,
     GuiGlobalSpaceID.BATTLE_LOADING: BattleLoadingSpaceEnv,
     GuiGlobalSpaceID.BATTLE: BattleSpaceEnv}
    hangarSpace = dependency.descriptor(IHangarSpace)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, soundsCtrl):
        self._spaceEnv = EmptySpaceEnv(soundsCtrl)
        self._filters = defaultdict(int)
        self._soundsCtrl = soundsCtrl
        self._customEnvs = defaultdict(dict)

    def init(self):
        self.appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        self.appLoader.onGUISpaceLeft += self.__onGUISpaceLeft
        self.hangarSpace.onSpaceChanged += self.__onSpaceChanged

    def fini(self):
        self.appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.appLoader.onGUISpaceLeft -= self.__onGUISpaceLeft
        self.hangarSpace.onSpaceChanged -= self.__onSpaceChanged
        self.stopAllSounds()
        if self._spaceEnv is not None:
            self._clearSoundEnv(self._spaceEnv)
            self._spaceEnv = None
        self._soundsCtrl = None
        return

    def start(self):
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        g_eventBus.addListener(events.LobbySimpleEvent.CHANGE_SOUND_ENVIRONMENT, self.__onEnvChangeRequested)

    def stop(self, isDisconnected=False):
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        if isDisconnected:
            if self.appLoader.getSpaceID() == GuiGlobalSpaceID.LOGIN:
                SOUND_DEBUG('Restart login space sound environment after banks reloading')
                self._restartSounds()
        g_eventBus.removeListener(events.LobbySimpleEvent.CHANGE_SOUND_ENVIRONMENT, self.__onEnvChangeRequested)

    def stopAllSounds(self):
        SOUND_DEBUG('Stop all music and sounds')
        for container in self._customEnvs.itervalues():
            for env in container.itervalues():
                env.stop()

        self._customEnvs.clear()
        for fID in self._filters.iterkeys():
            snd_filters.get(fID).stop()

        self._filters.clear()
        if _MC.g_musicController is not None:
            _MC.g_musicController.stop()
        return

    def setEnvForSpace(self, spaceID, newEnv):
        if spaceID not in self._spaces:
            SOUND_DEBUG('Wrong spaceID - ', spaceID)
            return None
        else:
            oldEnv, self._spaces[spaceID] = self._spaces[spaceID], newEnv
            return oldEnv

    @sf_lobby
    def app(self):
        return None

    def _restartSounds(self):
        result = []
        for vt in (ViewTypes.TOP_WINDOW,
         ViewTypes.WINDOW,
         ViewTypes.LOBBY_TOP_SUB,
         ViewTypes.LOBBY_SUB):
            result.extend(self._customEnvs[vt].values())

        result.append(self._spaceEnv)
        music, ambient = EmptySound(), EmptySound()
        while result and (music.isEmpty() or ambient.isEmpty()):
            env = result.pop(0)
            m, a = env.getMusicEvent(), env.getAmbientEvent()
            if music.isEmpty() and not m.isEmpty():
                music = m
            if ambient.isEmpty() and not a.isEmpty():
                ambient = a

        SOUND_DEBUG('Starting sound events', music, ambient)
        for event in (music, ambient):
            event.start()

    def _buildSoundEnv(self, soundEnvClass):
        env = soundEnvClass(self._soundsCtrl)
        env.start()
        env.onChanged += self.__onAmbientChanged
        for fID in env.getFilters():
            self._filters[fID] += 1
            if self._filters[fID] == 1:
                f = snd_filters.get(fID)
                f.start()
                SOUND_DEBUG('Filter has been started', f)

        return env

    def _clearSoundEnv(self, env, view=None):
        env.stop()
        env.onChanged -= self.__onAmbientChanged
        for fID in env.getFilters():
            self._filters[fID] -= 1
            if self._filters[fID] <= 0:
                f = snd_filters.get(fID)
                f.stop()
                if view is not None:
                    f.stopView(view)
                SOUND_DEBUG('Filter has been stopped', f)

        return env

    def __onGUISpaceEntered(self, spaceID):
        SOUND_DEBUG('Entering GUI space', spaceID, spaceID in self._spaces)
        if spaceID in self._spaces:
            self._clearSoundEnv(self._spaceEnv)
            self._spaceEnv = self._buildSoundEnv(self._spaces[spaceID])
            self._restartSounds()

    def __onGUISpaceLeft(self, spaceID):
        SOUND_DEBUG('Leaving GUI space', spaceID, spaceID in self._spaces)
        if self.app is not None and self.app.containerManager is not None and spaceID in self._spaces:
            customViews = []
            for vt in (ViewTypes.TOP_WINDOW, ViewTypes.WINDOW, ViewTypes.LOBBY_SUB):
                container = self.app.containerManager.getContainer(vt)
                for viewAlias in self._customEnvs[vt].iterkeys():
                    view = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: viewAlias})
                    if view is not None:
                        customViews.append(view)

            for view in customViews:
                self.__onViewDisposed(view)

        return

    def __onViewLoaded(self, view, *args, **kwargs):
        if view is not None:
            self.__registerSoundEnv(view)
            self._restartSounds()
        return

    def __onViewDisposed(self, view):
        uniqueName = view.getUniqueName()
        if uniqueName in self._customEnvs[view.viewType]:
            self.__removeSoundEnv(view, uniqueName)
            view.onDispose -= self.__onViewDisposed
            self._restartSounds()

    def __onEnvChangeRequested(self, event):
        view = event.ctx
        uniqueName = view.getUniqueName()
        if uniqueName in self._customEnvs[view.viewType]:
            self.__removeSoundEnv(view, uniqueName)
        self.__registerSoundEnv(view)
        self._restartSounds()

    def __registerSoundEnv(self, view):
        soundEnvClass = _getViewSoundEnv(view) or _getGFViewSoundEnv(view)
        if soundEnvClass is not None:
            alias = view.alias
            SOUND_DEBUG('Custom sound environ has been detected', alias, soundEnvClass)
            self._customEnvs[view.viewType][view.getUniqueName()] = self._buildSoundEnv(soundEnvClass)
            view.onDispose += self.__onViewDisposed
        else:
            SOUND_DEBUG('Custom sound environ has not been detected', view)
        return

    def __removeSoundEnv(self, view, uniqueName):
        env = self._clearSoundEnv(self._customEnvs[view.viewType][uniqueName], view)
        SOUND_DEBUG('Custom sound environ has been stopped', view.alias, env)
        del self._customEnvs[view.viewType][uniqueName]

    def __onAmbientChanged(self, ambient):
        SOUND_DEBUG('Ambient has been changed', ambient)
        self._restartSounds()

    def __onSpaceChanged(self):
        _MC.g_musicController.stopAmbient(True)
        _MC.g_musicController.stopMusic()
        self._restartSounds()
