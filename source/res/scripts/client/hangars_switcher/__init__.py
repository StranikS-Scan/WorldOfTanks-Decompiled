# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangars_switcher/__init__.py
__all__ = ('getHangarsSwitcherConfig',)

def getHangarsSwitcherConfig(manager):
    from hangars_switch_manager import HangarsSwitchManager
    from skeletons.hangars_switcher import IHangarsSwitchManager
    from hangars_switcher.switchers_auto_selector import SwitchersAutoSelector
    from skeletons.hangars_switcher import ISwitchersAutoSelector
    from skeletons.hangars_switcher import IHangarPlaceManager
    from hangars_switcher.hangar_place_manager import HangarPlaceManager
    hangarsSwitchMgr = HangarsSwitchManager()
    hangarsSwitchMgr.init()
    manager.addInstance(IHangarsSwitchManager, hangarsSwitchMgr, finalizer='destroy')
    autoSelector = SwitchersAutoSelector()
    autoSelector.init()
    manager.addInstance(ISwitchersAutoSelector, autoSelector, finalizer='destroy')
    hangarPlaceMgr = HangarPlaceManager()
    hangarPlaceMgr.init()
    manager.addInstance(IHangarPlaceManager, hangarPlaceMgr, finalizer='destroy')
