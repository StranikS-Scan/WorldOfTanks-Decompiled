# Embedded file name: scripts/client/gui/wgnc/gui_items.py
from collections import namedtuple
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_DEBUG
from gui.game_control import getRefSysCtrl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import WGNCShowItemEvent
from gui.shared.utils.decorators import ReprInjector
from gui.wgnc.client import ClosePollWindowFromPopUp, ClientLogic
from ids_generators import SequenceIDGenerator
from gui.wgnc.errors import ValidationError
from gui.wgnc.events import g_wgncEvents
from gui.wgnc.settings import WGNC_GUI_TYPE, WGNC_GUI_INVALID_SEQS, convertToLocalIcon, convertToLocalBG
_ButtonData = namedtuple('_ButtonData', ['label',
 'action',
 'visible',
 'focused'])

@ReprInjector.simple(('_name', 'name'), ('_buttons', 'buttons'), ('_hidden', 'hidden'))

class _GUIItem(object):
    __slots__ = ('_name', '_topic', '_body', '_note', '_buttons', '_hidden')

    def __init__(self, name, body, topic = '', buttons = None, hidden = True):
        super(_GUIItem, self).__init__()
        self._name = name
        self._body = body
        self._topic = topic
        self._note = ''
        self._hidden = hidden
        self._buttons = []
        if buttons:
            for idx, (label, actions) in enumerate(buttons):
                self._buttons.append(_ButtonData(label, actions, True, idx == 0))

    def getName(self):
        return self._name

    def getBody(self):
        return self._body

    def getTopic(self):
        return self._topic

    def getNote(self):
        return self._note

    def setNote(self, note):
        self._note = note

    def getButtons(self):
        return self._buttons

    def getButtonsMap(self):
        return map(lambda button: button._asdict(), self.getButtons())

    def getSubmitButton(self):
        if self._buttons:
            return self._buttons[0]
        else:
            return None

    def getCancelButton(self):
        if len(self._buttons) > 1:
            return self._buttons[-1]
        else:
            return None

    def hideButtons(self):
        pass

    def isHidden(self):
        return self._hidden

    def setHidden(self, value):
        self._hidden = value

    def getType(self):
        raise NotImplementedError

    def getClientLogic(self):
        return None

    def validate(self, actionsHolder):
        for idx, button in enumerate(self._buttons[:]):
            if not actionsHolder.hasAllActions(button.action):
                self._buttons[idx] = self._buttons[idx]._replace(visible=False)
                LOG_WARNING('Some actions are not defined for button', button)

    def show(self, notID):
        g_wgncEvents.onItemShowByDefault(notID, self)

    def close(self, notID):
        pass


_idGen = SequenceIDGenerator()

@ReprInjector.withParent(('_priority', 'priority'), ('_icon', 'icon'), ('_bg', 'bg'))

class PopUpItem(_GUIItem):
    __slots__ = ('_priority', '_icon', '_bg')

    def __init__(self, body, topic, priority, buttons = None, icon = 'information', bg = ''):
        super(PopUpItem, self).__init__('pop-up-{0}'.format(_idGen.next()), body, topic, buttons, False)
        self._priority = priority
        self._icon = icon
        self._bg = bg

    def hideButtons(self):
        self._buttons = map(lambda button: button._replace(visible=False), self._buttons)

    def getType(self):
        return WGNC_GUI_TYPE.POP_UP

    def getPriority(self):
        return self._priority

    def getIcon(self):
        return self._icon

    def getLocalIcon(self):
        return convertToLocalIcon(self._icon)

    def getBG(self):
        return self._bg

    def getLocalBG(self):
        return convertToLocalBG(self._bg)


@ReprInjector.withParent(('_modal', 'modal'))

class WindowItem(_GUIItem):
    __slots__ = ('_modal',)

    def __init__(self, name, body, topic = '', buttons = None, modal = False, hidden = True):
        super(WindowItem, self).__init__(name, body, topic, buttons, hidden)
        self._modal = modal

    def getType(self):
        return WGNC_GUI_TYPE.BASIC_WINDOW

    def isModal(self):
        return self._modal

    def show(self, notID):
        LOG_DEBUG('WindowItem.show', notID, self._name)
        g_eventBus.handleEvent(WGNCShowItemEvent(notID, self._name, WGNCShowItemEvent.SHOW_BASIC_WINDOW), EVENT_BUS_SCOPE.LOBBY)


@ReprInjector.withParent(('_count', 'count'))

class ReferrerItem(WindowItem):
    __slots__ = ('_count',)

    def __init__(self, name, count = 0, hidden = True):
        super(ReferrerItem, self).__init__(name, '', '', None, False, hidden)
        self._count = count
        return

    def getType(self):
        return WGNC_GUI_TYPE.COMPLEX_WINDOW

    def getInvitationsCount(self):
        return self._count

    def show(self, notID):
        ctrl = getRefSysCtrl()
        if ctrl:
            ctrl.showReferrerIntroWindow(self._count)
        else:
            LOG_ERROR('Referral system controller is not found')


@ReprInjector.withParent(('_referrer', 'referrer'), ('_isNewbie', 'isNewbie'))

class ReferralItem(WindowItem):
    __slots__ = ('_referrer', '_isNewbie')

    def __init__(self, name, referrer, isNewbie = False, hidden = True):
        super(ReferralItem, self).__init__(name, '', '', None, False, hidden)
        self._referrer = referrer
        self._isNewbie = isNewbie
        return

    def getType(self):
        return WGNC_GUI_TYPE.COMPLEX_WINDOW

    def getReferrer(self):
        return self._referrer

    def show(self, notID):
        ctrl = getRefSysCtrl()
        if ctrl:
            ctrl.showReferralIntroWindow(self._referrer, self._isNewbie)
        else:
            LOG_ERROR('Referral system controller is not found')


@ReprInjector.withParent()

class PollItem(WindowItem):

    def getType(self):
        return WGNC_GUI_TYPE.COMPLEX_WINDOW

    def getClientLogic(self):
        return ClosePollWindowFromPopUp(self._name)

    def show(self, notID):
        LOG_DEBUG('PollItem.show', notID, self._name)
        g_eventBus.handleEvent(WGNCShowItemEvent(notID, self._name, WGNCShowItemEvent.SHOW_POLL_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def close(self, notID):
        LOG_DEBUG('PollItem.close', notID, self._name)
        g_eventBus.handleEvent(WGNCShowItemEvent(notID, self._name, WGNCShowItemEvent.CLOSE_POLL_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def validate(self, actionsHolder):
        if len(self._buttons) < 2:
            raise ValidationError, 'Poll item "{0}" must has two buttons.'.format(self._name)
        super(PollItem, self).validate(actionsHolder)


@ReprInjector.simple(('__items', 'items'))

class GUIHolder(object):
    __slots__ = ('__items',)

    def __init__(self, items):
        super(GUIHolder, self).__init__()
        self.__items = {item.getType():item for item in items}

    def clear(self):
        self.__items.clear()

    def all(self):
        return self.__items.itervalues()

    def hasItemType(self, itemType):
        return itemType in self.__items

    def getItemByType(self, itemType):
        item = None
        if self.hasItemType(itemType):
            item = self.__items[itemType]
        return item

    def getItemByName(self, name):
        for item in self.__items.itervalues():
            if item.getName() == name:
                return item

        return None

    def getItemsNames(self):
        names = set()
        for item in self.__items.itervalues():
            if item.getType() == WGNC_GUI_TYPE.POP_UP:
                continue
            names.add(item.getName())

        return names

    def getClientLogic(self):
        seq = []
        for item in self.__items.itervalues():
            itemLogic = item.getClientLogic()
            if itemLogic:
                seq.append(itemLogic)

        if seq:
            logic = ClientLogic(seq)
        else:
            logic = None
        return logic

    def showItem(self, notID, target):
        item = self.getItemByName(target)
        if item:
            item.show(notID)

    def closeItem(self, notID, target):
        item = self.getItemByName(target)
        if item:
            item.close(notID)

    def validate(self, actionsHolder = None):
        combination = sum(self.__items.keys())
        if combination in WGNC_GUI_INVALID_SEQS:
            raise ValidationError('Combination of GUI items is not valid: {0}'.format(combination))
        if not actionsHolder:
            return
        for itemType, item in self.__items.iteritems():
            item.validate(actionsHolder)
