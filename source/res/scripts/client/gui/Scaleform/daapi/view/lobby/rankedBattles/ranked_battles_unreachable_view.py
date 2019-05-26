# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_unreachable_view.py
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_OVERLAY_SOUND_SPACE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesUnreachableViewMeta import RankedBattlesUnreachableViewMeta
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from helpers import dependency, int2roman
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesUnreachableView(LobbySubView, RankedBattlesUnreachableViewMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    _COMMON_SOUND_SPACE = RANKED_OVERLAY_SOUND_SPACE
    __background_alpha__ = 0.5

    def __init__(self, ctx=None):
        super(RankedBattlesUnreachableView, self).__init__()
        self.__levelsRangeStr = ''

    def onEscapePress(self):
        self._exitHangar()

    def onCloseBtnClick(self):
        self._exitHangar()

    def _populate(self):
        super(RankedBattlesUnreachableView, self)._populate()
        self.as_setDataS(self.__getData())

    def __getData(self):
        bottomItems = self.__getBottomItems()
        centerTextStr = text_styles.vehicleStatusCriticalText(backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.unreachableText()))
        bottomTextStr = text_styles.highTitle(backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.bottomText()))
        return {'bottomRules': bottomItems,
         'header': {'title': backport.text(R.strings.ranked_battles.rankedBattle.title()),
                    'leftSideText': backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.subtitleText())},
         'centerText': self.__formatUnreachableLevels(centerTextStr),
         'bottomText': self.__formatUnreachableLevels(bottomTextStr),
         'closeBtnLabel': backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.closeBtnLabel()),
         'closeBtnTooltip': '',
         'bgImage': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
         'centerImg': backport.image(R.images.gui.maps.icons.rankedBattles.XlessView.ranked_battle_locked_sm()),
         'centerImgBig': backport.image(R.images.gui.maps.icons.rankedBattles.XlessView.ranked_battle_locked_big())}

    def __getBottomItems(self):
        result = list()
        result.append({'tooltip': '',
         'image': backport.image(R.images.gui.maps.icons.rankedBattles.XlessView.icon_prem()),
         'description': text_styles.main(backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.bottom.premium(), premiumType=backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.bottom.premium.plus())))})
        result.append({'tooltip': '',
         'image': backport.image(R.images.gui.maps.icons.rankedBattles.XlessView.icon_ranks_task_200x100()),
         'description': text_styles.main(backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.bottom.missions()))})
        result.append({'tooltip': '',
         'image': backport.image(R.images.gui.maps.icons.rankedBattles.XlessView.icon_reserves()),
         'description': text_styles.main(backport.text(R.strings.ranked_battles.rankedBattlesUnreachableView.bottom.reserves()))})
        return result

    def _exitHangar(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __formatUnreachableLevels(self, message):
        if self.__levelsRangeStr == '':
            minLevel, maxLevel = self.__rankedController.getSuitableVehicleLevels()
            if minLevel == maxLevel:
                self.__levelsRangeStr = int2roman(minLevel)
            else:
                self.__levelsRangeStr = '{0}-{1}'.format(int2roman(minLevel), int2roman(maxLevel))
        return message.format(levels=self.__levelsRangeStr)
