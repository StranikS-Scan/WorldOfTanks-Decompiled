# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/buffs/__init__.py
import logging
import BigWorld
from buffs_common import Buff, BuffComponent, BuffsRepository, BuffFactory, BuffComponentVisibilityMode
import configs
_logger = logging.getLogger(__name__)
COMPONENTS_FACTORIES = {}

class ClientBuffsRepository(BuffsRepository):

    @property
    def _buffFactory(self):
        return ClientBuffFactory


class ClientBuff(Buff):
    pass


class ClientBuffComponent(BuffComponent):
    VisibilityModes = BuffComponentVisibilityMode

    def apply(self, ctx=None):
        if self._isVisible():
            self._apply()

    def unapply(self):
        if self._isVisible():
            self._unapply()

    def _apply(self):
        pass

    def _unapply(self):
        pass

    def _isVehicleObservedByAvatar(self):
        avatar = BigWorld.player()
        return False if not avatar else avatar.getVehicleAttached() == self._owner

    def _isVisibleToPlayer(self):
        return self._owner.isPlayerVehicle or self._isVehicleObservedByAvatar()

    def _isVisible(self):
        if self._config.visibleTo == self.VisibilityModes.ALL:
            return True
        if self._config.visibleTo == self.VisibilityModes.SELF and self._isVisibleToPlayer():
            return True
        return True if self._config.visibleTo == self.VisibilityModes.OTHERS and not self._isVisibleToPlayer() else False


class ClientBuffFactory(BuffFactory):
    COMPONENTS_CONFIGS = configs

    @property
    def _buffClass(self):
        return ClientBuff

    @property
    def _xmlFactories(self):
        import components
        return self.COMPONENTS_FACTORIES

    @property
    def _component(self):
        pass


clientBuffComponent = ClientBuffFactory.registerBuffComponent
