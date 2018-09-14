# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReferralManagementWindow.py
from operator import methodcaller
import pickle
import itertools
import BigWorld
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_WARNING
from gui import game_control, SystemMessages
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.ReferralManagementWindowMeta import ReferralManagementWindowMeta
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.prb_control.context import prb_ctx, SendInvitesCtx
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared.utils import findFirst
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import i18n, time_utils
from gui.shared.events import OpenLinkEvent
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from messenger.m_constants import USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

class ReferralManagementWindow(View, AbstractWindowView, ReferralManagementWindowMeta, AppRef, GlobalListener, Notifiable):
    MIN_REF_NUMBER = 4
    TOTAL_QUESTS = 6
    BONUSES_PRIORITY = ('vehicles', 'tankmen', 'credits')

    @storage_getter('users')
    def usersStorage(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def onInvitesManagementLinkClick(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.INVIETES_MANAGEMENT))

    def inviteIntoSquad(self, referralID):
        self.__inviteOrCreateSquad(referralID)

    def onPlayerAdded(self, functional, playerInfo):
        self.__makeTableData()

    def onPlayerRemoved(self, functional, playerInfo):
        self.__makeTableData()

    def _populate(self):
        super(ReferralManagementWindow, self)._populate()
        self.startGlobalListening()
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived += self.__onUserRosterChanged
        g_messengerEvents.users.onUsersListReceived += self.__onUsersListReceived
        g_messengerEvents.users.onClanMembersListChanged += self.__onClanMembersListChanged
        refSystem = game_control.g_instance.refSystem
        refSystem.onUpdated += self.__onRefSystemUpdated
        refSystem.onQuestsUpdated += self.__onRefSystemQuestsUpdated
        self.addNotificator(PeriodicNotifier(self.__getClosestNotification, self.__update, (time_utils.ONE_MINUTE,)))
        self.startNotification()
        self.__update()

    def _dispose(self):
        self.clearNotification()
        refSystem = game_control.g_instance.refSystem
        refSystem.onUpdated -= self.__onRefSystemUpdated
        refSystem.onQuestsUpdated -= self.__onRefSystemQuestsUpdated
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived -= self.__onUserRosterChanged
        g_messengerEvents.users.onUsersListReceived -= self.__onUsersListReceived
        g_messengerEvents.users.onClanMembersListChanged -= self.__onClanMembersListChanged
        self.stopGlobalListening()
        super(ReferralManagementWindow, self)._dispose()

    @classmethod
    def __getClosestNotification(cls):
        updates = map(lambda r: r.getBonus()[1], game_control.g_instance.refSystem.getReferrals())
        if len(updates):
            return min(updates)
        return 0

    def __update(self):
        self.__makeData()
        self.__makeTableData()
        self.__makeProgresData()

    def __makeData(self):
        ms = i18n.makeString
        refSystem = game_control.g_instance.refSystem
        invitedPlayers = len(refSystem.getReferrals())
        infoIcon = self.app.utilsManager.textManager.getIcon(TextIcons.INFO_ICON)
        multiplyExpText = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_EXPMULTIPLIER))
        tableExpText = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_EXP))
        data = {'windowTitle': ms(MENU.REFERRALMANAGEMENTWINDOW_TITLE),
         'infoHeaderText': ms(MENU.REFERRALMANAGEMENTWINDOW_INFOHEADER_HAVENOTTANK) if not refSystem.isTotallyCompleted() else ms(MENU.REFERRALMANAGEMENTWINDOW_INFOHEADER_HAVETANK),
         'descriptionText': ms(MENU.REFERRALMANAGEMENTWINDOW_DESCRIPTION),
         'invitedPlayersText': ms(MENU.REFERRALMANAGEMENTWINDOW_INVITEDPLAYERS, playersNumber=invitedPlayers),
         'invitesManagementLinkText': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(MENU.REFERRALMANAGEMENTWINDOW_INVITEMANAGEMENTLINK)),
         'closeBtnLabel': ms(MENU.REFERRALMANAGEMENTWINDOW_CLOSEBTNLABEL),
         'tableNickText': ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_NICK),
         'tableExpText': ms(tableExpText + ' ' + infoIcon),
         'tableExpTT': TOOLTIPS.REFERRALMANAGEMENTWINDOW_TABLE_EXPERIENCE,
         'tableExpMultiplierText': ms(multiplyExpText + ' ' + infoIcon)}
        self.as_setDataS(data)

    def __makeTableData(self):
        ms = i18n.makeString
        result = []
        refSystem = game_control.g_instance.refSystem
        referrals = refSystem.getReferrals()
        numOfReferrals = len(referrals)
        for i, item in enumerate(referrals):
            referralNumber = self.app.utilsManager.textManager.getText(TextType.STATS_TEXT, ms('%d.' % (i + 1)))
            dbID = item.getAccountDBID()
            user = self.usersStorage.getUser(dbID)
            if not user:
                raise AssertionError('User must be defined')
                isOnline = user.isOnline()
                xpIcon = RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON
                icon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(xpIcon, 16, 16, -3, 0))
                bonus, timeLeft = item.getBonus()
                if bonus == 1:
                    multiplier = '-'
                    multiplierTooltip = TOOLTIPS.REFERRALMANAGEMENTWINDOW_MULTIPLIER_X1
                    icon = ''
                else:
                    multiplier = 'x%s' % BigWorld.wg_getNiceNumberFormat(bonus)
                    multiplierTooltip = ''
                if timeLeft:
                    multiplierTime = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(item.getBonusTimeLeftStr()))
                    expMultiplierText = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_LEFTTIME, time=multiplierTime))
                else:
                    expMultiplierText = ''
                multiplierFactor = self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, multiplier)
                multiplierStr = ms(icon + '<nobr>' + multiplierFactor + ' ' + expMultiplierText)
                referralData = {'accID': dbID,
                 'fullName': user.getFullName(),
                 'userName': user.getName(),
                 'clanAbbrev': user.getClanAbbrev()}
                canInviteToSquad = self.prbFunctional.getPrbType() == PREBATTLE_TYPE.NONE or self.prbFunctional.getPrbType() == PREBATTLE_TYPE.SQUAD and self.prbFunctional.getPermissions().canSendInvite()
                btnEnabled = canInviteToSquad or False
                btnTooltip = TOOLTIPS.REFERRALMANAGEMENTWINDOW_CREATESQUADBTN_DISABLED_SQUADISFULL
            else:
                btnEnabled = True
                btnTooltip = TOOLTIPS.REFERRALMANAGEMENTWINDOW_CREATESQUADBTN_ENABLED
            result.append({'isEmpty': False,
             'isOnline': isOnline,
             'referralNo': referralNumber,
             'referralVO': referralData,
             'exp': BigWorld.wg_getNiceNumberFormat(item.getXPPool()),
             'multiplier': multiplierStr,
             'multiplierTooltip': multiplierTooltip,
             'btnEnabled': btnEnabled,
             'btnTooltip': btnTooltip})

        if numOfReferrals < self.MIN_REF_NUMBER:
            for i in xrange(numOfReferrals, self.MIN_REF_NUMBER):
                referralNumber = self.app.utilsManager.textManager.getText(TextType.DISABLE_TEXT, ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_EMPTYLINE, lineNo=str(i + 1)))
                result.append({'isEmpty': True,
                 'referralNo': referralNumber})

        self.as_setTableDataS(result)

    def __makeProgresData(self):
        refSystem = game_control.g_instance.refSystem
        totalXP = refSystem.getTotalXP()
        currentXP = refSystem.getReferralsXPPool()
        progressText = '%(currentXP)s / %(totalXP)s %(icon)s' % {'currentXP': self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, BigWorld.wg_getIntegralFormat(currentXP)),
         'totalXP': BigWorld.wg_getIntegralFormat(totalXP),
         'icon': self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON, 16, 16, -3, 0))}
        text = i18n.makeString(MENU.REFERRALMANAGEMENTWINDOW_PROGRESSINDICATOR_PROGRESS, progress=progressText)
        data = {'isCompleted': refSystem.isTotallyCompleted(),
         'text': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, text)}
        if refSystem.isTotallyCompleted():
            completedText = i18n.makeString(MENU.REFERRALMANAGEMENTWINDOW_PROGRESSINDICATOR_COMPLETE)
            completedText = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, completedText)
            data['completedText'] = completedText
            _, lastStepQuests = refSystem.getQuests()[-1]
            vehicleBonus = findFirst(lambda q: q.getBonuses('vehicles'), reversed(lastStepQuests))
            vehicleBonusIcon = ''
            if vehicleBonus is not None:
                vehicleBonusIcon = vehicleBonus.getBonuses('vehicles')[0].getTooltipIcon()
            data['completedImage'] = vehicleBonusIcon
        else:
            stepsData = []
            progress = 0.0
            isProgressAvailable = True
            progressAlertText = ''
            quests = refSystem.getQuests()
            totalQuestsCount = len(tuple(itertools.chain(*dict(quests).values())))
            if quests and totalQuestsCount == self.TOTAL_QUESTS:
                currentCompletedStep = -1
                totalSteps = len(quests)
                lastStep = totalSteps - 1
                for i, (xp, events) in enumerate(quests):
                    notCompleted = filter(lambda q: not q.isCompleted(), reversed(events))
                    lastNotCompleted = findFirst(None, notCompleted)
                    if lastNotCompleted is not None:
                        questIDs = map(methodcaller('getID'), notCompleted)
                        icon = self.__getBonusIcon(lastNotCompleted)
                    else:
                        questIDs = map(methodcaller('getID'), events)
                        icon = RES_ICONS.MAPS_ICONS_LIBRARY_COMPLETE
                        currentCompletedStep = i
                    stepsData.append({'id': pickle.dumps((xp, questIDs)),
                     'icon': icon})

                nextStep = min(currentCompletedStep + 1, lastStep)
                nextStepXP, _ = quests[nextStep]
                if currentXP:
                    totalProgress = 0.0
                    currentCompletedStepXP = 0
                    oneStepWeight = 1.0 / totalSteps
                    if currentCompletedStep != -1:
                        currentCompletedStepXP, _ = quests[currentCompletedStep]
                        totalProgress = (currentCompletedStep + 1) * oneStepWeight
                    xpForNextStep = nextStepXP - currentCompletedStepXP
                    xpFromPrevStep = currentXP - currentCompletedStepXP
                    stepProgress = float(xpFromPrevStep) / xpForNextStep
                    totalStepProgress = stepProgress * oneStepWeight
                    progress = totalProgress + totalStepProgress
            else:
                LOG_WARNING('Referral quests is in invalid state: ', quests)
                isProgressAvailable = False
                progressAlertIcon = self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON)
                progressAlertText = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, i18n.makeString(MENU.REFERRALMANAGEMENTWINDOW_PROGRESSNOTAVAILABLE))
                progressAlertText = i18n.makeString(progressAlertIcon + ' ' + progressAlertText)
            data.update({'steps': stepsData,
             'progress': progress,
             'isProgressAvailable': isProgressAvailable,
             'progressAlertText': progressAlertText})
        self.as_setProgressDataS(data)
        return

    def __getBonusIcon(self, event):
        for bonusName in self.BONUSES_PRIORITY:
            bonuses = event.getBonuses(bonusName)
            if bonuses:
                return bonuses[0].getIcon()

        return ''

    @process
    def __inviteOrCreateSquad(self, referralID):
        if self.prbFunctional.getPrbType() == PREBATTLE_TYPE.NONE or self.prbFunctional.getPrbType() == PREBATTLE_TYPE.SQUAD and self.prbFunctional.getPermissions().canSendInvite():
            user = self.usersStorage.getUser(referralID)
            if self.prbFunctional.getPrbType() == PREBATTLE_TYPE.NONE:
                result = yield self.prbDispatcher.create(prb_ctx.SquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=[referralID], isForced=True))
            else:
                result = yield self.prbDispatcher.sendPrbRequest(SendInvitesCtx([referralID], ''))
            if result:
                self.__showInviteMessage(user)

    def __showInviteMessage(cls, user):
        if user:
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite/name', type=SystemMessages.SM_TYPE.Information, name=user.getFullName())
        else:
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite', type=SystemMessages.SM_TYPE.Information)

    def __onUserStatusUpdated(self, *args):
        self.__makeTableData()

    def __onClanMembersListChanged(self, *args):
        self.__makeTableData()

    def __onUsersListReceived(self, tags):
        if USER_TAG.FRIEND in tags:
            self.__makeTableData()

    def __onUserRosterChanged(self, *args):
        self.__makeTableData()

    def __onRefSystemUpdated(self):
        self.startNotification()
        self.__update()

    def __onRefSystemQuestsUpdated(self):
        self.__update()
