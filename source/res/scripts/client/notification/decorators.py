# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/decorators.py
import typing
from copy import deepcopy
import BigWorld
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.INVITES import INVITES
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.clans.formatters import ClanSingleNotificationHtmlTextFormatter, ClanMultiNotificationsHtmlTextFormatter, ClanAppActionHtmlTextFormatter
from gui.clans.settings import CLAN_APPLICATION_STATES, CLAN_INVITE_STATES
from gui.customization.shared import isVehicleCanBeCustomized
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbInvitesProperty
from gui.prb_control.formatters.invites import getPrbInviteHtmlFormatter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType, HangarSpacesSwitcherEvent
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.notifications import NotificationPriorityLevel, NotificationGuiSettings, NotificationGroup
from gui.shared.utils.functions import makeTooltip
from gui.wgnc.settings import WGNC_DEFAULT_ICON, WGNC_POP_UP_BUTTON_WIDTH
from helpers import dependency
from helpers import i18n, int2roman
from helpers import time_utils
from messenger import g_settings
from messenger.formatters.users_messages import makeFriendshipRequestText
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from notification.settings import makePathToIcon
from skeletons.gui.game_control import IBattlePassController, IMapboxController, IResourceWellController, IFunRandomController, ICNLootBoxesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from gui.shared.events import LoadViewEvent

def _makeShowTime():
    return BigWorld.time()


_ICONS_FIELDS = ('icon', 'defaultIcon', 'bgIcon')

def _getClanName(clanInfo):
    return '[{}] {}'.format(clanInfo[1], clanInfo[0])


@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def _getDisabledFunRandomTooltip(tooltipStr, funRandomCtrl=None):
    availableLevels = funRandomCtrl.getModeSettings().levels
    minLevel, maxLevel = min(availableLevels), max(availableLevels)
    levels = int2roman(minLevel) if minLevel == maxLevel else toRomanRangeString(availableLevels)
    return backport.text(tooltipStr, levels=levels)


class _NotificationDecorator(object):
    __slots__ = ('_entityID', '_entity', '_settings', '_vo', '_isOrderChanged')

    def __init__(self, entityID, entity=None, settings=None):
        super(_NotificationDecorator, self).__init__()
        self._isOrderChanged = False
        self._entityID = entityID
        self._entity = entity
        self._make(entity, settings)

    def __repr__(self):
        return '{0:>s}(typeID = {1:n}, entityID = {2:n})'.format(self.__class__.__name__, self.getType(), self.getID())

    def __cmp__(self, other):
        return cmp(self.getOrder(), other.getOrder())

    def __eq__(self, other):
        return self.getType() == other.getType() and self.getID() == other.getID()

    def clear(self):
        self._entityID = 0
        self._entity = None
        self._vo.clear()
        self._settings = None
        return

    def getID(self):
        return self._entityID

    def getEntity(self):
        return self._entity

    def getSavedData(self):
        return None

    def getType(self):
        return NOTIFICATION_TYPE.UNDEFINED

    @staticmethod
    def isPinned():
        return False

    def getGroup(self):
        return NotificationGroup.INFO

    def getSettings(self):
        return self._settings

    def getPriorityLevel(self):
        result = NotificationPriorityLevel.MEDIUM
        if self._settings:
            result = self._settings.priorityLevel
        return result

    def isAlert(self):
        result = False
        if self._settings:
            result = self._settings.isAlert
        return result

    def isNotify(self):
        result = False
        if self._settings:
            result = self._settings.isNotify
        return result

    def showAt(self):
        if self._settings:
            result = self._settings.showAt
        else:
            result = _makeShowTime()
        return result

    def isOrderChanged(self):
        return self._isOrderChanged

    def update(self, entity):
        self._entity = entity

    def getVisibilityTime(self):
        return None

    def getListVO(self, newId=None):
        vo = self._vo.copy()
        if newId is not None:
            vo['entityID'] = newId
        return vo

    def getPopUpVO(self, newId=None):
        vo = self.getListVO(newId)
        settings = g_settings.lobby.serviceChannel
        if self.getPriorityLevel() == NotificationPriorityLevel.HIGH:
            vo['lifeTime'] = settings.highPriorityMsgLifeTime
            vo['hidingAnimationSpeed'] = settings.highPriorityMsgAlphaSpeed
        else:
            vo['lifeTime'] = settings.mediumPriorityMsgLifeTime
            vo['hidingAnimationSpeed'] = settings.mediumPriorityMsgAlphaSpeed
        if self._settings is not None:
            overrideTimeout = getattr(self._settings.auxData, 'timeoutMS', 0)
            if overrideTimeout > 0:
                vo['lifeTime'] = self._settings.auxData.timeoutMS
        return vo

    def getButtonLayout(self):
        return tuple()

    def getOrder(self):
        return (self.showAt(), 0)

    def _make(self, entity=None, settings=None):
        self._vo = {}
        self._settings = settings

    def getCounterInfo(self):
        return (self.getGroup(), self.getType(), self.getID())

    def decrementCounterOnHidden(self):
        return True


class SearchCriteria(_NotificationDecorator):
    __slots__ = ('_typeID',)

    def __init__(self, typeID, itemID):
        super(SearchCriteria, self).__init__(itemID)
        self._typeID = typeID

    def clear(self):
        super(SearchCriteria, self).clear()
        self._typeID = 0

    def getType(self):
        return self._typeID


class MessageDecorator(_NotificationDecorator):

    def __init__(self, entityID, entity=None, settings=None, model=None):
        self._model = model
        super(MessageDecorator, self).__init__(entityID, entity, settings)

    def getSavedData(self):
        return self._vo['message'].get('savedData')

    def getType(self):
        return NOTIFICATION_TYPE.MESSAGE

    def getGroup(self):
        return self._settings.groupID

    def update(self, formatted):
        super(MessageDecorator, self).update(formatted)
        self._make(formatted)

    def getOrder(self):
        return (self.showAt(), self._entityID)

    def _make(self, formatted=None, settings=None):
        if settings:
            self._settings = settings
            if not self._settings.showAt:
                self._settings.showAt = _makeShowTime()
        message = formatted.copy() if formatted else {}
        for key in _ICONS_FIELDS:
            if key in formatted:
                message[key] = makePathToIcon(message[key])
            message[key] = ''

        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify()}


class RecruitReminderMessageDecorator(MessageDecorator):

    def __init__(self, entityID, message, savedData, msgPrLevel=NotificationPriorityLevel.LOW):
        entity = g_settings.msgTemplates.format('RecruitReminder', ctx={'text': message}, data={'savedData': savedData})
        settings = NotificationGuiSettings(isNotify=True, priorityLevel=msgPrLevel)
        super(RecruitReminderMessageDecorator, self).__init__(entityID, entity, settings)

    def getType(self):
        return NOTIFICATION_TYPE.RECRUIT_REMINDER

    def getGroup(self):
        return NotificationGroup.OFFER

    def getSavedData(self):
        return self._vo['message'].get('savedData', {})


class EmailConfirmationReminderMessageDecorator(MessageDecorator):

    def __init__(self, entityID, message):
        entity = g_settings.msgTemplates.format('EmailConfirmationReminder', ctx={'text': message})
        settings = NotificationGuiSettings(isNotify=True)
        super(EmailConfirmationReminderMessageDecorator, self).__init__(entityID, entity, settings)

    def getType(self):
        return NOTIFICATION_TYPE.EMAIL_CONFIRMATION_REMINDER

    def getGroup(self):
        return NotificationGroup.OFFER


class PsaCoinReminderMessageDecorator(MessageDecorator):

    def __init__(self, entityID, coinCount, msgPrLevel=NotificationPriorityLevel.LOW):
        entity = g_settings.msgTemplates.format('PsaCoinReminder', ctx={'count': str(coinCount)}, data={'savedData': coinCount})
        settings = NotificationGuiSettings(isNotify=True, priorityLevel=msgPrLevel)
        super(PsaCoinReminderMessageDecorator, self).__init__(entityID, entity, settings)

    def getType(self):
        return NOTIFICATION_TYPE.PSACOIN_REMINDER

    def getGroup(self):
        return NotificationGroup.OFFER

    def getSavedData(self):
        return self._vo['message'].get('savedData', 0)


class LockButtonMessageDecorator(MessageDecorator):

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(LockButtonMessageDecorator, self).__init__(entityID, entity, settings, model)
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self._viewLoaded, EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        super(LockButtonMessageDecorator, self).clear()
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._viewLoaded, EVENT_BUS_SCOPE.LOBBY)

    def update(self, formatted):
        _NotificationDecorator.update(self, formatted)

    def _make(self, formatted=None, settings=None):
        super(LockButtonMessageDecorator, self)._make(formatted, settings)
        self._updateButtons(None)
        return

    def _getLockAliases(self):
        return (VIEW_ALIAS.BATTLE_QUEUE,)

    def _updateButtons(self, _):
        self._updateButtonsState(lock=False)

    def _viewLoaded(self, event):
        if event.alias in self._getLockAliases():
            self._updateButtonsState(lock=True)
        elif VIEW_ALIAS.LOBBY_HANGAR == event.alias:
            self._updateButtons(event)

    def _updateButtonsState(self, lock=False):
        if self._entity is None or not self._entity.get('buttonsLayout'):
            return
        else:
            state = NOTIFICATION_BUTTON_STATE.VISIBLE if lock else NOTIFICATION_BUTTON_STATE.DEFAULT
            self._entity['buttonsStates'].update({'submit': state})
            if self._model is not None:
                self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
            return


class C11nMessageDecorator(LockButtonMessageDecorator):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(C11nMessageDecorator, self).__init__(entityID, entity, settings, model)
        g_clientUpdateManager.addCallbacks({'inventory': self._updateButtons})
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self._updateButtons})
        g_eventBus.addListener(HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE, self._updateButtons, EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        super(C11nMessageDecorator, self).clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_eventBus.removeListener(HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE, self._updateButtons, EVENT_BUS_SCOPE.LOBBY)

    def _updateButtons(self, _):
        isLocked = True
        if not currentHangarIsBattleRoyale() and self.__vehicle is not None and self.__vehicle.isCustomizationEnabled():
            isLocked = self._entity.get('savedData', {}).get('toStyle', False) and not isVehicleCanBeCustomized(self.__vehicle, GUI_ITEM_TYPE.STYLE)
        self._updateButtonsState(lock=isLocked)
        return

    def _getLockAliases(self):
        return (VIEW_ALIAS.HERO_VEHICLE_PREVIEW,) + super(C11nMessageDecorator, self)._getLockAliases()

    @property
    def __vehicle(self):
        vehicle = None
        if self.itemsCache is not None and self.itemsCache.isSynced():
            savedData = self._entity.get('savedData')
            if savedData is not None:
                vehicleIntCD = savedData.get('vehicleIntCD')
                if vehicleIntCD is not None:
                    vehicle = self.itemsCache.items.getItemByCD(vehicleIntCD)
        return vehicle


class PrbInviteDecorator(_NotificationDecorator):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __slots__ = ('_createdAt',)

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def __init__(self, invite):
        self._createdAt = invite.getCreateTime()
        super(PrbInviteDecorator, self).__init__(invite.clientID, invite)

    def clear(self):
        self._createdAt = 0
        super(PrbInviteDecorator, self).clear()

    def getSavedData(self):
        return self.getID()

    def getType(self):
        return NOTIFICATION_TYPE.INVITE

    def getGroup(self):
        return NotificationGroup.INVITE

    def update(self, entity):
        super(PrbInviteDecorator, self).update(entity)
        self._make(entity)

    def getOrder(self):
        return (self.showAt(), self._createdAt)

    def _make(self, invite=None, settings=None):
        invite = invite or self.prbInvites.getInvite(self._entityID)
        if not invite:
            LOG_ERROR('Invite not found', self._entityID)
            self._vo = {}
            self._settings = NotificationGuiSettings(False, NotificationPriorityLevel.LOW, showAt=_makeShowTime())
            return
        if not invite.showAt or invite.isActive():
            if invite.showAt > 0:
                self._isOrderChanged = True
            invite.showAt = _makeShowTime()
        if invite.isActive():
            self._settings = NotificationGuiSettings(True, NotificationPriorityLevel.HIGH, showAt=invite.showAt)
        else:
            self._settings = NotificationGuiSettings(False, NotificationPriorityLevel.LOW, showAt=invite.showAt)
        formatter = getPrbInviteHtmlFormatter(invite)
        canAccept = self.prbInvites.canAcceptInvite(invite)
        canDecline = self.prbInvites.canDeclineInvite(invite)
        if canAccept or canDecline:
            submitState = cancelState = NOTIFICATION_BUTTON_STATE.VISIBLE
            if canAccept:
                submitState |= NOTIFICATION_BUTTON_STATE.ENABLED
            if canDecline:
                cancelState |= NOTIFICATION_BUTTON_STATE.ENABLED
        else:
            submitState = cancelState = 0
        message = g_settings.msgTemplates.format('invite', ctx={'text': formatter.getText(invite)}, data={'timestamp': invite.createTime,
         'icon': makePathToIcon(formatter.getIconName(invite)),
         'defaultIcon': makePathToIcon('prebattleInviteIcon'),
         'buttonsStates': {'submit': submitState,
                           'cancel': cancelState}})
        message = self.__updateTooltips(canAccept, message)
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}

    def __updateTooltips(self, canAccept, message):
        if 'buttonsLayout' not in message:
            return message
        tooltip = ''
        message = deepcopy(message)
        buttonsLayout = message.get('buttonsLayout')
        if not canAccept and self.__funRandomCtrl.isAvailable() and not self.__funRandomCtrl.canGoToMode():
            tooltipStr = R.strings.invites.invites.tooltip.funRandom.noVehicles()
            tooltip = makeTooltip(body=_getDisabledFunRandomTooltip(tooltipStr))
        buttonsLayout[0]['tooltip'] = tooltip
        return message


class FriendshipRequestDecorator(_NotificationDecorator):
    __slots__ = ('_receivedAt',)

    def __init__(self, user):
        self._receivedAt = None
        super(FriendshipRequestDecorator, self).__init__(user.getID(), entity=user, settings=NotificationGuiSettings(True, NotificationPriorityLevel.HIGH, showAt=_makeShowTime()))
        return

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def getType(self):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    def getGroup(self):
        return NotificationGroup.INVITE

    def getOrder(self):
        return (self.showAt(), self._receivedAt)

    def update(self, user):
        super(FriendshipRequestDecorator, self).update(user)
        self._make(user=user, settings=NotificationGuiSettings(False, NotificationPriorityLevel.LOW, showAt=self.showAt()))

    def _make(self, user=None, settings=None):
        if settings:
            self._settings = settings
        contacts = self.proto.contacts
        if user.getItemType() in XMPP_ITEM_TYPE.SUB_PENDING_ITEMS:
            self._receivedAt = user.getItem().receivedAt()
        canCancel, error = contacts.canCancelFriendship(user)
        if canCancel:
            canApprove, error = contacts.canApproveFriendship(user)
        else:
            canApprove = False
        if canApprove or canCancel:
            submitState = cancelState = NOTIFICATION_BUTTON_STATE.VISIBLE
            if canApprove:
                submitState |= NOTIFICATION_BUTTON_STATE.ENABLED
            if canCancel:
                cancelState |= NOTIFICATION_BUTTON_STATE.ENABLED
            self._settings.isNotify = True
            self._settings.priorityLevel = NotificationPriorityLevel.HIGH
        else:
            submitState = cancelState = NOTIFICATION_BUTTON_STATE.HIDDEN
        message = g_settings.msgTemplates.format('friendshipRequest', ctx={'text': makeFriendshipRequestText(user, error)}, data={'timestamp': self._receivedAt,
         'icon': makePathToIcon('friendshipIcon'),
         'buttonsStates': {'submit': submitState,
                           'cancel': cancelState}})
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}


class WGNCPopUpDecorator(_NotificationDecorator):
    __slots__ = ('_itemName', '__receivedAt')

    def __init__(self, entityID, item, offset=0, receivedAt=None):
        super(WGNCPopUpDecorator, self).__init__(entityID, item, NotificationGuiSettings(item.isNotify(), item.getPriority(), showAt=_makeShowTime() + offset))
        self.__receivedAt = receivedAt

    def getType(self):
        return NOTIFICATION_TYPE.WGNC_POP_UP

    def getGroup(self):
        return self.getEntity().getGroup()

    def getOrder(self):
        timeCriteria = self.__receivedAt or self.showAt()
        return (timeCriteria, self._entityID)

    def getSavedData(self):
        return self._itemName

    def update(self, item):
        super(WGNCPopUpDecorator, self).update(item)
        self._make(item)

    def _make(self, item=None, settings=None):
        self._itemName = item.getName()
        if settings:
            self._settings = settings
        layout, states = self._makeButtonsLayout(item)
        topic = i18n.encodeUtf8(item.getTopic())
        if topic:
            topic = g_settings.htmlTemplates.format('notificationsCenterTopic', ctx={'topic': topic})
        body = i18n.encodeUtf8(item.getBody())
        note = item.getNote()
        if note:
            body += g_settings.htmlTemplates.format('notificationsCenterNote', ctx={'note': note})
        bgSource, (_, bgHeight) = item.getLocalBG()
        message = g_settings.msgTemplates.format('wgncNotification_v2', ctx={'topic': topic,
         'body': body}, data={'icon': makePathToIcon(item.getLocalIcon()),
         'defaultIcon': makePathToIcon(WGNC_DEFAULT_ICON),
         'bgIcon': {None: makePathToIcon(bgSource)},
         'bgIconHeight': bgHeight,
         'buttonsLayout': layout,
         'buttonsStates': states})
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}
        return

    def _makeButtonsLayout(self, item):
        layout = []
        states = {}
        seq = ['submit', 'cancel']
        for _, button in enumerate(item.getButtons()):
            if not seq:
                LOG_ERROR('Button is ignored to display', button)
                continue
            buttonType = seq.pop(0)
            layout.append({'label': button.label,
             'type': buttonType,
             'action': button.action,
             'width': WGNC_POP_UP_BUTTON_WIDTH})
            if button.visible:
                state = NOTIFICATION_BUTTON_STATE.ENABLED | NOTIFICATION_BUTTON_STATE.VISIBLE
            else:
                state = NOTIFICATION_BUTTON_STATE.HIDDEN
            states[buttonType] = state

        return (layout, states)


class _ClanBaseDecorator(_NotificationDecorator):
    __slots__ = ('_createdAt',)

    def __init__(self, entityID, entity=None, settings=None):
        self._createdAt = time_utils.getCurrentTimestamp()
        super(_ClanBaseDecorator, self).__init__(entityID, entity, settings)

    def clear(self):
        self._createdAt = 0
        super(_ClanBaseDecorator, self).clear()

    def getOrder(self):
        return (self.showAt(), self._createdAt)

    def getSavedData(self):
        return self.getID()

    def getGroup(self):
        return NotificationGroup.INVITE


class _ClanDecorator(_ClanBaseDecorator):
    clanCtrl = dependency.descriptor(IWebController)

    def __init__(self, entityID, entity=None, settings=None):
        self._settings = None
        super(_ClanDecorator, self).__init__(entityID, entity, settings)
        return

    def update(self, entity):
        super(_ClanBaseDecorator, self).update(entity)
        self._make(entity)

    def _make(self, entity=None, settings=None):
        if self._settings is None:
            self._settings = NotificationGuiSettings(True, NotificationPriorityLevel.MEDIUM, showAt=_makeShowTime())
        formatter = self._getFormatter()
        message = g_settings.msgTemplates.format(self._getTemplateId(), ctx={'text': self._getText(formatter, entity)}, data={'timestamp': self._createdAt,
         'icon': makePathToIcon('clanInviteIcon'),
         'defaultIcon': makePathToIcon('InformationIcon'),
         'buttonsStates': self._getButtonsStates(entity)})
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}
        return

    def _getFormatter(self):
        raise NotImplementedError

    def _getText(self, formatter, entity):
        return formatter.getText(entity)

    def _getTemplateId(self):
        raise NotImplementedError

    def _getButtonsStates(self, entity):
        raise NotImplementedError


class _ClanSingleDecorator(_ClanDecorator):

    def __init__(self, entityID, entity=None, settings=None):
        self._state = self._getDefState()
        super(_ClanSingleDecorator, self).__init__(entityID, entity, settings)

    def setState(self, value):
        self._state = value

    def _getDefState(self):
        raise NotImplementedError


class ClanSingleAppDecorator(_ClanSingleDecorator):

    def __init__(self, entityID, entity=None, settings=None, userName=None):
        self.__userName = userName
        self.__isInClanEnterCooldown = False
        super(ClanSingleAppDecorator, self).__init__(entityID, entity, settings)

    def setUserName(self, value):
        self.__userName = value

    def setClanEnterCooldown(self, value):
        self.__isInClanEnterCooldown = value

    def getUserName(self):
        return self.__userName

    def getType(self):
        return NOTIFICATION_TYPE.CLAN_APP

    def getAccountID(self):
        return self._entity.getAccountID()

    def getApplicationID(self):
        return self._entity.getApplicationID()

    def _getTemplateId(self):
        pass

    def _getDefState(self):
        return CLAN_APPLICATION_STATES.ACTIVE

    def _getFormatter(self):
        return ClanSingleNotificationHtmlTextFormatter('appTitle', 'appComment', 'showUserProfileAction')

    def _getButtonsStates(self, entity):
        if self._state in (CLAN_APPLICATION_STATES.ACCEPTED, CLAN_APPLICATION_STATES.DECLINED) or not self.clanCtrl.getAccountProfile().getMyClanPermissions().canHandleClanInvites() or not self.clanCtrl.isEnabled() or self.__isInClanEnterCooldown:
            submit = cancel = NOTIFICATION_BUTTON_STATE.HIDDEN
        elif not self.clanCtrl.isAvailable():
            submit = cancel = NOTIFICATION_BUTTON_STATE.VISIBLE
        else:
            submit = cancel = NOTIFICATION_BUTTON_STATE.DEFAULT
        return {'submit': submit,
         'cancel': cancel}

    def _getText(self, formatter, entity):
        if self.__isInClanEnterCooldown:
            stateStr = INVITES.CLANS_STATE_APP_ERROR_INCLANENTERCOOLDOWN
            isWarning = True
        else:
            stateStr = '#invites:clans/state/app/%s' % self._state
            isWarning = False
        return formatter.getText((self.__userName, stateStr, isWarning))


class ClanSingleInviteDecorator(_ClanSingleDecorator):

    def getInviteID(self):
        return self._entity.getInviteId()

    def getClanID(self):
        return self._entity.getClanId()

    def getClanAbbrev(self):
        return self._entity.getClanTag()

    def getType(self):
        return NOTIFICATION_TYPE.CLAN_INVITE

    def _getTemplateId(self):
        pass

    def _getDefState(self):
        return CLAN_INVITE_STATES.ACTIVE

    def _getFormatter(self):
        return ClanSingleNotificationHtmlTextFormatter('inviteTitle', 'inviteComment', 'showClanProfileAction')

    def _getButtonsStates(self, entity):
        if self._state in (CLAN_INVITE_STATES.ACCEPTED, CLAN_INVITE_STATES.DECLINED) or self.clanCtrl.getAccountProfile().isInClan() or not self.clanCtrl.isEnabled() or self.__isInClanEnterCooldown():
            submit = cancel = NOTIFICATION_BUTTON_STATE.HIDDEN
        elif not self.clanCtrl.isAvailable():
            submit = cancel = NOTIFICATION_BUTTON_STATE.VISIBLE
        else:
            submit = cancel = NOTIFICATION_BUTTON_STATE.DEFAULT
        return {'submit': submit,
         'cancel': cancel}

    def _getText(self, formatter, entity):
        if self.__isInClanEnterCooldown():
            isWarning = True
            stateStr = INVITES.CLANS_STATE_INVITE_ERROR_INCLANENTERCOOLDOWN
        else:
            isWarning = False
            stateStr = '#invites:clans/state/invite/%s' % self._state
        return formatter.getText((_getClanName((entity.getClanName(), entity.getClanTag())), stateStr, isWarning))

    def __isInClanEnterCooldown(self):
        profile = self.clanCtrl.getAccountProfile()
        return not profile.isInClan() and profile.isInClanEnterCooldown()


class _ClanMultiDecorator(_ClanDecorator):

    def _getButtonsStates(self, entity):
        if not self.clanCtrl.isEnabled():
            submit = NOTIFICATION_BUTTON_STATE.HIDDEN
        elif not self.clanCtrl.isAvailable():
            submit = NOTIFICATION_BUTTON_STATE.VISIBLE
        else:
            submit = NOTIFICATION_BUTTON_STATE.DEFAULT
        return {'submit': submit}


class ClanAppsDecorator(_ClanMultiDecorator):

    def getType(self):
        return NOTIFICATION_TYPE.CLAN_APPS

    def _getTemplateId(self):
        pass

    def _getFormatter(self):
        return ClanMultiNotificationsHtmlTextFormatter('appsTitle', 'multiAppsCommon', 'showClanSettingsAction')


class ClanInvitesDecorator(_ClanMultiDecorator):

    def getType(self):
        return NOTIFICATION_TYPE.CLAN_INVITES

    def _getTemplateId(self):
        pass

    def _getFormatter(self):
        return ClanMultiNotificationsHtmlTextFormatter('invitesTitle', 'multiAppsCommon', 'showClanSettingsAction')


class _ClassBaseActionDecorator(_ClanBaseDecorator):

    def __init__(self, entityID, actionType, userName=None, settings=None):
        self._actionType = actionType
        super(_ClassBaseActionDecorator, self).__init__(entityID, userName, settings)

    def _getName(self, entity):
        raise NotImplementedError

    def _make(self, entity=None, settings=None):
        self._settings = NotificationGuiSettings(True, NotificationPriorityLevel.MEDIUM, showAt=_makeShowTime())
        name = self._getName(entity)
        formatter = ClanAppActionHtmlTextFormatter(self._actionType)
        message = g_settings.msgTemplates.format('clanSimple', ctx={'text': formatter.getText(name)}, data={'timestamp': self._createdAt,
         'icon': makePathToIcon('clanInviteIcon'),
         'defaultIcon': makePathToIcon('InformationIcon')})
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}


class ClanAppActionDecorator(_ClassBaseActionDecorator):

    def getType(self):
        return NOTIFICATION_TYPE.CLAN_APP_ACTION

    def _getName(self, clanInfo):
        return _getClanName(clanInfo)


class ClanInvitesActionDecorator(_ClassBaseActionDecorator):

    def setUserName(self, value):
        self._entity = value

    def getType(self):
        return NOTIFICATION_TYPE.CLAN_INVITE_ACTION

    def update(self, formatted):
        super(ClanInvitesActionDecorator, self).update(formatted)
        self._make(formatted)

    def _getName(self, entity):
        return entity


class ProgressiveRewardDecorator(_NotificationDecorator):
    ENTITY_ID = 0

    def __init__(self):
        super(ProgressiveRewardDecorator, self).__init__(self.ENTITY_ID)

    def getType(self):
        return NOTIFICATION_TYPE.PROGRESSIVE_REWARD

    def getGroup(self):
        return NotificationGroup.OFFER

    def update(self, entity):
        super(ProgressiveRewardDecorator, self).update(entity)
        self._make(entity)

    def decrementCounterOnHidden(self):
        return False

    def _make(self, entity=None, settings=None):
        self._settings = NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.MEDIUM)
        message = g_settings.msgTemplates.format('ProgressiveRewardNotification', data={'icon': makePathToIcon('InformationIcon')})
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}


class MissingEventsDecorator(_NotificationDecorator):
    ENTITY_ID = 0

    def __init__(self, count):
        super(MissingEventsDecorator, self).__init__(self.ENTITY_ID, count)

    def getType(self):
        return NOTIFICATION_TYPE.MISSING_EVENTS

    def getGroup(self):
        return NotificationGroup.OFFER

    @staticmethod
    def isPinned():
        return True

    def update(self, entity):
        super(MissingEventsDecorator, self).update(entity)
        self._make(entity)

    def decrementCounterOnHidden(self):
        return False

    def _make(self, entity=None, settings=None):
        self._settings = NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.HIGH)
        message = g_settings.msgTemplates.format('MissingEventsNotification', ctx={'count': entity})
        message['icon'] = makePathToIcon(message['icon'])
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}


class BattlePassSwitchChapterReminderDecorator(MessageDecorator):

    def __init__(self, entityID, message):
        super(BattlePassSwitchChapterReminderDecorator, self).__init__(entityID, self.__makeEntity(message), self.__makeSettings())

    def getGroup(self):
        return NotificationGroup.OFFER

    def getType(self):
        return NOTIFICATION_TYPE.BATTLE_PASS_SWITCH_CHAPTER_REMINDER

    def __makeEntity(self, message):
        return g_settings.msgTemplates.format('BattlePassSwitchChapterReminder', ctx={'text': message})

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.LOW)


class BattlePassLockButtonDecorator(MessageDecorator):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(BattlePassLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.__battlePassController.onBattlePassSettingsChange += self.__update
        self.__battlePassController.onSeasonStateChanged += self.__update

    def clear(self):
        self.__battlePassController.onBattlePassSettingsChange -= self.__update
        self.__battlePassController.onSeasonStateChanged -= self.__update
        super(BattlePassLockButtonDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(BattlePassLockButtonDecorator, self)._make(formatted, settings)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            if self.__battlePassController.isActive():
                state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
                tooltip = makeTooltip(body=backport.text(R.strings.system_messages.battlePass.switch_pause.body()))
            buttonsStates = self._entity.get('buttonsStates')
            if buttonsStates is None:
                return
            buttonsStates['submit'] = state
            buttonsLayout[0]['tooltip'] = tooltip
            return

    def __update(self, *_):
        self.__updateEntityButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return


class MapboxButtonDecorator(MessageDecorator):
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(MapboxButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__update

    def clear(self):
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__update
        super(MapboxButtonDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateButtons()
        super(MapboxButtonDecorator, self)._make(formatted, settings)

    def __updateButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            buttonsStates = self._entity.get('buttonsStates')
            if not buttonsLayout or buttonsStates is None:
                return
            if self.__mapboxCtrl.isActive():
                state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
                tooltip = makeTooltip(body=backport.text(R.strings.mapbox.buttonDisable.tooltip()))
            buttonsStates['submit'] = state
            buttonsLayout[0]['tooltip'] = tooltip
            return

    def __update(self, *_):
        self.__updateButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return


class ResourceWellLockButtonDecorator(MessageDecorator):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(ResourceWellLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.__resourceWell.onEventUpdated += self.__update

    def clear(self):
        self.__resourceWell.onEventUpdated -= self.__update

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(ResourceWellLockButtonDecorator, self)._make(formatted, settings)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            if self.__resourceWell.isActive():
                state = NOTIFICATION_BUTTON_STATE.DEFAULT
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
            self._entity['buttonsStates'] = {'submit': state}
            return

    def __update(self, *_):
        self.__updateEntityButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return


class ResourceWellStartDecorator(ResourceWellLockButtonDecorator):

    def __init__(self, entityID, message, model):
        super(ResourceWellStartDecorator, self).__init__(entityID, self.__makeEntity(message), self.__makeSettings(), model)

    def getType(self):
        return NOTIFICATION_TYPE.RESOURCE_WELL_START

    def __makeEntity(self, message):
        return g_settings.msgTemplates.format('ResourceWellStartSysMessage', ctx=message)

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.LOW)


class FunRandomButtonDecorator(MessageDecorator):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __STR_PATH = R.strings.fun_random.message.startEvent
    __TEMPLATE = 'FunRandomStarted'

    def __init__(self, entityId):
        super(FunRandomButtonDecorator, self).__init__(entityId, entity=g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': backport.text(self.__STR_PATH.text())}, data={'buttonsStates': {'submit': self.__isActive()}}), settings=NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.MEDIUM))

    def _make(self, formatted=None, settings=None):
        self.__updateButtons()
        super(FunRandomButtonDecorator, self)._make(formatted, settings)

    def __updateButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            buttonsStates = self._entity.get('buttonsStates')
            if not buttonsLayout or buttonsStates is None:
                return
            if self.__funRandomCtrl.isFunRandomPrbActive():
                state, tooltip = NOTIFICATION_BUTTON_STATE.HIDDEN, ''
            elif self.__isActive():
                state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
                tooltip = self.__getDisabledTooltip()
            buttonsStates['submit'] = state
            buttonsLayout[0]['tooltip'] = tooltip
            return

    def __isActive(self):
        return self.__funRandomCtrl.isAvailable() and self.__funRandomCtrl.canGoToMode()

    def __getDisabledTooltip(self):
        if self.__funRandomCtrl.isAvailable() and not self.__funRandomCtrl.canGoToMode():
            tooltipText = _getDisabledFunRandomTooltip(self.__STR_PATH.disabledButton.noVehicles.tooltip())
        else:
            tooltipText = backport.text(self.__STR_PATH.disabledButton.disabledEvent.tooltip())
        return makeTooltip(body=tooltipText)


class ChinaLootBoxesDecorator(MessageDecorator):
    __cnLootBoxes = dependency.descriptor(ICNLootBoxesController)

    def __init__(self, entityID, message, model):
        super(ChinaLootBoxesDecorator, self).__init__(entityID, self.__makeEntity(message), self.__makeSettings(), model)
        self.__cnLootBoxes.onStatusChange += self.__update
        self.__cnLootBoxes.onAvailabilityChange += self.__update

    def clear(self):
        self.__cnLootBoxes.onStatusChange -= self.__update
        self.__cnLootBoxes.onAvailabilityChange -= self.__update

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(ChinaLootBoxesDecorator, self)._make(formatted, settings)

    def __makeEntity(self, message):
        return g_settings.msgTemplates.format('ChinaLootBoxStartSysMessage', ctx=message)

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.MEDIUM)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            if self.__cnLootBoxes.isActive() and self.__cnLootBoxes.isLootBoxesAvailable():
                state = NOTIFICATION_BUTTON_STATE.DEFAULT
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
            self._entity['buttonsStates'] = {'submit': state}
            return

    def __update(self, *_):
        self.__updateEntityButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return
