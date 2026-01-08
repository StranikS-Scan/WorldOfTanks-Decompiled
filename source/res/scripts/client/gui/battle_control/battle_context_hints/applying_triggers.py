# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/applying_triggers.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

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
