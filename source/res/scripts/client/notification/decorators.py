# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/decorators.py
import typing
import BigWorld
from debug_utils import LOG_ERROR
from gifts.gifts_common import GiftEventID, GiftEventState
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.INVITES import INVITES
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsSteelHunter
from gui.clans.formatters import ClanSingleNotificationHtmlTextFormatter, ClanMultiNotificationsHtmlTextFormatter, ClanAppActionHtmlTextFormatter, getClanAbbrevString
from gui.clans.settings import CLAN_APPLICATION_STATES, CLAN_INVITE_STATES
from gui.customization.shared import isVehicleCanBeCustomized
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import getGiftSystemCongratulationText
from gui.prb_control import prbInvitesProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.formatters.invites import getPrbInviteHtmlFormatter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType, HangarSpacesSwitcherEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.loot_box import NewYearCategories
from gui.shared.notifications import NotificationPriorityLevel, NotificationGuiSettings, NotificationGroup
from gui.shared.utils.functions import makeTooltip
from gui.wgnc.settings import WGNC_DEFAULT_ICON, WGNC_POP_UP_BUTTON_WIDTH
from helpers import dependency
from helpers import i18n
from helpers import time_utils
from messenger import g_settings
from messenger.formatters.users_messages import makeFriendshipRequestText
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.xmpp.xmpp_constants import XMPP_ITEM_TYPE
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from notification.settings import makePathToIcon
from skeletons.gui.game_control import IGiftSystemController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.shared.events import LoadViewEvent

def _makeShowTime():
    return BigWorld.time()


_ICONS_FIELDS = ('icon', 'defaultIcon', 'bgIcon')

def _getClanName(clanInfo):
    return '[{}] {}'.format(clanInfo[1], clanInfo[0])


class _NotificationDecorator(object):
    __slots__ = ('_entityID', '_entity', '_settings', '_vo', '_isOrderChanged')

    def __init__(self, entityID, entity=None, settings=None):
        super(_NotificationDecorator, self).__init__()
        self._isOrderChanged = False
        self._entityID = entityID
        self._entity = entity
        self._settings = settings
        self._make(entity, settings)

    def __repr__(self):
        return '{0:>s}(typeID = {1:n}, entityID = {2:n})'.format(self.__class__.__name__, self.getType(), self.getID())

    def __cmp__(self, other):
        return cmp(self.getOrder(), other.getOrder()) if isinstance(other, _NotificationDecorator) else -1

    def __eq__(self, other):
        return isinstance(other, _NotificationDecorator) and self.getType() == other.getType() and self.getID() == other.getID()

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

    def onlyNCList(self):
        result = False
        if self._settings:
            result = self._settings.onlyNCList
        return result

    def onlyPopUp(self):
        result = False
        if self._settings:
            result = self._settings.onlyPopUp
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
        return (self.getGroup(),
         self.getType(),
         self.getID(),
         self.getCount(),
         self.resetCounter())

    def decrementCounterOnHidden(self):
        return True

    def resetCounter(self):
        return True

    def getCount(self):
        pass

    def updateCounter(self):
        return False


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
            if key in message:
                message[key] = makePathToIcon(message[key])
            message[key] = ''

        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify()}


class ChoosingDevicesMessageDecorator(MessageDecorator):

    def getType(self):
        return NOTIFICATION_TYPE.CHOOSING_DEVICES

    def getGroup(self):
        return NotificationGroup.OFFER

    def getSavedData(self):
        return self._vo['message'].get('savedData', {})


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
        if not currentHangarIsSteelHunter() and self.__vehicle is not None and self.__vehicle.isCustomizationEnabled():
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
        self._vo = {'typeID': self.getType(),
         'entityID': self.getID(),
         'message': message,
         'notify': self.isNotify(),
         'auxData': []}


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


class GiftSystemOperationDecorator(MessageDecorator):

    def __init__(self, entityID, entity=None, settings=None, model=None, ctx=None):
        super(GiftSystemOperationDecorator, self).__init__(entityID, entity, settings, model)
        self._userID, self._userName, self._clanAbbrev, self._ctx = (None,
         '',
         '',
         ctx)
        return

    def getType(self):
        return NOTIFICATION_TYPE.GIFT_SYSTEM_OPERATION

    def getUserID(self):
        return self._userID

    def initUserInfo(self, userName, clanAbbrev):
        self._userName, self._clanAbbrev = userName, clanAbbrev
        self.update(self._makeEntity(self._ctx, bool(self._userName)))

    def setUserInfo(self, userName):
        self._userName = userName
        self._entity = self._makeEntity(self._ctx, bool(self._userName))

    def _makeEntity(self, ctx, userResolved=False):
        raise NotImplementedError

    def _makeSettings(self, template):
        return NotificationGuiSettings(isNotify=True, priorityLevel=g_settings.msgTemplates.priority(template))


class NYGiftOpenedDecorator(GiftSystemOperationDecorator):
    _DEFAULT_TEMPLATE = 'LootBoxRewardsSysMessage'
    _GIFT_TEMPLATE = 'GiftLootBoxRewardsSysMessage'

    def __init__(self, entityID, model, ctx):
        self.__lootbox, self.__template = ctx['lootbox'], self.__getTemplateByCtx(ctx)
        entity, settings = self._makeEntity(ctx), self._makeSettings(self.__template)
        super(NYGiftOpenedDecorator, self).__init__(entityID, entity, settings, model, ctx)
        self._userID = ctx['giftsInfo'][0].senderID

    def clear(self):
        self.__lootbox = None
        return

    def _makeEntity(self, ctx, userResolved=False):
        text = ctx['fmtBonuses']
        if self.__template == self._GIFT_TEMPLATE:
            text = self.__wrapWithGiftCongrats(text, ctx['giftsInfo'][0], userResolved)
        return g_settings.msgTemplates.format(self.__template, ctx={'text': text})

    def __getTemplateByCtx(self, ctx):
        giftsInfo = ctx['giftsInfo']
        return self._GIFT_TEMPLATE if len(giftsInfo) == 1 else self._DEFAULT_TEMPLATE

    def __wrapWithGiftCongrats(self, text, giftInfo, userResolved):
        lootboxType = self.__lootbox.getType()
        resourceShortcut = R.strings.ny.giftSystem.notification.congrats
        congratsText = text_styles.warning(getGiftSystemCongratulationText(giftInfo.metaInfo.get('message_id', 0)))
        if userResolved:
            clanAbbrev = getClanAbbrevString(self._clanAbbrev) if self._clanAbbrev else ''
            user = text_styles.warning(text_styles.concatStylesWithSpace(self._userName, clanAbbrev))
            giftMessage = backport.text(resourceShortcut.withName.dyn(lootboxType)(), name=user, text=congratsText)
        else:
            giftMessage = backport.text(resourceShortcut.empty.dyn(lootboxType)(), text=congratsText)
        return text_styles.concatStylesToMultiLine(giftMessage, '', text)


class NYGiftSentDecorator(GiftSystemOperationDecorator):
    _TEMPLATE = 'GiftSendSysMessage'

    def __init__(self, entityID, model, ctx):
        entity, settings = self._makeEntity(ctx), self._makeSettings(self._TEMPLATE)
        super(NYGiftSentDecorator, self).__init__(entityID, entity, settings, model)
        self._userID = ctx['userID']

    def _makeEntity(self, _, userResolved=False):
        if userResolved:
            clanAbbrev = getClanAbbrevString(self._clanAbbrev) if self._clanAbbrev else ''
            user = text_styles.warning(text_styles.concatStylesWithSpace(self._userName, clanAbbrev))
            text = backport.text(R.strings.ny.giftSystem.notification.sent.withName(), name=user)
        else:
            text = backport.text(R.strings.ny.giftSystem.notification.sent.empty())
        return g_settings.msgTemplates.format(self._TEMPLATE, ctx={'text': text})


class GiftSystemOperationsFactory(object):
    __giftsController = dependency.descriptor(IGiftSystemController)
    __OPENED_DECORATORS = {GiftEventID.NY_HOLIDAYS: NYGiftOpenedDecorator}
    __SENT_DECORATORS = {GiftEventID.NY_HOLIDAYS: NYGiftSentDecorator}

    @classmethod
    def createGiftOpenedDecorator(cls, clientID, model, ctx):
        lootboxID = ctx['lootbox'].getID()
        eventID = cls.__giftsController.getSettings().itemToEventID.get(lootboxID, GiftEventID.UNKNOWN)
        return cls.__OPENED_DECORATORS.get(eventID, cls.__createNothing)(clientID, model, ctx)

    @classmethod
    def createGiftSentDecorator(cls, clientID, model, ctx):
        return cls.__SENT_DECORATORS.get(ctx['eventID'], cls.__createNothing)(clientID, model, ctx)

    @classmethod
    def __createNothing(cls, *_):
        return None


class NyMessageButtonDecorator(MessageDecorator, IGlobalListener):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(NyMessageButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.startGlobalListening()
        self._nyController.onStateChanged += self.__doUpdateButtons

    def clear(self):
        self.stopGlobalListening()
        self._nyController.onStateChanged -= self.__doUpdateButtons
        super(NyMessageButtonDecorator, self).clear()

    def onEnqueued(self, queueType, *args):
        self.__doUpdateButtons()

    def onDequeued(self, queueType, *args):
        self.__doUpdateButtons()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__doUpdateButtons()

    def _make(self, formatted=None, settings=None):
        self._updateEntityButtons()
        super(NyMessageButtonDecorator, self)._make(formatted, settings)

    def _updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            buttonsStates = self._entity.get('buttonsStates')
            state, tooltip = self._getButtonState()
            buttonsStates['submit'] = state
            buttonsLayout[0]['tooltip'] = tooltip
            return

    def _getButtonState(self):
        state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
        bodyId = None
        if self.prbEntity is not None and self.prbEntity.isInQueue():
            state = NOTIFICATION_BUTTON_STATE.VISIBLE
            bodyId = R.strings.system_messages.queue.isInQueue()
        elif not self._isButtonEnabled():
            state = NOTIFICATION_BUTTON_STATE.VISIBLE
            if self._nyController.isSuspended():
                bodyId = R.strings.ny.notification.suspend()
            elif self._nyController.isPostEvent():
                bodyId = R.strings.ny.notification.postEvent()
            elif self._nyController.isFinished():
                bodyId = R.strings.ny.notification.finish()
        if bodyId:
            tooltip = makeTooltip(body=backport.text(bodyId))
        return (state, tooltip)

    def _updateButtons(self):
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return

    def _isButtonEnabled(self):
        return self._nyController.isEnabled()

    def __doUpdateButtons(self):
        self._updateEntityButtons()
        self._updateButtons()


class NyCelebrityRewardDecorator(NyMessageButtonDecorator):

    def _isButtonEnabled(self):
        return self._nyController.isVehicleBranchEnabled()


class NySpecialBoxesLockDecorator(NyMessageButtonDecorator):

    def _getGiftEventState(self):
        raise NotImplementedError

    def _getButtonState(self):
        if not self._canButtonBeDisabledByGiftState():
            return super(NySpecialBoxesLockDecorator, self)._getButtonState()
        else:
            state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
            bodyId = None
            giftEventState = self._getGiftEventState()
            if self.prbEntity is not None and self.prbEntity.isInQueue():
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
                bodyId = R.strings.system_messages.queue.isInQueue()
            elif giftEventState == GiftEventState.SUSPENDED:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE | NOTIFICATION_BUTTON_STATE.WARNING
                bodyId = R.strings.ny.giftSystem.notification.specialLootBoxes.disabledTooltip()
            elif giftEventState == GiftEventState.DISABLED:
                state = NOTIFICATION_BUTTON_STATE.HIDDEN
            if bodyId:
                tooltip = makeTooltip(body=backport.text(bodyId))
            return (state, tooltip)

    def _canButtonBeDisabledByGiftState(self):
        return True


class NyLootBoxesReceivedDecorator(NySpecialBoxesLockDecorator, GiftEventHubWatcher):
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(NyLootBoxesReceivedDecorator, self).__init__(entityID, entity, settings, model)
        self.catchGiftEventHub()

    def clear(self):
        self.releaseGiftEventHub()
        super(NyLootBoxesReceivedDecorator, self).clear()

    def _canButtonBeDisabledByGiftState(self):
        return self._entity and self._entity.get('nyData', {}).get('category', '') == NewYearCategories.SPECIAL

    def _getGiftEventState(self):
        return self.getGiftEventState(isCached=False)

    def _onGiftHubUpdate(self, reason, extra=None):
        if reason == HubUpdateReason.SETTINGS and self._canButtonBeDisabledByGiftState():
            self._updateEntityButtons()
            self._updateButtons()


class NySpecialBoxesEntryDecorator(NySpecialBoxesLockDecorator):
    __TEMPLATE = 'NYSpecialLootBoxesMessage'

    def __init__(self, entityID, count, giftEventState, model=None):
        self.__count, self.__giftEventState = count, giftEventState
        entity, settings = self.__makeEntity(), self.__makeSettings()
        super(NySpecialBoxesEntryDecorator, self).__init__(entityID, entity, settings, model)

    @staticmethod
    def isPinned():
        return True

    def getCount(self):
        return self.__count if self.__giftEventState == GiftEventState.ENABLED else 0

    def getType(self):
        return NOTIFICATION_TYPE.NEW_YEAR_SPECIAL_LOOTBOXES

    def getGiftEventState(self):
        return self.__giftEventState

    def setExternalInfo(self, count, giftEventState):
        self.__count, self.__giftEventState = count, giftEventState
        self._entity = self.__makeEntity()

    def decrementCounterOnHidden(self):
        return False

    def resetCounter(self):
        return not self.getCount()

    def updateCounter(self):
        return True

    def _getGiftEventState(self):
        return self.__giftEventState

    def __makeEntity(self):
        ctx = {'header': backport.text(R.strings.ny.notification.lootBox.header.newYear_special()),
         'body': text_styles.neutral(backport.text(R.strings.ny.notification.lootBox.body.newYear_special()))}
        data = {'savedData': {'category': NewYearCategories.SPECIAL,
                       'count': self.__count}}
        return g_settings.msgTemplates.format(self.__TEMPLATE, ctx=ctx, data=data)

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, groupID=NotificationGroup.INVITE, onlyNCList=True)
