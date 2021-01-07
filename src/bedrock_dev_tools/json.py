from __future__ import annotations
from typing import Dict, Generic, IO, Iterator, List, NewType, Tuple, Type, TypeVar, Union
import re
import json
from json import scanner, JSONDecodeError  # type: ignore
from json.decoder import WHITESPACE, WHITESPACE_STR, scanstring  # type: ignore



# JSON Decoder
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
INLINE_COMMENT = re.compile(r'//[^\n]*\n?', FLAGS)
INLINE_COMMENT_STRING_START='//'
MULTILINE_COMMENT = re.compile(r"/[*]([^*]|([*][^/]))*[*]+/", FLAGS)
MULTILINE_COMMENT_STRING_START='/*'


def parse_object(
    s_and_end, strict, scan_once, object_hook, object_pairs_hook,
    memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR,
    _ilcs=INLINE_COMMENT_STRING_START, _ilc=INLINE_COMMENT.match,
    _mlcs=MULTILINE_COMMENT_STRING_START, _mlc=MULTILINE_COMMENT.match
):
    '''
    Modified json.decoder.JSONObject function from standard json module
    (python 3.7.7).
    '''
    s, end = s_and_end
    pairs = []
    pairs_append = pairs.append
    # Backwards compatibility
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    # Use a slice to prevent IndexError from being raised, the following
    # check will raise a more specific ValueError if the string is empty
    nextchar = s[end:end + 1]
    # Normally we expect nextchar == '"'
    if nextchar != '"':
        while True:  # Handle comments and whitespaces
            if nextchar in _ws:
                end = _w(s, end).end()
            elif s[end:].startswith(_ilcs):
                end = _ilc(s, end).end()
            elif s[end:].startswith(_mlcs):
                end = _mlc(s, end).end()
            else:
                break
            nextchar = s[end:end + 1]

        # Trivial empty object
        if nextchar == '}':
            if object_pairs_hook is not None:
                result = object_pairs_hook(pairs)
                return result, end + 1
            pairs = {}
            if object_hook is not None:
                pairs = object_hook(pairs)
            return pairs, end + 1
        elif nextchar != '"':
            raise JSONDecodeError(
                "Expecting property name enclosed in double quotes", s, end)
    end += 1
    while True:
        key, end = scanstring(s, end, strict)
        key = memo_get(key, key)
        # To skip some function call overhead we optimize the fast paths where
        # the JSON key separator is ": " or just ":".
        if s[end:end + 1] != ':':
            while True:  # Handle comments and whitespaces
                if s[end:end + 1] in _ws:
                    end = _w(s, end).end()
                elif s[end:].startswith(_ilcs):
                    end = _ilc(s, end).end()
                elif s[end:].startswith(_mlcs):
                    end = _mlc(s, end).end()
                else:
                    break
            if s[end:end + 1] != ':':
                raise JSONDecodeError("Expecting ':' delimiter", s, end)
        end += 1

        try:
            while True:  # Handle comments and whitespaces
                if s[end] in _ws:
                    end = _w(s, end).end()
                elif s[end:].startswith(_ilcs):
                    end = _ilc(s, end).end()
                elif s[end:].startswith(_mlcs):
                    end = _mlc(s, end).end()
                else:
                    break
        except IndexError:
            pass

        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        pairs_append((key, value))

        try:
            nextchar = s[end]
            while True:  # Handle comments and whitespaces
                if nextchar in _ws:
                    end = _w(s, end).end()
                elif s[end:].startswith(_ilcs):
                    end = _ilc(s, end).end()
                elif s[end:].startswith(_mlcs):
                    end = _mlc(s, end).end()
                else:
                    break
                nextchar = s[end]
        except IndexError:
            nextchar = ''
        end += 1

        if nextchar == '}':
            break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)

        while True:  # Handle comments and whitespaces
            if s[end] in _ws:
                end = _w(s, end).end()
            elif s[end:].startswith(_ilcs):
                end = _ilc(s, end).end()
            elif s[end:].startswith(_mlcs):
                end = _mlc(s, end).end()
            else:
                break
        nextchar = s[end:end + 1]
        end += 1
        if nextchar != '"':
            raise JSONDecodeError(
                "Expecting property name enclosed in double quotes", s, end - 1)
    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return result, end
    pairs = dict(pairs)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return pairs, end


def parse_array(
    s_and_end, scan_once, _w=WHITESPACE.match, _ws=WHITESPACE_STR,
    _ilcs=INLINE_COMMENT_STRING_START, _ilc=INLINE_COMMENT.match,
    _mlcs=MULTILINE_COMMENT_STRING_START, _mlc=MULTILINE_COMMENT.match
):
    '''
    Modified json.decoder.JSONArray function from standard module json
    (python 3.7.7).
    '''
    s, end = s_and_end
    values = []
    nextchar = s[end:end + 1]
    while True:  # Handle comments and whitespaces
        if nextchar in _ws:
            end = _w(s, end).end()
        elif s[end:].startswith(_ilcs):
            end = _ilc(s, end).end()
        elif s[end:].startswith(_mlcs):
            end = _mlc(s, end).end()
        else:
            break
        nextchar = s[end:end + 1]

    # Look-ahead for trivial empty array
    if nextchar == ']':
        return values, end + 1
    _append = values.append
    while True:
        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        _append(value)
        nextchar = s[end:end + 1]

        while True:  # Handle comments and whitespaces
            if nextchar in _ws:
                end = _w(s, end).end()
            elif s[end:].startswith(_ilcs):
                end = _ilc(s, end).end()
            elif s[end:].startswith(_mlcs):
                end = _mlc(s, end).end()
            else:
                break
            nextchar = s[end:end + 1]
        end += 1

        if nextchar == ']':
            break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)

        try:
            while True:  # Handle comments and whitespaces
                if s[end] in _ws:
                    end = _w(s, end).end()
                elif s[end:].startswith(_ilcs):
                    end = _ilc(s, end).end()
                elif s[end:].startswith(_mlcs):
                    end = _mlc(s, end).end()
                else:
                    break
        except IndexError:
            pass

    return values, end


class JSONCDecoder(json.JSONDecoder):
    '''
    JSONDecoder with support for C-style comments. Similar to JSONC files from
    Visual Studio code but without support for trailing commas.

    source:
    https://gist.github.com/Nusiq/4d6cc83a6acc8b373b5e56801d273ba3
    '''
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, *args, **kwargs)
        self.parse_object = parse_object
        self.parse_array = parse_array

        # we need to recreate the internal scan function ..
        self.scan_once = scanner.py_make_scanner(self)

    def decode(
        self, s, _w=WHITESPACE.match,
        _ws=WHITESPACE_STR,
        _ilcs=INLINE_COMMENT_STRING_START, _ilc=INLINE_COMMENT.match,
        _mlcs=MULTILINE_COMMENT_STRING_START, _mlc=MULTILINE_COMMENT.match
    ):
        idx = 0
        try:
            while True:  # Handle comments and whitespaces
                if s[idx] in _ws:
                    idx = _w(s, idx).end()
                elif s[idx:].startswith(_ilcs):
                    idx = _ilc(s, idx).end()
                elif s[idx:].startswith(_mlcs):
                    idx = _mlc(s, idx).end()
                else:
                    break
        except IndexError:
            pass
        obj, end = self.raw_decode(s, idx)
        end = _w(s, end).end()
        if end != len(s):
            raise JSONDecodeError("Extra data", s, end)
        return obj

# JSON Encoder
class CompactEncoder(json.JSONEncoder):
    '''
    JSONEncoder which tries to find a compromise between compact and multiline
    formatting from standard python json module. Creates relatively compact
    file which is also easy to read.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = -1
        self.respect_indent = True

    def _is_primitive(self, obj):
        return isinstance(obj, (int, bool, str, float))

    def encode(self, obj):
        '''
        Return a JSON string representation of a Python data structure.
        Example:
            >>> CompactEncoder().encode({"foo": ["bar", "baz"]})
            '{\\n\\t"foo": ["bar", "baz"]\\n}'
        '''
        return ''.join([i for i in self.iterencode(obj)])

    def iterencode(self, obj):
        '''
        Encode the given object and yield each string representation line by
        line.
        Example:
            >>> item = {"foo": ["bar", "baz"]}
            >>> ''.join(list(CompactEncoder().iterencode(item))) == \\
            ... CompactEncoder().encode(item)
            True
        '''
        self.indent += 1
        if self.respect_indent:
            ind = self.indent*'\t'
        else:
            ind = ''
        if isinstance(obj, dict):
            if len(obj) == 0:
                yield f"{ind}{{}}"
            else:
                body = []
                if self.sort_keys is True:
                    obj_iter = sorted(iter(obj.items()))
                else:
                    obj_iter = obj.items()
                for k, v in obj_iter:
                    body.extend([
                        f'{j[:self.indent]}"{k}": {j[self.indent:]}'
                        for j in self.iterencode(v)
                    ])
                body_str = ",\n".join(body)
                yield (
                    f'{ind}{{\n'
                    f'{body_str}\n'
                    f'{ind}}}'
                )
        elif isinstance(obj, (list, tuple)):
            primitive_list = True
            for i in obj:
                if not self._is_primitive(i):
                    primitive_list = False
                    break
            if primitive_list:
                body = []
                self.respect_indent = False
                for i in obj:
                    body.extend([j for j in self.iterencode(i)])
                self.respect_indent = True
                yield f'{ind}[{", ".join(body)}]'
            else:
                body = []
                for i in obj:
                    body.extend([j for j in self.iterencode(i)])
                body_str = ",\n".join(body)
                yield (
                    f'{ind}[\n'
                    f'{body_str}\n'
                    f'{ind}]'
                )
        elif self._is_primitive(obj):
            if isinstance(obj, str):
                obj_str = obj.replace("\\", "\\\\").replace('"', '\\"')
                yield f'{ind}"{obj_str}"'
            else:
                yield f'{ind}{str(obj).lower()}'
        elif obj is None:
            yield f'{ind}null'
        else:
            raise TypeError('Object of type set is not JSON serializable')
        self.indent -= 1

# JSON path

## Type definitions
JSON = Union[Dict, List, str, float, int, bool, None]
JSON_KEY = Union[str, int]
JSON_SPLIT_KEY = Union[str, Type[int], Type[str], None]
J = TypeVar('J', Dict, List, str, float, int, bool, None)

class JSONWalker(Generic[J]):
    '''
    Safe access to data accessed with json.load without risk of exceptions.
    '''
    def __init__(self, data: J, path: Tuple[JSON_KEY, ...] = ()):
        self._data: J = data
        self._path: Tuple[JSON_KEY, ...] = path
        if type(self) is JSONWalker:
            raise TypeError("Can't instantiate abstract class JSONWalker")

    @staticmethod
    def loads(json_text: Union[str, bytes], **kwargs) -> JSONWalker:
        '''
        Create :class:`JSONWalker` from string with json.loads().
        '''
        data = json.loads(json_text, **kwargs)
        return JSONWalker.from_json(data)

    @staticmethod
    def load(json_file: IO, **kwargs) -> JSONWalker:
        '''
        Create :class:`JSONWalker` from file input with json.load().
        '''
        data = json.load(json_file, **kwargs)
        return JSONWalker.from_json(data)

    @staticmethod
    def from_json(data: JSON, path: Tuple[JSON_KEY, ...] = ()) -> JSONWalker:
        '''
        Create :class:`JSONWalker` from valid parsed JSON file. Input data is
        not validated. Passing invalid data may result in ValueError.
        '''
        if isinstance(data, dict):
            return JSONWalkerDict(data, path)
        elif isinstance(data, list):
            return JSONWalkerList(data, path)
        elif isinstance(data, str):
            return JSONWalkerStr(data, path)
        elif isinstance(data, float):
            return JSONWalkerFloat(data, path)
        elif isinstance(data, int):
            return JSONWalkerInt(data, path)
        elif isinstance(data, bool):
            return JSONWalkerBool(data, path)
        elif isinstance(data, type(None)):
            return JSONWalkerNone(data, path)
        else:
            raise ValueError('Input data is not JSON.')

    @property
    def data(self) -> J:
        return self._data

    @property
    def path(self) -> Tuple[JSON_KEY, ...]:
        return self._path

    def __truediv__(self, key: JSON_KEY) -> JSONWalker:
        path: Tuple[JSON_KEY, ...] = self.path + (key,)
        try:
            return JSONWalker.from_json(self.data[key], path)  # type: ignore
        except IndexError:  # index out of list bounds
            return JSONWalkerIndexError(None, path)
        except KeyError:  # bad dictionary key
            return JSONWalkerKeyError(None, path)
        except TypeError:  # data doesn't accept this type of key
            return JSONWalkerInvalidPath(None, path)

    def __floordiv__(self, key: JSON_SPLIT_KEY) -> JsonSplitWalker:
        '''
        Access multiple objects from JsonWalker at once. Return
        JsonSplitWalker.

        :param key: "str", "int", "None" or string with regular expression to
            access various types of data.

        - str - any item from dictionary
        - int - any item from list
        - regular expression - regular expression that matches dictionary keys
        - None - any item from dictionary or list
        
        :raises: TypeError on invalid input data type or
        re.error on invlid regular expression.
        '''
        # ANYTHING
        if key is None:
            if isinstance(self.data, dict):
                return JsonSplitWalker([
                    JSONWalker.from_json(v, self.path+(k,))
                    for k, v in self.data.items()
                ])
            elif isinstance(self.data, list):
                return JsonSplitWalker([
                    JSONWalker.from_json(v, self.path+(i,))
                    for i, v in enumerate(self.data)
                ])
        # ANY LIST ITEM
        elif key is int:
            if isinstance(self.data, list):
                return JsonSplitWalker([
                    JSONWalker.from_json(v, self.path+(i,))
                    for i, v in enumerate(self.data)
                ])
        # ANY DICT ITEM
        elif key is str:
            if isinstance(self.data, dict):
                return JsonSplitWalker([
                    JSONWalker.from_json(v, self.path+(k,))
                    for k, v in self.data.items()
                ])
        # REGEX DICT ITEM
        elif isinstance(key, str):
            if isinstance(self.data, dict):
                result: List[JSONWalker] = []
                for k, v in self.data.items():
                    if re.fullmatch(key, k):
                        result.append(JSONWalker.from_json(v, k))
                return JsonSplitWalker(result)
        else:  # INVALID KEY TYPE
            raise TypeError(
                'Key must be a regular expression or one of the values: '
                'str, int, or None')
        # DATA DOESN'T ACCEPT THIS TYPE OF KEY
        return JsonSplitWalker([])

class JSONWalkerDict(JSONWalker[Dict]): ...
class JSONWalkerList(JSONWalker[List]): ...
class JSONWalkerStr(JSONWalker[str]): ...
class JSONWalkerFloat(JSONWalker[float]): ...
class JSONWalkerInt(JSONWalker[int]): ...
class JSONWalkerBool(JSONWalker[bool]): ...
class JSONWalkerNone(JSONWalker[None]): ...

class JSONWalkerInvalidPath(JSONWalker[None]): ...
class JSONWalkerIndexError(JSONWalkerInvalidPath): ...
class JSONWalkerKeyError(JSONWalkerInvalidPath): ...

class JsonSplitWalker:
    '''
    Multiple :class:`JSONWalker`s grouped together. This class can be browse
    JSON file in multiple places at once.
    '''
    def __init__(self, data: List[JSONWalker]) -> None:
        self._data: List[JSONWalker] = data

    @property
    def data(self) -> List[JSONWalker]:
        return self._data

    def __truediv__(self, key: JSON_KEY) -> JsonSplitWalker:
        result = []
        for walker in self.data:
            new_walker = walker / key
            if not isinstance(new_walker, JSONWalkerInvalidPath):
                result.append(new_walker)
        return JsonSplitWalker(result)

    def __floordiv__(self, key: JSON_SPLIT_KEY) -> JsonSplitWalker:
        result: List[JSONWalker] = []
        for walker in self.data:
            new_walker = walker // key
            result.extend(new_walker.data)
        return JsonSplitWalker(result)

    def __add__(self, other: JsonSplitWalker) -> JsonSplitWalker:
        return JsonSplitWalker(self.data + other.data)

    def __iter__(self) -> Iterator[JSONWalker]:
        for i in self.data:
            yield i
