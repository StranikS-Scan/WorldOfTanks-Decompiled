# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/sixth_sense_context_hint_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.battle.battle_page.battle_context_hints.battle_context_hint_view import BattleContextHintsView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_context_hints.base_battle_context_hint_model import BaseBattleContextHintModel
_logger = logging.getLogger(__name__)

class SixthSenseContextHintView(BattleContextHintsView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.battle.battle_page.SixthSenseContextHint(), flags=ViewFlags.VIEW, model=BaseBattleContextHintModel(), args=args, kwargs=kwargs)
        super(SixthSenseContextHintView, self).__init__(settings)
