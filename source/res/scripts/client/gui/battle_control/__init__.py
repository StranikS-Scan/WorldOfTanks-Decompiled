# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/__init__.py
from gui.battle_control.battle_session import BattleSessionProvider
from gui.battle_control.controllers import BattleSessionSetup
from skeletons.gui.battle_session import IBattleSessionProvider
__all__ = ('BattleSessionSetup', 'getBattleSessionConfig')

def getBattleSessionConfig(manager):
    """ Configures services for package battle_control.
    :param manager: helpers.dependency.DependencyManager
    """
    manager.addInstance(IBattleSessionProvider, BattleSessionProvider(), finalizer='stop')
