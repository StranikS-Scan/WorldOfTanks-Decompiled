# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/se20/__init__.py
from skeletons.festivity_factory import IFestivityFactory
from skeletons.se20 import ICustomizableObjectsManager
from festivity.dummy.df_factory import DummyFactory

def getSE20ServiceConfig(manager):
    from .customizable_objects_manager import CustomizableObjectsManager
    custObjMgr = CustomizableObjectsManager()
    custObjMgr.init()
    manager.addInstance(ICustomizableObjectsManager, custObjMgr, finalizer='fini')
    manager.addInstance(IFestivityFactory, DummyFactory())
