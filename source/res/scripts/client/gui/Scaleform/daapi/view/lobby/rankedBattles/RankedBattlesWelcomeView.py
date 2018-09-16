# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesWelcomeView.py
import SoundGroups
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesWelcomeViewMeta import RankedBattlesWelcomeViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles.constants import SOUND
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesWelcomeView(LobbySubView, RankedBattlesWelcomeViewMeta):
    settingsCore = dependency.descriptor(ISettingsCore)
    rankedController = dependency.descriptor(IRankedBattlesController)
    __background_alpha__ = 0.5

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onNextBtnClick(self):
        self.__close()

    def onAnimationFinished(self, forced):
        if forced:
            self.soundManager.playSound(SOUND.ANIMATION_WINDOW_CLOSED)
        stateFlags = self.__getShowStateFlags()
        stateFlags['isRankedWelcomeViewShowed'] = True
        self.__setShowStateFlags(stateFlags)

    def onSoundTrigger(self, eventName):
        self.soundManager.playSound(eventName)

    def _populate(self):
        super(RankedBattlesWelcomeView, self)._populate()
        self.as_setDataS(self.__getData())

    def __getData(self):
        stateFlags = self.__getShowStateFlags()
        isCompleted = stateFlags['isRankedWelcomeViewStarted']
        stateFlags['isRankedWelcomeViewStarted'] = True
        self.__setShowStateFlags(stateFlags)
        rulePositive, ruleNegative = self.__getRules()
        self.rankedController.getRanksChain()
        ranks = [ rank.getIcon('big') for rank in self.rankedController.getRanksChain() if rank.getID() > 0 ]
        return {'header': text_styles.superPromoTitle(RANKED_BATTLES.WELCOMESCREEN_HEADER),
         'rules': [{'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICN_TANKS,
                    'description': text_styles.hightlight(RANKED_BATTLES.WELCOMESCREEN_LEFTRULE),
                    'tooltip': makeTooltip(RANKED_BATTLES.WELCOMESCREEN_LEFTRULETOOLTIP_HEADER, RANKED_BATTLES.WELCOMESCREEN_LEFTRULETOOLTIP_BODY)}, {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICN_CREW,
                    'description': text_styles.hightlight(RANKED_BATTLES.WELCOMESCREEN_CENTERRULE),
                    'tooltip': makeTooltip(RANKED_BATTLES.WELCOMESCREEN_CENTERRULETOOLTIP_HEADER, RANKED_BATTLES.WELCOMESCREEN_CENTERRULETOOLTIP_BODY)}, {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_AWARD,
                    'description': text_styles.hightlight(RANKED_BATTLES.WELCOMESCREEN_RIGHTRULE),
                    'tooltip': makeTooltip(RANKED_BATTLES.WELCOMESCREEN_RIGHTRULETOOLTIP_HEADER, RANKED_BATTLES.WELCOMESCREEN_RIGHTRULETOOLTIP_BODY)}],
         'ranks': ranks,
         'rulePositive': rulePositive,
         'ruleNegative': ruleNegative,
         'rankDescription': text_styles.superPromoTitle(RANKED_BATTLES.WELCOMESCREEN_RANKDESCR),
         'ranksDescription': text_styles.promoSubTitle(RANKED_BATTLES.WELCOMESCREEN_RANKSDESCR),
         'equalityText': RANKED_BATTLES.WELCOMESCREEN_EQUALITYTEXT,
         'rulesDelimeterText': text_styles.promoSubTitle(RANKED_BATTLES.WELCOMESCREEN_RULESDELIMETER),
         'btnLbl': RANKED_BATTLES.WELCOMESCREEN_BTN,
         'btnTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_OKTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_OKTOOLTIP_BODY),
         'closeLbl': RANKED_BATTLES.WELCOMESCREEN_CLOSEBTN,
         'closeBtnTooltip': makeTooltip(RANKED_BATTLES.WELCOMESCREEN_CLOSEBTNTOOLTIP_HEADER, RANKED_BATTLES.WELCOMESCREEN_CLOSEBTNTOOLTIP_BODY),
         'bgImage': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR,
         'isComplete': bool(isCompleted)}

    def __getRules(self):
        topWinNum = self.rankedController.getRanksTops(isLoser=False, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_EARN)
        topLoserNum = self.rankedController.getRanksTops(isLoser=True, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_EARN)
        teamStr = text_styles.bonusAppliedText(RANKED_BATTLES.WELCOMESCREEN_POSITIVE_TEAM)
        descr = text_styles.hightlight(RANKED_BATTLES.WELCOMESCREEN_POSITIVE_BODY)
        rulePositive = {'image': RES_ICONS.getRankedPostBattleTopIcon(topWinNum),
         'description': descr.format(team=teamStr, topNumber=topWinNum)}
        if topLoserNum:
            teamStr = text_styles.error(RANKED_BATTLES.WELCOMESCREEN_NEGATIVE_TEAM)
            descr = text_styles.hightlight(RANKED_BATTLES.WELCOMESCREEN_NEGATIVE_BODY)
            ruleNegative = {'image': RES_ICONS.getRankedPostBattleLoseIcon(topLoserNum),
             'description': descr.format(team=teamStr, topNumber=topLoserNum)}
        else:
            ruleNegative = None
        return (rulePositive, ruleNegative)

    def __close(self):
        self.onAnimationFinished(False)
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        SoundGroups.g_instance.playSound2D(SOUND.ANIMATION_WINDOW_CLOSED)
        self.destroy()

    def __getShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __setShowStateFlags(self, filters):
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)
