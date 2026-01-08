# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/hint_descriptor.py
from typing import Optional, Type, NamedTuple
from gui.impl.battle.battle_page.battle_context_hints.battle_context_hint_view import BattleContextHintsView
from gui.impl.battle.battle_page.battle_context_hints.battle_context_hints_presenters import BattleContextHintsViewPresenter
from gui.battle_control.battle_context_hints.activation_triggers import HintActivationTrigger
from gui.battle_control.battle_context_hints.applying_triggers import HintApplyingTrigger
from gui.battle_control.battle_context_hints.hint_lifecycle_managers import HintLifecycleMgr
from gui.battle_control.battle_context_hints.settings_data_block import HintDataBlock
HintDescriptor = NamedTuple('HintDescriptor', [('priority', int),
 ('hintId', str),
 ('injectComponentAlias', Optional[str]),
 ('hintView', Optional[Type[BattleContextHintsView]]),
 ('hintPresenter', Optional[Type[BattleContextHintsViewPresenter]]),
 ('activationTrigger', Optional[Type[HintActivationTrigger]]),
 ('applyingTrigger', Optional[Type[HintApplyingTrigger]]),
 ('hintLifecycleMgr', Optional[Type[HintLifecycleMgr]]),
 ('dataBlock', HintDataBlock),
 ('soundEvent', Optional[str]),
 ('delay', float),
 ('duration', float),
 ('maxWatchingQty', int),
 ('maxWatchingQtyPerBattle', int),
 ('battlesCooldown', int)])
