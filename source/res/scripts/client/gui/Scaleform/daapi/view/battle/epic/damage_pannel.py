# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/damage_pannel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EpicDamagePanelMeta import EpicDamagePanelMeta
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel

class EpicDamagePanel(DamagePanel, EpicDamagePanelMeta):

    def _populate(self):
        super(EpicDamagePanel, self)._populate()
        BigWorld.player().arena.componentSystem.playerDataComponent.onCrewRolesFactorUpdated += self.__setGeneralBonus

    def _dispose(self):
        super(EpicDamagePanel, self)._dispose()
        arena = BigWorld.player().arena if hasattr(BigWorld.player(), 'arena') else None
        if arena and hasattr(arena, 'componentSystem'):
            componentSystem = BigWorld.player().arena.componentSystem
            if componentSystem:
                componentSystem.playerDataComponent.onCrewRolesFactorUpdated -= self.__setGeneralBonus
        return

    def __setGeneralBonus(self, newFactor, _=None, __=None):
        self.as_setGeneralBonusS(newFactor)
