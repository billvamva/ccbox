import io
from typing import Union, List, Dict, Optional, Any, ClassVar, Callable

class NamedTextIOWrapper(io.TextIOWrapper):
    def __init__(self, buffer, _name=None, **kwargs):
        vars(self)['_name'] = _name
        super().__init__(buffer, **kwargs)

    def __getattribute__(self, _name):
        if _name == '_name':
            return vars(self)['_name']
        return super().__getattribute__(_name)
