# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_factory.py
from new_year.ny_controller import NewYearController
from new_year.ny_processor import NewYearCommandsProcessor
from new_year.ny_requester import NewYearRequester
from ny_common.settings import CURRENT_PDATA_KEY
from skeletons.festivity_factory import IFestivityFactory

class NewYearFactory(IFestivityFactory):

    def __init__(self):
        self.__requester = NewYearRequester()
        self.__processor = NewYearCommandsProcessor()
        self.__controller = NewYearController()
        self.__dataSyncKey = CURRENT_PDATA_KEY

    def getDataSyncKey(self):
        return self.__dataSyncKey

    def getRequester(self):
        return self.__requester

    def getProcessor(self):
        return self.__processor

    def getController(self):
        return self.__controller
