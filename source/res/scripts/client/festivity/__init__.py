# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/__init__.py


def getFestivityConfig(manager):
    from festivity.festival.factory import FestivalFactory
    from skeletons.festival import IFestivalController
    from skeletons.festivity_factory import IFestivityFactory
    festivityFactory = FestivalFactory()
    manager.addInstance(IFestivityFactory, festivityFactory)
    manager.addInstance(IFestivalController, festivityFactory.getController())
