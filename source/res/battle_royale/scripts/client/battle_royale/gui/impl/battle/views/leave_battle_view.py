# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/battle/views/leave_battle_view.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.gen import R
from battle_royale.gui.impl.gen.view_models.views.battle.views.leave_battle_view_model import LeaveBattleViewModel

class LeaveBattleView(DialogTemplateView):
    __slots__ = ()
    LAYOUT_ID = R.views.battle_royale.battle.views.LeaveBattleView()
    VIEW_MODEL = LeaveBattleViewModel

    @property
    def viewModel(self):
        return super(LeaveBattleView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LeaveBattleView, self)._onLoading(*args, **kwargs)
        backgroundImagePath = R.images.gui.maps.icons.battleRoyale.battle.deserterLeaveBattle()
        buttonStrings = R.strings.battle_royale_progression.leaveBattleView.confirmation
        self.setBackgroundImagePath(backgroundImagePath)
        self.addButton(ConfirmButton(label=buttonStrings.submit()))
        self.addButton(CancelButton(label=buttonStrings.cancel()))
