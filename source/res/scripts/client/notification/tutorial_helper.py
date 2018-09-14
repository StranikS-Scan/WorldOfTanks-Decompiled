# Embedded file name: scripts/client/notification/tutorial_helper.py
try:
    from tutorial import GlobalStorage as TutorialGlobalStorage
    from tutorial.control.context import GLOBAL_VAR as TUTORIAL_GLOBAL_VAR
except ImportError:

    class TutorialGlobalStorage(object):

        def __init__(self, *args):
            pass

        def __get__(self, instance, owner = None):
            if instance is None:
                return self
            else:
                return 0


    class TUTORIAL_GLOBAL_VAR(object):
        LAST_HISTORY_ID = ''
        SERVICE_MESSAGES_IDS = ''
