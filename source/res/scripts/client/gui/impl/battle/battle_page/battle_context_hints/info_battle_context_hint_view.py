# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/info_battle_context_hint_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.battle.battle_page.battle_context_hints.battle_context_hint_view import BattleContextHintsView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_context_hints.info_battle_context_hint_model import InfoBattleContextHintModel

class InfoBattleContextHintView(BattleContextHintsView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.battle.battle_page.InfoBattleContextHint(), flags=ViewFlags.VIEW, model=InfoBattleContextHintModel(), args=args, kwargs=kwargs)
        super(InfoBattleContextHintView, self).__init__(settings)

    def setVisibility(self, visible):
        viewModel = super(InfoBattleContextHintView, self).getViewModel()
        with viewModel.transaction() as model:
            model.setIsVisible(visible)
