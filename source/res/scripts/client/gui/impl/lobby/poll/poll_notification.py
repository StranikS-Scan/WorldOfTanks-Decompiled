# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/poll/poll_notification.py
from debug_utils import LOG_WARNING, LOG_ERROR
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl.gen.view_models.views.lobby.poll.poll_view_model import PollViewType
from gui.shared.notifications import NotificationPriorityLevel

class PollNotification(object):

    @classmethod
    def invoke(cls, **kwargs):
        value = kwargs.get('value', None)
        if isinstance(value, dict):
            header = value.get('header', '')
            text = value.get('text', '')
            priority = value.get('priority', '')
            target = value.get('target', '')
            url = value.get('url', '')
            notID = kwargs.get('notID', '')
        else:
            LOG_ERROR('{}: "value" should be dict'.format(cls.__name__))
            return
        if not all([ bool(x) for x in [header,
         text,
         priority,
         target,
         url,
         notID] ]):
            LOG_ERROR('{}: some items are not correct'.format(cls.__name__))
            return
        else:
            if priority not in NotificationPriorityLevel.RANGE:
                LOG_WARNING('Notification priority is not allowed, priority={}'.format(priority))
            notType = None
            if target == PollViewType.SURVEY.value:
                notType = SM_TYPE.SurveyNotification
            elif target == PollViewType.APPLICATION_FORM.value:
                notType = SM_TYPE.ApplicationFormNotification
            else:
                LOG_WARNING('Notification target is not allowed, target={}'.format(target))
            if notType:
                SystemMessages.pushMessage('', priority=priority, type=notType, messageData={'text': text,
                 'header': header,
                 'target': target}, savedData={'value': {'url': url,
                           'target': target},
                 'notID': notID})
            return
