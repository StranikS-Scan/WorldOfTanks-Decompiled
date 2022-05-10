# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/frag_panel.py
from gui.Scaleform.daapi.view.meta.FragPanelMeta import FragPanelMeta
from battle_royale.gui.battle_control.controllers.vehicles_count_ctrl import IVehicleCountListener
from gui.battle_control.avatar_getter import getArena
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.impl import backport
from gui.impl.gen import R

class FragPanel(IVehicleCountListener, FragPanelMeta):
    __slots__ = ()
    __ADDITIONAL_FRAG_TEMPLATE = '<font color="#333333">[&nbsp;<font color="#999999">{}</font>&nbsp;]</font>'

    def setFrags(self, frags, isPlayerVehicle):
        self.as_setRightFieldS(frags)

    def setTotalCount(self, vehicles, teams):
        isSquad = ARENA_BONUS_TYPE_CAPS.checkAny(getArena().bonusType, ARENA_BONUS_TYPE_CAPS.SQUADS)
        countText = str(vehicles)
        if isSquad:
            countText = ' '.join((countText, self.__ADDITIONAL_FRAG_TEMPLATE.format(backport.text(R.strings.battle_royale.fragPanel.squadsCount(), squadsCount=str(teams)))))
        self.as_setLeftFieldS(countText)
