# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/battle_loading.py
from account_helpers.AccountSettings import FunRandomMaps
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from fun_random.gui.feature.util.fun_mixins import FunAccountSettingsHelper

class FepBattleLoading(BattleLoading, FunAccountSettingsHelper):

    def _populate(self):
        super(FepBattleLoading, self)._populate()
        self.setAccSetting(FunRandomMaps.FUN_RANDOM_LAST_SELECTED_MAP, self._arenaVisitor.type.getGeometryName())

    def _getSettingsID(self, loadingInfo):
        return self.settingsCore.options.getSetting(loadingInfo).getSettingID(isVisualOnly=True)
