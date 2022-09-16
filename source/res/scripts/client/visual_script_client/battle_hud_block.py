# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/battle_hud_block.py
import BigWorld
from skeletons.gui.battle_session import IBattleSessionProvider
from visual_script import ASPECT
from visual_script.block import Meta, Block
from visual_script.dependency import dependencyImporter
from visual_script.misc import errorVScript
from visual_script.slot_types import SLOT_TYPE
helpers, dependency = dependencyImporter('helpers', 'helpers.dependency')
Math = dependencyImporter('Math')

class BattleHUDMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @property
    def _avatar(self):
        if helpers.isPlayerAvatar():
            return BigWorld.player()
        errorVScript(self, 'BigWorld.player is not player avatar.')


class BattleHUDEventMeta(BattleHUDMeta):

    @classmethod
    def blockIcon(cls):
        pass


class OnShowMessage(BattleHUDEventMeta, Block):

    def __init__(self, *args, **kwargs):
        super(OnShowMessage, self).__init__(*args, **kwargs)
        self._active = self._makeDataInputSlot('active', SLOT_TYPE.BOOL)
        self._onVehicleMessage = self._makeEventOutputSlot('onVehicleMessage')
        self._onVehicleError = self._makeEventOutputSlot('onVehicleError')
        self._onPlayerMessage = self._makeEventOutputSlot('onPlayerMessage')
        self._key = self._makeDataOutputSlot('key', SLOT_TYPE.STR, None)
        return

    def onStartScript(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey += self.__onShowVehicleErrorByKey
            ctrl.onShowVehicleMessageByKey += self.__onShowVehicleMessageByKey
            ctrl.onShowVehicleMessageByCode += self.__onShowVehicleMessageByCode
            ctrl.onShowPlayerMessageByKey += self.__onShowPlayerMessageByKey
            ctrl.onShowPlayerMessageByCode += self.__onShowPlayerMessageByCode
        else:
            errorVScript(self, "Can't access the BattleMessagesController")
        return

    def onFinishScript(self):
        sessionProvider = helpers.dependency.instance(IBattleSessionProvider)
        ctrl = sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey -= self.__onShowVehicleErrorByKey
            ctrl.onShowVehicleMessageByKey -= self.__onShowVehicleMessageByKey
            ctrl.onShowVehicleMessageByCode -= self.__onShowVehicleMessageByCode
            ctrl.onShowPlayerMessageByKey -= self.__onShowPlayerMessageByKey
            ctrl.onShowPlayerMessageByCode -= self.__onShowPlayerMessageByCode
        return

    def validate(self):
        return super(OnShowMessage, self).validate()

    @property
    def active(self):
        return True if not self._active.hasValue() else self._active.getValue()

    def __onShowVehicleErrorByKey(self, key, args=None, extra=None):
        if self.active:
            self._key.setValue(key)
            self._onVehicleError.call()

    def __onShowVehicleMessageByKey(self, key, args=None, extra=None):
        if self.active:
            self._key.setValue(key)
            self._onVehicleMessage.call()

    def __onShowPlayerMessageByKey(self, key, args=None, extra=None):
        if self.active:
            self._key.setValue(key)
            self._onPlayerMessage.call()

    def __onShowVehicleMessageByCode(self, code, postfix, entityID, extra, equipmentID):
        if self.active:
            self._key.setValue(code)
            self._onVehicleMessage.call()

    def __onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID):
        if self.active:
            self._key.setValue(code)
            self._onPlayerMessage.call()
