# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/overviewmap_screen.py
from collections import namedtuple
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME, _MISSION_SECTOR_ID_MAPPING
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.EpicOverviewMapScreenMeta import EpicOverviewMapScreenMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from helpers import dependency
from helpers import i18n
from skeletons.gui.battle_session import IBattleSessionProvider
EpicOverviewMapScreenVO = namedtuple('EpicOverviewMapScreenVO', ('key1Text', 'key2Text', 'key3Text', 'key4Text', 'key5Text', 'key6Text'))

class OverviewMapScreen(EpicOverviewMapScreenMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def start(self):
        pass

    def _populate(self):
        super(OverviewMapScreen, self)._populate()
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
        super(OverviewMapScreen, self)._dispose()
        return

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
