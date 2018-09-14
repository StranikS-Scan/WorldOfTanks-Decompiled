# Embedded file name: scripts/client/tutorial/gui/Scaleform/offbattle/settings.py
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from tutorial.gui.Scaleform.pop_ups import TutorialGreetingDialog, TutorialQueueDialog
from tutorial.gui.Scaleform.offbattle import pop_ups as off_pop_ups

class OFFBATTLE_VIEW_ALIAS(object):
    GREETING_DIALOG = 'tGreetingDialog'
    QUEUE_DIALOG = 'tQueueDialog'
    FINAL_RESULTS_WINDOW = 'tFinalResultWindow'
    NO_FINAL_RESULTS_WINDOW = 'tNoFinalResultWindow'
    CONFIRM_REFUSE_DIALOG = 'tConfirmRefuseDialog'


OFFBATTLE_VIEW_SETTINGS = (GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.GREETING_DIALOG, TutorialGreetingDialog, 'tutorialGreetingDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.QUEUE_DIALOG, TutorialQueueDialog, 'tutorialQueueDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.FINAL_RESULTS_WINDOW, off_pop_ups.TutorialBattleStatisticWindow, 'tutorialBattleStatistic.swf', ViewTypes.WINDOW, 'tBattleStatisticGroup', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.NO_FINAL_RESULTS_WINDOW, off_pop_ups.TutorialBattleNoResultWindow, 'tutorialBattleNoResults.swf', ViewTypes.WINDOW, 'tBattleStatisticGroup', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.CONFIRM_REFUSE_DIALOG, off_pop_ups.TutorialConfirmRefuseDialog, 'tutorialConfirmRefuseDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE))
DIALOG_ALIAS_MAP = {'greeting': OFFBATTLE_VIEW_ALIAS.GREETING_DIALOG,
 'queue': OFFBATTLE_VIEW_ALIAS.QUEUE_DIALOG,
 'confirmRefuse': OFFBATTLE_VIEW_ALIAS.CONFIRM_REFUSE_DIALOG}
WINDOW_ALIAS_MAP = {'final': OFFBATTLE_VIEW_ALIAS.FINAL_RESULTS_WINDOW,
 'noResults': OFFBATTLE_VIEW_ALIAS.NO_FINAL_RESULTS_WINDOW}
