# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/factory.py
from festivity.festival.constants import FEST_DATA_SYNC_KEY
from festivity.festival.controller import FestivalController
from festivity.festival.command_processor import FestivalCommandsProcessor
from festivity.festival.requester import FestivalRequester
from skeletons.festivity_factory import IFestivityFactory

class FestivalFactory(IFestivityFactory):

    def __init__(self):
        self.__requester = FestivalRequester()
        self.__processor = FestivalCommandsProcessor()
        self.__controller = FestivalController()
        self.__dataSyncKey = FEST_DATA_SYNC_KEY

    def getDataSyncKey(self):
        return self.__dataSyncKey

    def getRequester(self):
        return self.__requester

    def getProcessor(self):
        return self.__processor

    def getController(self):
        return self.__controller
