# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/logitech/LogitechMonitorMeta.py
from gui.Scaleform.daapi.view.logitech.LogitechComponentMeta import LogitechMonitorComponentMeta

class LogitechMonitorScreenMeta(LogitechMonitorComponentMeta):

    def __init__(self, frame):
        self._frame = frame
        super(LogitechMonitorScreenMeta, self).__init__()

    def _onLoaded(self):
        """ The way we notify inheritor that screen is loaded
        """
        pass

    def _onUnloaded(self):
        """ The way we notify inheritor that screen is unloaded
        """
        pass


class LogitechMonitor(LogitechMonitorScreenMeta):

    def start(self, flashObject):
        self._populate(flashObject)

    def stop(self):
        self._dispose()


class LogitechMonitorMonoScreenMeta(LogitechMonitor):

    def as_setText(self, text):
        if self._flashObject is not None:
            self._flashObject.call('logitech.setMonoText', [text])
        return

    def _populate(self, flashObject):
        super(LogitechMonitorMonoScreenMeta, self)._populate(flashObject)
        self._onLoaded()

    def _dispose(self):
        self._onUnloaded()
        super(LogitechMonitorMonoScreenMeta, self)._dispose()


class LogitechMonitorColoredScreenMeta(LogitechMonitor):

    def __init__(self, flashObject):
        super(LogitechMonitorColoredScreenMeta, self).__init__(flashObject)
        self.__isLoaded = False

    def loadedWithOldFrame(self):
        """
        Called by root entry to notify that screen was constructed on existing flash frame, so it's
        expected that no 'logitech.frameLoaded' is fired.
        This is our chance to be nice and imitate clean load
        """
        self.__isLoaded = True
        self._onLoaded()

    def as_gotoFrameS(self, frame):
        if self._flashObject is not None:
            self._flashObject.call('logitech.gotoFrame', [frame])
        return

    def as_changeViewS(self):
        if self._flashObject is not None:
            self._flashObject.call('logitech.changeView', [])
        return

    def _populate(self, flashObject):
        super(LogitechMonitorColoredScreenMeta, self)._populate(flashObject)
        self.__isLoaded = False
        flashObject.addExternalCallback('logitech.frameLoaded', self.__onFrameLoaded)
        self.as_gotoFrameS(self._frame)

    def _dispose(self):
        if self._flashObject is not None:
            self._flashObject.removeExternalCallback('logitech.frameLoaded', self.__onFrameLoaded)
        if self.__isLoaded:
            self._onUnloaded()
        super(LogitechMonitorColoredScreenMeta, self)._dispose()
        return

    def __onFrameLoaded(self, callBackID, screenLabel):
        self.__isLoaded = True
        self._onLoaded()


class LogitechMonitorHangarColoredScreenMeta(LogitechMonitorColoredScreenMeta):

    def as_setStatsData(self, statsData):
        assert isinstance(statsData, list)
        if self._flashObject is not None:
            self._flashObject.call('logitech.setStatsData', statsData)
        return


class LogitechMonitorBattleLoadingColoredScreenMeta(LogitechMonitorColoredScreenMeta):

    def as_setMap(self, arenaTypeName, battleType, mapImage):
        if self._flashObject is not None:
            self._flashObject.call('logitech.setMap', [arenaTypeName, battleType, mapImage])
        return


class LogitechMonitorBattleMonoScreenMeta(LogitechMonitorMonoScreenMeta):
    pass


class LogitechMonitorBattleColoredScreenMeta(LogitechMonitorColoredScreenMeta):

    def as_setTeamNames(self, alliedTeamName, enemyTeamName):
        if self._flashObject is not None:
            self._flashObject.call('battle.fragCorrelationBar.setTeamNames', [alliedTeamName, enemyTeamName])
            assert False, 'Removed in AS'
        return

    def as_updateFrags(self, progress, label):
        if self._flashObject is not None:
            self._flashObject.call('battle.fragCorrelationBar.updateFrags', [progress, label])
        return

    def as_setTotalTime(self, level, minutes, seconds):
        assert isinstance(minutes, str) and isinstance(seconds, str)
        if self._flashObject is not None:
            self._flashObject.call('battle.timerBar.setTotalTime', [level, minutes, seconds])
        return

    def as_updateDebugInfo(self, fps, ping, isLagging):
        if self._flashObject is not None:
            self._flashObject.call('battle.debugBar.updateInfo', [fps, ping, isLagging])
        return

    def as_setCommandMapping(self, cmdMapping):
        assert isinstance(cmdMapping, list)
        if self._flashObject is not None:
            self._flashObject.call('battle.ingameHelp.setCommandMapping', cmdMapping)
        return

    def as_hideCommandMapping(self, isHide):
        assert isHide
        self.as_setCommandMapping([])
