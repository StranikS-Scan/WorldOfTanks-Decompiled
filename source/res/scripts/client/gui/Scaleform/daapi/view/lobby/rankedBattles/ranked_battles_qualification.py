# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_qualification.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_FIRST_ENTRY_BY_DIVISION_ID
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RankedBattlesDivisionQualificationMeta import RankedBattlesDivisionQualificationMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles import ranked_formatters
from gui.ranked_battles.ranked_builders import shared_vos
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesQualification(RankedBattlesDivisionQualificationMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _populate(self):
        super(RankedBattlesQualification, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.__rankedController.onUpdated += self.__onRankedUpdate
        qualificationRank = self.__getQualificationRank()
        self.__updateRankedData(qualificationRank)
        self.__setQualificationData(qualificationRank)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__rankedController.onUpdated -= self.__onRankedUpdate
        super(RankedBattlesQualification, self)._dispose()

    def __updateRankedData(self, rank):
        divisionID = rank.getDivision().getID()
        self.__setQualificationSteps(divisionID)
        self.__setQualificationProgress(rank)
        self.__setQualificationEfficiency(divisionID)

    def __dossierUpdateCallBack(self, *args):
        self.__updateRankedData(self.__getQualificationRank())

    def __onRankedUpdate(self, *args):
        self.__updateRankedData(self.__getQualificationRank())

    def __setQualificationData(self, rank):
        divisionID = rank.getDivision().getID()
        smallImageSrc = rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_BIG)
        bigImageSrc = rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_HUGE)
        isFirstEntryMap = AccountSettings.getSettings(IS_FIRST_ENTRY_BY_DIVISION_ID)
        isFirstEntry = isFirstEntryMap.get(divisionID, True)
        if isFirstEntry:
            isFirstEntryMap[divisionID] = False
            AccountSettings.setSettings(IS_FIRST_ENTRY_BY_DIVISION_ID, isFirstEntryMap)
        self.as_setQualificationDataS(smallImageSrc, bigImageSrc, isFirstEntry)

    def __getQualificationRank(self):
        qualificationDivision = findFirst(lambda d: d.isQualification(), self.__rankedController.getDivisions())
        return self.__rankedController.getRank(qualificationDivision.firstRank)

    def __setQualificationProgress(self, rank):
        division = rank.getDivision()
        divisionID = division.getID()
        total = self.__rankedController.getTotalQualificationBattles()
        stats = self.__rankedController.getStatsComposer()
        current = stats.divisionsStats.get(divisionID, {}).get('battles', 0)
        isCompleted = division.isCompleted()
        if not isCompleted:
            progressShortcut = R.strings.ranked_battles.division.status.qualification.progress()
            titleShortcut = R.strings.ranked_battles.division.status.qualification()
            progressSmall = text_styles.superPromoTitle(backport.text(progressShortcut, current=text_styles.superPromoTitleEm(current), total=total))
            progressTextSmall = text_styles.superPromoTitle(backport.text(titleShortcut, progress=progressSmall))
            progressBig = text_styles.grandTitle(backport.text(progressShortcut, current=text_styles.grandTitleYellow(current), total=total))
            progressTextBig = text_styles.grandTitle(backport.text(titleShortcut, progress=progressBig))
        else:
            progressTextSmall = ''
            progressTextBig = ''
        qualificationDescr = ''
        numQualificationQuestBattles = sorted(self.__rankedController.getQualificationQuests().keys())
        if numQualificationQuestBattles:
            numQualificationQuestBattles.append(total)
            if isCompleted:
                qualificationDescr = text_styles.concatStylesToSingleLine(icons.check(), text_styles.statInfo(backport.text(R.strings.ranked_battles.division.status.qualificationDescr.complete())))
            else:
                qualificationDescr = text_styles.main(backport.text(R.strings.ranked_battles.division.status.qualificationDescr.progress(), battlesTotal=total, battlesList=', '.join([ str(x) for x in numQualificationQuestBattles ])))
        self.as_setQualificationProgressS(progressTextSmall, progressTextBig, isCompleted, qualificationDescr)

    def __setQualificationSteps(self, divisionID):
        steps = self.__rankedController.getStatsComposer().divisionsStats.get(divisionID, {}).get('stepsCount', 0)
        self.as_setQualificationStepsDataS(shared_vos.getStatVO(ranked_formatters.getIntegerStrStat(float(steps)), 'qualificationSteps', 'steps', 'qualificationSteps'))

    def __setQualificationEfficiency(self, divisionsID):
        statsComposer = self.__rankedController.getStatsComposer()
        divisionEfficiency = statsComposer.getDivisionEfficiencyPercent(divisionsID)
        self.as_setQualificationEfficiencyDataS(shared_vos.getStatVO(ranked_formatters.getFloatPercentStrStat(divisionEfficiency), 'qualificationEfficiency', 'efficiency', 'qualificationEfficiency'))
