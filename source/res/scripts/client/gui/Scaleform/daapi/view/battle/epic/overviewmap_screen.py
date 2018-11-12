# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/overviewmap_screen.py
from collections import namedtuple
import Keys
import BigWorld
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.EpicOverviewMapScreenMeta import EpicOverviewMapScreenMeta
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME
from epic_constants import EPIC_BATTLE_TEAM_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import EVENT_BUS_SCOPE, events
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import i18n
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
_MISSION_SECTOR_ID_MAPPING = {1: {0: 4,
     1: 4,
     2: 1},
 2: {0: 5,
     1: 5,
     2: 2},
 3: {0: 6,
     1: 6,
     2: 3}}
EpicOverviewMapScreenVO = namedtuple('EpicOverviewMapScreenVO', ('key1Text', 'key2Text', 'key3Text', 'key4Text', 'key5Text', 'key6Text'))

class OverviewMapScreen(EpicOverviewMapScreenMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def start(self):
        pass

    def _populate(self):
        super(OverviewMapScreen, self)._populate()
        self.addListener(events.GameEvent.EPIC_GLOBAL_MSG_CMD, self._handleGlobalMsg, scope=EVENT_BUS_SCOPE.BATTLE)
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseCaptured += self.__onSectorBaseCaptured
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        self.__updateLaneButtons()
        self.__setKeyBindings()
        return

    def _dispose(self):
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseCaptured -= self.__onSectorBaseCaptured
        self.removeListener(events.GameEvent.EPIC_GLOBAL_MSG_CMD, self._handleGlobalMsg, scope=EVENT_BUS_SCOPE.BATTLE)
        super(OverviewMapScreen, self)._dispose()
        return

    def _handleGlobalMsg(self, event):
        isDown = event.ctx['isDown']
        key = event.ctx['key']
        if isDown:
            self.__onGlobalMsgRecieved(key)

    def __setKeyBindings(self):
        data = EpicOverviewMapScreenVO(key1Text=READABLE_KEY_NAMES.KEY_F4, key2Text=READABLE_KEY_NAMES.KEY_F5, key3Text=READABLE_KEY_NAMES.KEY_F6, key4Text=READABLE_KEY_NAMES.KEY_F7, key5Text=READABLE_KEY_NAMES.KEY_F8, key6Text=READABLE_KEY_NAMES.KEY_F9)
        self.as_setKeyBindingsS(data._asdict())

    def __getCurrentZoneNamePerLane(self, lane):
        if lane > 0:
            sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
            if sectorBaseComp is not None:
                nonCapturedBases = sectorBaseComp.getNumNonCapturedBasesByLane(lane)
                return ID_TO_BASENAME[_MISSION_SECTOR_ID_MAPPING[lane][nonCapturedBases]]
            LOG_ERROR('Expected SectorBaseComponent not present!')
        return ''

    def __onSectorBaseCaptured(self, id_, isPlayerTeam):
        self.__updateLaneButtons()

    def __updateLaneButtons(self):
        self.as_updateLaneButtonNamesS(i18n.makeString(EPIC_BATTLE.GLOBAL_MSG_LANE_WEST_SHORT, strArg1=self.__getCurrentZoneNamePerLane(1)), i18n.makeString(EPIC_BATTLE.GLOBAL_MSG_LANE_CENTER_SHORT, strArg1=self.__getCurrentZoneNamePerLane(2)), i18n.makeString(EPIC_BATTLE.GLOBAL_MSG_LANE_EAST_SHORT, strArg1=self.__getCurrentZoneNamePerLane(3)))

    def __onGlobalMsgRecieved(self, key):
        isAttacker = BigWorld.player().team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
        ctrl = self.sessionProvider.dynamic.maps
        if not ctrl:
            return
        elif not ctrl.overviewMapScreenVisible:
            return
        else:
            lane = 0
            msg = None
            if key == Keys.KEY_F4:
                if isAttacker:
                    msg = 'EPIC_GLOBAL_SAVETANKS_ATK'
                else:
                    msg = 'EPIC_GLOBAL_SAVETANKS_DEF'
            elif key == Keys.KEY_F5:
                if isAttacker:
                    msg = 'EPIC_GLOBAL_TIME_ATK'
                else:
                    msg = 'EPIC_GLOBAL_TIME_DEF'
            elif key == Keys.KEY_F6:
                msg = 'EPIC_GLOBAL_WEST'
                lane = 1
            elif key == Keys.KEY_F7:
                msg = 'EPIC_GLOBAL_CENTER'
                lane = 2
            elif key == Keys.KEY_F8:
                msg = 'EPIC_GLOBAL_EAST'
                lane = 3
            elif key == Keys.KEY_F9:
                if isAttacker:
                    msg = 'EPIC_GLOBAL_HQ_ATK'
                else:
                    msg = 'EPIC_GLOBAL_HQ_DEF'
            baseName = self.__getCurrentZoneNamePerLane(lane)
            commands = self.sessionProvider.shared.chatCommands
            if commands is not None:
                commands.sendEpicGlobalCommand(msg, baseName)
            return
