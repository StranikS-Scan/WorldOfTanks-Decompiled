# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortIntroView.py
import time
import BigWorld
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_text import ALERT_TEXT
from gui.Scaleform.daapi.view.meta.FortIntroMeta import FortIntroMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import i18n

class CLAN_BATTLE_STATEMENT:
    SOON_BATTLE = 1
    NOT_SOON_BATTLE_IN_24_HOURS = 2
    NOT_SOON_BATTLES_IN_TWO_WEEKS = 3


class FortIntroView(FortIntroMeta, FortViewHelper):

    def __init__(self):
        super(FortIntroView, self).__init__()

    def _populate(self):
        super(FortIntroView, self)._populate()
        self.__makeData()

    def _dispose(self):
        super(FortIntroView, self)._dispose()

    def __makeData(self):
        data = {}
        isDefenceTime = self.__isActivatedDefenseTime()
        nextbattleState = self.__getTimeOfNextBattle()
        clanBattleBtnSimpleTooltip = ''
        clanBattleBtnComplexTooltip = ''
        clanBattleAdditionalText = None
        if not isDefenceTime:
            if self.fortCtrl.getPermissions().canChangeDefHour():
                clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_LEADER
            else:
                clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_NOTLEADER
            clanBattleAdditionalText = i18n.makeString(FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NOTACTIVATEDDEFENCETIME)
        elif nextbattleState == CLAN_BATTLE_STATEMENT.SOON_BATTLE:
            clanBattleBtnComplexTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_ENABLED
        elif nextbattleState == CLAN_BATTLE_STATEMENT.NOT_SOON_BATTLE_IN_24_HOURS:
            clanBattleAdditionalText = i18n.makeString(FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLE, nextDate=self.__formatBattleDate())
            clanBattleBtnSimpleTooltip = i18n.makeString(TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_NEXTBATTLE, currentDate=self.__formatBattleDate())
        elif nextbattleState == CLAN_BATTLE_STATEMENT.NOT_SOON_BATTLES_IN_TWO_WEEKS:
            if self.fortCtrl.getPermissions().canPlanAttack():
                clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_LEADERNOACTION
            else:
                clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_NOTLEADERNOACTION
            clanBattleAdditionalText = i18n.makeString(FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NOTACTIVATED)
        if clanBattleAdditionalText:
            clanBattleAdditionalText = self.__makeAdditionalText(clanBattleAdditionalText)
        data['clanBattleAdditionalText'] = clanBattleAdditionalText
        data['clanBattleBtnSimpleTooltip'] = clanBattleBtnSimpleTooltip
        data['clanBattleBtnComplexTooltip'] = clanBattleBtnComplexTooltip
        data['enableBtn'] = isDefenceTime and nextbattleState == CLAN_BATTLE_STATEMENT.SOON_BATTLE
        data['fortBattleTitle'] = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_TITLE
        data['fortBattleDescr'] = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_DESCR
        data['fortBattleBtnTitle'] = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_BTNLABEL
        self.as_setIntroDataS(data)
        return

    def __makeAdditionalText(self, value):
        return fort_text.getText(ALERT_TEXT, value)

    def __formatBattleDate(self):
        return BigWorld.wg_getLongDateFormat(time.time() + 100000)

    def __isActivatedDefenseTime(self):
        return True

    def __getTimeOfNextBattle(self):
        return CLAN_BATTLE_STATEMENT.SOON_BATTLE
