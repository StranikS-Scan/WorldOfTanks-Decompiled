# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/plugin_items/base_sector.py
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import THERMAL_VISION_SECTOR_AS3_DESCR, ENTRY_SYMBOL_NAME, CONTAINER_NAME
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from wotdecorators import noexcept

class SectorState(object):
    DISABLED = 0
    IDLE = 1
    ACTIVE = 2


class BaseSectorPlugin(EntriesPlugin):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parent, clazz=None):
        super(BaseSectorPlugin, self).__init__(parent, clazz)
        self.__id = None
        return

    @property
    def matrixProvider(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    def _onMinimapFeedbackReceived(self, eventID, entityID, value):
        raise NotImplementedError

    def initControlMode(self, mode, available):
        super(BaseSectorPlugin, self).initControlMode(mode, available)
        self.__preWarm()

    def start(self):
        super(BaseSectorPlugin, self).start()
        ctrl = self._sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived += self._onMinimapFeedbackReceived
        return

    def stop(self):
        ctrl = self._sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived -= self._onMinimapFeedbackReceived
        super(BaseSectorPlugin, self).stop()
        return

    def show(self):
        self._toggleVisibility(True)

    def hide(self):
        self._toggleVisibility(False)

    def setSectorSettings(self, fov, distance):
        self.show()
        self._invoke(self.__id, THERMAL_VISION_SECTOR_AS3_DESCR.AS_SET_SETTINGS, fov, distance)

    def _toggleVisibility(self, state):
        if self.__id is None:
            return
        else:
            self._invoke(self.__id, THERMAL_VISION_SECTOR_AS3_DESCR.AS_UPDATE_VISIBILITY, state)
            return

    def _toggleActive(self, state):
        if self.__id is None:
            return
        else:
            self._invoke(self.__id, THERMAL_VISION_SECTOR_AS3_DESCR.AS_UPDATE_STATE, state)
            return

    def __createSector(self):
        if self.__id is not None:
            return
        else:
            matrix = self.matrixProvider
            (left, top), (right, bottom) = self._sessionProvider.arenaVisitor.type.getBoundingBox()
            mapMaxSize = max(abs(right - left), abs(bottom - top))
            self.__id = self._addEntry(ENTRY_SYMBOL_NAME.THERMAL_VISION_ENTRY, CONTAINER_NAME.PERSONAL, matrix=matrix, active=self.isEnabled)
            self._invoke(self.__id, THERMAL_VISION_SECTOR_AS3_DESCR.AS_INIT_MAP_SIZE, mapMaxSize)
            return

    @noexcept
    def __preWarm(self):
        if self.__id is None:
            self.__createSector()
        return
