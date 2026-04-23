# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/ingame_help/hb_help_pages.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.ingame_help.detailed_help_pages import DetailedHelpPagesBuilder, addPage
from gui.shared.formatters import text_styles
from historical_battles.gui.ingame_help import HelpPagePriority
from historical_battles_common.hb_constants_extension import ARENA_GUI_TYPE
if typing.TYPE_CHECKING:
    from historical_battles.gui.Scaleform.daapi.view.battle.slides import SlideData

class HBPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isHB',)
    _IMG_PATH = R.images.historical_battles.gui.maps.icons.hintBackground.inBattleHelp

    @classmethod
    def priority(cls):
        return HelpPagePriority.HB

    @classmethod
    def buildPages(cls, ctx):
        from historical_battles.gui.Scaleform.daapi.view.battle.slides import LoadingScreenSlidesCfg
        from gui.battle_control import avatar_getter
        arena = avatar_getter.getArena()
        hintList = LoadingScreenSlidesCfg.instance().getLoadingScreen(arena.arenaType.geometryName).slides
        pages = []
        header = backport.text(R.strings.hb_battle.helpScreen.missionTitle.num(arena.guiType)())
        for hintData in hintList:
            battleData = hintData.getBattleData()
            addPage(datailedList=pages, headerTitle=header, title=battleData.get('title', ''), descr=text_styles.mainBig(battleData.get('description', '')), vKeys=[], buttons=[], image=backport.image(HBPagesBuilder._IMG_PATH.dyn(battleData.get('background', ''))()))

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isHB = arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.HB_RANGE
        ctx['isHB'] = isHB
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isHB
