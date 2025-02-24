# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/minimap.py
import BigWorld
import logging
from functools import partial
import Math
from helpers.CallbackDelayer import CallbackDelayer
from chat_commands_consts import getUniqueTeamOrControlPointID
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent, GlobalSettingsPlugin, TeamsOrControlsPointsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.points_of_interest import minimap as poi_plugins
from account_helpers.AccountSettings import COMP7_PREBATTLE_MINIMAP_SIZE, MINIMAP_SIZE
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
_logger = logging.getLogger(__name__)

class Comp7MinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(Comp7MinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['pointsOfInterest'] = poi_plugins.PointsOfInterestPlugin
        setup['settings'] = Comp7GlobalSettingsPlugin
        setup['points'] = Comp7ControlPointsPlugin
        setup['reconEquipment'] = Comp7ReconPlugin
        return setup


class Comp7GlobalSettingsPlugin(GlobalSettingsPlugin):
    __slots__ = ()

    def start(self):
        super(Comp7GlobalSettingsPlugin, self).start()
        arenaPeriod = self.sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod >= ARENA_PERIOD.BATTLE:
            self._changeSizeSettings(MINIMAP_SIZE)
        else:
            prebattleMinimapSize = self._AccountSettingsClass.getSettings(COMP7_PREBATTLE_MINIMAP_SIZE)
            if prebattleMinimapSize == -1:
                self._sizeIndex = settings.clampMinimapSizeIndex(prebattleMinimapSize)
                self._currentSizeSettings = COMP7_PREBATTLE_MINIMAP_SIZE
                self._parentObj.as_initPrebattleSizeS(self._AccountSettingsClass.getSettings(MINIMAP_SIZE))
            else:
                self._changeSizeSettings(COMP7_PREBATTLE_MINIMAP_SIZE)
            prebattleSetup = self.sessionProvider.dynamic.comp7PrebattleSetup
            if prebattleSetup:
                prebattleSetup.onBattleStarted += self.__onBattleStarted

    def stop(self):
        prebattleSetup = self.sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleSetup:
            prebattleSetup.onBattleStarted -= self.__onBattleStarted
        super(Comp7GlobalSettingsPlugin, self).stop()

    def __onBattleStarted(self):
        self._changeSizeSettings(MINIMAP_SIZE)


class Comp7ControlPointsPlugin(TeamsOrControlsPointsPlugin):

    def start(self):
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate += self._onBasePointsUpdate
        super(Comp7ControlPointsPlugin, self).start()
        return

    def stop(self):
        super(Comp7ControlPointsPlugin, self).stop()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate -= self._onBasePointsUpdate
        return

    def _onBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        uid = getUniqueTeamOrControlPointID(team, baseID)
        model = self._markerIDs.get(uid)
        if model is None:
            _logger.error('No marker with id: %d', uid)
            return
        else:
            self._invoke(model.getID(), 'setProgress', points)
            return


class Comp7ReconPlugin(common.EntriesPlugin):
    COMP7_RECON = 'ReconEquipmentMinimapEntryUI'
    CONTAINER_NAME = 'points'

    def __init__(self, *args, **kwargs):
        super(Comp7ReconPlugin, self).__init__(*args, **kwargs)
        self._callbackDelayer = None
        return

    def start(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentAreaCreated += self._onEquipmentAreaCreated
        self._callbackDelayer = CallbackDelayer()
        super(Comp7ReconPlugin, self).start()
        return

    def stop(self):
        super(Comp7ReconPlugin, self).stop()
        self._callbackDelayer.destroy()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentAreaCreated -= self._onEquipmentAreaCreated
        return

    def _onEquipmentAreaCreated(self, equipment, position, endTime, level=None, team=None):
        if equipment.name != 'comp7_recon':
            return
        radius = equipment.radius[level - 1]
        duration = equipment.duration[level - 1]
        delay = equipment.delay
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        arenaBB = BigWorld.player().arena.getArenaBB()
        size = radius * 2 * 10 / (arenaBB[1][0] - arenaBB[0][0])
        entryID = self._addEntry(self.COMP7_RECON, self.CONTAINER_NAME, matrix=matrix, active=True)
        self._callbackDelayer.delayCallback(duration + delay, partial(self._delEntry, entryID))
        self._invoke(entryID, 'setInitialData', team == BigWorld.player().team, duration, delay, size)
