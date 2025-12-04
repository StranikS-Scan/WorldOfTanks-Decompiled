# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/dependency/registrator.py
import typing
if typing.TYPE_CHECKING:
    from dependency_injection_container import DependencyManager

def registerSkeletons(manager):
    from new_year.skeletons.new_year import ITamagotchiDataProvider, ITamagotchiWebRequester
    from new_year.tamagotchi.data_provider import TamagotchiDataProvider
    from new_year.tamagotchi.requester import TamagotchiWebRequester
    manager.addInstance(ITamagotchiWebRequester, TamagotchiWebRequester())
    manager.addInstance(ITamagotchiDataProvider, TamagotchiDataProvider())
