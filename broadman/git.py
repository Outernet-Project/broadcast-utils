"""
Git wrapper functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
from os.path import abspath

from git import Repo, Actor

from . import path
from . import __version__


MSG_MARKER = '[OBM]'
AUTHOR = Actor("Outernet Broadman", "apps@outernet.is")


class Git():
    def __init__(self):
        repo = Repo(abspath(path.POOLDIR))
        index = repo.index
        self.add = index.add
        self.git = repo.git
        self.commit = index.commit
        self.remove = index.remove


def init():
    p = path.POOLDIR
    git = Repo.init(p)
    vfile = os.path.join(p, '.version')
    with open(vfile, 'w') as f:
        f.write(__version__ + '\n')
    git.index.add([vfile])
    git.index.commit('Initialized content pool', author=AUTHOR)


def has_changes(p):
    g = Git()
    """ Check whether some path contains changes """
    return g.git.status(p, s=True)


def get_history(p):
    g = Git()
    """ Get all commit hashes for a given path as a list """
    hashes = g.git.log(pretty='format:%H')
    return hashes.split('\n')


def commit(p, action, msg=None, extra_data=[], noadd=False):
    g = Git()
    if not noadd:
        g.add(p)
    cid = path.cid(p)
    if not cid:
        cid = 'BACKLOG'
    cmsg = [MSG_MARKER, action, cid]
    cmsg.extend(extra_data)
    cmsg = ' '.join(cmsg)
    if msg:
        cmsg += '\n\n' + msg
    g.commit(cmsg)


def commit_import(p):
    commit(p, action='IMP', msg='Imported new content')


def commit_add_to_server(p, server):
    cid = path.cid(p)
    msg = 'Added {} -> {}'.format(cid, server)
    commit(p, action='ADD', msg=msg, extra_data=[server])


def commit_remove_from_server(p, server):
    g = Git()
    g.remove([p], cached=True)
    cid = path.cid(p)
    msg = 'Removed {} <- {}'.format(cid, server)
    commit(p, action='DEL', msg=msg, extra_data=[server], noadd=True)


def commit_update(p):
    g = Git()
    has_history = len(get_history(p)) > 0
    g.add(p)
    changes = has_changes(p)
    if has_history:
        msg = 'Files changed:\n\n{}'.format(changes)
        action = 'UPD'
    else:
        msg = 'Files added:\n\n{}'.format(changes)
        action = 'NEW'
    commit(p, action, msg=msg, noadd=True)


def commit_backlog(processed):
    msg = 'Backlog processed:\n\n{}'.format('\n'.join(processed))
    commit(path.BROADCAST, action='BKL', msg=msg)


def revert(p):
    """ Revert given path to specified hash """
    g = Git()
    history = get_history(p)
    print(history)
    print(history[1])
    if len(history) < 2:
        raise ValueError('nothing to do')
    g.git.checkout(history[1], p=True)
    msg = 'Reverted {} to previous state'.format(history[1])
    commit(p, 'REV', msg=msg)


def reset(p):
    g = Git()
    """ Remove any changes on path """
    history = get_history(p)
    if len(history) < 1:
        raise ValueError('nothing to do')
    g.git.clean(f=True, d=True, p=True)
    g.git.checkout(history[0], p=True)


def remove(p):
    g = Git()
    """ Remove directory and all contents """
    g.remove([p])
    msg = 'Removed {} from pool'.format(p)
    commit(p, 'REM', msg)


def check_dir(dir):
    """ GitPython doesn't like absolute paths
    We check if the root of the provided path is the same as path.POOLDIR. If
    it is, we remove it. """
    p = path.POOLDIR
    if dir[:len(p)] == p:
        return dir[len(p):]

