# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/__init__.py
from historical_battles.skeletons.gui.customizable_objects_manager import ICustomizableObjectsManager
from historical_battles.skeletons.gui.sound_controller import IHBSoundController
from historical_battles.gui.customizable_objects_manager import CustomizableObjectsManager
from historical_battles.gui.sounds.sound_ctrl import HBSoundController

def getCustomizableObjectsManagar(manager):
    _getStandartController(manager, ICustomizableObjectsManager, CustomizableObjectsManager)


def getHBSoundController(manager):
    _getStandartController(manager, IHBSoundController, HBSoundController)


def _getStandartController(manager, interfaceType, implType):
    controller = implType()
    controller.init()
    manager.addInstance(interfaceType, controller, finalizer='fini')
