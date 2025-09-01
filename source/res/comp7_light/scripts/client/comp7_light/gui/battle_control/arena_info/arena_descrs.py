# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_control/arena_info/arena_descrs.py
from gui.battle_control.arena_info.arena_descrs import ArenaDescriptionWithInvitation
from gui.impl import backport
from gui.impl.gen import R

class Comp7LightBattlesDescription(ArenaDescriptionWithInvitation):

    def getBattleTypeIconPath(self, sizeFolder='c_136x136'):
        iconRes = R.images.comp7_light.gui.maps.icons.battleTypes.dyn(sizeFolder).dyn(self.getFrameLabel())
        return backport.image(iconRes()) if iconRes.exists() else ''
