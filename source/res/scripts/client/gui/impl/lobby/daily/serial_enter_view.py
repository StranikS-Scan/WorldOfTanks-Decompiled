# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/serial_enter_view.py
from account_helpers.AccountSettings import AccountSettings, SESSION_PROGRESS_REWARDS_LAST_SEEN_STEP
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gui_decorators import args2params
from helpers import dependency
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.serial_enter_view_model import SerialEnterViewModel
from gui.impl.gen.view_models.views.lobby.daily.serial_enter_day_model import SerialEnterDayModel, DayState
from gui.impl.lobby.daily import DailyTabs
from gui.impl.lobby.daily.daily_quests_subview import DailyQuestsSubviewBase
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.session_progress_rewards.session_progress_rewards_bonus_packers import getSessionProgressRewardsBonusPacker
from gui.shared.event_dispatcher import selectVehicleInHangar, showVehiclePreview
from gui.shared.formatters import text_styles
from gui.server_events.events_dispatcher import showDailyQuests
from skeletons.gui.game_control import ISessionProgressRewardsController
from skeletons.gui.shared import IItemsCache

class SerialEnterView(DailyQuestsSubviewBase):
    LAYOUT_ID = R.views.lobby.daily.SerialEnterView()
    __sessionProgressRewardsController = dependency.descriptor(ISessionProgressRewardsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData',)

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.LAYOUT_ID, ViewFlags.VIEW, SerialEnterViewModel())
        super(SerialEnterView, self).__init__(settings)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(SerialEnterView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SerialEnterView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            tooltipIds = [ tooltipId for tooltipId in event.getArgument('tooltipIds', '').split(',') if tooltipId ]
            if not tooltipIds:
                return None
            bonusesByTooltipId = {}
            for day in self.viewModel.getDays():
                for bonus in day.getBonuses():
                    bonusTooltipId = bonus.getTooltipId()
                    if bonusTooltipId in tooltipIds:
                        bonusesByTooltipId[bonusTooltipId] = bonus

            bonuses = [ bonusesByTooltipId[tooltipId] for tooltipId in tooltipIds if tooltipId in bonusesByTooltipId ]
            if bonuses:
                return AdditionalRewardsTooltip(bonuses)
            return None
        else:
            return super(SerialEnterView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _update(self):
        rewardsCalendar = self.__sessionProgressRewardsController.rewardsCalendar
        finalRewardsIndex = len(rewardsCalendar) - 1
        currentStep = self.__sessionProgressRewardsController.currentStep
        isRewardWasReceivedToday = self.__sessionProgressRewardsController.isRewardWasReceivedToday
        lastSeenStep = AccountSettings.getSettings(SESSION_PROGRESS_REWARDS_LAST_SEEN_STEP)
        with self.viewModel.transaction() as tx:
            tx.setIsEnabled(self.__sessionProgressRewardsController.isEnabled)
            daysArray = tx.getDays()
            daysArray.clear()
            for index, (step, stepRewards) in enumerate(rewardsCalendar):
                dayModel = SerialEnterDayModel()
                dayModel.setDay(step + 1)
                dayModel.setState(self.__getState(step, currentStep, lastSeenStep, isRewardWasReceivedToday))
                dayModel.setIsFinal(index == finalRewardsIndex)
                packBonusModelAndTooltipData(stepRewards, dayModel.getBonuses(), self.__tooltipData, getSessionProgressRewardsBonusPacker())
                daysArray.addViewModel(dayModel)

            daysArray.invalidate()
        AccountSettings.setSettings(SESSION_PROGRESS_REWARDS_LAST_SEEN_STEP, currentStep)

    def _getEvents(self):
        return ((self.viewModel.onPreviewVehicle, self.__onPreviewVehicle), (self.__sessionProgressRewardsController.onDataUpdated, self.__onDataUpdated))

    def __getState(self, step, currentStep, lastSeenStep, isRewardWasReceivedToday):
        todayStep = currentStep - 1 if isRewardWasReceivedToday else currentStep
        if step < todayStep:
            return DayState.COMPLETED
        if step == todayStep:
            if not isRewardWasReceivedToday:
                return DayState.NEEDRELOGIN
            if lastSeenStep == currentStep:
                return DayState.TODAY
            return DayState.CURRENT
        return DayState.DISABLED

    @args2params(str)
    def __onPreviewVehicle(self, tooltipId):
        tooltipData = self.__tooltipData.get(tooltipId)
        if tooltipData is None:
            return
        else:
            specialArgs = getattr(tooltipData, 'specialArgs', None)
            if not specialArgs:
                return
            vehicleCD = int(specialArgs[0])
            vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
            if vehicle.isInInventory:
                selectVehicleInHangar(vehicle.intCD)
            else:
                showVehiclePreview(vehicle.intCD, previewBackCb=lambda : showDailyQuests(subTab=DailyTabs.SERIAL), bottomPanelTextData={'uniqueVehicleTitle': text_styles.tutorial(backport.text(R.strings.vehicle_preview.buyingPanel.uniqueVehicleLabel.sessionProgressRewards())),
                 'hideBuyBlock': True}, backBtnLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.sessionProgressRewards()), showCloseBtn=False, disableHints=True)
            return

    def __onDataUpdated(self):
        self._update()
