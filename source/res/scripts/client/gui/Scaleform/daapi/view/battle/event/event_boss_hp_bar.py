# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_boss_hp_bar.py
import logging
import BigWorld
from gui.Scaleform.daapi.view.meta.EventBossHPBarMeta import EventBossHPBarMeta
from gui.shared import EVENT_BUS_SCOPE, events
_logger = logging.getLogger(__name__)

def getArenaInfoBossHealthBarComponent():
    arenaInfo = BigWorld.player().arena.arenaInfo
    return arenaInfo.hwBossHealthBarComponent


class EventBossHPBar(EventBossHPBarMeta):

    def __init__(self):
        super(EventBossHPBar, self).__init__()
        self.__isActive = False

    def _populate(self):
        super(EventBossHPBar, self)._populate()
        self.addListener(events.BossHPBarEvent.ON_HIDE, self.__onHideBossHPBar, scope=EVENT_BUS_SCOPE.BATTLE)
        component = getArenaInfoBossHealthBarComponent()
        if component.isActive:
            _logger.info('Restore EventBossHPBar component on loading')
            self.__onBossHealthPrepared()
            return
        component.onBossHealthPrepared += self.__onBossHealthPrepared

    def _dispose(self):
        super(EventBossHPBar, self)._dispose()
        self.removeListener(events.BossHPBarEvent.ON_HIDE, self.__onHideBossHPBar, scope=EVENT_BUS_SCOPE.BATTLE)

    def __onBossHealthPrepared(self):
        _logger.info('EventBossHPBar is ready to be used')
        component = getArenaInfoBossHealthBarComponent()
        if not self.__isActive:
            self.__isActive = True
            self.__showBossHPBar(True)
            component.onBossHealthChanged += self.__onBossHealthChanged
        curHealth, maxHealth = component.getBossMarkerCurrentHealthValues()
        uiPhase = component.getCurrentUIPhase()
        self.__updateBossHPBar(uiPhase, curHealth, maxHealth)

    def __showBossHPBar(self, isEnabled):
        _logger.info('Change EventBossHPBar visibility state to %d', isEnabled)
        self.as_setVisibleS(isEnabled)

    def __onBossHealthChanged(self):
        component = getArenaInfoBossHealthBarComponent()
        curHealth, maxHealth = component.getBossMarkerCurrentHealthValues()
        if curHealth <= 0:
            if self.__isActive:
                self.__showBossHPBar(False)
        else:
            uiPhase = component.getCurrentUIPhase()
            self.__updateBossHPBar(uiPhase, curHealth, maxHealth)

    def __updateBossHPBar(self, phase, health, maxHealth):
        progress = 100 - int(health * 100 / maxHealth)
        progress = min(progress, 100)
        progress = max(0, progress)
        values = str(health) + '/' + str(maxHealth)
        _logger.info('Update EventBossHPBar values: phase=%d, values="%s"', phase, values)
        self.as_setPhaseS(phase)
        self.as_setBossHPS(values, progress)

    def __onHideBossHPBar(self, event):
        if self.__isActive:
            self.__showBossHPBar(False)
