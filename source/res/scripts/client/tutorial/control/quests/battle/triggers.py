# Embedded file name: scripts/client/tutorial/control/quests/battle/triggers.py
from gui.battle_control import g_sessionProvider
from tutorial.control.triggers import TriggerWithValidateVar

class UseItemsTrigger(TriggerWithValidateVar):

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            eqCtrl = g_sessionProvider.getEquipmentsCtrl()
            if eqCtrl is not None:
                eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        self.toggle(isOn=self.isOn())
        return

    def isOn(self, result = False):
        return result

    def __onEquipmentUpdated(self, intCD, item):
        conditionVar = self.getVar()
        itemsList = conditionVar.get('items', [])
        if intCD in itemsList and item.getQuantity() == 0:
            self.toggle(isOn=self.isOn(True))

    def clear(self):
        eqCtrl = g_sessionProvider.getEquipmentsCtrl()
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        self.isSubscribed = False
        self.isRunning = False
        return
