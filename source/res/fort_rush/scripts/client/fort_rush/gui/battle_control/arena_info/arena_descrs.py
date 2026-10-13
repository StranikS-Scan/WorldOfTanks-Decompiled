# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_control/arena_info/arena_descrs.py
from __future__ import absolute_import
from gui.battle_control.arena_info.arena_descrs import ArenaDescriptionWithInvitation
from gui.battle_control.arena_info.settings import DEFAULT_SCREEN_MAP_IMAGE_RES_PATH
from gui.impl import backport
from gui.impl.gen import R
_BATTLE_LOADING_TEXT_RES = R.strings.fort_rush.battleLoading
_FORT_RUSH_LOADING_SCREEN_ICONS = {'127_japort_fortrush_26': 'fort_rush/gui/maps/icons/battle_loading_screen/127_japort_fortrush_26.dds',
 '11_murovanka_fortrush_26': 'fort_rush/gui/maps/icons/battle_loading_screen/11_murovanka_fortrush_26.dds',
 '114_czech_fortrush_26': 'fort_rush/gui/maps/icons/battle_loading_screen/114_czech_fortrush_26.dds'}

class FortRushArenaDescription(ArenaDescriptionWithInvitation):

    def getDescriptionString(self, isInBattle=True):
        return backport.text(_BATTLE_LOADING_TEXT_RES.header())

    def getWinString(self, isInBattle=True):
        return backport.text(_BATTLE_LOADING_TEXT_RES.description())

    def getBattleTypeIconPath(self, sizeFolder='c_136x136'):
        iconRes = R.images.gui.maps.icons.battleTypes.dyn(sizeFolder).fort_rush_battle()
        return backport.image(iconRes)

    def getScreenIcon(self):
        geometryName = self._visitor.getArenaType().geometryName
        return _FORT_RUSH_LOADING_SCREEN_ICONS.get(geometryName, DEFAULT_SCREEN_MAP_IMAGE_RES_PATH)
