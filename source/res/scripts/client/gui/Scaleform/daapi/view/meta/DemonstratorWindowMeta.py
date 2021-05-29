# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DemonstratorWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class DemonstratorWindowMeta(AbstractWindowView):

    def onGameplaySelected(self, index):
        self._printOverrideError('onGameplaySelected')

    def onLvlSelected(self, index):
        self._printOverrideError('onLvlSelected')

    def onSpawnSelected(self, index):
        self._printOverrideError('onSpawnSelected')

    def onMapSelected(self, index):
        self._printOverrideError('onMapSelected')

    def onBattleStart(self):
        self._printOverrideError('onBattleStart')

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_setGameplayTabsS(self, tabList, selectedTab):
        return self.flashObject.as_setGameplayTabs(tabList, selectedTab) if self._isDAAPIInited() else None

    def as_setSpawnsS(self, spawnList, selectedSpawn):
        return self.flashObject.as_setSpawns(spawnList, selectedSpawn) if self._isDAAPIInited() else None

    def as_setLevelsS(self, lvlList, selectedLvl):
        return self.flashObject.as_setLevels(lvlList, selectedLvl) if self._isDAAPIInited() else None

    def as_enablePlatoonWarningS(self, value):
        return self.flashObject.as_enablePlatoonWarning(value) if self._isDAAPIInited() else None

    def as_enableExtendedSettingsS(self, value):
        return self.flashObject.as_enableExtendedSettings(value) if self._isDAAPIInited() else None

    def as_enableBattleButtonS(self, value):
        return self.flashObject.as_enableBattleButton(value) if self._isDAAPIInited() else None
