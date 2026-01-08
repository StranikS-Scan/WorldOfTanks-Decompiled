# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/updaters_common.py
from __future__ import absolute_import
import typing
import weakref
from events_containers.common.containers import ClientEventsContainer

class IViewUpdater(object):

    def initialize(self):
        pass

    def finalize(self):
        pass

    def destroy(self):
        pass


class ViewUpdatersCollection(object):

    def __init__(self):
        self.__updaters = []

    def initialize(self, updaters):
        self.__updaters = updaters
        for updater in self.__updaters:
            updater.initialize()

    def finalize(self):
        for updater in self.__updaters:
            updater.finalize()

    def destroy(self):
        updaters, self.__updaters = self.__updaters, []
        for updater in updaters:
            updater.destroy()


class ViewUpdater(ClientEventsContainer, IViewUpdater):

    def __init__(self, view):
        super(ViewUpdater, self).__init__()
        self.__view = weakref.proxy(view)

    @property
    def view(self):
        return self.__view

    def destroy(self):
        self.__view = None
        super(ViewUpdater, self).destroy()
        return
