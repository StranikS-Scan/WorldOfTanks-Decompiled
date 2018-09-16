# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/ConsoleCommands.py
import BigWorld
import FantasyDemo
import Avatar
import Math
import FDGUI
import re

def who(player, string):
    playerList = 'Players near you:\n'
    for i in BigWorld.entities.values():
        if i.__class__.__name__ == 'Avatar':
            playerList = playerList + i.playerName + '\n'

    FantasyDemo.addChatMsg(-1, playerList)


def help(player, string):
    if string:
        try:
            func = globals()[string]
            if callable(func) and func.__doc__:
                for s in func.__doc__.split('\n'):
                    FantasyDemo.addChatMsg(-1, s)

            else:
                raise 'Not callable'
        except:
            FantasyDemo.addChatMsg(-1, 'No help for ' + string)

    else:
        isCallable = lambda x: callable(globals()[x])
        ignoreList = ('getV4FromString', 'help')
        notIgnored = lambda x: x not in ignoreList
        keys = filter(isCallable, globals().keys())
        keys = filter(notIgnored, keys)
        keys.sort()
        FantasyDemo.addChatMsg(-1, '/help {command} for more info.')
        stripper = lambda c: c not in '[]\'"'
        string = filter(stripper, str(keys))
        FantasyDemo.addChatMsg(-1, string)


def target(player, string):
    t = BigWorld.target()
    if t:
        try:
            t.cell.directedChat(player.id, string)
            FantasyDemo.addChatMsg(player.id, '[To ' + t.playerName + '] ' + string)
        except:
            pass


def pushUp(player, string):
    player.pushUpKey()


def pullUp(player, string):
    player.pullUpKey()


def follow(player, string):
    if BigWorld.target() != None:
        player.physics.chase(BigWorld.target(), 2.0, 0.5)
        player.physics.velocity = (0, 0, 6.0)
    return


def summon(player, string):
    if isinstance(BigWorld.connectedEntity(), Avatar.Avatar):
        BigWorld.connectedEntity().cell.summonEntity(str(string))
    else:
        FantasyDemo.addChatMsg(-1, 'Summon can only be called when connected to the server')


def weather(player, string):
    import Weather
    Weather.weather().toggleRandomWeather(False)
    Weather.weather().summon(str(string))


def rain(player, string):
    import Weather
    Weather.weather().rain(float(string))


def getV4FromString(string):
    tokens = string.split(' ')
    v = [1,
     1,
     1,
     1]
    for i in tokens:
        try:
            v.append(float(i))
        except:
            pass

    return Math.Vector4(v[-4:])


def fog(player, string):
    import Weather
    Weather.weather().fog(getV4FromString(string))


def ambient(player, string):
    import Weather
    Weather.weather().ambient(getV4FromString(string))


def sunlight(player, string):
    import Weather
    Weather.weather().sun(getV4FromString(string))


def wave(player, string):
    player.playGesture(1)


def laugh(player, string):
    player.playGesture(16)


def cry(player, string):
    player.playGesture(3)


def point(player, string):
    player.playGesture(24)


def shrug(player, string):
    player.playGesture(4)


def yes(player, string):
    player.playGesture(19)


def no(player, string):
    player.playGesture(20)


def beckon(player, string):
    player.playGesture(21)


def fat(player, string):
    player.playGesture(44)


def skinny(player, string):
    player.playGesture(45)


def addTransportAccount(player, string):
    string = string.encode('utf8').strip()
    m = re.match('(.+?)\\s+(.+?)\\s+(.+)', string)
    if not m:
        FantasyDemo.addChatMsg(-1, 'Invalid transport registration details.', FDGUI.TEXT_COLOUR_SYSTEM)
        return
    transport = m.group(1)
    username = m.group(2)
    password = m.group(3)
    registerMsg = 'Attempting to register %s account %s.' % (transport, username)
    FantasyDemo.addChatMsg(-1, registerMsg, FDGUI.TEXT_COLOUR_SYSTEM)
    player.base.xmppTransportAccountRegister(transport, username, password)


def delTransportAccount(player, string):
    transport = string.encode('utf8').strip()
    wasFound = False
    for transportDetails in player.xmppTransportDetails:
        if not wasFound and transportDetails['transport'] == transport:
            wasFound = True

    if not wasFound:
        FantasyDemo.addChatMsg(-1, 'Transport not known.', FDGUI.TEXT_COLOUR_SYSTEM)
    else:
        player.base.xmppTransportAccountDeregister(transport)


def addFriend(player, string):
    if string.find('@') >= 0:
        transport = 'xmpp'
        if string.startswith('@'):
            FantasyDemo.addChatMsg(-1, 'Invalid IM friend name.', FDGUI.TEXT_COLOUR_SYSTEM)
            return
        imContents = string.rsplit(':', 1)
        friendID = imContents[0]
        if len(imContents) == 2:
            transport = imContents[1].encode('utf8').lower()
        if friendID.endswith('@'):
            friendID += 'eval.bigworldtech.com'
        friendsList = player.roster.findFriendsLike(friendID, transport)
        if len(friendsList):
            FantasyDemo.addChatMsg(-1, '%s is already a friend.' % friendID, FDGUI.TEXT_COLOUR_SYSTEM)
            return
        player.base.xmppAddFriend(friendID, transport)
    else:
        player.addFriend(string.encode('utf8'))


def delFriend(player, string):
    friendsList = player.roster.findFriendsLike(string)
    if not len(friendsList):
        player.delFriend(string.encode('utf8'))
    elif len(friendsList) > 1:
        FantasyDemo.addChatMsg(-1, "Found multiple friends that match '%s'.", FDGUI.TEXT_COLOUR_SYSTEM)
        for friendItem in friendsList:
            FantasyDemo.addChatMsg(-1, friendItem[0], FDGUI.TEXT_COLOUR_SYSTEM)

    else:
        friend = friendsList[0]
        player.base.xmppDelFriend(friend[0], friend[1])


def infoFriend(player, string):
    player.infoFriend(string)


def listFriends(player, string):
    player.listFriends()


def msgFriend(player, string):
    words = string.split(':', 1)
    if len(words) < 2:
        FantasyDemo.addChatMsg(-1, 'Invalid format - /help msgFriend for details', FDGUI.TEXT_COLOUR_SYSTEM)
        return
    recipient = words[0].strip()
    message = words[1].strip()
    if not len(message):
        FantasyDemo.addChatMsg(-1, 'Invalid format - /help msgFriend for details', FDGUI.TEXT_COLOUR_SYSTEM)
        return
    friendsList = player.roster.findFriendsLike(recipient)
    if not len(friendsList):
        player.msgFriend(recipient.encode('utf8'), message)
    elif len(friendsList) > 1:
        FantasyDemo.addChatMsg(-1, "Found multiple friends that match '%s'.", FDGUI.TEXT_COLOUR_SYSTEM)
        for friendItem in friendsList:
            FantasyDemo.addChatMsg(-1, friendItem[0], FDGUI.TEXT_COLOUR_SYSTEM)

    else:
        friend = friendsList[0]
        player.base.xmppMsgFriend(friend[0], friend[1], message)
        recipient = friend[0] + ' [IM]'
    FantasyDemo.addChatMsg(-1, 'You say to ' + recipient + ': ' + message, FDGUI.TEXT_COLOUR_YOU_SAY)


tell = msgFriend
t = msgFriend

def teleport(player, dst):
    try:
        spaceName, pointName = str(dst).rsplit(' ', 1)
    except ValueError:
        try:
            spaceName, pointName = str(dst).rsplit('/', 1)
        except ValueError:
            return

    BigWorld.player().tryToTeleport(spaceName, pointName)
    FantasyDemo.rds.fdgui.chatWindow.script.hideNow()


def addNote(player, description):
    if description == None or len(description) == 0:
        FantasyDemo.addChatMsg(-1, 'Must provide a note description')
    else:
        print 'Adding a note:', description
        if isinstance(description, unicode):
            description = description.encode('utf8')
        player.base.addNote(description)
    return


def getNotes(player, arg):
    player.base.getNotes()
