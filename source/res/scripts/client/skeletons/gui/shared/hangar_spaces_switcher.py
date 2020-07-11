# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/hangar_spaces_switcher.py


class IHangarSpacesSwitcher(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    @property
    def itemsToSwitch(self):
        raise NotImplementedError

    @property
    def currentItem(self):
        raise NotImplementedError
