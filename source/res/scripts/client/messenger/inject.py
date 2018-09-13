# Embedded file name: scripts/client/messenger/inject.py
from messenger import MessengerEntry

class messengerEntryProperty(property):
    __messenger_entry_property__ = True


class channelsCtrlProperty(property):
    __channels_ctrl_property__ = True


class InjectMessengerEntry(type):

    def __new__(mcls, name, bases, namespace):
        cls = super(InjectMessengerEntry, mcls).__new__(mcls, name, bases, namespace)

        def getMessengerEntry(_):
            return MessengerEntry.g_instance

        def getChannelsCtrl(_):
            return MessengerEntry.g_instance.gui.channelsCtrl

        for name, value in namespace.items():
            if getattr(value, '__messenger_entry_property__', False):
                setattr(cls, name, property(getMessengerEntry))
            if getattr(value, '__channels_ctrl_property__', False):
                setattr(cls, name, property(getChannelsCtrl))

        return cls
