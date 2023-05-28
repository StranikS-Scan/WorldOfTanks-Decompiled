# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/edit_view.py
import typing
import SoundGroups
import wg_async as future_async
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from adisp import adisp_process
from constants import AchievementsLayoutStates, Configs
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.achievements.achievements_helper import fillAchievementSectionModel, fillAchievementModel, convertAchievementsToDbIds, convertDbIdsToAchievements
from gui.impl.backport import TooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.achievements.dialogs.edit_confirm_model import DialogType
from gui.impl.gen.view_models.views.lobby.achievements.views.edit_view_model import EditViewModel
from gui.impl.lobby.achievements.dialogs.achievement_edit_confirm import showDialog
from gui.impl.lobby.achievements.profile_utils import isLayoutEnabled, isSummaryEnabled
from gui.impl.lobby.achievements.tooltips.auto_setting_tooltip import AutoSettingTooltip
from gui.impl.lobby.achievements.tooltips.editing_tooltip import EditingTooltip
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from gui.shared.gui_items.processors.achievements import SetAchievementsLayout
from helpers import dependency, server_settings
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
if typing.TYPE_CHECKING:
    from typing import Dict

class EditView(ViewImpl):
    __slots__ = ('__dossier', '__isAutoSelect', '__selectedAchievements', '__achievementBitmask', '__dialogType', '__initialState')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.achievements.EditView())
        settings.flags = ViewFlags.VIEW
        settings.model = EditViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__dossier = None
        self.__isAutoSelect = True
        self.__selectedAchievements = []
        self.__dialogType = None
        self.__initialState = None
        super(EditView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(EditView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(EditView, self).createToolTip(event)

    def getTooltipData(self, event):
        name = event.getArgument('name')
        block = event.getArgument('block')
        return self.__getBackportTooltipData(name, block) if name is not None and block is not None else None

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.achievements.tooltips.EditingTooltip():
            return EditingTooltip(str(event.getArgument('tooltipType')))
        return AutoSettingTooltip(event.getArgument('isSwitchedOn')) if contentID == R.views.lobby.achievements.tooltips.AutoSettingTooltip() else None

    def _getEvents(self):
        return ((self.viewModel.onChangeAutoSelect, self.__onChangeAutoSelect),
         (self.viewModel.onReplaceAchievement, self.__onReplaceAchievement),
         (self.viewModel.onSave, self.__onSave),
         (self.viewModel.onCancel, self.__onCancel),
         (self.viewModel.onExitConfirm, self.__onShowExitConfirm),
         (self.viewModel.onHideFirstEntryState, self.__onHideFirstEntryState),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _onLoading(self, *args, **kwargs):
        achievements20 = self.__itemsCache.items.achievements20
        self.__dossier = self.__itemsCache.items.getAccountDossier()
        self.__initialState = self.__isAutoSelect = achievements20.getLayoutState() == AchievementsLayoutStates.AUTO
        self.__achievementBitmask = achievements20.getAchievementBitmask()
        self.__selectedAchievements = self.__significantAchievements()
        with self.viewModel.transaction() as model:
            self.__fillAchievementsModel(model=model)
            self.__fillFirstEntryState(model=model)
        super(EditView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.__dossier = None
        g_eventBus.handleEvent(events.Achievements20Event(events.Achievements20Event.CLOSE_EDIT_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)
        super(EditView, self)._finalize()
        return

    @replaceNoneKwargsModel
    def __fillAchievementsModel(self, model=None):
        model.setIsAutoSelect(self.__isAutoSelect)
        self.__fillSelectedAchievement()
        self.__fillOtherAchievements(model)

    def __fillOtherAchievements(self, model):
        achievements = self.__dossier.getTotalStats().getAchievements(isInDossier=True, showHidden=False)
        achievementSections = model.getAchievementSections()
        achievementSections.clear()
        selectedAchievements = [ achieve.getName() for achieve in self.__selectedAchievements ]
        for section in achievements:
            section = [ achieve for achieve in section if achieve.getName() not in selectedAchievements ]
            if section:
                achievementSectionModel = fillAchievementSectionModel(section)
                achievementSectionModel.setType(section[0].getSection())
                achievementSections.addViewModel(achievementSectionModel)

        achievementSections.invalidate()

    @replaceNoneKwargsModel
    def __fillFirstEntryState(self, model=None):
        uiStorage = self.__settingsCore.serverSettings.getUIStorage2()
        isVisited = uiStorage.get(UI_STORAGE_KEYS.ACHIEVEMENT_EDIT_VIEW_VISITED)
        model.setIsFirstEntry(not isVisited)

    def __getSignificantAchievementsList(self):
        achievements20GeneralConfig = self.__lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        layoutLength = achievements20GeneralConfig.getLayoutLength()
        mainlRules = achievements20GeneralConfig.getAutoGeneratingMainRules()
        extraRules = achievements20GeneralConfig.getAutoGeneratingExtraRules()
        significantAchievementsList = self.__dossier.getTotalStats().getSignificantAchievements(mainlRules, extraRules, layoutLength)
        return significantAchievementsList

    def __significantAchievements(self):
        if self.__itemsCache.items.achievements20.getLayoutState() == AchievementsLayoutStates.AUTO:
            significantAchievementsList = self.__getSignificantAchievementsList()
        else:
            significantAchievementsList = convertDbIdsToAchievements(self.__itemsCache.items.achievements20.getLayout(), self.__dossier)
        return significantAchievementsList

    def __getBackportTooltipData(self, name, block):
        achievement = self.__dossier.getTotalStats().getAchievement((block, name))
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ACHIEVEMENT, specialArgs=(self.__dossier.getDossierType(),
         dumpDossier(self.__dossier),
         block,
         name,
         isRareAchievement(achievement)))

    @replaceNoneKwargsModel
    def __onChangeAutoSelect(self, model=None):
        if not self.__isAutoSelect:
            significantAchievements = self.__getSignificantAchievementsList()
            if not self.__isIdenticalToSelectedAchievements(significantAchievements):
                self.__selectedAchievements = significantAchievements
                self.__fillSelectedAchievement()
                self.__fillOtherAchievements(model)
                SoundGroups.g_instance.playSound2D('achievements_change_ribbon_autotune_on')
        else:
            self.__achievementBitmask = None
        self.__isAutoSelect = not self.__isAutoSelect
        model.setHasChanges(self.__hasChanges())
        model.setIsAutoSelect(self.__isAutoSelect)
        return

    def __isIdenticalToSelectedAchievements(self, achievements):
        for selectedAchievement, achievement in zip(self.__selectedAchievements, achievements):
            if selectedAchievement.getName() != achievement.getName():
                return False

        return True

    @replaceNoneKwargsModel
    def __onReplaceAchievement(self, args, model=None):
        index = args.get('index')
        name = args.get('name')
        if index is None or name is None:
            return
        else:
            index = int(index)
            self.__isAutoSelect = False
            selectedAchievements = [ achieve.getName() for achieve in self.__selectedAchievements ]
            try:
                idx = selectedAchievements.index(name)
                self.__selectedAchievements[idx], self.__selectedAchievements[index] = self.__selectedAchievements[index], self.__selectedAchievements[idx]
            except ValueError:
                self.__selectedAchievements[index] = self.__getAchievementByName(name)
                self.__fillSelectedAchievement()
                self.__fillOtherAchievements(model)

            model.setIsAutoSelect(self.__isAutoSelect)
            model.setHasChanges(self.__hasChanges())
            self.__fillSelectedAchievement()
            return

    def __hasChanges(self):
        hasChanges = True
        if self.__isAutoSelect:
            hasChanges = self.__isAutoSelect != self.__initialState
        elif self.__isAutoSelect == self.__initialState:
            defaultAchievementsList = convertDbIdsToAchievements(self.__itemsCache.items.achievements20.getLayout(), self.__dossier)
            hasChanges = not self.__isIdenticalToSelectedAchievements(defaultAchievementsList)
        return hasChanges

    def __getAchievementByName(self, name):
        for section in self.__dossier.getTotalStats().getAchievements(isInDossier=True, showHidden=False):
            for achievement in section:
                if achievement.getName() == name:
                    return achievement

    def __fillSelectedAchievement(self):
        with self.viewModel.transaction() as model:
            selectedAchievements = model.getSelectedAchievements()
            selectedAchievements.clear()
            for achievement in self.__selectedAchievements:
                achievementModel = fillAchievementModel(achievement)
                selectedAchievements.addViewModel(achievementModel)

            selectedAchievements.invalidate()

    def __getAchievementsBitmask(self):
        if self.__achievementBitmask is None:
            defaultAchievementsList = self.__getSignificantAchievementsList()
            self.__achievementBitmask = 0
        else:
            defaultAchievementsList = convertDbIdsToAchievements(self.__itemsCache.items.achievements20.getLayout(), self.__dossier)
            if not defaultAchievementsList:
                defaultAchievementsList = self.__getSignificantAchievementsList()
        for idx, achievement in enumerate(self.__selectedAchievements):
            if achievement.getName() != defaultAchievementsList[idx].getName():
                self.__achievementBitmask |= 1 << idx

        return self.__achievementBitmask

    @adisp_process
    def __onSave(self):
        achievementsLayout = []
        achievementsLayout.append(AchievementsLayoutStates.AUTO.value if self.__isAutoSelect else AchievementsLayoutStates.MANUAL.value)
        achievementsLayout.append(self.__getAchievementsBitmask())
        if not self.__isAutoSelect:
            achievementsIdx = convertAchievementsToDbIds(self.__selectedAchievements)
            achievementsLayout.extend(achievementsIdx)
        result = yield SetAchievementsLayout(achievementsLayout).request()
        if result.success:
            self.destroyWindow()
            g_eventBus.handleEvent(events.Achievements20Event(events.Achievements20Event.LAYOUT_CHANGED), scope=EVENT_BUS_SCOPE.LOBBY)

    @replaceNoneKwargsModel
    def __onCancel(self, model=None):
        self.__isAutoSelect = self.__itemsCache.items.achievements20.getLayoutState() == AchievementsLayoutStates.AUTO
        self.__selectedAchievements = self.__getSignificantAchievementsList()
        self.__selectedAchievements = self.__significantAchievements()
        model.setIsAutoSelect(self.__isAutoSelect)
        model.setHasChanges(False)
        self.__fillSelectedAchievement()
        self.__fillOtherAchievements(model)

    @nextTick
    @future_async.wg_async
    def __onShowExitConfirm(self):
        self.__dialogType = self.__getConfirmDialogType()
        result = yield future_async.wg_await(showDialog(dialogType=self.__dialogType, parent=self.getParentWindow()))
        isOK, data = result.result
        isCancel = data.get('isUserCancelAction', False)
        if self.__dialogType == DialogType.ERROR or isCancel:
            self.destroyWindow()
        elif isOK:
            self.__onSave()
        self.__dialogType = None
        return

    def __getConfirmDialogType(self):
        if not isLayoutEnabled() or not isSummaryEnabled():
            return DialogType.ERROR
        return DialogType.AUTO_SELECT_ENABLED if self.__isAutoSelect else DialogType.AUTO_SELECT_DISABLED

    @server_settings.serverSettingsChangeListener(Configs.ACHIEVEMENTS20_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        if not isLayoutEnabled() or not isSummaryEnabled():
            if self.__dialogType is None:
                self.__onShowExitConfirm()
            else:
                self.__dialogType = DialogType.ERROR
        return

    def __onHideFirstEntryState(self):
        self.__settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.ACHIEVEMENT_EDIT_VIEW_VISITED: True})
        self.viewModel.setIsFirstEntry(False)


class EditWindow(LobbyWindow):

    def __init__(self, parent=None, *args, **kwargs):
        super(EditWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=EditView(*args, **kwargs), parent=parent, layer=WindowLayer.WINDOW)
