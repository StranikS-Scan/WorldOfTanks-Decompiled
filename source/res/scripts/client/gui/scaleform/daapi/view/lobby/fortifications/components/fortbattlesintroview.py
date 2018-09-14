# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortBattlesIntroView.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortIntroMeta import FortIntroMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import i18n, time_utils

class FortBattlesIntroView(FortIntroMeta, FortViewHelper):

    def onClientStateChanged(self, state):
        if state.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            self.__makeData()

    def onFortBattleRemoved(self, cache, battleID):
        self.__makeData()

    def onFortBattleChanged(self, cache, item, battleItem):
        self.__makeData()

    def _populate(self):
        super(FortBattlesIntroView, self)._populate()
        self.startFortListening()
        self.__makeData()

    def _dispose(self):
        self.stopFortListening()
        super(FortBattlesIntroView, self)._dispose()

    def __makeData(self):
        data = {}
        isBattleEnabled, clanBattleBtnSimpleTooltip, clanBattleBtnComplexTooltip, clanBattleAdditionalText = self.__getButtonData()
        if clanBattleAdditionalText:
            clanBattleAdditionalText = self.__makeAdditionalText(clanBattleAdditionalText)
        data['clanBattleAdditionalText'] = clanBattleAdditionalText
        data['clanBattleBtnSimpleTooltip'] = clanBattleBtnSimpleTooltip
        data['clanBattleBtnComplexTooltip'] = clanBattleBtnComplexTooltip
        data['enableBtn'] = isBattleEnabled
        data['fortBattleTitle'] = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_TITLE
        data['fortBattleDescr'] = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_DESCR
        data['fortBattleBtnTitle'] = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_BTNLABEL
        self.as_setIntroDataS(data)

    def __makeAdditionalText(self, value):
        return text_styles.alert(value)

    def __getButtonData(self):
        if self.fortState.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            fort = self.fortCtrl.getFort()
            if not fort.isDefenceHourEnabled():
                if self.fortCtrl.getPermissions().canChangeDefHour():
                    clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_LEADER
                else:
                    clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_NOTLEADER
                clanBattleAdditionalText = i18n.makeString(FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NOTACTIVATEDDEFENCETIME)
                return (False,
                 clanBattleBtnSimpleTooltip,
                 '',
                 clanBattleAdditionalText)
            attacksInOneDay = fort.getAttacksIn(timePeriod=time_utils.ONE_DAY)
            defencesInOneDay = fort.getDefencesIn(timePeriod=time_utils.ONE_DAY)
            if attacksInOneDay or defencesInOneDay:
                return (True,
                 '',
                 TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_ENABLED,
                 None)
            battlesInTwoWeeks = fort.getAttacksAndDefencesIn(timePeriod=2 * time_utils.ONE_WEEK)
            if battlesInTwoWeeks:
                closestBattle = battlesInTwoWeeks[0]
                battleDate = BigWorld.wg_getLongDateFormat(closestBattle.getStartTime())
                clanBattleAdditionalText = i18n.makeString(FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLE, nextDate=battleDate)
                clanBattleBtnSimpleTooltip = i18n.makeString(TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_NEXTBATTLE, currentDate=battleDate)
                return (False,
                 clanBattleBtnSimpleTooltip,
                 '',
                 clanBattleAdditionalText)
            if self.fortCtrl.getPermissions().canPlanAttack():
                clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_LEADERNOACTION
            else:
                clanBattleBtnSimpleTooltip = TOOLTIPS.FORTIFICATION_INTROVIEW_CLANBATTLEBTN_DISABLED_NOTLEADERNOACTION
            clanBattleAdditionalText = i18n.makeString(FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NOTACTIVATED)
            return (False,
             clanBattleBtnSimpleTooltip,
             '',
             clanBattleAdditionalText)
        else:
            return (False,
             '',
             '',
             None)
