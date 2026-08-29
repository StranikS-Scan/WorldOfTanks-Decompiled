# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/applying_triggers.py
from typing import Optional, TYPE_CHECKING
from gui.battle_control.battle_context_hints.common import getBestPiercingShellCD
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController

class HintApplyingTrigger(object):

    def __init__(self, hintId, logger, applyingCallback, *args, **kwargs):
        self._hintId = hintId
        self._logger = logger
        self._applyingCallback = applyingCallback
        self._args = args
        self._kwargs = kwargs

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class RepairKitApplyingTrigger(HintApplyingTrigger):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def start(self):
        eqCtrl = self.__sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def stop(self):
        eqCtrl = self.__sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __onEquipmentUpdated(self, intCD, item):
        if 'repairkit' in item.getTags():
            self._applyingCallback(self._hintId, self._logger)


class MedKitApplyingTrigger(HintApplyingTrigger):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def start(self):
        eqCtrl = self.__sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def stop(self):
        eqCtrl = self.__sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __onEquipmentUpdated(self, intCD, item):
        if 'medkit' in item.getTags():
            self._applyingCallback(self._hintId, self._logger)


class AmmoTypeSwitchApplyingTrigger(HintApplyingTrigger):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hintId, logger, applyingCallback, *args, **kwargs):
        super(AmmoTypeSwitchApplyingTrigger, self).__init__(hintId, logger, applyingCallback, *args, **kwargs)
        self.__ammoCtrl = None
        self.__targetShellCD = None
        return

    def start(self):
        self.__ammoCtrl = self.__sessionProvider.shared.ammo
        if self.__ammoCtrl is not None:
            self.__targetShellCD = getBestPiercingShellCD(self.__ammoCtrl)
            self.__ammoCtrl.onCurrentShellChanged += self.__onShellChanged
        return

    def stop(self):
        if self.__ammoCtrl is not None:
            self.__ammoCtrl.onCurrentShellChanged -= self.__onShellChanged
            self.__ammoCtrl = None
        self.__targetShellCD = None
        return

    def __onShellChanged(self, intCD):
        if self.__targetShellCD is not None and intCD == self.__targetShellCD:
            self._applyingCallback(self._hintId, self._logger)
        return
