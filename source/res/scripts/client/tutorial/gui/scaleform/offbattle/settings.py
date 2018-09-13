# Embedded file name: scripts/client/tutorial/gui/Scaleform/offbattle/settings.py
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from tutorial.gui.Scaleform.pop_ups import TutorialDialog
from tutorial.gui.Scaleform.offbattle import pop_ups as off_pop_ups

class OFFBATTLE_VIEW_ALIAS(object):
    GREETING_DIALOG = 'tGreetingDialog'
    QUEUE_DIALOG = 'tQueueDialog'
    VIDEO_DIALOG = 'tVideoDialog'
    FINAL_RESULTS_WINDOW = 'tFinalResultWindow'
    NO_FINAL_RESULTS_WINDOW = 'tNoFinalResultWindow'


OFFBATTLE_VIEW_SETTINGS = (GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.GREETING_DIALOG, TutorialDialog, 'tutorialGreetingDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.QUEUE_DIALOG, TutorialDialog, 'tutorialQueueDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.VIDEO_DIALOG, off_pop_ups.TutorialVideoDialog, 'tutorialVideoDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.FINAL_RESULTS_WINDOW, off_pop_ups.TutorialBattleStatisticWindow, 'tutorialBattleStatistic.swf', ViewTypes.WINDOW, 'tBattleStatisticGroup', None, ScopeTemplates.DEFAULT_SCOPE),
 GroupedViewSettings(OFFBATTLE_VIEW_ALIAS.NO_FINAL_RESULTS_WINDOW, off_pop_ups.TutorialBattleNoResultWindow, 'tutorialBattleNoResults.swf', ViewTypes.WINDOW, 'tBattleStatisticGroup', None, ScopeTemplates.DEFAULT_SCOPE))
DIALOG_ALIAS_MAP = {'greeting': OFFBATTLE_VIEW_ALIAS.GREETING_DIALOG,
 'queue': OFFBATTLE_VIEW_ALIAS.QUEUE_DIALOG,
 'video': OFFBATTLE_VIEW_ALIAS.VIDEO_DIALOG}
WINDOW_ALIAS_MAP = {'final': OFFBATTLE_VIEW_ALIAS.FINAL_RESULTS_WINDOW,
 'noResults': OFFBATTLE_VIEW_ALIAS.NO_FINAL_RESULTS_WINDOW}
