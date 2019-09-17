# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/fest_race_ingame_help.py
from gui.Scaleform.daapi.view.meta.FestRaceIngameHelpMeta import FestRaceIngameHelpMeta
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.formatters import icons
from gui.shared.utils import key_mapping
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class FestRaceIngameHelp(FestRaceIngameHelpMeta):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def _populate(self):
        super(FestRaceIngameHelp, self)._populate()
        self.as_setTitleS(backport.text(R.strings.festival.festival.loading.gametype()))
        self.as_setItemsS(self._getItemsData())
        self._settingsCore.onSettingsApplied += self._refreshItemsData
        self.as_setHotKeyHintS(self._getHintText())

    def _dispose(self):
        self._settingsCore.onSettingsApplied -= self._refreshItemsData

    def setHintEnabled(self, enabled):
        self.as_setHotKeyHintEnabledS(enabled)

    def _refreshItemsData(self, diff):
        controls = diff.get('keyboard', {})
        if 'item04' in controls:
            self.as_setItemsS(self._getItemsData())

    def _getHintText(self):
        icon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.festival.tip_ESCbtn()), width=94, height=40, vSpace=-15)
        return backport.text(R.strings.festival.festival.f1_screen.close_hint(), HintKeyESC=icon)

    def _getItemsData(self):
        key = self._settingsCore.getSetting('keyboard')['item04']
        keyName = key_mapping.getBigworldNameFromKey(key_mapping.SCALEFORM_TO_BW[key])
        keyText = backport.text(R.strings.readable_key_names.dyn(keyName)())
        return ({'title': backport.text(R.strings.festival.festival.loading_hint.victory.name()),
          'desc': backport.text(R.strings.festival.festival.loading_hint.victory.descr())}, {'title': backport.text(R.strings.festival.festival.loading_hint.forsage.name()),
          'desc': backport.text(R.strings.festival.festival.loading_hint.forsage.descr(), hotkey=keyText)}, {'title': backport.text(R.strings.festival.festival.loading_hint.repair.name()),
          'desc': backport.text(R.strings.festival.festival.loading_hint.repair.descr())})
