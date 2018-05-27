# Copyright (c) 2005-2010 Zooko Wilcox-O'Hearn
#  This file is part of pyutil; see README.rst for licensing terms.

import warnings
# from the Python Standard Library
from weakref import ref

# from the pyutil library
from .assertutil import precondition


# Thanks to Thomas Wouters, JP Calderone and the authors from the Python Cookbook.

# class WeakMethod copied from The Python Cookbook and simplified.

class WeakMethod:
    """ Wraps a function or, more importantly, a bound method, in
    a way that allows a bound method's object to be GC'd """
    def __init__(self, fn, callback=None):
        warnings.warn("deprecated", DeprecationWarning)
        precondition(hasattr(fn, 'im_self'), "fn is required to be a bound method.")
        self._cleanupcallback = callback
        self._obj = ref(fn.__self__, self.call_cleanup_cb)
        self._meth = fn.__func__

    def __call__(self, *args, **kws):
        s = self._obj()
        if s:
            return self._meth(s, *args,**kws)

    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name__, self._obj, self._meth,)

    def call_cleanup_cb(self, thedeadweakref):
        if self._cleanupcallback is not None:
            self._cleanupcallback(self, thedeadweakref)

def factory_function_name_here(o):
    if hasattr(o, 'im_self'):
        return WeakMethod(o)
    else:
        return o
