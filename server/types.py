# Taken from pyspades project
# https://github.com/infogulch/pyspades/blob/evented/pyspades/types.py
# Fixed some errors

# Copyright (c) Mathias Kaerlev 2011-2012.

# This file is part of pyspades.

# pyspades is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyspades is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyspades.  If not, see <http://www.gnu.org/licenses/>.

class DictItem(object):
    keys = None
    value = None
    
    def __init__(self, keys, value):
        self.keys = keys
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

class MultikeyDict(dict):
    """
    dict with multiple keys, i.e.
        
        foo = MultikeyDict()
        foo[(1, 'bar')] = 'hello'
        foo[1] == foo['bar'] == 'hello'
    
    To delete: "del foo[1]" or "del foo['bar']" or "del foo['hello']"
    
    This is an alternative to maintaining 2 seperate dicts for e.g. player
    IDs and their names, so you can do both dict[player_id] and 
    dict[player_name].
    """

    def __init__(self, *arg, **kw):
        dict.__init__(self, *arg, **kw)
        self.value_set = set()
    
    def __getitem__(self, key):
        item = dict.__getitem__(self, key)
        return item.value
    
    def __delitem__(self, key):
        item = dict.__getitem__(self, key)
        for key in item.keys:
            dict.__delitem__(self, key)
        self.value_set.remove(item.value)
    
    def __setitem__(self, keys, value):
        keys = list(keys)
        keys.append(value)
        new_item = DictItem(keys, value)
        self.value_set.add(value)
        for key in keys:
            if key in self:
                raise KeyError('key %s already exists' % key)
            dict.__setitem__(self, key, new_item)
    
    def get(self, key, default = None):
        return self[key] if key in self else default
    
    def clear(self):
        dict.clear(self)
        self.value_set.clear()
    
    def values(self):
        return self.value_set
    
    def itervalues(self):
        return iter(self.value_set)
    
    def __len__(self):
        return len(self.value_set)
