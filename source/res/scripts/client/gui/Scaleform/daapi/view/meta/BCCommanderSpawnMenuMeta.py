# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCCommanderSpawnMenuMeta.py
from gui.Scaleform.daapi.view.battle.commander.spawn_menu import SpawnMenu

class BCCommanderSpawnMenuMeta(SpawnMenu):

    def as_showFooterHintTextS(self, isVisible, textValue):
        return self.flashObject.as_showFooterHintText(isVisible, textValue) if self._isDAAPIInited() else None

    def as_showButtonArrowHintS(self, isVisible, textValue):
        return self.flashObject.as_showButtonArrowHint(isVisible, textValue) if self._isDAAPIInited() else None

    def as_setEnemyNameVisibilityS(self, isVisible):
        return self.flashObject.as_setEnemyNameVisibility(isVisible) if self._isDAAPIInited() else None
