# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesAfterBattleView.py
from collections import namedtuple
from gui.Scaleform.daapi.view.meta.EpicBattlesAfterBattleViewMeta import EpicBattlesAfterBattleViewMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
EpicBattlesAfterBattleViewVO = namedtuple('EpicBattlesAfterBattleViewVO', ('awards', 'progress', 'barText', 'currentPrestigeLevel', 'epicMetaLevelIconData', 'rank', 'rankText', 'rankSubText', 'levelUpText', 'backgroundImageSrc', 'maxLevel'))

class EpicBattlesAfterBattleView(EpicBattlesAfterBattleViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx=None):
        super(EpicBattlesAfterBattleView, self).__init__()
        self.__ctx = ctx

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(EpicBattlesAfterBattleView, self)._populate()
        extInfo = self.__ctx['reusableInfo'].personal.avatar.extensionInfo
        epicMetaGame = extInfo['epicMetaGame']
        questsProgressData = self.__ctx['reusableInfo'].personal.getQuestsProgress()
        bonuses = sum([ self.eventsCache.getAllQuests().get(q).getBonuses() for q in questsProgressData ], [])
        awardsVO = sum([ bonus.getEpicAwardVOs() for bonus in bonuses ], [])
        pPrestigeLevel, pMetaLevel, pFamePts = self.epicMetaGameCtrl.getPlayerLevelInfo()
        _, prevPMetaLevel, prevPFamePts = epicMetaGame.get('metaLevel', (None, None, None))
        achievedRank = extInfo['playerRank'].get('rank', -1)
        rankName = getattr(EPIC_BATTLE, 'RANK_RANK{}'.format(achievedRank))
        achievedRank += 1
        mlSettings = dependency.instance(ILobbyContext).getServerSettings().epicMetaGame.metaLevel
        maxMetaLevel = mlSettings.get('maxLevel', 0)
        famePtsToProgress = mlSettings.get('famePtsToProgress', None)
        famePointsReceived = sum(famePtsToProgress[prevPMetaLevel - 1:pMetaLevel - 1]) + pFamePts - prevPFamePts
        data = EpicBattlesAfterBattleViewVO(awards=awardsVO, progress=self.__getProgress(pMetaLevel, pFamePts, prevPMetaLevel, prevPFamePts, maxMetaLevel), barText='{}'.format(text_styles.stats('+' + str(famePointsReceived))), currentPrestigeLevel=pPrestigeLevel, epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel, pMetaLevel), rank=achievedRank, rankText=rankName, rankSubText=EPIC_BATTLE.EPIC_BATTLES_AFTER_BATTLE_ACHIEVED_RANK, levelUpText=EPIC_BATTLE.EPIC_BATTLES_AFTER_BATTLE_LEVEL_UP_TITLE, backgroundImageSrc='../maps/icons/epicBattles/backgrounds/meta_bg.jpg', maxLevel=maxMetaLevel)
        self.as_setDataS(data._asdict())
        return

    def _dispose(self):
        super(EpicBattlesAfterBattleView, self)._dispose()

    def __close(self):
        self.destroy()

    def __getProgress(self, curLevel, curFamePoints, prevLevel, prevFamePoints, maxLevel):
        pLevel = prevLevel + float(prevFamePoints) / float(self.epicMetaGameCtrl.getPointsProgessForLevel(prevLevel)) if prevLevel != maxLevel else maxLevel
        cLevel = curLevel + float(curFamePoints) / float(self.epicMetaGameCtrl.getPointsProgessForLevel(curLevel)) if curLevel != maxLevel else maxLevel
        return (pLevel, cLevel)
