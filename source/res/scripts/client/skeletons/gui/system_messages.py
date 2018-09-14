# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/system_messages.py


class ISystemMessages(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def pushMessage(self, text, type, priority=None, messageData=None):
        """
        Push system message
        
        :param text: message's body text
        :param type: message's type
        :param priority: message's priority
        :param messageData: dict, contains data for keywords replacement in notification's templates
        """
        raise NotImplementedError

    def pushI18nMessage(self, key, *args, **kwargs):
        """
        Push localized system message using i18n-key
        
        :param key: i18n-key
        :param args: contains data for keywords replacement in localized text
        :param kwargs: contains different data such as notification type, priority and
                       data for keywords replacement in localized text and
                       data for keywords replacement in notification's templates (messageData)
        """
        raise NotImplementedError
