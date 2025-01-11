# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/__init__.py
from skeletons.festivity_factory import IFestivityFactory
from skeletons.new_year import INewYearController

def getFestivityConfig(manager):
    from new_year.ny_factory import NewYearFactory
    festivityFactory = NewYearFactory()
    manager.addInstance(IFestivityFactory, festivityFactory)
    manager.addInstance(INewYearController, festivityFactory.getController())
