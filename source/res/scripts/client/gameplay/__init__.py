# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/__init__.py
__all__ = ('getGameplayConfig',)

def getGameplayConfig(manager):
    from gameplay.delegator import GameplayLogic
    from gameplay.machine import create
    from skeletons.gameplay import IGameplayLogic
    manager.addInstance(IGameplayLogic, GameplayLogic(create()), finalizer='stop')
