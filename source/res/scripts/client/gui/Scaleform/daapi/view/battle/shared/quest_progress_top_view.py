# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/quest_progress_top_view.py
from account_helpers.settings_core.options import QuestsProgressViewType, QuestsProgressDisplayType
from account_helpers.settings_core.settings_constants import QUESTS_PROGRESS
from gui.Scaleform.daapi.view.meta.QuestProgressTopViewMeta import QuestProgressTopViewMeta
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
import SoundGroups

class QuestProgressTopView(QuestProgressTopViewMeta):
    settingsCore = dependency.descriptor(ISettingsCore)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(QuestProgressTopView, self).__init__()
        progressViewType = self.settingsCore.getSetting(QUESTS_PROGRESS.VIEW_TYPE)
        progressDsiplayType = self.settingsCore.getSetting(QUESTS_PROGRESS.DISPLAY_TYPE)
        self.__isProgressAvailable = False
        self.__isProgressEnabled = progressViewType == QuestsProgressViewType.TYPE_STANDARD
        self.__isFlagVisible = progressDsiplayType == QuestsProgressDisplayType.SHOW_ALL

    def onPlaySound(self, soundType):
        SoundGroups.g_instance.playSound2D(soundType)

    def _populate(self):
        super(QuestProgressTopView, self)._populate()
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        qProgressCtrl = self.sessionProvider.shared.questProgress
        if qProgressCtrl is not None:
            qProgressCtrl.onFullConditionsUpdate += self.__onFullConditionsUpdate
            qProgressCtrl.onQuestProgressInited += self.__onFullConditionsUpdate
            if qProgressCtrl.isInited():
                quest = qProgressCtrl.getSelectedQuest()
                if quest and quest.hasBattleProgress():
                    self.__isProgressAvailable = True
                self.__setVisibility()
        return

    def _dispose(self):
        super(QuestProgressTopView, self)._dispose()
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        qProgressCtrl = self.sessionProvider.shared.questProgress
        if qProgressCtrl is not None:
            qProgressCtrl.onFullConditionsUpdate -= self.__onFullConditionsUpdate
            qProgressCtrl.onQuestProgressInited -= self.__onFullConditionsUpdate
        return

    def __onSettingsChange(self, diff):
        if QUESTS_PROGRESS.VIEW_TYPE in diff:
            progressViewType = self.settingsCore.getSetting(QUESTS_PROGRESS.VIEW_TYPE)
            self.__isProgressEnabled = progressViewType == QuestsProgressViewType.TYPE_STANDARD
            self.as_setVisibleS(self.__isProgressEnabled)
        if QUESTS_PROGRESS.DISPLAY_TYPE in diff:
            progressDsiplayType = self.settingsCore.getSetting(QUESTS_PROGRESS.DISPLAY_TYPE)
            self.__isFlagVisible = progressDsiplayType == QuestsProgressDisplayType.SHOW_ALL
            self.as_setFlagVisibleS(self.__isFlagVisible)

    def __onFullConditionsUpdate(self, *args):
        quest = self.sessionProvider.shared.questProgress.getSelectedQuest()
        self.__isProgressAvailable = quest and quest.hasBattleProgress()
        self.__setVisibility()

    def __setVisibility(self):
        self.as_setVisibleS(self.__isProgressEnabled and self.__isProgressAvailable)
        self.as_setFlagVisibleS(self.__isFlagVisible and self.__isProgressAvailable)
