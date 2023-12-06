# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/__init__.py
from skeletons.festivity_factory import IFestivityFactory

def getNewYearServiceConfig(manager):
    from new_year.ny_factory import NewYearFactory
    manager.addInstance(IFestivityFactory, NewYearFactory())
