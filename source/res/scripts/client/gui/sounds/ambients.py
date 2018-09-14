# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/ambients.py
import weakref
from collections import defaultdict
from Event import Event
import MusicControllerWWISE as _MC
from constants import FORT_BUILDING_TYPE as FBT, ARENA_PERIOD as _PERIOD
from ClientFortifiedRegion import BUILDING_UPDATE_REASON as _BUR
from shared_utils import BoundMethodWeakref
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable
from gui.shared.fortifications.settings import CLIENT_FORT_STATE as _CFS
from gui.sounds import filters as snd_filters
from gui.sounds.sound_constants import SoundFilters, PLAYING_SOUND_CHECK_PERIOD
from gui.sounds.sound_utils import SOUND_DEBUG
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import WinStatus
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from gui.app_loader import g_appLoader
from gui.app_loader.decorators import sf_lobby
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.framework import ViewTypes

def _getViewSoundEnv(view):
    """Check if view has '__sound_env__' attribute and return it.
    If view is modal window then we need to apply hangar sound filter,
    so return ModalWindowEnv class as '__sound_env__' attribute.
    """
    if hasattr(view, '__sound_env__'):
        return getattr(view, '__sound_env__')
    else:
        return ModalWindowEnv if isinstance(view, WindowViewMeta) and view.as_isModalS() else None


class SoundEvent(Notifiable):
    """
    Sound event object. Contains of one sound event (music or ambient)
    and playing addition parameters. Can check sound ending and fire
    corresponded event according to the given ctor's flag @checkFinish
    """

    def __init__(self, soundEventID, params=None, checkFinish=False):
        super(SoundEvent, self).__init__()
        self._soundEventID = soundEventID
        self._params = params or {}
        self._checkFinish = checkFinish
        self.onStarted = Event()
        self.onFinished = Event()

    def __del__(self):
        self.clearNotification()

    def getID(self):
        return self._soundEventID

    def isEmpty(self):
        """Is sound empty or not
        :return: bool
        """
        return self._soundEventID is None

    def clearParams(self):
        """Playing parameters can be changed during playing time, reset
        them to the defaults
        """
        self._params.clear()

    def start(self):
        if not self.isPlaying():
            SOUND_DEBUG('Start playing sound event', self._soundEventID, self._params)
            _MC.g_musicController.play(self._soundEventID, self._params)
            if self._checkFinish:
                self.addNotificators(PeriodicNotifier(BoundMethodWeakref(self._getNotificationDelta), BoundMethodWeakref(self._onCheckAmbientNotification), (PLAYING_SOUND_CHECK_PERIOD,)))
                self.startNotification()
                self.onStarted()
        else:
            SOUND_DEBUG('Sound is already playing', self._soundEventID, self._params)

    def stop(self):
        if self.isPlaying():
            SOUND_DEBUG('Stop sound event playing', self._soundEventID)
            _MC.g_musicController.stopEvent(self._soundEventID)
            if self._checkFinish:
                self.clearNotification()
                self.onFinished()
        else:
            SOUND_DEBUG('Skip stopping, sound is already stopped', self._soundEventID)

    def isPlaying(self):
        return _MC.g_musicController.isPlaying(self._soundEventID)

    def isCompleted(self):
        return _MC.g_musicController.isCompleted(self._soundEventID)

    def setParam(self, paramName, value):
        """Setting sound event's playing parameter value
        :param paramName: str, parameter name
        :param value: parameter value
        """
        self._params[paramName] = value
        _MC.g_musicController.setEventParam(self._soundEventID, paramName, int(value))

    def _getNotificationDelta(self):
        """Is sound still playing or not, this helper is needed to check sound's ending
        :return: int, seconds to delay checking handler
        """
        if self.isPlaying():
            return PLAYING_SOUND_CHECK_PERIOD
        else:
            return 0

    def _onCheckAmbientNotification(self):
        SOUND_DEBUG('Current ambient playing check: is playing now', self, self.isPlaying())
        if not self.isPlaying():
            self.onFinished(self.isCompleted())

    def __repr__(self):
        return '%s(id = %d, params = %s)' % (self.__class__.__name__, self._soundEventID, self._params)


class EmptySound(SoundEvent):
    """Empty sound event stub, used to mark environment sounds as
    'pass-through'
    """

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
    """Empty music event stub, used to stop any previous played music
    """

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
    """Empty ambient event stub, used to stop any previous played ambient
    """

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
    """Root sound environment class. Contains of one music event and
    one ambient event, also has bunch of filters, that can be applied to
    the sound system at @start method
    """

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

    def getMusicEvent(self):
        """:return: SoundEvent object instance
        """
        return self._music

    def getAmbientEvent(self):
        """:return: SoundEvent object instance
        """
        return self._ambient

    def getFilters(self):
        """:return: list, filters ids
        """
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
        super(LoginSpaceEnv, self).__init__(soundsCtrl, 'login', music=SoundEvent(_MC.MUSIC_EVENT_LOGIN), ambient=NoAmbient())


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
    """Simple battle space sound environment, has logic to stop music event
    only after BEFOREBATTLE period on arena
    """

    def __init__(self, soundsCtrl):
        super(BattleSpaceEnv, self).__init__(soundsCtrl, 'battle', music=SoundEvent(_MC.MUSIC_EVENT_COMBAT_LOADING), ambient=SoundEvent(_MC.AMBIENT_EVENT_COMBAT))

    def start(self):
        super(BattleSpaceEnv, self).start()
        g_sessionProvider.addArenaCtrl(self)
        periodCtrl = g_sessionProvider.shared.arenaPeriod
        if periodCtrl is not None:
            self._updateBattleAmbient(periodCtrl.getPeriod())
        return

    def stop(self):
        g_sessionProvider.removeArenaCtrl(self)
        super(BattleSpaceEnv, self).stop()

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID):
        self._updateBattleAmbient(period)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self._updateBattleAmbient(period)

    def _updateBattleAmbient(self, period):
        if period in (_PERIOD.BATTLE,):
            SOUND_DEBUG('Change battle music event in the battle period')
            self._music = SoundEvent(_MC.MUSIC_EVENT_COMBAT)
            self._onChanged()
        elif period in (_PERIOD.AFTERBATTLE,):
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
    """Enable Hangar sound filter for modal window
    """

    def __init__(self, soundsCtrl):
        super(ModalWindowEnv, self).__init__(soundsCtrl, 'modal', filters=(SoundFilters.FILTERED_HANGAR,))


class FortEnv(SoundEnv, FortViewHelper):
    """This environment plays fort specific ambient and changes playing
    parameters on runtime according to the fortification events.
    """

    def __init__(self, soundsCtrl):
        self.filter = weakref.proxy(snd_filters.get(SoundFilters.FORT_FILTER))
        super(FortEnv, self).__init__(soundsCtrl, 'fort', ambient=SoundEvent(_MC.AMBIENT_EVENT_LOBBY_FORT, {self.filter.getDefencePeriodField(): 0,
         self.filter.getBuildNumberField(): 0,
         self.filter.getTransportModeField(): 0}), filters=(SoundFilters.FORT_FILTER, SoundFilters.FILTERED_HANGAR))

    def start(self):
        super(FortEnv, self).start()
        g_eventBus.addListener(events.FortEvent.IS_IN_TRANSPORTING_MODE, self.__onTransportingModeChanged, scope=EVENT_BUS_SCOPE.FORT)
        self.startFortListening()

    def stop(self):
        g_eventBus.removeListener(events.FortEvent.IS_IN_TRANSPORTING_MODE, self.__onTransportingModeChanged, scope=EVENT_BUS_SCOPE.FORT)
        self.stopFortListening()
        if self._soundsCtrl is not None:
            self._soundsCtrl.system.sendGlobalEvent('fa_music_global_unmute')
        super(FortEnv, self).stop()
        return

    def onClientStateChanged(self, state):
        if state.getStateID() in (_CFS.WIZARD, _CFS.HAS_FORT):
            self._updateBuildsNumber()

    def onBuildingChanged(self, buildingTypeID, reason, ctx=None):
        if reason in (_BUR.UPDATED, _BUR.COMPLETED, _BUR.DELETED):
            self._updateBuildsNumber()

    def onDefenceHourStateChanged(self):
        fort = self.fortCtrl.getFort()
        if fort is not None:
            self._setAmbientParam(self.filter.getDefencePeriodField(), fort.isOnDefenceHour())
        return

    def _updateBuildsNumber(self):
        fort = self.fortCtrl.getFort()
        if fort is not None:
            self._setAmbientParam(self.filter.getBuildNumberField(), len(fort.getBuildingsCompleted(FBT.MILITARY_BASE)))
        return

    def __onTransportingModeChanged(self, event):
        self._setAmbientParam(self.filter.getTransportModeField(), event.ctx.get('isInTransportingMode', False))


class BattleResultsEnv(SoundEnv):
    """ After arena was finished there is last winner status in the BattleContext
    object instance can be found. This environment is linked with battle results
    window and trying to play battle-results-music according to saved winner status.
    Directly after music has finished music event should be cleared to EmptySound to
    avoid repeating of playing.
    """
    _battleEndSounds = {WinStatus.WIN: SoundEvent(_MC.MUSIC_EVENT_COMBAT_VICTORY, checkFinish=True),
     WinStatus.DRAW: SoundEvent(_MC.MUSIC_EVENT_COMBAT_DRAW, checkFinish=True),
     WinStatus.LOSE: SoundEvent(_MC.MUSIC_EVENT_COMBAT_LOSE, checkFinish=True)}
    _eventBattleEndSounds = {WinStatus.WIN: SoundEvent(_MC.MUSIC_EVENT_COMBAT_EVENT_VICTORY, checkFinish=True),
     WinStatus.DRAW: SoundEvent(_MC.MUSIC_EVENT_COMBAT_EVENT_DRAW, checkFinish=True),
     WinStatus.LOSE: SoundEvent(_MC.MUSIC_EVENT_COMBAT_EVENT_LOSE, checkFinish=True)}

    def __init__(self, soundsCtrl):
        super(BattleResultsEnv, self).__init__(soundsCtrl, 'battleResults')

    def start(self):
        super(BattleResultsEnv, self).start()
        ctx = g_sessionProvider.getCtx()
        lastWinStatus = ctx.extractLastArenaWinStatus()
        if lastWinStatus is not None:
            SOUND_DEBUG('There is last arena win status need to be processed', lastWinStatus)
            sounds = self._eventBattleEndSounds if ctx.isEventBattle() else self._battleEndSounds
            self._music = sounds.get(lastWinStatus.getStatus(), EmptySound())
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


class GuiAmbientsCtrl(object):
    """All ambients in client (lobby and battle) packed on several layers with
    different playing priority:
    - there is space environment with the lowest priority, only one space environment
    can be played in every moment of time; spaces are corresponded to the GUI spaces GUI_GLOBAL_SPACE_ID
    - there are some additional environments layers corresponded to the top-window, window and
    lobby-sub-view GUI containers;
    
    Sound environment can be attached to the any of view classes using '__sound_env__' attribute.
    This controller catches view loading events and checks whether view has custom
    environment, builds it and starts playing in success case. After view has been disposed
    controller stops environment and removes it from queue.
    
    There are only two sound event can be played at one moment of time. But active opened
    views can be more, though there is algo (@_restartSounds method) that collects music and
    ambient events walking through all active environments from @__customEnvs in priority order.
    Any ambient can fire onChanged event and starts restart this algo.
    """
    _spaces = {_SPACE_ID.LOBBY: LobbySpaceEnv,
     _SPACE_ID.BATTLE_LOADING: BattleLoadingSpaceEnv,
     _SPACE_ID.BATTLE: BattleSpaceEnv}

    def __init__(self, soundsCtrl):
        self._spaceEnv = EmptySpaceEnv(soundsCtrl)
        self._filters = defaultdict(int)
        self._soundsCtrl = soundsCtrl
        self._customEnvs = defaultdict(dict)

    def init(self):
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered

    def fini(self):
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.stopAllSounds()
        self._clearSoundEnv(self._spaceEnv)
        self._spaceEnv = None
        self._soundsCtrl = None
        return

    def start(self):
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    def stop(self, isDisconnected=False):
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        if isDisconnected:
            if g_appLoader.getSpaceID() == _SPACE_ID.LOGIN:
                SOUND_DEBUG('Restart login space sound environment after banks reloading')
                self._restartSounds()

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

    @sf_lobby
    def app(self):
        return None

    def _restartSounds(self):
        result = []
        for vt in (ViewTypes.TOP_WINDOW, ViewTypes.WINDOW, ViewTypes.LOBBY_SUB):
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

    def _clearSoundEnv(self, env):
        env.stop()
        env.onChanged -= self.__onAmbientChanged
        for fID in env.getFilters():
            self._filters[fID] -= 1
            if self._filters[fID] <= 0:
                f = snd_filters.get(fID)
                f.stop()
                SOUND_DEBUG('Filter has been stopped', f)

        return env

    def __onGUISpaceEntered(self, spaceID):
        SOUND_DEBUG('GUI space has been changed', spaceID, spaceID in self._spaces)
        if spaceID in self._spaces:
            self._clearSoundEnv(self._spaceEnv)
            self._spaceEnv = self._buildSoundEnv(self._spaces[spaceID])
            self._restartSounds()

    def __onViewLoaded(self, view):
        if view is not None and view.settings is not None:
            soundEnvClass = _getViewSoundEnv(view)
            if soundEnvClass is not None:
                alias = view.settings.alias
                SOUND_DEBUG('Custom sound environ has been detected', alias, soundEnvClass)
                self._customEnvs[view.settings.type][view.getUniqueName()] = self._buildSoundEnv(soundEnvClass)
                view.onModuleDispose += self.__onViewDisposed
                self._restartSounds()
            else:
                SOUND_DEBUG('Custom sound environ has not been detected', view)
        return

    def __onViewDisposed(self, view):
        uniqueName = view.getUniqueName()
        if uniqueName in self._customEnvs[view.settings.type]:
            env = self._clearSoundEnv(self._customEnvs[view.settings.type][uniqueName])
            SOUND_DEBUG('Custom sound environ has been stopped', view.settings.alias, env)
            del self._customEnvs[view.settings.type][uniqueName]
            view.onModuleDispose -= self.__onViewDisposed
            self._restartSounds()

    def __onAmbientChanged(self, ambient):
        SOUND_DEBUG('Ambient has been changed', ambient)
        self._restartSounds()
