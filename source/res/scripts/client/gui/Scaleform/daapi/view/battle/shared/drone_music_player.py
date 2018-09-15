# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/drone_music_player.py
import BigWorld
import WWISE
import Event
import SoundGroups
from functools import wraps
from constants import ARENA_GUI_TYPE_LABEL, ARENA_PERIOD
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.battle_control.controllers import team_bases_ctrl
from gui.battle_control.controllers.arena_load_ctrl import IArenaLoadCtrlListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.team_bases_ctrl import ITeamBasesListener
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider

def _delegate(func):

    @wraps(func)
    def __wrapper(self, *args, **kwargs):
        assert isinstance(self, DroneMusicPlayer)
        self._delegateToConditions(func.__name__, *args, **kwargs)
        func(self, *args, **kwargs)

    return __wrapper


def _initCondition(func):

    @wraps(func)
    def __wrapper(self, *args, **kwargs):
        assert isinstance(self, _Condition)
        self._initialized = True
        return func(self, *args, **kwargs)

    return __wrapper


class _Severity(CONST_CONTAINER):
    MEDIUM = 1
    LOW = 2


class _MusicID(CONST_CONTAINER):
    INTENSIVE = 'wwmusicIntensive'
    RELAXED = 'wwmusicRelaxed'
    STOP = 'wwmusicStop'


class _RtpcEvents(CONST_CONTAINER):
    ALLIES_INVADERS_COUNT = 'RTPC_ext_base_capturing_invaders_ally'
    ENEMIES_INVADERS_COUNT = 'RTPC_ext_base_capturing_invaders_enemy'
    ALLIES_BASE_POINTS_CAPTURING = 'RTPC_ext_base_capturing_score_ally'
    ENEMIES_BASE_POINTS_CAPTURING = 'RTPC_ext_base_capturing_score_enemy'


class _Condition(IBattleFieldListener, IAbstractPeriodView, ITeamBasesListener):

    def __init__(self, criticalValue, severity):
        super(_Condition, self).__init__()
        self.criticalValue = criticalValue
        self.__isSatisfied = False
        self.__severity = severity
        self._initialized = False
        self.onValidChangedInternally = Event.Event()

    def isInitialized(self):
        return self._initialized

    def isSatisfied(self):
        return self.__isSatisfied

    def getSeverity(self):
        return self.__severity

    def addCapturingTeamBase(self, clientID, playerTeam, points, rate, timeLeft, invadersCnt, capturingStopped):
        return False

    def updateTeamBasePoints(self, clientID, points, rate, timeLeft, invadersCnt):
        return False

    def removeTeamBase(self, clientID):
        return False

    def removeTeamsBases(self):
        return False

    def setTotalTime(self, totalTime):
        return False

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        return False

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        return False

    def dispose(self):
        self.onValidChangedInternally.clear()

    def _updateValidValue(self, newValue):
        """
        Updates member field if received value is different
        :param newValue: (bool) new value of field
        :return: True if value has been changed, otherwise False
        """
        if self.__isSatisfied != newValue:
            self.__isSatisfied = newValue
            return True
        return False


class _TimeRemainedCondition(_Condition):
    """ This condition goes off when critical time remained till battle end.
    """

    def __init__(self, criticalValue):
        super(_TimeRemainedCondition, self).__init__(criticalValue, _Severity.MEDIUM)
        self.__period = None
        self.__totalTime = None
        return

    def setTotalTime(self, totalTime):
        self.__totalTime = totalTime
        return self._isCriticalAchieved()

    def setPeriod(self, period):
        if self.__period != period:
            self.__period = period
            if period == ARENA_PERIOD.BATTLE:
                self.__totalTime = None
                return False
        return self._isCriticalAchieved()

    def _isCriticalAchieved(self):
        if self.__period is not None and self.__totalTime is not None:
            self._initialized = True
        return self._updateValidValue(True) if self.__period == ARENA_PERIOD.BATTLE and self.__totalTime is not None and self.__totalTime <= self.criticalValue else False


class _DeadVehiclesCondition(_Condition):
    """ The common implementation for conditions that go off when critical amount of alive vehicles remain in team.
    """

    def __init__(self, criticalValue, severity):
        super(_DeadVehiclesCondition, self).__init__(criticalValue, severity)

    @_initCondition
    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        return super(_DeadVehiclesCondition, self).updateDeadVehicles(aliveAllies, deadAllies, aliveEnemies, deadEnemies)

    def _isCriticalAchieved(self, dead, total):
        return self._updateValidValue(True) if total and len(total) - len(dead) <= self.criticalValue else False


class _DeadAlliesCondition(_DeadVehiclesCondition):

    def __init__(self, criticalValue):
        super(_DeadAlliesCondition, self).__init__(criticalValue, _Severity.MEDIUM)

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        super(_DeadAlliesCondition, self).updateDeadVehicles(aliveAllies, deadAllies, aliveEnemies, deadEnemies)
        return self._isCriticalAchieved(deadAllies, aliveAllies | deadAllies)


class _DeadEnemiesCondition(_DeadVehiclesCondition):

    def __init__(self, criticalValue):
        super(_DeadEnemiesCondition, self).__init__(criticalValue, _Severity.LOW)

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        super(_DeadEnemiesCondition, self).updateDeadVehicles(aliveAllies, deadAllies, aliveEnemies, deadEnemies)
        return self._isCriticalAchieved(deadEnemies, aliveEnemies | deadEnemies)


class _TeamHPCondition(_Condition):
    """ The common implementation for conditions that go off when critical amount of team heals remain.
    """

    @_initCondition
    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        return super(_TeamHPCondition, self).updateTeamHealth(alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP)

    def _isCriticalAchieved(self, currentHP, totalHP):
        criticalValue = float(self.criticalValue) / 100
        return self._updateValidValue(True) if totalHP > 0 and float(currentHP) / totalHP <= criticalValue else False


class _AlliesHPCondition(_TeamHPCondition):

    def __init__(self, criticalValue):
        super(_AlliesHPCondition, self).__init__(criticalValue, _Severity.MEDIUM)

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        super(_AlliesHPCondition, self).updateTeamHealth(alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP)
        return self._isCriticalAchieved(alliesHP, totalAlliesHP)


class _EnemiesHPCondition(_TeamHPCondition):

    def __init__(self, criticalValue):
        super(_EnemiesHPCondition, self).__init__(criticalValue, _Severity.LOW)

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        super(_EnemiesHPCondition, self).updateTeamHealth(alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP)
        return self._isCriticalAchieved(enemiesHP, totalEnemiesHP)


class _BaseCaptureCondition(_Condition):
    """ The common implementation for conditions that go off when critical amount of team base points are captured.
    This condition restores to init state after delay specified in settings after base capturing is stopped.
    """

    def __init__(self, criticalValue, severity):
        super(_BaseCaptureCondition, self).__init__(criticalValue, severity)
        self.__pointsToBase = {}
        self.__stopCapturingCooldown = None
        return

    def dispose(self):
        super(_BaseCaptureCondition, self).dispose()
        if self.__stopCapturingCooldown is not None:
            BigWorld.cancelCallback(self.__stopCapturingCooldown)
            self.__stopCapturingCooldown = None
        return

    @_initCondition
    def setNoBaseCapturing(self):
        pass

    @_initCondition
    def addCapturingTeamBase(self, clientID, playerTeam, points, rate, timeLeft, invadersCnt, capturingStopped):
        baseTeam, baseID = team_bases_ctrl.parseClientTeamBaseID(clientID)
        if self._getValidBaseMask() == baseTeam ^ playerTeam:
            self.__pointsToBase[clientID] = points
            self.__setRtpcGlobal(points, invadersCnt)
            return self._validatePoints()
        return False

    @_initCondition
    def updateTeamBasePoints(self, clientID, points, rate, timeLeft, invadersCnt):
        if clientID in self.__pointsToBase:
            self.__pointsToBase[clientID] = points
            self.__setRtpcGlobal(points, invadersCnt)
            return self._validatePoints()
        return False

    def removeTeamBase(self, clientID):
        if clientID in self.__pointsToBase:
            del self.__pointsToBase[clientID]
            self.__setRtpcGlobal(0, 0)
            return self._validatePoints()
        return False

    def removeTeamsBases(self):
        if self.__pointsToBase:
            self.__pointsToBase.clear()
            self.__setRtpcGlobal(0, 0)
            return self._validatePoints()
        else:
            return False

    def _getValidBaseMask(self):
        raise NotImplementedError

    def _getRtpcPointsID(self):
        raise NotImplementedError

    def _getRtpcInvadersCountID(self):
        raise NotImplementedError

    def _validatePoints(self):
        criticalPointsCount, musicStopPredelay = self.criticalValue
        for points in self.__pointsToBase.itervalues():
            if self.__stopCapturingCooldown is not None and points:
                assert self.isSatisfied(), 'Condition must be in the valid state while cooldown is working'
                BigWorld.cancelCallback(self.__stopCapturingCooldown)
                LOG_DEBUG('Base Capturing. Cooldown stopped')
                self.__stopCapturingCooldown = None
                return False
            if points >= criticalPointsCount:
                return self._updateValidValue(True)

        if self.isSatisfied():
            assert self.__stopCapturingCooldown is None, 'Cooldown must be set only once!'
            LOG_DEBUG('Base Capturing. Stop music cooldown has been started')
            self.__stopCapturingCooldown = BigWorld.callback(musicStopPredelay, self.__onCooldownOver)
        return False

    def __onCooldownOver(self):
        self.__stopCapturingCooldown = None
        if self._updateValidValue(False):
            self.onValidChangedInternally()
        return

    def __setRtpcGlobal(self, points, invadersCount):
        WWISE.WW_setRTCPGlobal(self._getRtpcPointsID(), points)
        WWISE.WW_setRTCPGlobal(self._getRtpcInvadersCountID(), invadersCount)


class _AlliedBaseCaptureCondition(_BaseCaptureCondition):

    def __init__(self, criticalValue):
        super(_AlliedBaseCaptureCondition, self).__init__(criticalValue, _Severity.MEDIUM)

    def _getValidBaseMask(self):
        pass

    def _getRtpcPointsID(self):
        return _RtpcEvents.ALLIES_BASE_POINTS_CAPTURING

    def _getRtpcInvadersCountID(self):
        return _RtpcEvents.ALLIES_INVADERS_COUNT


class _EnemyBaseCaptureCondition(_BaseCaptureCondition):

    def __init__(self, criticalValue):
        super(_EnemyBaseCaptureCondition, self).__init__(criticalValue, _Severity.LOW)

    def _getValidBaseMask(self):
        pass

    def _getRtpcPointsID(self):
        return _RtpcEvents.ENEMIES_BASE_POINTS_CAPTURING

    def _getRtpcInvadersCountID(self):
        return _RtpcEvents.ENEMIES_INVADERS_COUNT


class DroneMusicPlayer(IBattleFieldListener, IAbstractPeriodView, ITeamBasesListener, IViewComponentsCtrlListener, IArenaLoadCtrlListener):
    """ This is the consumer which launch the music in some important situations happening during the battle.
    If our team in troubles it launches intensive music which motivates team member to try hard.
    If enemy team is in troubles it launches relaxed music.
    This situations describes in the list of conditions which handle data received from controllers.
    Music can be stopped in some cases (base capturing is over for example).
    """
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _SETTING_TO_CONDITION_MAPPING = {'vehiclesRemained': (lambda player: not player.sessionProvider.arenaVisitor.hasArenaFogOfWarHiddenVehicles(), (_DeadAlliesCondition, _DeadEnemiesCondition), lambda name, key, data: data[name][key]),
     'timeRemained': (lambda player: True, (_TimeRemainedCondition,), lambda name, key, data: data[name][key]),
     'capturedPoints': (lambda player: True, (_AlliedBaseCaptureCondition, _EnemyBaseCaptureCondition), lambda name, key, data: (data[name][key], data['musicStopPredelay'][key])),
     'hpPercentRemained': (lambda player: not player.sessionProvider.arenaVisitor.hasArenaFogOfWarHiddenVehicles(), (_AlliesHPCondition, _EnemiesHPCondition), lambda name, key, data: data[name][key])}

    def __init__(self):
        super(DroneMusicPlayer, self).__init__()
        self.__arenaPeriod = None
        self.__isArenaLoadingCompleted = False
        arenaType = self.sessionProvider.arenaVisitor.getArenaType()
        self.__guiTypeName = ARENA_GUI_TYPE_LABEL.LABELS[self.sessionProvider.arenaVisitor.getArenaGuiType()]
        self.__gameplayName = arenaType.gameplayName
        self._musicSetup = self._initializeMusicData(arenaType)
        self._conditions = []
        if self._musicSetup is not None:
            self._conditions = self._initializeConditionsData(arenaType)
        for condition in self._conditions:
            condition.onValidChangedInternally += self.__onConditionChangedItself

        self.__playingMusicID = None
        self._initialized = False
        return

    @_delegate
    def addCapturingTeamBase(self, clientID, playerTeam, points, rate, timeLeft, invadersCnt, capturingStopped):
        pass

    @_delegate
    def updateTeamBasePoints(self, clientID, points, rate, timeLeft, invadersCnt):
        pass

    @_delegate
    def setNoBaseCapturing(self):
        pass

    @_delegate
    def removeTeamBase(self, clientID):
        pass

    @_delegate
    def removeTeamsBases(self):
        pass

    @_delegate
    def setPeriod(self, period):
        if self.__arenaPeriod != period:
            self.__arenaPeriod = period
            self.__checkInitialization()

    @_delegate
    def setTotalTime(self, totalTime):
        pass

    @_delegate
    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        pass

    @_delegate
    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        pass

    def arenaLoadCompleted(self):
        self.__isArenaLoadingCompleted = True
        self.__checkInitialization()

    def detachedFromCtrl(self, ctrlID):
        if self.__isMusicCurrentlyPlaying():
            self.__stopMusic()
        while self._conditions:
            condition = self._conditions.pop()
            condition.onValidChangedInternally -= self.__onConditionChangedItself
            condition.dispose()

    def _initializeMusicData(self, arenaType):
        """
        Extract music IDs from <wwmusicSetup/> section from .../arena_defs/_default_.xml
        :param arenaType: ArenaType
        :return: dict: key - settingName, value - settingValue
        """
        wwSetup = arenaType.wwmusicSetup
        if wwSetup is None:
            return
        else:
            outcome = {}
            for tagName in _MusicID.ALL():
                musicID = wwSetup.get(tagName)
                if musicID is None:
                    LOG_ERROR("Music ID for '{}' tag is not defined! Music drone can't be initialized properly!".format(tagName))
                outcome[tagName] = musicID

            return outcome

    def _initializeConditionsData(self, arena_type):
        """Creates conditions and initializes them using extracted data
        of <wwmusicDroneSetup/> section from .../arena_defs/_default_.xml
        :param arena_type: ArenaType
        :return: None
        """
        wwmusicDroneSetup = arena_type.wwmusicDroneSetup
        outcome = []
        for settingName, conditionsData in self._SETTING_TO_CONDITION_MAPPING.iteritems():
            setting = wwmusicDroneSetup.get(settingName)
            if setting:
                key = (self.__guiTypeName, self.__gameplayName)
                value = setting.get(key)
                if value:
                    canBeCreated, condClasses, extractor = conditionsData
                    if canBeCreated(self):
                        for conditionClazz in condClasses:
                            outcome.append(conditionClazz(extractor(settingName, key, wwmusicDroneSetup)))

        return outcome

    def _delegateToConditions(self, event, *args, **kwargs):
        for condition in self._conditions:
            notifier = getattr(condition, event)
            if callable(notifier):
                satisfiedChanged = notifier(*args, **kwargs)
                if self.__isProperBattlePeroid():
                    if self._initialized:
                        if satisfiedChanged:
                            self.__validateConditions()
                    else:
                        self.__checkFullInitialization()
            LOG_ERROR('Listener method not found', condition, event)

    def _launchEvent(self, soundType):
        soundID = self._musicSetup[soundType]
        LOG_DEBUG('Attempt to launch Drone event "{}"'.format(soundID))
        if soundID is not None:
            SoundGroups.g_instance.playSound2D(soundID)
        return

    def __onConditionChangedItself(self):
        if self.__isProperBattlePeroid():
            self.__validateConditions()

    def __checkFullInitialization(self):
        allInited = True
        for condition in self._conditions:
            if condition.isInitialized():
                if condition.isSatisfied() and condition.getSeverity() == _Severity.MEDIUM:
                    self._initialized = True
                    self.__validateConditions()
                    return
            allInited = False

        if allInited:
            self._initialized = True
            self.__validateConditions()

    def __validateConditions(self):
        """
        This method starts music playing if conditions list is not empty.
        And stops music if there are no active conditions
        """
        isPlaying = self.__isMusicCurrentlyPlaying()
        satisfied = filter(lambda condition: condition.isSatisfied(), self._conditions)
        if satisfied:
            if not isPlaying:
                for condition in satisfied:
                    if condition.getSeverity() == _Severity.MEDIUM:
                        self.__playingMusicID = _MusicID.INTENSIVE
                        break
                else:
                    self.__playingMusicID = _MusicID.RELAXED

                LOG_DEBUG('Satisfied Drone conditions: {}'.format(satisfied))
                self.__playMusic()
        elif isPlaying:
            self.__stopMusic()

    def __checkInitialization(self):
        if self.__isProperBattlePeroid():
            if self._initialized:
                self.__validateConditions()
            else:
                self.__checkFullInitialization()

    def __isProperBattlePeroid(self):
        return self.__arenaPeriod == ARENA_PERIOD.BATTLE and self.__isArenaLoadingCompleted

    def __stopMusic(self):
        LOG_DEBUG('Playing Drone music "{}" has been stopped'.format(self.__playingMusicID))
        self._launchEvent(_MusicID.STOP)
        self.__playingMusicID = None
        return

    def __playMusic(self):
        LOG_DEBUG('Drone music "{}" has been launched'.format(self.__playingMusicID))
        self._launchEvent(self.__playingMusicID)

    def __isMusicCurrentlyPlaying(self):
        return self.__playingMusicID is not None
