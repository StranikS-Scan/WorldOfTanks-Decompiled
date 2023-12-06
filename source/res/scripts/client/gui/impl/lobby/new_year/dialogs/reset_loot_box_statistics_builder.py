# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/reset_loot_box_statistics_builder.py
from frameworks.wulf import WindowLayer
from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper

class ResetLootBoxStatisticsBuilder(ConfirmCancelDialogBuilder):

    def build(self, withBlur=False):
        return FullScreenDialogWindowWrapper(self.buildView(), doBlur=withBlur, layer=WindowLayer.OVERLAY)
