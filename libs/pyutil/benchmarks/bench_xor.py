#!/usr/bin/env python

#  Copyright (c) 2002-2010 Zooko Wilcox-O'Hearn
#  This file is part of pyutil; see README.rst for licensing terms.

import hmac
import random
import sys

from pyutil import benchfunc
from pyutil import randutil
from pyutil.assertutil import _assert
from pyutil.xor import xor

SFUNCS = [hmac._strxor, xor.py_xor,]

SFNAMES = ["hmac", "pyutil py",]
inputs = {}

def _help_init_string(N):
    global inputs
    if N not in inputs:
        inputs[N] = [randutil.insecurerandstr(N), randutil.insecurerandstr(N),]

def _help_make_bench_xor(f):
    def g(n):
        assert n in inputs
        _assert(isinstance(inputs[n][0], str), "Required to be a string.", inputs[n][0])
        assert len(inputs[n][0]) == n
        _assert(isinstance(inputs[n][1], str), "Required to be a string.", inputs[n][1])
        assert len(inputs[n][1]) == n
        for SF in SFUNCS:
            assert f(inputs[n][0], inputs[n][1]) == SF(inputs[n][0], inputs[n][1])

        return f(inputs[n][0], inputs[n][1])
    return g

def bench(SETSIZES=[2**x for x in range(0, 22, 3)]):
    random.seed(0)
    if len(SFUNCS) <= 1: print("")
    maxnamel = max(list(map(len, SFNAMES)))
    for SETSIZE in SETSIZES:
        seed = random.random()
        # print "seed: ", seed
        random.seed(seed)
        i = 0
        if len(SFUNCS) > 1: print("")
        for FUNC in SFUNCS:
            funcname = SFNAMES[i] + " " * (maxnamel - len(SFNAMES[i]))
            print("%s" % funcname, end=' ')
            sys.stdout.flush()
            benchfunc.rep_bench(_help_make_bench_xor(FUNC), SETSIZE, initfunc=_help_init_string, MAXREPS=2**9, MAXTIME=30)
            i = i + 1

bench()
