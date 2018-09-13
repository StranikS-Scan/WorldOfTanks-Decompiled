# Embedded file name: scripts/client/messenger/__init__.py
from messenger.m_settings import MessengerSettings

class error(Exception):
    pass


g_settings = MessengerSettings()
