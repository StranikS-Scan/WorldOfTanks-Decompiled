# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/LobbyAutomation.py
import BigWorld
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import settings as app_settings
from AccountCommands import CMD_PRB_TEAM_READY
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader

def _getLobby():
    appLoader = dependency.descriptor(IAppLoader)
    return appLoader.getApp(app_settings.APP_NAME_SPACE.SF_LOBBY)


_isConnecting = False
_server = ''
_login = ''
_password = ''
_battleTime = 10
_arenaId = 1
_justLogin = True

def setServerName(name):
    global _server
    _server = name


def setLogin(login):
    global _login
    _login = login


def setPassword(password):
    global _password
    _password = password


def setBattleTime(time):
    global _battleTime
    _battleTime = time


def setArenaId(arenaId):
    global _arenaId
    _arenaId = arenaId


def configure(serverName, login, password, battleTime, arenaId):
    setServerName(serverName)
    setLogin(login)
    setPassword(password)
    setBattleTime(battleTime)
    setArenaId(arenaId)


def logIn():
    global _isConnecting
    global _justLogin
    _isConnecting = False
    _justLogin = True
    _detectCurrentScreen()


def startBattle():
    global _isConnecting
    global _justLogin
    _isConnecting = False
    _justLogin = False
    _detectCurrentScreen()


def _detectCurrentScreen():
    global _isConnecting
    if Waiting.isVisible():
        BigWorld.callback(0.2, _detectCurrentScreen)
        return
    else:
        lobby = _getLobby()
        if lobby is None or lobby.containerManager is None:
            BigWorld.callback(0.2, _detectCurrentScreen)
            return
        dialogsContainer = lobby.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if dialogsContainer is not None:
            dialog = dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EULA})
            if dialog is not None:
                dialog.onApply()
            dialog = dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: 'tGreetingDialog'})
            if dialog is not None:
                dialog.cancel()
        view = lobby.containerManager.getView(ViewTypes.DEFAULT)
        connectionMgr = dependency.instance(IConnectionManager)
        if view and view.alias == VIEW_ALIAS.LOGIN and view.isCreated() and connectionMgr.isDisconnected() and not _isConnecting:
            _isConnecting = True
            _connect()
            BigWorld.callback(0.2, _detectCurrentScreen)
            return
        view = lobby.containerManager.getView(ViewTypes.DEFAULT)
        if view is not None and view.alias == 'lobby':
            if _justLogin:
                return
            subView = lobby.containerManager.getView(ViewTypes.LOBBY_SUB)
            if subView.alias == 'hangar':
                _leaveDevRoom()
                BigWorld.callback(0.2, _detectCurrentScreen)
                return
            if subView.alias == 'trainingRoom':
                _enterBattle()
                return
        BigWorld.callback(0.2, _detectCurrentScreen)
        return


def _connect():
    connectionMgr = dependency.instance(IConnectionManager)
    connectionMgr.connect(_server, _login, _password, isNeedSavingPwd=True)


def _leaveDevRoom():
    BigWorld.player().prb_leave(lambda result: _enterDevRoom())


def _enterDevRoom():
    BigWorld.player().prb_createDev(_arenaId, _battleTime, '')


def _enterBattle():
    BigWorld.player()._doCmdInt3(CMD_PRB_TEAM_READY, 1, 1, 0, _battleCallback)
    BigWorld.player()._doCmdInt3(CMD_PRB_TEAM_READY, 2, 1, 0, _battleCallback)


def _battleCallback(p1, p2, p3):
    pass
