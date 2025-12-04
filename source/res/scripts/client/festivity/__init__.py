# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/__init__.py
from festivity.dummy.df_factory import DummyFactory
from gui.shared.system_factory import collectFestivityFactories
from skeletons.festivity_factory import IFestivityFactory
from soft_exception import SoftException

def getFestivityConfig(manager):
    festivityFactories = collectFestivityFactories()
    if len(festivityFactories) > 1:
        raise SoftException('To many festivity factories registered: {}'.format(festivityFactories))
    if festivityFactories:
        festivityFactory = festivityFactories[0]()
    else:
        festivityFactory = DummyFactory()
    manager.addInstance(IFestivityFactory, festivityFactory)
