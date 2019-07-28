# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hb1/hb1_factory.py


def getHB1Config(manager):
    from hb1.customizable_objects_manager import CustomizableObjectsManager
    from skeletons.festivity_factory import IFestivityFactory
    from skeletons.hb1 import ICustomizableObjectsManager
    from festivity.dummy.df_factory import DummyFactory
    festivityFactory = DummyFactory()
    manager.addInstance(IFestivityFactory, festivityFactory)

    def _create():
        customizableObjMgr = CustomizableObjectsManager()
        customizableObjMgr.init()
        return customizableObjMgr

    manager.addRuntime(ICustomizableObjectsManager, _create, finalizer='fini')
