# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/resource_points.py
import weakref
import BigWorld
from CTFManager import g_ctfManager
from constants import RESOURCE_POINT_STATE
from gui.battle_control import g_sessionProvider
from gui.shared.utils.plugins import IPlugin
from gui.Scaleform.locale.FALLOUT import FALLOUT
from helpers import i18n, time_utils
from account_helpers.settings_core.SettingsCore import g_settingsCore
_CALLBACK_INDICATOR_NAME = 'battle.onLoadResourceIndicator'
_CALLBACK_PANEL_NAME = 'battle.onLoadResourcePointsPanel'

class _POINTS_STATE:
    FREEZE = 'freeze'
    COOLDOWN = 'cooldown'
    READY = 'ready'
    OWN_MINING = 'ownMining'
    ENEMY_MINING = 'enemyMining'
    OWN_MINING_FROZEN = 'ownMiningFrozen'
    ENEMY_MINING_FROZEN = 'enemyMiningFrozen'
    CONFLICT = 'conflict'


_CAPTURE_STATE_BY_TEAMS = {True: _POINTS_STATE.OWN_MINING,
 False: _POINTS_STATE.ENEMY_MINING}
_CAPTURE_FROZEN_STATE_BY_TEAMS = {True: _POINTS_STATE.OWN_MINING_FROZEN,
 False: _POINTS_STATE.ENEMY_MINING_FROZEN}

class _ResourceIndicator(object):

    def __init__(self, plugin):
        self.__plugin = weakref.proxy(plugin)
        self.__flashObject = weakref.proxy(plugin.parentObj.movie.resourceIndicator.instance)

    def init(self):
        disabledStr = i18n.makeString(FALLOUT.RESOURCEPOINTS_DISABLED_DESCR)
        miningStr = i18n.makeString(FALLOUT.RESOURCEPOINTS_MINING_DESCR)
        cooldownStr = i18n.makeString(FALLOUT.RESOURCEPOINTS_COOLDOWN_DESCR)
        self.flashObject.as_setTexts(cooldownStr, miningStr, disabledStr)
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged

    def destroy(self):
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__plugin = None
        self.__flashObject = None
        return

    def __onSettingsChanged(self, diff = None):
        self.flashObject.as_onSettingsChanged()

    @property
    def flashObject(self):
        return self.__flashObject

    def show(self, pointIdx):
        self.flashObject.as_show(pointIdx)

    def setFreeze(self, isFrozen, timeStr):
        self.flashObject.as_setFreeze(isFrozen, timeStr)

    def hide(self):
        self.flashObject.as_hide()


class _ResourcePointsPanel(object):

    def __init__(self, plugin):
        self.__plugin = weakref.proxy(plugin)
        self.__flashObject = weakref.proxy(plugin.parentObj.movie.resourcePointsPanel.instance)

    def init(self):
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.flashObject.as_init(self._makeData())

    def update(self):
        self.flashObject.as_updateData(self._makeData())

    def destroy(self):
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__plugin = None
        self.__flashObject = None
        return

    @property
    def flashObject(self):
        return self.__flashObject

    def _makeData(self):
        result = []
        arenaDP = g_sessionProvider.getArenaDP()
        for pointID, point in g_ctfManager.getResourcePoints():
            pointState = point['state']
            timeLeft = ''
            amount = point['amount']
            progress = float(amount) / point['totalAmount'] * 100
            if pointState == RESOURCE_POINT_STATE.FREE:
                state = _POINTS_STATE.READY
            elif pointState == RESOURCE_POINT_STATE.COOLDOWN:
                self.__plugin.setUpdateRequired(True)
                state = _POINTS_STATE.COOLDOWN
                timeDelta = max(0, point['cooldownTime'] - BigWorld.serverTime())
                timeLeft = time_utils.getTimeLeftFormat(timeDelta)
            elif pointState == RESOURCE_POINT_STATE.CAPTURED:
                state = _CAPTURE_STATE_BY_TEAMS[arenaDP.isAllyTeam(point['team'])]
            elif pointState == RESOURCE_POINT_STATE.CAPTURED_LOCKED:
                state = _CAPTURE_FROZEN_STATE_BY_TEAMS[arenaDP.isAllyTeam(point['team'])]
            elif pointState == RESOURCE_POINT_STATE.BLOCKED:
                state = _POINTS_STATE.CONFLICT
            else:
                state = _POINTS_STATE.FREEZE
            result.append(self._makeItem(progress, state, amount, timeLeft))

        return result

    def _makeItem(self, progress, state, pointsCount, timeLeftStr):
        return {'progress': progress,
         'state': state,
         'pointsCount': pointsCount,
         'timeLeftStr': timeLeftStr}

    def __onSettingsChanged(self, diff = None):
        if 'isColorBlind' in diff:
            self.flashObject.as_onSettingsChanged()


class ResourcePointsPlugin(IPlugin):

    def __init__(self, parentObj):
        super(ResourcePointsPlugin, self).__init__(parentObj)
        self.__resourceIndicator = None
        self.__resourcePointsPanel = None
        self.__updateCallbackID = None
        self.__freezeCallbackID = None
        self.__updateRequired = False
        return

    def init(self):
        super(ResourcePointsPlugin, self).init()
        self._parentObj.addExternalCallback(_CALLBACK_INDICATOR_NAME, self.__onLoadResourceIndicator)
        self._parentObj.addExternalCallback(_CALLBACK_PANEL_NAME, self.__onLoadResourcePointsPanel)
        g_ctfManager.onResPointIsFree += self.__processUpdate
        g_ctfManager.onResPointCooldown += self.__processUpdate
        g_ctfManager.onResPointCaptured += self.__processUpdate
        g_ctfManager.onResPointCapturedLocked += self.__processUpdate
        g_ctfManager.onResPointBlocked += self.__processUpdate
        g_ctfManager.onResPointAmountChanged += self.__processUpdate
        g_ctfManager.onOwnVehicleInsideResPoint += self.__onOwnVehicleInside
        g_ctfManager.onOwnVehicleLockedForResPoint += self.__onOwnVehicleLocked

    def fini(self):
        self._parentObj.removeExternalCallback(_CALLBACK_INDICATOR_NAME)
        self._parentObj.removeExternalCallback(_CALLBACK_PANEL_NAME)
        g_ctfManager.onResPointIsFree -= self.__processUpdate
        g_ctfManager.onResPointCooldown -= self.__processUpdate
        g_ctfManager.onResPointCaptured -= self.__processUpdate
        g_ctfManager.onResPointCapturedLocked -= self.__processUpdate
        g_ctfManager.onResPointBlocked -= self.__processUpdate
        g_ctfManager.onResPointAmountChanged -= self.__processUpdate
        g_ctfManager.onOwnVehicleInsideResPoint -= self.__onOwnVehicleInside
        g_ctfManager.onOwnVehicleLockedForResPoint -= self.__onOwnVehicleLocked
        super(ResourcePointsPlugin, self).fini()

    def start(self):
        super(ResourcePointsPlugin, self).start()
        self._parentObj.movie.falloutItems.as_loadResourceIndicator()
        self._parentObj.movie.falloutItems.as_loadResourcePointsPanel()

    def stop(self):
        self.__cancelUpdateCallback()
        self.__cancelFreezeCallback()
        if self.__resourceIndicator is not None:
            self.__resourceIndicator.destroy()
            self.__resourceIndicator = None
        if self.__resourcePointsPanel is not None:
            self.__resourcePointsPanel.destroy()
            self.__resourcePointsPanel = None
        super(ResourcePointsPlugin, self).stop()
        return

    def setUpdateRequired(self, updateRequired):
        self.__updateRequired = updateRequired

    def __processUpdate(self, *args):
        if self.__updateCallbackID is not None:
            self.__updateRequired = True
        else:
            self.__update()
        return

    def __initUpdateCallback(self):
        if self.__updateRequired:
            self.__updateRequired = False
            self.__updateCallbackID = BigWorld.callback(1.0, self.__update)
        else:
            self.__updateCallbackID = None
        return

    def __cancelUpdateCallback(self):
        if self.__updateCallbackID is not None:
            BigWorld.cancelCallback(self.__updateCallbackID)
            self.__updateCallbackID = None
        return

    def __update(self):
        if self.__resourcePointsPanel is not None:
            self.__resourcePointsPanel.update()
        self.__initUpdateCallback()
        return

    def __initFreezeCallback(self):
        self.__freezeCallbackID = BigWorld.callback(1.0, self.__updateFreeze)

    def __cancelFreezeCallback(self):
        if self.__freezeCallbackID is not None:
            BigWorld.cancelCallback(self.__freezeCallbackID)
            self.__freezeCallbackID = None
        return

    def __updateFreeze(self):
        lock = g_ctfManager.getResourcePointLock()
        if lock is not None:
            timeDelta = max(0, g_ctfManager.getResourcePointLock() - BigWorld.serverTime())
        else:
            timeDelta = 0
        timeStr = time_utils.getTimeLeftFormat(timeDelta)
        if self.__resourceIndicator is not None:
            self.__resourceIndicator.setFreeze(True, timeStr)
        self.__initFreezeCallback()
        return

    def __onLoadResourceIndicator(self, _):
        self.__resourceIndicator = _ResourceIndicator(self)
        self.__resourceIndicator.init()
        for pointID, point in g_ctfManager.getResourcePoints():
            if point['isPlayerCapture']:
                self.__resourceIndicator.show(pointID)
                break

    def __onLoadResourcePointsPanel(self, _):
        self.__resourcePointsPanel = _ResourcePointsPanel(self)
        self.__resourcePointsPanel.init()
        self.__processUpdate()

    def __onOwnVehicleInside(self, pointID):
        self.__cancelFreezeCallback()
        if pointID is None:
            if self.__resourceIndicator is not None:
                self.__resourceIndicator.setFreeze(False, '')
                self.__resourceIndicator.hide()
        else:
            if self.__resourcePointsPanel is not None:
                self.__resourcePointsPanel.update()
            if self.__resourceIndicator is not None:
                self.__resourceIndicator.show(pointID)
            if g_ctfManager.getResourcePointLock() is not None:
                self.__updateFreeze()
        return

    def __onOwnVehicleLocked(self, unlockTime):
        self.__cancelFreezeCallback()
        if unlockTime is not None:
            self.__updateFreeze()
        elif self.__resourceIndicator is not None:
            self.__resourceIndicator.setFreeze(False, '')
        return
