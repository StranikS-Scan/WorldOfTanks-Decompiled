# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/__init__.py
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, ILootBoxManager, INewYearUIManager
from skeletons.new_year import INYSoundEvents
from .customizable_objects_manager import CustomizableObjectsManager
from .new_year_controller import NewYearController
from .fader_switcher import FaderSwitcher
from .camera_switcher import CameraSwitcher
from .new_year_ui_manager import NewYearUIManager
from .new_year_sounds import NYSoundEvents
from LootBoxManager import LootBoxManager
from .ui_switcher import UiSwitcher
from .mappings import AnchorNames, NewYearObjectIDs, Mappings, UiStates, UiTabs

def getNewYearServiceConfig(manager, tracker):
    """ Configures services for package new_year.
    :param manager: helpers.dependency.DependencyManager.
    """
    uiSwitcher = UiSwitcher()
    cameraSwitcher = CameraSwitcher()
    cameraSwitcher.init()
    cameraSwitcher.setNextHandler(uiSwitcher)
    faderSwitcher = FaderSwitcher()
    faderSwitcher.setNextHandler(cameraSwitcher)
    custObjMgr = CustomizableObjectsManager()
    custObjMgr.setNextHandler(faderSwitcher)
    custObjMgr.init()
    newYearController = NewYearController()
    tracker.addController(newYearController)
    newYearController.init()
    lootBoxManager = LootBoxManager()
    lootBoxManager.init()
    newYearUIManager = NewYearUIManager()
    nySoundEvents = NYSoundEvents()
    manager.addInstance(INewYearUIManager, newYearUIManager, finalizer='fini')
    manager.addInstance(ILootBoxManager, lootBoxManager, finalizer='fini')
    manager.addInstance(ICustomizableObjectsManager, custObjMgr, finalizer='fini')
    manager.addInstance(INewYearController, newYearController, finalizer='fini')
    manager.addInstance(INYSoundEvents, nySoundEvents, finalizer='fini')
