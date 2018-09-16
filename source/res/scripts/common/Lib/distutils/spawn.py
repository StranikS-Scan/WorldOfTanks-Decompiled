# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/spawn.py
__revision__ = '$Id$'
import sys
import os
from distutils.errors import DistutilsPlatformError, DistutilsExecError
from distutils.debug import DEBUG
from distutils import log

def spawn(cmd, search_path=1, verbose=0, dry_run=0):
    cmd = list(cmd)
    if os.name == 'posix':
        _spawn_posix(cmd, search_path, dry_run=dry_run)
    elif os.name == 'nt':
        _spawn_nt(cmd, search_path, dry_run=dry_run)
    elif os.name == 'os2':
        _spawn_os2(cmd, search_path, dry_run=dry_run)
    else:
        raise DistutilsPlatformError, "don't know how to spawn programs on platform '%s'" % os.name


def _nt_quote_args(args):
    for i, arg in enumerate(args):
        if ' ' in arg:
            args[i] = '"%s"' % arg

    return args


def _spawn_nt(cmd, search_path=1, verbose=0, dry_run=0):
    executable = cmd[0]
    cmd = _nt_quote_args(cmd)
    if search_path:
        executable = find_executable(executable) or executable
    log.info(' '.join([executable] + cmd[1:]))
    if not dry_run:
        try:
            rc = os.spawnv(os.P_WAIT, executable, cmd)
        except OSError as exc:
            if not DEBUG:
                cmd = executable
            raise DistutilsExecError, 'command %r failed: %s' % (cmd, exc[-1])

        if rc != 0:
            if not DEBUG:
                cmd = executable
            raise DistutilsExecError, 'command %r failed with exit status %d' % (cmd, rc)


def _spawn_os2(cmd, search_path=1, verbose=0, dry_run=0):
    executable = cmd[0]
    if search_path:
        executable = find_executable(executable) or executable
    log.info(' '.join([executable] + cmd[1:]))
    if not dry_run:
        try:
            rc = os.spawnv(os.P_WAIT, executable, cmd)
        except OSError as exc:
            if not DEBUG:
                cmd = executable
            raise DistutilsExecError, 'command %r failed: %s' % (cmd, exc[-1])

        if rc != 0:
            if not DEBUG:
                cmd = executable
            log.debug('command %r failed with exit status %d' % (cmd, rc))
            raise DistutilsExecError, 'command %r failed with exit status %d' % (cmd, rc)


if sys.platform == 'darwin':
    from distutils import sysconfig
    _cfg_target = None
    _cfg_target_split = None

def _spawn_posix(cmd, search_path=1, verbose=0, dry_run=0):
    global _cfg_target
    global _cfg_target_split
    log.info(' '.join(cmd))
    if dry_run:
        return
    else:
        executable = cmd[0]
        exec_fn = search_path and os.execvp or os.execv
        env = None
        if sys.platform == 'darwin':
            if _cfg_target is None:
                _cfg_target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET') or ''
                if _cfg_target:
                    _cfg_target_split = [ int(x) for x in _cfg_target.split('.') ]
            if _cfg_target:
                cur_target = os.environ.get('MACOSX_DEPLOYMENT_TARGET', _cfg_target)
                if _cfg_target_split > [ int(x) for x in cur_target.split('.') ]:
                    my_msg = '$MACOSX_DEPLOYMENT_TARGET mismatch: now "%s" but "%s" during configure' % (cur_target, _cfg_target)
                    raise DistutilsPlatformError(my_msg)
                env = dict(os.environ, MACOSX_DEPLOYMENT_TARGET=cur_target)
                exec_fn = search_path and os.execvpe or os.execve
        pid = os.fork()
        if pid == 0:
            try:
                if env is None:
                    exec_fn(executable, cmd)
                else:
                    exec_fn(executable, cmd, env)
            except OSError as e:
                if not DEBUG:
                    cmd = executable
                sys.stderr.write('unable to execute %r: %s\n' % (cmd, e.strerror))
                os._exit(1)

            if not DEBUG:
                cmd = executable
            sys.stderr.write('unable to execute %r for unknown reasons' % cmd)
            os._exit(1)
        else:
            while 1:
                try:
                    pid, status = os.waitpid(pid, 0)
                except OSError as exc:
                    import errno
                    if exc.errno == errno.EINTR:
                        continue
                    if not DEBUG:
                        cmd = executable
                    raise DistutilsExecError, 'command %r failed: %s' % (cmd, exc[-1])

                if os.WIFSIGNALED(status):
                    if not DEBUG:
                        cmd = executable
                    raise DistutilsExecError, 'command %r terminated by signal %d' % (cmd, os.WTERMSIG(status))
                if os.WIFEXITED(status):
                    exit_status = os.WEXITSTATUS(status)
                    if exit_status == 0:
                        return
                    if not DEBUG:
                        cmd = executable
                    raise DistutilsExecError, 'command %r failed with exit status %d' % (cmd, exit_status)
                if os.WIFSTOPPED(status):
                    continue
                if not DEBUG:
                    cmd = executable
                raise DistutilsExecError, 'unknown error executing %r: termination status %d' % (cmd, status)

        return


def find_executable(executable, path=None):
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    base, ext = os.path.splitext(executable)
    if (sys.platform == 'win32' or os.name == 'os2') and ext != '.exe':
        executable = executable + '.exe'
    if not os.path.isfile(executable):
        for p in paths:
            f = os.path.join(p, executable)
            if os.path.isfile(f):
                return f

        return
    else:
        return executable
        return
