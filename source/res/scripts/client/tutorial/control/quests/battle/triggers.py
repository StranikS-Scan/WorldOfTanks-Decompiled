# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/quests/battle/triggers.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from tutorial.control.triggers import TriggerWithValidateVar

class UseItemsTrigger(TriggerWithValidateVar):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            eqCtrl = self.sessionProvider.shared.equipments
            if eqCtrl is not None:
                eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        self.toggle(isOn=self.isOn())
        return

    def isOn(self, result=False):
        return result

    def __onEquipmentUpdated(self, intCD, item):
        conditionVar = self.getVar()
        itemsList = conditionVar.get('items', [])
        if intCD in itemsList and item.getQuantity() == 0:
            self.toggle(isOn=self.isOn(True))

    def clear(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        self.isSubscribed = False
        self.isRunning = False
        return


class InstallItemsTrigger(TriggerWithValidateVar):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            eqCtrl = self.sessionProvider.shared.equipments
            if eqCtrl is not None:
                eqCtrl.onEquipmentUpdated += self.__onEquipmentAdded
        self.toggle(isOn=self.isOn())
        return

    def isOn(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            conditionVar = self.getVar()
            itemsList = conditionVar.get('items', [])
            for eqCD in itemsList:
                if eqCtrl.hasEquipment(eqCD):
                    return True

        return False

    def __onEquipmentAdded(self, *args):
        self.toggle(isOn=self.isOn())

    def clear(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentAdded
        self.isSubscribed = False
        self.isRunning = False
        return
