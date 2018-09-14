# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReferralManagementWindow.py
import itertools
import pickle
from adisp import process
from operator import methodcaller
import BigWorld
from constants import PREBATTLE_TYPE
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.meta.ReferralManagementWindowMeta import ReferralManagementWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers import i18n, time_utils
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter
from shared_utils import findFirst
from gui.shared.events import OpenLinkEvent
from gui.shared.formatters import icons, text_styles
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from messenger.m_constants import USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from shared_utils import findFirst
from gui.shared.utils.functions import showSentInviteMessage
from skeletons.gui.game_control import IRefSystemController

class ReferralManagementWindow(ReferralManagementWindowMeta, IGlobalListener, Notifiable):
    MIN_REF_NUMBER = 4
    TOTAL_QUESTS = 6
    BONUSES_PRIORITY = ('vehicles', 'tankmen', 'credits')
    refSystem = dependency.descriptor(IRefSystemController)

    @storage_getter('users')
    def usersStorage(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def onInvitesManagementLinkClick(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.INVIETES_MANAGEMENT))

    def inviteIntoSquad(self, referralID):
        self.__inviteOrCreateSquad(referralID)

    def onPlayerAdded(self, entity, playerInfo):
        self.__makeTableData()

    def onPlayerRemoved(self, entity, playerInfo):
        self.__makeTableData()

    def _populate(self):
        super(ReferralManagementWindow, self)._populate()
        self.startGlobalListening()
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived += self.__onUserRosterChanged
        g_messengerEvents.users.onUsersListReceived += self.__onUsersListReceived
        g_messengerEvents.users.onClanMembersListChanged += self.__onClanMembersListChanged
        self.refSystem.onUpdated += self.__onRefSystemUpdated
        self.refSystem.onQuestsUpdated += self.__onRefSystemQuestsUpdated
        self.addNotificator(PeriodicNotifier(self.__getClosestNotification, self.__update, (time_utils.ONE_MINUTE,)))
        self.startNotification()
        self.__update()

    def _dispose(self):
        self.clearNotification()
        self.refSystem.onUpdated -= self.__onRefSystemUpdated
        self.refSystem.onQuestsUpdated -= self.__onRefSystemQuestsUpdated
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived -= self.__onUserRosterChanged
        g_messengerEvents.users.onUsersListReceived -= self.__onUsersListReceived
        g_messengerEvents.users.onClanMembersListChanged -= self.__onClanMembersListChanged
        self.stopGlobalListening()
        super(ReferralManagementWindow, self)._dispose()

    @classmethod
    def __getClosestNotification(cls):
        updates = map(lambda r: r.getBonus()[1], cls.refSystem.getReferrals())
        return min(updates) if len(updates) else 0

    def __update(self):
        self.__makeData()
        self.__makeTableData()
        self.__makeProgresData()

    def __makeData(self):
        ms = i18n.makeString
        invitedPlayers = len(self.refSystem.getReferrals())
        data = {'windowTitle': ms(MENU.REFERRALMANAGEMENTWINDOW_TITLE),
         'infoHeaderText': ms(MENU.REFERRALMANAGEMENTWINDOW_INFOHEADER_HAVENOTTANK) if not self.refSystem.isTotallyCompleted() else ms(MENU.REFERRALMANAGEMENTWINDOW_INFOHEADER_HAVETANK),
         'descriptionText': ms(MENU.REFERRALMANAGEMENTWINDOW_DESCRIPTION),
         'invitedPlayersText': ms(MENU.REFERRALMANAGEMENTWINDOW_INVITEDPLAYERS, playersNumber=invitedPlayers),
         'invitesManagementLinkText': text_styles.main(ms(MENU.REFERRALMANAGEMENTWINDOW_INVITEMANAGEMENTLINK)),
         'closeBtnLabel': ms(MENU.REFERRALMANAGEMENTWINDOW_CLOSEBTNLABEL),
         'tableHeader': self.__makeTableHeader()}
        self.as_setDataS(data)

    def __makeTableHeader(self):
        ms = i18n.makeString
        infoIcon = icons.info()
        multiplyExpText = text_styles.standard(ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_EXPMULTIPLIER))
        tableExpText = text_styles.standard(ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_EXP))
        return (self.__makeSortingButton(ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_NICK), 146, TEXT_ALIGN.LEFT),
         self.__makeSortingButton(ms(tableExpText + ' ' + infoIcon), 143, TEXT_ALIGN.RIGHT, toolTip=TOOLTIPS.REFERRALMANAGEMENTWINDOW_TABLE_EXPERIENCE),
         self.__makeSortingButton(ms(multiplyExpText + ' ' + infoIcon), 193, TEXT_ALIGN.CENTER, toolTipSpecial='refSysXPMultiplier'),
         self.__makeSortingButton('', 166, TEXT_ALIGN.CENTER))

    def __makeSortingButton(self, label, buttonWidth, textAlign, toolTip='', toolTipSpecial=''):
        return {'label': label,
         'buttonWidth': buttonWidth,
         'sortOrder': 0,
         'textAlign': textAlign,
         'toolTip': toolTip,
         'toolTipSpecialType': toolTipSpecial}

    def __makeTableData(self):
        ms = i18n.makeString
        result = []
        referrals = self.refSystem.getReferrals()
        numOfReferrals = len(referrals)
        for i, item in enumerate(referrals):
            referralNumber = text_styles.stats(ms('%d.' % (i + 1)))
            dbID = item.getAccountDBID()
            user = self.usersStorage.getUser(dbID)
            assert user, 'User must be defined'
            contactConverter = ContactConverter()
            contactData = contactConverter.makeVO(user)
            xpIcon = RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON
            icon = icons.makeImageTag(xpIcon, 16, 16, -3, 0)
            bonus, timeLeft = item.getBonus()
            if bonus == 1:
                multiplier = '-'
                multiplierTooltip = TOOLTIPS.REFERRALMANAGEMENTWINDOW_MULTIPLIER_X1
                icon = ''
            else:
                multiplier = 'x%s' % BigWorld.wg_getNiceNumberFormat(bonus)
                multiplierTooltip = ''
            if timeLeft:
                multiplierTime = text_styles.main(ms(item.getBonusTimeLeftStr()))
                expMultiplierText = text_styles.standard(ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_LEFTTIME, time=multiplierTime))
            else:
                expMultiplierText = ''
            multiplierFactor = text_styles.credits(multiplier)
            multiplierStr = ms(icon + '<nobr>' + multiplierFactor + ' ' + expMultiplierText)
            referralData = {'accID': dbID,
             'fullName': user.getFullName(),
             'userName': user.getName(),
             'clanAbbrev': user.getClanAbbrev()}
            permissions = self.prbEntity.getPermissions()
            canInviteToSquad = permissions.canCreateSquad() or self.prbEntity.getEntityType() == PREBATTLE_TYPE.SQUAD and permissions.canSendInvite()
            if not canInviteToSquad:
                btnEnabled = False
                btnTooltip = TOOLTIPS.REFERRALMANAGEMENTWINDOW_CREATESQUADBTN_DISABLED_SQUADISFULL
            else:
                btnEnabled = True
                btnTooltip = TOOLTIPS.REFERRALMANAGEMENTWINDOW_CREATESQUADBTN_ENABLED
            result.append({'isEmpty': False,
             'contactData': contactData,
             'referralNo': referralNumber,
             'referralVO': referralData,
             'exp': BigWorld.wg_getNiceNumberFormat(item.getXPPool()),
             'multiplier': multiplierStr,
             'multiplierTooltip': multiplierTooltip,
             'btnEnabled': btnEnabled,
             'btnTooltip': btnTooltip})

        if numOfReferrals < self.MIN_REF_NUMBER:
            for i in xrange(numOfReferrals, self.MIN_REF_NUMBER):
                referralNumber = text_styles.disabled(ms(MENU.REFERRALMANAGEMENTWINDOW_REFERRALSTABLE_EMPTYLINE, lineNo=str(i + 1)))
                result.append({'isEmpty': True,
                 'referralNo': referralNumber})

        self.as_setTableDataS(result)

    def __makeProgresData(self):
        totalXP = self.refSystem.getTotalXP()
        currentXP = self.refSystem.getReferralsXPPool()
        progressText = '%(currentXP)s / %(totalXP)s %(icon)s' % {'currentXP': text_styles.credits(BigWorld.wg_getIntegralFormat(currentXP)),
         'totalXP': BigWorld.wg_getIntegralFormat(totalXP),
         'icon': icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON, 16, 16, -3, 0)}
        text = i18n.makeString(MENU.REFERRALMANAGEMENTWINDOW_PROGRESSINDICATOR_PROGRESS, progress=progressText)
        awardData = {}
        progresData = {'text': text_styles.main(text)}
        progressAlertText = ''
        if self.refSystem.isTotallyCompleted():
            completedText = i18n.makeString(MENU.REFERRALMANAGEMENTWINDOW_PROGRESSINDICATOR_COMPLETE)
            completedText = text_styles.middleTitle(completedText)
            awardData['completedText'] = completedText
            _, lastStepQuests = self.refSystem.getQuests()[-1]
            vehicleBonus = findFirst(lambda q: q.getBonuses('vehicles'), reversed(lastStepQuests))
            vehicleBonusIcon = ''
            if vehicleBonus is not None:
                vehicleBonusIcon = vehicleBonus.getBonuses('vehicles')[0].getTooltipIcon()
            awardData['completedImage'] = vehicleBonusIcon
        else:
            stepsData = []
            progress = 0.0
            quests = self.refSystem.getQuests()
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
                    stepProgress = float(xpFromPrevStep) / xpForNextStep if xpFromPrevStep else 0.0
                    totalStepProgress = stepProgress * oneStepWeight
                    progress = totalProgress + totalStepProgress
            else:
                LOG_WARNING('Referral quests is in invalid state: ', quests)
                progressAlertIcon = icons.alert()
                progressAlertText = text_styles.alert(i18n.makeString(MENU.REFERRALMANAGEMENTWINDOW_PROGRESSNOTAVAILABLE))
                progressAlertText = i18n.makeString(progressAlertIcon + ' ' + progressAlertText)
            progresData.update({'steps': stepsData,
             'progress': progress})
        if progressAlertText != '':
            self.as_showAlertS(progressAlertText)
        elif self.refSystem.isTotallyCompleted():
            self.as_setAwardDataDataS(awardData)
        else:
            self.as_setProgressDataS(progresData)
        return

    def __getBonusIcon(self, event):
        for bonusName in self.BONUSES_PRIORITY:
            bonuses = event.getBonuses(bonusName)
            if bonuses:
                return bonuses[0].getIcon()

    @process
    def __inviteOrCreateSquad(self, referralID):
        """ Send invite to the target player if squad is already exist or
        make the new one with invitation
        """
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.SQUAD, accountsToInvite=(referralID,)))

    def __showInviteMessage(cls, user):
        showSentInviteMessage(user)

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
