# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/dummy/df_factory.py
from festivity.dummy.df_controller import DummyController
from festivity.dummy.df_processor import DummyCommandsProcessor
from festivity.dummy.df_requester import DummyRequester
from skeletons.festivity_factory import IFestivityFactory

class DummyFactory(IFestivityFactory):

    def __init__(self):
        self.__requester = DummyRequester()
        self.__processor = DummyCommandsProcessor()
        self.__controller = DummyController()

    def getRequester(self):
        return self.__requester

    def getProcessor(self):
        return self.__processor

    def getController(self):
        return self.__controller
