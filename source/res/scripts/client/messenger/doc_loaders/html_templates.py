# Embedded file name: scripts/client/messenger/doc_loaders/html_templates.py
import types
from debug_utils import LOG_WARNING
from gui.shared.notifications import NotificationPriorityLevel
from helpers.html import translation as html_translation, templates

class _MessageTemplate(templates.Template):

    def __init__(self, source, data, priority):
        super(_MessageTemplate, self).__init__({'message': source})
        self.data = data
        self.priority = priority

    def format(self, ctx = None, data = None):
        vo = self.data.copy()
        if type(data) is types.DictionaryType:
            for key, value in data.iteritems():
                if key in vo:
                    vo[key] = value

            if 'buttonsStates' in data:
                vo['buttonsStates'] = data['buttonsStates']
            else:
                vo['buttonsStates'] = {}
            if 'bgIconHeight' in data:
                vo['bgIconHeight'] = data['bgIconHeight']
        vo['message'] = super(_MessageTemplate, self).format(ctx=ctx, sourceKey='message')
        return vo

    def priority(self):
        pass


class MessageTemplates(templates.XMLCollection):

    def format(self, key, ctx = None, **kwargs):
        bgIconSource = kwargs.pop('bgIconSource', None)
        formatted = super(MessageTemplates, self).format(key, ctx, **kwargs)
        source = formatted['bgIcon']
        if bgIconSource in source:
            formatted['bgIcon'] = source[bgIconSource]
        else:
            formatted['bgIcon'] = source.get(None, '')
        return formatted

    def priority(self, key):
        return self[key].priority

    def __missing__(self, key):
        self[key] = value = _MessageTemplate(key, {}, NotificationPriorityLevel.MEDIUM)
        return value

    def _make(self, source):
        sourceID = source.name
        data = {'type': source.readString('type'),
         'timestamp': -1,
         'savedData': None,
         'bgIcon': self._makeBgIconsData(source['bgIcon']),
         'icon': source.readString('icon'),
         'defaultIcon': source.readString('defaultIcon'),
         'filters': [],
         'buttonsLayout': []}
        priority = source.readString('priority', NotificationPriorityLevel.MEDIUM)
        if priority not in NotificationPriorityLevel.RANGE:
            LOG_WARNING('Priority is invalid', sourceID, priority)
            priority = NotificationPriorityLevel.MEDIUM
        message = html_translation(source.readString('message'))
        section = source['filters']
        if section is None:
            section = {}
        for _, subSec in section.items():
            data['filters'].append({'name': subSec.readString('name'),
             'color': subSec.readString('color')})

        section = source['buttonsLayout']
        if section is not None:
            layout = data['buttonsLayout']
            buttonTypes = set([])
            for _, subSec in section.items():
                button = self._makeButtonData(sourceID, subSec)
                if button is None:
                    continue
                buttonType = button['type']
                if buttonType in buttonTypes:
                    LOG_WARNING('Duplicated type of button', sourceID, buttonType)
                    continue
                buttonTypes.add(buttonType)
                layout.append(button)

        return _MessageTemplate(message, data, priority)

    def _makeButtonData(self, sourceID, section):
        action = section.readString('action')
        if not action:
            LOG_WARNING('button/action is not defined', sourceID)
            return None
        else:
            label = html_translation(section.readString('label'))
            if not label:
                LOG_WARNING('button/label is not defined', sourceID)
                return None
            buttonType = section.readString('type')
            if not buttonType and buttonType not in ('submit', 'cancel'):
                LOG_WARNING('button/type is not defined or invalid', sourceID, buttonType)
                return None
            result = {'label': label,
             'type': buttonType,
             'action': action}
            width = section.readInt('width')
            if width > 0:
                result['width'] = width
            return result

    def _makeBgIconsData(self, section):
        result = {}
        if section is not None:
            result[None] = section.readString('')
            if len(section.items()):
                for secName, subSec in section.items():
                    result[secName] = subSec.readString('')

        return result


def loadForMessage(_, section, settings):
    settings.msgTemplates.load(section=section)


def loadForOthers(_, section, settings):
    settings.htmlTemplates.load(section=section)
