import re

protocols = None

# https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
import collections
import functools

class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)


class Protocols(object):
    class Protocol(object):
        def __init__(self, name, id, parent=None):
            self._id = id
            self._name = name
            self._parent = parent

        def __str__(self):
            return self._name

        def __repr__(self):
            if len(self._attributes()) > 0:
                return self._name + ' ' + str(self._attributes())
            else:
                return self._name

        def __int__(self):
            return self._id

        @memoized
        def _attributes(self):
            return [self.__dict__[attr] for attr in self.__dict__ 
                         if not attr.startswith('_')]

        @memoized
        def attr_from_id(self, value):
            for attr in self._attributes():
                if attr._id == value:
                    return attr
            return None

        @memoized
        def attr_from_name(self, value):
            for attr in self._attributes():
                if attr._name == value:
                    return attr
            return None

    def __repr__(self):
        return str([proto for proto in self.__dict__
                           if not proto.startswith('_')])

    def __init__(self, protocols):
        self.protoname_from_id = {}
        self.proto_from_name = {}
        for key in protocols.keys():
            self.__dict__[key] = Protocols.Protocol(key, protocols[key]['id'])
            self.protoname_from_id[protocols[key]['id']] = self.__dict__[key]
            self.proto_from_name[key] = self.__dict__[key]
            for key_attr in protocols[key]['attr'].keys():
                self.__dict__[key].__dict__[key_attr] = Protocols.Protocol(key_attr,
                                                                           protocols[key]['attr'][key_attr],
                                                                           self.__dict__[key])

    def proto_from_id(self, value):
        return self.protoname_from_id[value]


def _load():
    from pkg_resources import Requirement, resource_filename
    filename = resource_filename(Requirement.parse("network_spotlight_agentd"),
                                 "network_spotlight_agentd/ixe/protodef.proto")
    global protocols
    mpa = {}
    proto = {}
    current_proto = ''
    for l in open(filename).read().split('\n'):
        m_mpa = re.search('^  \(mpa ([a-zA-Z0-9_]*) ([\-0-9]*)\)$', l)
        m_proto = re.search('^  \(proto ([a-zA-Z0-9_]*) ([\-0-9]*)\)?$', l)
        m_proto_attr = re.search('^    \(([a-zA-Z0-9_]*) ([\-0-9]*)\)$', l)
        m_proto_attr_mpa = re.search('^    \(([a-zA-Z0-9_]*) mpa\)\)?$', l)
        if m_mpa:
            mpa[m_mpa.group(1)] = int(m_mpa.group(2))
        if m_proto:
            current_proto = m_proto.group(1)
            proto[current_proto] = {'id': int(m_proto.group(2)), 'attr': {}}
        if m_proto_attr:
            proto[current_proto]['attr'][m_proto_attr.group(1)] = int(m_proto_attr.group(2))
        if m_proto_attr_mpa:
            proto[current_proto]['attr'][m_proto_attr_mpa.group(1)] = mpa[m_proto_attr_mpa.group(1)]

    protocols = Protocols(proto)

_load()
