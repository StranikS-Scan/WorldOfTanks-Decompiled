# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/header/__init__.py
import create_squad as _create_squad
import fight_button_ as _fight_button
from battle_type_selector import configure_pointcuts as _configure_selector_pointcuts

def configure_pointcuts(config):
    _configure_selector_pointcuts()
    _create_squad.OnCreateSquadClickPointcut()
    _fight_button.DisableFightButtonPointcut(config)
