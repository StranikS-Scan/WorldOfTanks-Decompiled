# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/interfaces.py


class IProtoPlugin(object):
    """
    Interface for chat protocol.
    """
    __slots__ = ('__weakref__',)

    def connect(self, scope):
        """Connects client to required chat protocol.
        :param scope: integer that containing one of MESSENGER_SCOPE.*.
        """
        pass

    def disconnect(self):
        """Disconnects client from required chat protocol."""
        pass

    def view(self, scope):
        """Routine invokes when player starts to view GUI.
        :param scope: integer that containing one of MESSENGER_SCOPE.*.
        """
        pass

    def setFilters(self, msgFilterChain):
        """
        Sets shared filters to plugin.
        :param msgFilterChain: filter to change incoming/outgoing messages.
        """
        pass

    def init(self):
        """Initializes required chat protocol."""
        pass

    def clear(self):
        """Clears plugin data."""
        pass

    def isConnected(self):
        """Is plugin connected to specified chat server.
        :return: bool
        """
        return False


class IProtoSettings(object):
    """
    Settings for chat protocol.
    """

    def update(self, data):
        """
        Updates settings from data.
        :param data: dict
        """
        pass

    def clear(self):
        """
        Clears data.
        """
        pass

    def isEnabled(self):
        """
        Is protocol enabled.
        :return: bool
        """
        return False


class IProtoLimits(object):
    """
    Limits for chat protocol.
    """

    def getMessageMaxLength(self):
        """
        Gets max length of message in symbols.
        :return: integer containing max length.
        """
        raise NotImplementedError

    def getBroadcastCoolDown(self):
        """
        Gets value of coolDown between two message.
        :return: float containing coolDown in seconds.
        """
        raise NotImplementedError

    def getHistoryMaxLength(self):
        """
        Gets max length of message history.
        :return: integer containing max length.
        """
        raise NotImplementedError


class IBattleCommandFactory(object):
    """
    Interface of factory to create outgoing battle commands.
    """

    def createByName(self, name):
        """
        Creates command (decorator) by name.
        :param name: string containing name of command.
        :return: instance of OutChatCommand.
        """
        return None

    def createByNameTarget(self, name, targetID):
        """
        Creates command (decorator) by name and target (vehicle).
        :param name: string containing name of command.
        :param targetID: integer containing ID of target (vehicle).
        :return: instance of OutChatCommand.
        """
        return None

    def createByCellIdx(self, cellIdx):
        """
        Creates command (decorator) to indicate cell on the minimap.
        :param cellIdx: integer containing coordinates of cell on the minimap.
                        It equals row * size + column.
        :return: instance of OutChatCommand.
        """
        return None

    def create4Reload(self, isCassetteClip, timeLeft, quantity):
        """
        Creates command that gun is reloading, unavailable or ready.
        :param isCassetteClip: has vehicle cassette.
        :param timeLeft: time is left before charging.
        :param quantity: number of ammo that is selected.
        """
        return None

    def createSPGAimAreaCommand(self, desiredShotPosition, cellIdx, reloadTime):
        """
        Creates command contains position of spg aim marker on 3D scene and minimap.
        :param desiredShotPosition: coordinates on 3D scene
        :param cellIdx: integer containing bound coordinates of cell on the minimap.
        :param reloadTime: reloading time of ally spg
        :return: instance of _OutCmdDecorator.
        """
        return None


class IUnitCommandFactory(object):
    """
    Interface of factory to create outgoing unit commands.
    """

    def createByCellIdx(self, cellIdx):
        """
        Creates command (decorator) to indicate cell on the minimap.
        :param cellIdx: integer containing coordinates of cell on the minimap.
                        It equals row * size + column.
        :return: instance of OutChatCommand.
        """
        return None


class IEntityFindCriteria(object):
    """
    Interface of find criteria that uses to find entities in storage.
    """

    def filter(self, entity):
        """
        Return True if entity matches the search criteria, otherwise - False.
        :param entity: instance of entity.
        :return: bool
        """
        return False


class ISearchHandler(object):
    """
    Interface of search handler that uses in ISearchProcessor.
    """

    def onSearchComplete(self, result):
        """
        Routine invokes when search result received from server.
        :param result: list of entities found on a token.
        """
        pass

    def onSearchFailed(self, reason):
        """
        Routine invokes when search request is failed.
        :param reason: string containing i18n reason for failure.
        """
        pass

    def onExcludeFromSearch(self, entity):
        """
        Routine invokes when some entity has been excluded from search result. For
        example, channel has been destroyed.
        :param entity: instance of entity.
        """
        pass


class ISearchProcessor(object):
    """
    Interface of search processor that sends request to search entities on server.
    When it will receive response from server, than invokes handlers with result.
    """

    def addHandler(self, handler):
        """
        Adds search handler.
        :param handler: object that implemented ISearchHandler.
        :raise ValueError
        """
        pass

    def removeHandler(self, handler):
        """
        Removes search handler.
        :param handler: object that implemented ISearchHandler.
        """
        pass

    def find(self, token, **kwargs):
        """
        Sends request to search entities.
        :param token: string containing pattern for search.
        :param kwargs:
        :raise NotImplementedError
        """
        pass

    def getSearchResultLimit(self):
        """
        Gets max number of entities that can return server to search request.
        :raise NotImplementedError
        :return: integer containing max number of entities.
        """
        pass


class IChatMessage(object):
    """
    Interface for chat messages.
    """

    def getMessage(self):
        """
        Gets message of error.
        :return: string containing message.
        """
        pass


class IChatError(IChatMessage):
    """
    Interface for chat error that adds to event _MessengerEvents.onServerErrorReceived.
    """

    def getTitle(self):
        """
        Gets title of error.
        :return: string containing title.
        """
        pass

    def isModal(self):
        """
        Is error shown in dialog.
        :return: bool
        """
        return False


class IVOIPChatProvider(object):
    """
    Interface provides VOIP connection, parameters for the voice channel.
    """

    def getChannelParams(self):
        """
        Gets voice channel parameters.
        :return: tuple containing (uri, password)
        """
        pass

    def requestCredentials(self, reset=0):
        """
        Send the request to the server to receive a credentials.
        :param reset: generate new credentials.
        """
        pass

    def logVivoxLogin(self):
        """
        Logs event when client successfully logs-in into the Vivox.
        """
        pass


class IVOIPChatController(object):
    """
    This is an interface for VOIP chat controller.
    """

    def start(self):
        """
        Start VOIP controller. It is performed after user login.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stop VOIP controller. It is performed after user logoff (disconnect).
        """
        raise NotImplementedError

    def isReady(self):
        """
        Check if the controller is ready. It means VOIPManager is initialized.
        :return: bool with result
        """
        raise NotImplementedError

    def isPlayerSpeaking(self, accountDBID):
        """
        Check if the player is speaking
        :param accountDBID: player dbID
        :return: bool with result
        """
        raise NotImplementedError

    def isVOIPEnabled(self):
        """
        Check if VOIP is enabled in settings.
        :return: bool with result
        """
        raise NotImplementedError

    def isVivox(self):
        """
        Check if voip Vivox technology is supported.
        :return: bool with result
        """
        raise NotImplementedError

    def isYY(self):
        """
        Check if voip YY technology is supported.
        :return: bool with result
        """
        raise NotImplementedError

    def invalidateInitialization(self):
        """
        Invalidate initialization state. It may lead to onVoiceChatInitFailed event generating.
        """
        raise NotImplementedError

    def requestCaptureDevices(self, firstTime=False, callback=None):
        """
        Request sound capture devices. The result will be in the provided callback.
        :param firstTime: pass False here, usually the controller itself uses this param
        :param callback: pass callback if you are interested in a result
        """
        raise NotImplementedError


class IUserSearchLimits(object):

    def getMaxResultSize(self):
        raise NotImplementedError

    def getRequestCooldown(self):
        raise NotImplementedError
