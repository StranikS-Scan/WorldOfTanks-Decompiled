# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/run.py
# Compiled at: 2010-05-25 20:46:16
import sys
import linecache
import time
import socket
import traceback
import thread
import threading
import Queue
import CallTips
import AutoComplete
import RemoteDebugger
import RemoteObjectBrowser
import StackViewer
import rpc
import __main__
LOCALHOST = '127.0.0.1'
try:
    import warnings
except ImportError:
    pass
else:

    def idle_formatwarning_subproc(message, category, filename, lineno, file=None, line=None):
        """Format warnings the IDLE way"""
        s = '\nWarning (from warnings module):\n'
        s += '  File "%s", line %s\n' % (filename, lineno)
        line = linecache.getline(filename, lineno).strip() if line is None else line
        if line:
            s += '    %s\n' % line
        s += '%s: %s\n' % (category.__name__, message)
        return s


    warnings.formatwarning = idle_formatwarning_subproc

exit_now = False
quitting = False
interruptable = False

def main(del_exitfunc=False):
    """Start the Python execution server in a subprocess
    
    In the Python subprocess, RPCServer is instantiated with handlerclass
    MyHandler, which inherits register/unregister methods from RPCHandler via
    the mix-in class SocketIO.
    
    When the RPCServer 'server' is instantiated, the TCPServer initialization
    creates an instance of run.MyHandler and calls its handle() method.
    handle() instantiates a run.Executive object, passing it a reference to the
    MyHandler object.  That reference is saved as attribute rpchandler of the
    Executive instance.  The Executive methods have access to the reference and
    can pass it on to entities that they command
    (e.g. RemoteDebugger.Debugger.start_debugger()).  The latter, in turn, can
    call MyHandler(SocketIO) register/unregister methods via the reference to
    register and unregister themselves.
    
    """
    global no_exitfunc
    global exit_now
    global quitting
    no_exitfunc = del_exitfunc
    port = 8833
    if sys.argv[1:]:
        port = int(sys.argv[1])
    sys.argv[:] = ['']
    sockthread = threading.Thread(target=manage_socket, name='SockThread', args=((LOCALHOST, port),))
    sockthread.setDaemon(True)
    sockthread.start()
    while 1:
        try:
            if exit_now:
                try:
                    exit()
                except KeyboardInterrupt:
                    continue

            try:
                seq, request = rpc.request_queue.get(block=True, timeout=0.05)
            except Queue.Empty:
                continue

            method, args, kwargs = request
            ret = method(*args, **kwargs)
            rpc.response_queue.put((seq, ret))
        except KeyboardInterrupt:
            if quitting:
                exit_now = True
            continue
        except SystemExit:
            raise
        except:
            type, value, tb = sys.exc_info()
            try:
                print_exception()
                rpc.response_queue.put((seq, None))
            except:
                traceback.print_exception(type, value, tb, file=sys.__stderr__)
                exit()
            else:
                continue

    return


def manage_socket(address):
    global exit_now
    for i in range(3):
        time.sleep(i)
        try:
            server = MyRPCServer(address, MyHandler)
            break
        except socket.error as err:
            print >> sys.__stderr__, 'IDLE Subprocess: socket error: ' + err[1] + ', retrying....'

    else:
        print >> sys.__stderr__, 'IDLE Subprocess: Connection to IDLE GUI failed, exiting.'
        show_socket_error(err, address)
        exit_now = True
        return

    server.handle_request()


def show_socket_error(err, address):
    import Tkinter
    import tkMessageBox
    root = Tkinter.Tk()
    root.withdraw()
    if err[0] == 61:
        msg = "IDLE's subprocess can't connect to %s:%d.  This may be due to your personal firewall configuration.  It is safe to allow this internal connection because no data is visible on external ports." % address
        tkMessageBox.showerror('IDLE Subprocess Error', msg, parent=root)
    else:
        tkMessageBox.showerror('IDLE Subprocess Error', 'Socket Error: %s' % err[1])
    root.destroy()


def print_exception():
    import linecache
    linecache.checkcache()
    flush_stdout()
    efile = sys.stderr
    typ, val, tb = excinfo = sys.exc_info()
    sys.last_type, sys.last_value, sys.last_traceback = excinfo
    tbe = traceback.extract_tb(tb)
    print >> efile, '\nTraceback (most recent call last):'
    exclude = ('run.py', 'rpc.py', 'threading.py', 'Queue.py', 'RemoteDebugger.py', 'bdb.py')
    cleanup_traceback(tbe, exclude)
    traceback.print_list(tbe, file=efile)
    lines = traceback.format_exception_only(typ, val)
    for line in lines:
        print >> efile, line,


def cleanup_traceback--- This code section failed: ---

 165       0	LOAD_FAST         'tb'
           3	SLICE+0           ''
           4	STORE_FAST        'orig_tb'

 166       7	SETUP_LOOP        '72'
          10	LOAD_FAST         'tb'
          13	JUMP_IF_FALSE     '71'

 167      16	SETUP_LOOP        '61'
          19	LOAD_FAST         'exclude'
          22	GET_ITER          ''
          23	FOR_ITER          '59'
          26	STORE_FAST        'rpcfile'

 168      29	LOAD_FAST         'tb'
          32	LOAD_CONST        0
          35	BINARY_SUBSCR     ''
          36	LOAD_CONST        0
          39	BINARY_SUBSCR     ''
          40	LOAD_ATTR         'count'
          43	LOAD_FAST         'rpcfile'
          46	CALL_FUNCTION_1   ''
          49	JUMP_IF_FALSE     '56'

 169      52	BREAK_LOOP        ''
          53	JUMP_BACK         '23'
          56	JUMP_BACK         '23'
          59	POP_BLOCK         ''

 171      60	BREAK_LOOP        ''
        61_0	COME_FROM         '16'

 172      61	LOAD_FAST         'tb'
          64	LOAD_CONST        0
          67	DELETE_SUBSCR     ''
          68	JUMP_BACK         '10'
          71	POP_BLOCK         ''
        72_0	COME_FROM         '7'

 173      72	SETUP_LOOP        '137'
          75	LOAD_FAST         'tb'
          78	JUMP_IF_FALSE     '136'

 174      81	SETUP_LOOP        '126'
          84	LOAD_FAST         'exclude'
          87	GET_ITER          ''
          88	FOR_ITER          '124'
          91	STORE_FAST        'rpcfile'

 175      94	LOAD_FAST         'tb'
          97	LOAD_CONST        -1
         100	BINARY_SUBSCR     ''
         101	LOAD_CONST        0
         104	BINARY_SUBSCR     ''
         105	LOAD_ATTR         'count'
         108	LOAD_FAST         'rpcfile'
         111	CALL_FUNCTION_1   ''
         114	JUMP_IF_FALSE     '121'

 176     117	BREAK_LOOP        ''
         118	JUMP_BACK         '88'
         121	JUMP_BACK         '88'
         124	POP_BLOCK         ''

 178     125	BREAK_LOOP        ''
       126_0	COME_FROM         '81'

 179     126	LOAD_FAST         'tb'
         129	LOAD_CONST        -1
         132	DELETE_SUBSCR     ''
         133	JUMP_BACK         '75'
         136	POP_BLOCK         ''
       137_0	COME_FROM         '72'

 180     137	LOAD_GLOBAL       'len'
         140	LOAD_FAST         'tb'
         143	CALL_FUNCTION_1   ''
         146	LOAD_CONST        0
         149	COMPARE_OP        '=='
         152	JUMP_IF_FALSE     '179'

 182     155	LOAD_FAST         'orig_tb'
         158	SLICE+0           ''
         159	LOAD_FAST         'tb'
         162	STORE_SLICE+0     ''

 183     163	LOAD_GLOBAL       'sys'
         166	LOAD_ATTR         'stderr'
         169	DUP_TOP           ''
         170	LOAD_CONST        '** IDLE Internal Exception: '
         173	ROT_TWO           ''
         174	PRINT_ITEM_TO     ''
         175	PRINT_NEWLINE_TO  ''
         176	JUMP_FORWARD      '179'
       179_0	COME_FROM         '176'

 184     179	LOAD_GLOBAL       'rpc'
         182	LOAD_ATTR         'objecttable'
         185	LOAD_CONST        'exec'
         188	BINARY_SUBSCR     ''
         189	LOAD_ATTR         'rpchandler'
         192	STORE_FAST        'rpchandler'

 185     195	SETUP_LOOP        '344'
         198	LOAD_GLOBAL       'range'
         201	LOAD_GLOBAL       'len'
         204	LOAD_FAST         'tb'
         207	CALL_FUNCTION_1   ''
         210	CALL_FUNCTION_1   ''
         213	GET_ITER          ''
         214	FOR_ITER          '343'
         217	STORE_FAST        'i'

 186     220	LOAD_FAST         'tb'
         223	LOAD_FAST         'i'
         226	BINARY_SUBSCR     ''
         227	UNPACK_SEQUENCE_4 ''
         230	STORE_FAST        'fn'
         233	STORE_FAST        'ln'
         236	STORE_FAST        'nm'
         239	STORE_FAST        'line'

 187     242	LOAD_FAST         'nm'
         245	LOAD_CONST        '?'
         248	COMPARE_OP        '=='
         251	JUMP_IF_FALSE     '263'

 188     254	LOAD_CONST        '-toplevel-'
         257	STORE_FAST        'nm'
         260	JUMP_FORWARD      '263'
       263_0	COME_FROM         '260'

 189     263	LOAD_FAST         'line'
         266	UNARY_NOT         ''
         267	JUMP_IF_FALSE     '318'
         270	LOAD_FAST         'fn'
         273	LOAD_ATTR         'startswith'
         276	LOAD_CONST        '<pyshell#'
         279	CALL_FUNCTION_1   ''
       282_0	COME_FROM         '267'
         282	JUMP_IF_FALSE     '318'

 190     285	LOAD_FAST         'rpchandler'
         288	LOAD_ATTR         'remotecall'
         291	LOAD_CONST        'linecache'
         294	LOAD_CONST        'getline'

 191     297	LOAD_FAST         'fn'
         300	LOAD_FAST         'ln'
         303	BUILD_TUPLE_2     ''
         306	BUILD_MAP         ''
         309	CALL_FUNCTION_4   ''
         312	STORE_FAST        'line'
         315	JUMP_FORWARD      '318'
       318_0	COME_FROM         '315'

 192     318	LOAD_FAST         'fn'
         321	LOAD_FAST         'ln'
         324	LOAD_FAST         'nm'
         327	LOAD_FAST         'line'
         330	BUILD_TUPLE_4     ''
         333	LOAD_FAST         'tb'
         336	LOAD_FAST         'i'
         339	STORE_SUBSCR      ''
         340	JUMP_BACK         '214'
         343	POP_BLOCK         ''
       344_0	COME_FROM         '195'

Syntax error at or near 'POP_BLOCK' token at offset 71


def flush_stdout():
    try:
        if sys.stdout.softspace:
            sys.stdout.softspace = 0
            sys.stdout.write('\n')
    except (AttributeError, EOFError):
        pass


def exit():
    """Exit subprocess, possibly after first deleting sys.exitfunc
    
    If config-main.cfg/.def 'General' 'delete-exitfunc' is True, then any
    sys.exitfunc will be removed before exiting.  (VPython support)
    
    """
    if no_exitfunc:
        try:
            del sys.exitfunc
        except AttributeError:
            pass

    sys.exit(0)


class MyRPCServer(rpc.RPCServer):

    def handle_error(self, request, client_address):
        """Override RPCServer method for IDLE
        
        Interrupt the MainThread and exit server if link is dropped.
        
        """
        global exit_now
        global quitting
        try:
            raise
        except SystemExit:
            raise
        except EOFError:
            exit_now = True
            thread.interrupt_main()
        except:
            erf = sys.__stderr__
            print >> erf, '\n' + '-' * 40
            print >> erf, 'Unhandled server exception!'
            print >> erf, 'Thread: %s' % threading.currentThread().getName()
            print >> erf, 'Client Address: ', client_address
            print >> erf, 'Request: ', repr(request)
            traceback.print_exc(file=erf)
            print >> erf, '\n*** Unrecoverable, server exiting!'
            print >> erf, '-' * 40
            quitting = True
            thread.interrupt_main()


class MyHandler(rpc.RPCHandler):

    def handle(self):
        """Override base method"""
        executive = Executive(self)
        self.register('exec', executive)
        sys.stdin = self.console = self.get_remote_proxy('stdin')
        sys.stdout = self.get_remote_proxy('stdout')
        sys.stderr = self.get_remote_proxy('stderr')
        import IOBinding
        sys.stdin.encoding = sys.stdout.encoding = sys.stderr.encoding = IOBinding.encoding
        self.interp = self.get_remote_proxy('interp')
        rpc.RPCHandler.getresponse(self, myseq=None, wait=0.05)
        return

    def exithook(self):
        """override SocketIO method - wait for MainThread to shut us down"""
        time.sleep(10)

    def EOFhook(self):
        """Override SocketIO method - terminate wait on callback and exit thread"""
        global quitting
        quitting = True
        thread.interrupt_main()

    def decode_interrupthook(self):
        """interrupt awakened thread"""
        global quitting
        quitting = True
        thread.interrupt_main()


class Executive(object):

    def __init__(self, rpchandler):
        self.rpchandler = rpchandler
        self.locals = __main__.__dict__
        self.calltip = CallTips.CallTips()
        self.autocomplete = AutoComplete.AutoComplete()

    def runcode(self, code):
        global interruptable
        try:
            self.usr_exc_info = None
            interruptable = True
            try:
                exec code in self.locals
            finally:
                interruptable = False

        except:
            self.usr_exc_info = sys.exc_info()
            if quitting:
                exit()
            print_exception()
            jit = self.rpchandler.console.getvar('<<toggle-jit-stack-viewer>>')
            if jit:
                self.rpchandler.interp.open_remote_stack_viewer()
        else:
            flush_stdout()

        return

    def interrupt_the_server(self):
        if interruptable:
            thread.interrupt_main()

    def start_the_debugger(self, gui_adap_oid):
        return RemoteDebugger.start_debugger(self.rpchandler, gui_adap_oid)

    def stop_the_debugger(self, idb_adap_oid):
        """Unregister the Idb Adapter.  Link objects and Idb then subject to GC"""
        self.rpchandler.unregister(idb_adap_oid)

    def get_the_calltip(self, name):
        return self.calltip.fetch_tip(name)

    def get_the_completion_list(self, what, mode):
        return self.autocomplete.fetch_completions(what, mode)

    def stackviewer(self, flist_oid=None):
        if self.usr_exc_info:
            typ, val, tb = self.usr_exc_info
        else:
            return
        flist = None
        if flist_oid is not None:
            flist = self.rpchandler.get_remote_proxy(flist_oid)
        while 1:
            tb = tb and tb.tb_frame.f_globals['__name__'] in ('rpc', 'run') and tb.tb_next

        sys.last_type = typ
        sys.last_value = val
        item = StackViewer.StackTreeItem(flist, tb)
        return RemoteObjectBrowser.remote_object_tree_item(item)