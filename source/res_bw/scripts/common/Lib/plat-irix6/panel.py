# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-irix6/panel.py
from warnings import warnpy3k
warnpy3k('the panel module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
import pnl
debug = 0

def is_list(x):
    return type(x) == type([])


def reverse(list):
    res = []
    for item in list:
        res.insert(0, item)

    return res


def getattrlist(list, name):
    for item in list:
        if item and is_list(item) and item[0] == name:
            return item[1:]

    return []


def getproplist(list, name):
    for item in list:
        if item and is_list(item) and item[0] == 'prop':
            if len(item) > 1 and item[1] == name:
                return item[2:]

    return []


def is_endgroup(list):
    x = getproplist(list, 'end-of-group')
    return x and x[0] == '#t'


def show_actuator(prefix, a):
    for item in a:
        if not is_list(item):
            print prefix, item
        if item and item[0] == 'al':
            print prefix, 'Subactuator list:'
            for a in item[1:]:
                show_actuator(prefix + '    ', a)

        if len(item) == 2:
            print prefix, item[0], '=>', item[1]
        if len(item) == 3 and item[0] == 'prop':
            print prefix, 'Prop', item[1], '=>',
            print item[2]
        print prefix, '?', item


def show_panel(prefix, p):
    for item in p:
        if not is_list(item):
            print prefix, item
        if item and item[0] == 'al':
            print prefix, 'Actuator list:'
            for a in item[1:]:
                show_actuator(prefix + '    ', a)

        if len(item) == 2:
            print prefix, item[0], '=>', item[1]
        if len(item) == 3 and item[0] == 'prop':
            print prefix, 'Prop', item[1], '=>',
            print item[2]
        print prefix, '?', item


panel_error = 'panel error'

def dummy_callback(arg):
    pass


def assign_members(target, attrlist, exclist, prefix):
    for item in attrlist:
        if is_list(item) and len(item) == 2 and item[0] not in exclist:
            name, value = item[0], item[1]
            ok = 1
            if value[0] in '-0123456789':
                value = eval(value)
            elif value[0] == '"':
                value = value[1:-1]
            elif value == 'move-then-resize':
                ok = 0
            else:
                print 'unknown value', value, 'for', name
                ok = 0
            if ok:
                lhs = 'target.' + prefix + name
                stmt = lhs + '=' + repr(value)
                if debug:
                    print 'exec', stmt
                try:
                    exec stmt + '\n'
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    print 'assign failed:', stmt


def build_actuator(descr):
    namelist = getattrlist(descr, 'name')
    if namelist:
        actuatorname = namelist[0][1:-1]
    else:
        actuatorname = ''
    type = descr[0]
    if type[:4] == 'pnl_':
        type = type[4:]
    act = pnl.mkact(type)
    act.downfunc = act.activefunc = act.upfunc = dummy_callback
    assign_members(act, descr[1:], ['al', 'data', 'name'], '')
    datalist = getattrlist(descr, 'data')
    prefix = ''
    if type[-4:] == 'puck':
        prefix = 'puck_'
    elif type == 'mouse':
        prefix = 'mouse_'
    assign_members(act, datalist, [], prefix)
    return (act, actuatorname)


def build_subactuators(panel, super_act, al):
    for a in al:
        act, name = build_actuator(a)
        act.addsubact(super_act)
        if name:
            stmt = 'panel.' + name + ' = act'
            if debug:
                print 'exec', stmt
            exec stmt + '\n'
        if is_endgroup(a):
            panel.endgroup()
        sub_al = getattrlist(a, 'al')
        if sub_al:
            build_subactuators(panel, act, sub_al)

    super_act.fixact()


def build_panel(descr):
    if not descr or descr[0] != 'panel':
        raise panel_error, 'panel description must start with "panel"'
    if debug:
        show_panel('', descr)
    panel = pnl.mkpanel()
    assign_members(panel, descr[1:], ['al'], '')
    al = getattrlist(descr, 'al')
    al = reverse(al)
    for a in al:
        act, name = build_actuator(a)
        act.addact(panel)
        if name:
            stmt = 'panel.' + name + ' = act'
            exec stmt + '\n'
        if is_endgroup(a):
            panel.endgroup()
        sub_al = getattrlist(a, 'al')
        if sub_al:
            build_subactuators(panel, act, sub_al)

    return panel


def my_dopanel():
    a, down, active, up = pnl.dopanel()[:4]
    if down:
        down.downfunc(down)
    if active:
        active.activefunc(active)
    if up:
        up.upfunc(up)
    return a


def defpanellist(file):
    import panelparser
    descrlist = panelparser.parse_file(open(file, 'r'))
    panellist = []
    for descr in descrlist:
        panellist.append(build_panel(descr))

    return panellist


from pnl import *
dopanel = my_dopanel
