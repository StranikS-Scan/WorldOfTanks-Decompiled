# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_factory.py
from new_year.ny_controller import NewYearController
from new_year.ny_processor import NewYearCommandsProcessor
from new_year.ny_requester import NewYearRequester
from skeletons.festivity_factory import IFestivityFactory
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from .customizable_objects_manager import CustomizableObjectsManager

def getNewYearConfig(manager):
    festivityFactory = NewYearFactory()
    manager.addInstance(IFestivityFactory, festivityFactory)

    def _create():
        customizableObjMgr = CustomizableObjectsManager()
        customizableObjMgr.init()
        manager.addInstance(INewYearController, festivityFactory.getController())
        return customizableObjMgr

    manager.addRuntime(ICustomizableObjectsManager, _create, finalizer='fini')


class NewYearFactory(IFestivityFactory):

    def __init__(self):
        self.__requester = NewYearRequester()
        self.__processor = NewYearCommandsProcessor()
        self.__controller = NewYearController()
        self.__dataSyncKey = 'newYear19'

    def getDataSyncKey(self):
        return self.__dataSyncKey

    def getRequester(self):
        return self.__requester

    def getProcessor(self):
        return self.__processor

    def getController(self):
        return self.__controller
