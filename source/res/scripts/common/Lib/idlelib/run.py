# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/run.py
import sys
import io
import linecache
import time
import socket
import traceback
import thread
import threading
import Queue
from idlelib import CallTips
from idlelib import AutoComplete
from idlelib import RemoteDebugger
from idlelib import RemoteObjectBrowser
from idlelib import StackViewer
from idlelib import rpc
from idlelib import PyShell
from idlelib import IOBinding
import __main__
LOCALHOST = '127.0.0.1'
import warnings

def idle_showwarning_subproc(message, category, filename, lineno, file=None, line=None):
    if file is None:
        file = sys.stderr
    try:
        file.write(PyShell.idle_formatwarning(message, category, filename, lineno, line))
    except IOError:
        pass

    return


_warnings_showwarning = None

def capture_warnings(capture):
    global _warnings_showwarning
    if capture:
        if _warnings_showwarning is None:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning_subproc
    elif _warnings_showwarning is not None:
        warnings.showwarning = _warnings_showwarning
        _warnings_showwarning = None
    return


capture_warnings(True)
exit_now = False
quitting = False
interruptable = False

def main(del_exitfunc=False):
    global no_exitfunc
    global exit_now
    global quitting
    no_exitfunc = del_exitfunc
    try:
        port = int(sys.argv[-1])
    except:
        print >> sys.stderr, 'IDLE Subprocess: no IP port passed in sys.argv.'
        return

    capture_warnings(True)
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
            capture_warnings(False)
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
            print >> sys.__stderr__, 'IDLE Subprocess: socket error: ' + err.args[1] + ', retrying....'

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
    if err.args[0] == 61:
        msg = "IDLE's subprocess can't connect to %s:%d.  This may be due to your personal firewall configuration.  It is safe to allow this internal connection because no data is visible on external ports." % address
        tkMessageBox.showerror('IDLE Subprocess Error', msg, parent=root)
    else:
        tkMessageBox.showerror('IDLE Subprocess Error', 'Socket Error: %s' % err.args[1])
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


def cleanup_traceback(tb, exclude):
    orig_tb = tb[:]
    while tb:
        for rpcfile in exclude:
            if tb[0][0].count(rpcfile):
                break
        else:
            break

        del tb[0]

    while tb:
        for rpcfile in exclude:
            if tb[-1][0].count(rpcfile):
                break
        else:
            break

        del tb[-1]

    if len(tb) == 0:
        tb[:] = orig_tb[:]
        print >> sys.stderr, '** IDLE Internal Exception: '
    rpchandler = rpc.objecttable['exec'].rpchandler
    for i in range(len(tb)):
        fn, ln, nm, line = tb[i]
        if nm == '?':
            nm = '-toplevel-'
        if not line and fn.startswith('<pyshell#'):
            line = rpchandler.remotecall('linecache', 'getline', (fn, ln), {})
        tb[i] = (fn,
         ln,
         nm,
         line)


def flush_stdout():
    try:
        if sys.stdout.softspace:
            sys.stdout.softspace = 0
            sys.stdout.write('\n')
    except (AttributeError, EOFError):
        pass


def exit():
    if no_exitfunc:
        try:
            del sys.exitfunc
        except AttributeError:
            pass

    capture_warnings(False)
    sys.exit(0)


class MyRPCServer(rpc.RPCServer):

    def handle_error(self, request, client_address):
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
        executive = Executive(self)
        self.register('exec', executive)
        self.console = self.get_remote_proxy('console')
        sys.stdin = PyShell.PseudoInputFile(self.console, 'stdin', IOBinding.encoding)
        sys.stdout = PyShell.PseudoOutputFile(self.console, 'stdout', IOBinding.encoding)
        sys.stderr = PyShell.PseudoOutputFile(self.console, 'stderr', IOBinding.encoding)
        self._keep_stdin = sys.stdin
        self.interp = self.get_remote_proxy('interp')
        rpc.RPCHandler.getresponse(self, myseq=None, wait=0.05)
        return

    def exithook(self):
        time.sleep(10)

    def EOFhook(self):
        global quitting
        quitting = True
        thread.interrupt_main()

    def decode_interrupthook(self):
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

        except SystemExit:
            pass
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
        while tb and tb.tb_frame.f_globals['__name__'] in ('rpc', 'run'):
            tb = tb.tb_next

        sys.last_type = typ
        sys.last_value = val
        item = StackViewer.StackTreeItem(flist, tb)
        return RemoteObjectBrowser.remote_object_tree_item(item)


capture_warnings(False)
