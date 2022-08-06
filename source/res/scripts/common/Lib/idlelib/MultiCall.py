# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/MultiCall.py
import sys
import string
import re
import Tkinter
MC_KEYPRESS = 0
MC_KEYRELEASE = 1
MC_BUTTONPRESS = 2
MC_BUTTONRELEASE = 3
MC_ACTIVATE = 4
MC_CIRCULATE = 5
MC_COLORMAP = 6
MC_CONFIGURE = 7
MC_DEACTIVATE = 8
MC_DESTROY = 9
MC_ENTER = 10
MC_EXPOSE = 11
MC_FOCUSIN = 12
MC_FOCUSOUT = 13
MC_GRAVITY = 14
MC_LEAVE = 15
MC_MAP = 16
MC_MOTION = 17
MC_MOUSEWHEEL = 18
MC_PROPERTY = 19
MC_REPARENT = 20
MC_UNMAP = 21
MC_VISIBILITY = 22
MC_SHIFT = 1
MC_CONTROL = 4
MC_ALT = 8
MC_META = 32
MC_OPTION = 64
MC_COMMAND = 128
if sys.platform == 'darwin':
    _modifiers = (('Shift',),
     ('Control',),
     ('Option',),
     ('Command',))
    _modifier_masks = (MC_SHIFT,
     MC_CONTROL,
     MC_OPTION,
     MC_COMMAND)
else:
    _modifiers = (('Control',),
     ('Alt',),
     ('Shift',),
     ('Meta', 'M'))
    _modifier_masks = (MC_CONTROL,
     MC_ALT,
     MC_SHIFT,
     MC_META)
_modifier_names = dict([ (name, number) for number in range(len(_modifiers)) for name in _modifiers[number] ])

class _SimpleBinder:

    def __init__(self, type, widget, widgetinst):
        self.type = type
        self.sequence = '<' + _types[type][0] + '>'
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = []
        self.handlerid = None
        return

    def bind(self, triplet, func):
        if not self.handlerid:

            def handler(event, l=self.bindedfuncs, mc_type=self.type):
                event.mc_type = mc_type
                wascalled = {}
                for i in range(len(l) - 1, -1, -1):
                    func = l[i]
                    if func not in wascalled:
                        wascalled[func] = True
                        r = func(event)
                        if r:
                            return r

            self.handlerid = self.widget.bind(self.widgetinst, self.sequence, handler)
        self.bindedfuncs.append(func)

    def unbind(self, triplet, func):
        self.bindedfuncs.remove(func)
        if not self.bindedfuncs:
            self.widget.unbind(self.widgetinst, self.sequence, self.handlerid)
            self.handlerid = None
        return

    def __del__(self):
        if self.handlerid:
            self.widget.unbind(self.widgetinst, self.sequence, self.handlerid)


_states = range(1 << len(_modifiers))
_state_names = [ ''.join((m[0] + '-' for i, m in enumerate(_modifiers) if 1 << i & s)) for s in _states ]

def expand_substates(states):

    def nbits(n):
        nb = 0
        while n:
            n, rem = divmod(n, 2)
            nb += rem

        return nb

    statelist = []
    for state in states:
        substates = list(set((state & x for x in states)))
        substates.sort(key=nbits, reverse=True)
        statelist.append(substates)

    return statelist


_state_subsets = expand_substates(_states)
_state_codes = []
for s in _states:
    r = 0
    for i in range(len(_modifiers)):
        if 1 << i & s:
            r |= _modifier_masks[i]

    _state_codes.append(r)

class _ComplexBinder:

    def __create_handler(self, lists, mc_type, mc_state):

        def handler(event, lists=lists, mc_type=mc_type, mc_state=mc_state, ishandlerrunning=self.ishandlerrunning, doafterhandler=self.doafterhandler):
            ishandlerrunning[:] = [True]
            event.mc_type = mc_type
            event.mc_state = mc_state
            wascalled = {}
            r = None
            for l in lists:
                for i in range(len(l) - 1, -1, -1):
                    func = l[i]
                    if func not in wascalled:
                        wascalled[func] = True
                        r = l[i](event)
                        if r:
                            break

                if r:
                    break

            ishandlerrunning[:] = []
            for f in doafterhandler:
                f()

            doafterhandler[:] = []
            return r if r else None

        return handler

    def __init__(self, type, widget, widgetinst):
        self.type = type
        self.typename = _types[type][0]
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = {None: [ [] for s in _states ]}
        self.handlerids = []
        self.ishandlerrunning = []
        self.doafterhandler = []
        for s in _states:
            lists = [ self.bindedfuncs[None][i] for i in _state_subsets[s] ]
            handler = self.__create_handler(lists, type, _state_codes[s])
            seq = '<' + _state_names[s] + self.typename + '>'
            self.handlerids.append((seq, self.widget.bind(self.widgetinst, seq, handler)))

        return

    def bind(self, triplet, func):
        if triplet[2] not in self.bindedfuncs:
            self.bindedfuncs[triplet[2]] = [ [] for s in _states ]
            for s in _states:
                lists = [ self.bindedfuncs[detail][i] for detail in (triplet[2], None) for i in _state_subsets[s] ]
                handler = self.__create_handler(lists, self.type, _state_codes[s])
                seq = '<%s%s-%s>' % (_state_names[s], self.typename, triplet[2])
                self.handlerids.append((seq, self.widget.bind(self.widgetinst, seq, handler)))

        doit = lambda : self.bindedfuncs[triplet[2]][triplet[0]].append(func)
        if not self.ishandlerrunning:
            doit()
        else:
            self.doafterhandler.append(doit)
        return

    def unbind(self, triplet, func):
        doit = lambda : self.bindedfuncs[triplet[2]][triplet[0]].remove(func)
        if not self.ishandlerrunning:
            doit()
        else:
            self.doafterhandler.append(doit)

    def __del__(self):
        for seq, id in self.handlerids:
            self.widget.unbind(self.widgetinst, seq, id)


_types = (('KeyPress', 'Key'),
 ('KeyRelease',),
 ('ButtonPress', 'Button'),
 ('ButtonRelease',),
 ('Activate',),
 ('Circulate',),
 ('Colormap',),
 ('Configure',),
 ('Deactivate',),
 ('Destroy',),
 ('Enter',),
 ('Expose',),
 ('FocusIn',),
 ('FocusOut',),
 ('Gravity',),
 ('Leave',),
 ('Map',),
 ('Motion',),
 ('MouseWheel',),
 ('Property',),
 ('Reparent',),
 ('Unmap',),
 ('Visibility',))
_binder_classes = (_ComplexBinder,) * 4 + (_SimpleBinder,) * (len(_types) - 4)
_type_names = dict([ (name, number) for number in range(len(_types)) for name in _types[number] ])
_keysym_re = re.compile('^\\w+$')
_button_re = re.compile('^[1-5]$')

def _parse_sequence(sequence):
    if not sequence or sequence[0] != '<' or sequence[-1] != '>':
        return
    else:
        words = string.split(sequence[1:-1], '-')
        modifiers = 0
        while words and words[0] in _modifier_names:
            modifiers |= 1 << _modifier_names[words[0]]
            del words[0]

        if words and words[0] in _type_names:
            type = _type_names[words[0]]
            del words[0]
        else:
            return
        if _binder_classes[type] is _SimpleBinder:
            if modifiers or words:
                return
            detail = None
        else:
            if type in [ _type_names[s] for s in ('KeyPress', 'KeyRelease') ]:
                type_re = _keysym_re
            else:
                type_re = _button_re
            if not words:
                detail = None
            elif len(words) == 1 and type_re.match(words[0]):
                detail = words[0]
            else:
                return
        return (modifiers, type, detail)


def _triplet_to_sequence(triplet):
    if triplet[2]:
        return '<' + _state_names[triplet[0]] + _types[triplet[1]][0] + '-' + triplet[2] + '>'
    else:
        return '<' + _state_names[triplet[0]] + _types[triplet[1]][0] + '>'


_multicall_dict = {}

def MultiCallCreator(widget):
    if widget in _multicall_dict:
        return _multicall_dict[widget]

    class MultiCall(widget):

        def __init__(self, *args, **kwargs):
            widget.__init__(self, *args, **kwargs)
            self.__eventinfo = {}
            self.__binders = [ _binder_classes[i](i, widget, self) for i in range(len(_types)) ]

        def bind(self, sequence=None, func=None, add=None):
            if type(sequence) is str and len(sequence) > 2 and sequence[:2] == '<<' and sequence[-2:] == '>>':
                if sequence in self.__eventinfo:
                    ei = self.__eventinfo[sequence]
                    if ei[0] is not None:
                        for triplet in ei[1]:
                            self.__binders[triplet[1]].unbind(triplet, ei[0])

                    ei[0] = func
                    if ei[0] is not None:
                        for triplet in ei[1]:
                            self.__binders[triplet[1]].bind(triplet, func)

                else:
                    self.__eventinfo[sequence] = [func, []]
            return widget.bind(self, sequence, func, add)

        def unbind(self, sequence, funcid=None):
            if type(sequence) is str and len(sequence) > 2 and sequence[:2] == '<<' and sequence[-2:] == '>>' and sequence in self.__eventinfo:
                func, triplets = self.__eventinfo[sequence]
                if func is not None:
                    for triplet in triplets:
                        self.__binders[triplet[1]].unbind(triplet, func)

                    self.__eventinfo[sequence][0] = None
            return widget.unbind(self, sequence, funcid)

        def event_add(self, virtual, *sequences):
            if virtual not in self.__eventinfo:
                self.__eventinfo[virtual] = [None, []]
            func, triplets = self.__eventinfo[virtual]
            for seq in sequences:
                triplet = _parse_sequence(seq)
                if triplet is None:
                    widget.event_add(self, virtual, seq)
                if func is not None:
                    self.__binders[triplet[1]].bind(triplet, func)
                triplets.append(triplet)

            return

        def event_delete(self, virtual, *sequences):
            if virtual not in self.__eventinfo:
                return
            else:
                func, triplets = self.__eventinfo[virtual]
                for seq in sequences:
                    triplet = _parse_sequence(seq)
                    if triplet is None:
                        widget.event_delete(self, virtual, seq)
                    if func is not None:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    triplets.remove(triplet)

                return

        def event_info(self, virtual=None):
            if virtual is None or virtual not in self.__eventinfo:
                return widget.event_info(self, virtual)
            else:
                return tuple(map(_triplet_to_sequence, self.__eventinfo[virtual][1])) + widget.event_info(self, virtual)
                return

        def __del__(self):
            for virtual in self.__eventinfo:
                func, triplets = self.__eventinfo[virtual]
                if func:
                    for triplet in triplets:
                        self.__binders[triplet[1]].unbind(triplet, func)

    _multicall_dict[widget] = MultiCall
    return MultiCall


def _multi_call(parent):
    root = Tkinter.Tk()
    root.title('Test MultiCall')
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry('+%d+%d' % (x, y + 150))
    text = MultiCallCreator(Tkinter.Text)(root)
    text.pack()

    def bindseq(seq, n=[0]):

        def handler(event):
            print seq

        text.bind('<<handler%d>>' % n[0], handler)
        text.event_add('<<handler%d>>' % n[0], seq)
        n[0] += 1

    bindseq('<Key>')
    bindseq('<Control-Key>')
    bindseq('<Alt-Key-a>')
    bindseq('<Control-Key-a>')
    bindseq('<Alt-Control-Key-a>')
    bindseq('<Key-b>')
    bindseq('<Control-Button-1>')
    bindseq('<Button-2>')
    bindseq('<Alt-Button-1>')
    bindseq('<FocusOut>')
    bindseq('<Enter>')
    bindseq('<Leave>')
    root.mainloop()


if __name__ == '__main__':
    from idlelib.idle_test.htest import run
    run(_multi_call)
