# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/script_component/ScriptComponent.py
import logging
import BigWorld
import Avatar
from PlayerEvents import g_playerEvents
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class ScriptComponent(BigWorld.StaticScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    REQUIRED_BONUS_CAP = None

    def __init__(self):
        BigWorld.StaticScriptComponent.__init__(self)
        if not self.__checkBonusCaps():
            return
        if self._isAvatarReady:
            nextTick(self._onAvatarReady)()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    @property
    def _isAvatarReady(self):
        return BigWorld.player() is not None and BigWorld.player().userSeesWorld()

    def onEnterWorld(self, _):
        _logger.debug('%s.onEnterWorld. EntityID=%s', self.__class__.__name__, self.entity.id)

    def onLeaveWorld(self):
        _logger.debug('%s.onLeaveWorld. EntityID=%s', self.__class__.__name__, self.entity.id)

    def _onAvatarReady(self):
        pass

    def __onAvatarReady(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self._onAvatarReady()

    def __checkBonusCaps(self):
        if self.REQUIRED_BONUS_CAP is None:
            return True
        else:
            if isinstance(self.entity, Avatar.PlayerAvatar):
                arenaBonusType = self.entity.arenaBonusType
            else:
                arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
            return ARENA_BONUS_TYPE_CAPS.checkAny(arenaBonusType, self.REQUIRED_BONUS_CAP)
