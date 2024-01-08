# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/minimap.py
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent, GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.points_of_interest import minimap as poi_plugins
from account_helpers.settings_core.settings_constants import GAME
from gui.Scaleform.daapi.view.battle.shared.minimap import settings

class Comp7MinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(Comp7MinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['pointsOfInterest'] = poi_plugins.PointsOfInterestPlugin
        setup['settings'] = Comp7GlobalSettingsPlugin
        return setup


class Comp7GlobalSettingsPlugin(GlobalSettingsPlugin):
    __slots__ = ()

    def start(self):
        super(Comp7GlobalSettingsPlugin, self).start()
        arenaPeriod = self.sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod >= ARENA_PERIOD.BATTLE:
            self._changeSizeSettings(GAME.MINIMAP_SIZE)
        else:
            prebattleMinimapSize = self.settingsCore.getSetting(GAME.COMP7_MINIMAP_SIZE)
            if prebattleMinimapSize == -1:
                self._sizeIndex = settings.clampMinimapSizeIndex(prebattleMinimapSize)
                self._currentSizeSettings = GAME.COMP7_MINIMAP_SIZE
                self._parentObj.as_initPrebattleSizeS(self.settingsCore.getSetting(GAME.MINIMAP_SIZE))
            else:
                self._changeSizeSettings(GAME.COMP7_MINIMAP_SIZE)
            prebattleSetup = self.sessionProvider.dynamic.comp7PrebattleSetup
            if prebattleSetup:
                prebattleSetup.onBattleStarted += self.__onBattleStarted

    def stop(self):
        prebattleSetup = self.sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleSetup:
            prebattleSetup.onBattleStarted -= self.__onBattleStarted
        super(Comp7GlobalSettingsPlugin, self).stop()

    def __onBattleStarted(self):
        self._changeSizeSettings(GAME.MINIMAP_SIZE)
