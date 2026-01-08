# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/__init__.py
from festivity.dummy.df_factory import DummyFactory
from skeletons.festivity_factory import IFestivityFactory

def getFestivityConfig(manager):
    festivityFactory = DummyFactory()
    manager.addInstance(IFestivityFactory, festivityFactory)
