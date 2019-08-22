# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/hangars_switcher.py


class HangarNames(object):
    UNDEFINED = None
    FESTIVAL = 'festival'
    BATTLE_ROYALE = 'battle_royale'


class IHangarsSwitchManager(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def changeHangar(self, hangarName):
        raise NotImplementedError

    def registerHangarsSwitcher(self, switcher):
        raise NotImplementedError

    def unregisterHangarsSwitcher(self):
        raise NotImplementedError

    @property
    def lastHangarName(self):
        raise NotImplementedError


class IHangarsSwitcher(object):

    def switchToHangar(self, hangarName):
        raise NotImplementedError


class ISwitchersAutoSelector(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError


class IHangarPlaceManager(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def switchPlaceTo(self, placeName):
        raise NotImplementedError

    @property
    def currentPlace(self):
        raise NotImplementedError
