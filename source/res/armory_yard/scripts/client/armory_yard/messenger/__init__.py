# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/messenger/__init__.py
from gui.shared.system_factory import registerNotificationsListeners
from armory_yard.messenger.listeners import ArmoryYardListener

def registerArmoryYardNotificationListener():
    registerNotificationsListeners((ArmoryYardListener,))
