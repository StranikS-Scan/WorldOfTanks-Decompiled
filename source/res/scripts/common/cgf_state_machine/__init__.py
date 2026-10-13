# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_state_machine/__init__.py
from __future__ import absolute_import
from . import actions, transitions
from .registrar import StateActionsRegistrar, TransitionsRegistrar
g_actionsRegistrar = StateActionsRegistrar()
g_actionsRegistrar.regActionsFromModule(actions)
g_transitionsRegistrar = TransitionsRegistrar()
g_transitionsRegistrar.regTransitionsFromModule(transitions)
