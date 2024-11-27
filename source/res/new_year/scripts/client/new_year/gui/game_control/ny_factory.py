# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_factory.py
from new_year.gui.game_control.ny_controller import NewYearController
from new_year.gui.shared.gui_items.processors.ny_processor import NewYearCommandsProcessor
from new_year.gui.shared.utils.ny_requester import NewYearRequester
from new_year.skeletons.new_year import INewYearController
from new_year_common.settings import CURRENT_PDATA_KEY
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

    def getChildControllerInterface(self):
        return INewYearController
