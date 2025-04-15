# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_damage_pannel.py
import BigWorld
from frontline.gui.Scaleform.daapi.view.meta.FrontlineDamagePanelMeta import FrontlineDamagePanelMeta
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel

class FrontlineDamagePanel(DamagePanel, FrontlineDamagePanelMeta):

    def _populate(self):
        super(FrontlineDamagePanel, self)._populate()
        BigWorld.player().arena.componentSystem.playerDataComponent.onCrewRolesFactorUpdated += self.__setGeneralBonus

    def _dispose(self):
        super(FrontlineDamagePanel, self)._dispose()
        arena = BigWorld.player().arena if hasattr(BigWorld.player(), 'arena') else None
        if arena and hasattr(arena, 'componentSystem'):
            componentSystem = BigWorld.player().arena.componentSystem
            if componentSystem:
                componentSystem.playerDataComponent.onCrewRolesFactorUpdated -= self.__setGeneralBonus
        return

    def __setGeneralBonus(self, newFactor, allyVehID=None, allyNewRank=None):
        self.as_setGeneralBonusS(newFactor)
