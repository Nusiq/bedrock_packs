'''
Python module for working with Minecraft bedrock edition projects.
'''
from __future__ import annotations
from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty
from json.decoder import JSONDecodeError
from re import split

from typing import ClassVar, Dict, List, Optional, Tuple, TypeVar, Generic, Union
from copy import copy
from uuid import UUID
from pathlib import Path

from typing_extensions import Literal

from bedrock_dev_tools.json import JSONCDecoder, JSONWalker, JSONWalkerDict, JSONWalkerInvalidPath, JSONWalkerList, JSONWalkerStr

# Package version
VERSION = (0, 1)
__version__ = '.'.join([str(x) for x in VERSION])



# Type variables
MCPACK = TypeVar('MCPACK', bound='_Pack')
MCFILE_COLLECTION = TypeVar('MCFILE_COLLECTION', bound='_McFileCollection')
MCFILE = TypeVar('MCFILE', bound='_McFile')
MCFILE_SINGLE = TypeVar('MCFILE_SINGLE', bound='_McFileSingle')
MCFILE_MULTI = TypeVar('MCFILE_MULTI', bound='_McFileMulti')


# PROJECT
class Project:
    '''A collection of behavior packs and resource packs.'''
    def __init__(self, path: Optional[Path]=None) -> None:
        self._bps: List[BehaviorPack] = []  # Read only (use bps)
        self._rps: List[ResourcePack] = []  # Read only (use rps)
        if path is not None:
            bps_path = path / 'behavior_packs'
            rps_path = path / 'resource_packs'
            if bps_path.is_dir():
                for p in bps_path.iterdir():
                    if p.is_dir():
                        self._bps.append(BehaviorPack(p, self))
            if rps_path.is_dir():
                for p in rps_path.iterdir():
                    if p.is_dir():
                        self._rps.append(ResourcePack(p, self))

    @property
    def bps(self) -> Tuple[BehaviorPack, ...]:
        '''tuple with behaviorpacks from this project'''
        return tuple(self._bps)

    @property
    def rps(self) -> Tuple[ResourcePack, ...]:
        '''tuple with resourcepacks from this project'''
        return tuple(self._rps)

    def uuid_bps(self) -> Dict[str, BehaviorPack]:
        '''
        A view of :class:`BehaviorPack`s from this project. The packs
        without UUID are skipped.

        :returns: a dictionary with packs uuids for keys and packs for values
        '''
        result: Dict[str, BehaviorPack] = {}
        for bp in self.bps:
            try:
                result[bp.uuid] = bp
            except:
                pass
        return result

    def uuid_rps(self) -> Dict[str, ResourcePack]:
        '''
        A view of :class:`ResourcePack`s from this project. The packs
        without UUID are skipped.

        :returns: a dictionary with packs uuids for keys and packs for values
        '''
        result: Dict[str, ResourcePack] = {}
        for rp in self.rps:
            try:
                result[rp.uuid] = rp
            except:
                pass
        return result

    def path_bps(self) -> Dict[Path, BehaviorPack]:
        '''
        A view of :class:`BehaviorPack`s from this project.

        :returns: a dictionary with packs paths for keys and packs for values
        '''
        result: Dict[Path, BehaviorPack] = {}
        for bp in self.bps:
            result[bp.path] = bp
        return result

    def path_rps(self) -> Dict[Path, ResourcePack]:
        '''
        A view of :class:`ResourcePack`s from this project.

        :returns: a dictionary with packs paths for keys and packs for values
        '''
        result: Dict[Path, ResourcePack] = {}
        for rp in self.rps:
            result[rp.path] = rp
        return result

    def add_bp(self, pack: BehaviorPack) -> None:
        '''Adds behavior pack to this project'''
        self._bps.append(pack)
        pack.project = self

    def add_rp(self, pack: ResourcePack) -> None:
        '''Adds behavior pack to this project'''
        self._rps.append(pack)
        pack.project = self

    @property
    def bp_entities(self) -> BpEntities:
        return BpEntities.combined_collections(
            [i.entities for i in self.bps])

    @property
    def rp_entities(self) -> RpEntities:
        return RpEntities.combined_collections(
            [i.entities for i in self.rps])

    @property
    def bp_animation_controllers(self) -> BpAnimationControllers:
        return BpAnimationControllers.combined_collections(
            [i.animation_controllers for i in self.bps])

    @property
    def rp_animation_controllers(self) -> RpAnimationControllers:
        return RpAnimationControllers.combined_collections(
            [i.animation_controllers for i in self.rps])

    @property
    def bp_blocks(self) -> BpBlocks:
        return BpBlocks.combined_collections(
            [i.blocks for i in self.bps])

    @property
    def bp_items(self) -> BpItems:
        return BpItems.combined_collections(
            [i.items for i in self.bps])

    @property
    def rp_items(self) -> RpItems:
        return RpItems.combined_collections(
            [i.items for i in self.rps])

    @property
    def bp_loot_tables(self) -> BpLootTables:
        return BpLootTables.combined_collections(
            [i.loot_tables for i in self.bps])

    @property
    def bp_functions(self) -> BpFunctions:
        return BpFunctions.combined_collections(
            [i.functions for i in self.bps])

    @property
    def bp_spawn_rules(self) -> BpSpawnRules:
        return BpSpawnRules.combined_collections(
            [i.spawn_rules for i in self.bps])

    @property
    def bp_trades(self) -> BpTrades:
        return BpTrades.combined_collections(
            [i.trades for i in self.bps])

    @property
    def rp_models(self) -> RpModels:
        return RpModels.combined_collections(
            [i.models for i in self.rps])



# PACKS
class _Pack(ABC):
    '''
    Behavior pack or resource pack. A collection of
    :class:`_McFileCollection`s.
    '''
    def __init__(self, path: Path, project: Optional[Project]=None) -> None:
        self.project: Optional[Project] = project
        self.path: Path = path
        self._manifest: Optional[JSONWalker] = None

    @property
    def manifest(self) -> JSONWalker:
        ''':class:`JSONWalker` for manifest file'''
        if self._manifest is None:
            manifest_path = self.path / 'manifest.json'
            with manifest_path.open('r') as f:
                self._manifest = JSONWalker.load(f)
        return self._manifest

    @property
    def uuid(self) -> str:
        '''the UUID from manifest.'''
        uuid_walker = (self.manifest / 'header' / 'uuid')
        if isinstance(uuid_walker, JSONWalkerStr):
            return uuid_walker.data
        raise AttributeError('Unable to get uuid')

class BehaviorPack(_Pack):
    '''A part of a project or standalone behavior pack.'''
    def __init__(self, path: Path, project: Optional[Project]=None) -> None:
        super().__init__(path, project=project)
        self._entities: Optional[BpEntities] = None
        self._animation_controllers: Optional[BpAnimationControllers] = None
        self._animations: Optional[BpAnimations] = None
        self._blocks: Optional[BpBlocks] = None
        self._items: Optional[BpItems] = None
        self._loot_tables: Optional[BpLootTables] = None
        self._functions: Optional[BpFunctions] = None
        self._spawn_rules: Optional[BpSpawnRules] = None
        self._trades: Optional[BpTrades] = None

    @property
    def entities(self) -> BpEntities:
        if self._entities is None:
            self._entities = BpEntities(pack=self)
        return self._entities

    @property
    def animation_controllers(self) -> BpAnimationControllers:
        if self._animation_controllers is None:
            self._animation_controllers = BpAnimationControllers(pack=self)
        return self._animation_controllers

    @property
    def animations(self) -> BpAnimations:
        if self._animations is None:
            self._animations = BpAnimations(pack=self)
        return self._animations

    @property
    def blocks(self) -> BpBlocks:
        if self._blocks is None:
            self._blocks = BpBlocks(pack=self)
        return self._blocks

    @property
    def items(self) -> BpItems:
        if self._items is None:
            self._items = BpItems(pack=self)
        return self._items

    @property
    def loot_tables(self) -> BpLootTables:
        if self._loot_tables is None:
            self._loot_tables = BpLootTables(pack=self)
        return self._loot_tables

    @property
    def functions(self) -> BpFunctions:
        if self._functions is None:
            self._functions = BpFunctions(pack=self)
        return self._functions

    @property
    def spawn_rules(self) -> BpSpawnRules:
        if self._spawn_rules is None:
            self._spawn_rules = BpSpawnRules(pack=self)
        return self._spawn_rules

    @property
    def trades(self) -> BpTrades:
        if self._trades is None:
            self._trades = BpTrades(pack=self)
        return self._trades

class ResourcePack(_Pack):
    '''A part of a project or standalone resource pack.'''
    def __init__(self, path: Path, project: Optional[Project]=None) -> None:
        super().__init__(path, project=project)
        self._entities: Optional[RpEntities] = None
        self._animation_controllers: Optional[RpAnimationControllers] = None
        self._animations: Optional[RpAnimations] = None
        self._items: Optional[RpItems] = None
        self._models: Optional[RpModels] = None

    @property
    def entities(self) -> RpEntities:
        if self._entities is None:
            self._entities = RpEntities(pack=self)
        return self._entities

    @property
    def animation_controllers(self) -> RpAnimationControllers:
        if self._animation_controllers is None:
            self._animation_controllers = RpAnimationControllers(pack=self)
        return self._animation_controllers

    @property
    def animations(self) -> RpAnimations:
        if self._animations is None:
            self._animations = RpAnimations(pack=self)
        return self._animations

    @property
    def items(self) -> RpItems:
        if self._items is None:
            self._items = RpItems(pack=self)
        return self._items

    @property
    def models(self) -> RpModels:
        if self._models is None:
            self._models = RpModels(pack=self)
        return self._models

# OBJECT COLLECTIONS (GENERIC)
class _McFileCollection(Generic[MCPACK, MCFILE], ABC):
    '''
    Collection of :class:`_McFile`s.
    '''
    pack_path: ClassVar[str]
    file_pattern: ClassVar[str]

    def __init__(
            self, *,
            objects: Optional[List[MCFILE]]=None,
            path: Optional[Path]=None,
            pack: Optional[MCPACK]=None) -> None:

        if objects is None and pack is None and path is None:
            raise ValueError(
                'You must provide "path", "objects" or "pack" to '
                f'{type(self).__name__} constructor')
        if pack is not None and path is not None:
            raise ValueError(
                "You can't use both 'pack' and 'path' in "
                f'{type(self).__name__} constructor')
            

        self._objects: Optional[List[MCFILE]] = objects  # None->Lazy evaluation
        self._pack: Optional[MCPACK] = pack  # read only (use pack)
        self._path: Optional[Path] = path  # read only (use path)


    @property
    def objects(self) -> List[MCFILE]:
        if self._objects is None:
            self._objects = []
            self.reload_objects()
        return self._objects

    @property
    def path(self) -> Path:
        if self.pack is not None:  # Get path from pack
            return self.pack.path / self.__class__.pack_path
        if self._path is None:
            raise AttributeError("Can't get 'path' attribute.")
        return self._path

    @property
    def pack(self) -> Optional[MCPACK]:
        return self._pack

    def add(self, obj: MCFILE) -> None:
        self.objects.append(obj)

    def __getitem__(self, key: Union[str, slice]) -> MCFILE:
        path_ids, id_items = self._quick_access_list_views()
        path_key: Optional[Union[str, Path]]
        id_key: Optional[str]
        index: Optional[int]
        if isinstance(key, str):
            path_key, id_key, index = None, key, None
        elif isinstance(key, slice):
            path_key, id_key, index = key.start, key.stop, key.step
        else:
            raise TypeError(
                'key must be a string or slice or slices, not '
                f'{type(key).__name__}')
        # Check key types
        if not isinstance(id_key, (str, type(None))):
            raise TypeError(
                'identifier key must be a string, not '
                f'{type(id_key).__name__}')
        if not isinstance(path_key, (Path, str, type(None))):
            raise TypeError(
                'path key must be a string, Path or None, not '
                f'{type(path_key).__name__}')
        if not isinstance(index, (int, type(None))):
            raise TypeError(
                'index key must be an integer, not '
                f'{type(index).__name__}')
        # Access the object
        if path_key is not None:
            path_key = Path(path_key)
            # The length of this list is > 0 because path_ids don't have empty
            # lists
            id_list = path_ids[path_key]
            if id_key is None:
                if len(id_list) == 1:
                    id_key = id_list[0]
                else:
                    raise KeyError(f'{str(path_key)}:{id_key}:{index}')
            elif id_key not in id_list:
                raise KeyError(f'{str(path_key)}:{id_key}:{index}')
            obj_list = id_items[id_key]
        else:  # path_key is None
            if id_key is None:
                raise KeyError(f'{str(path_key)}:{id_key}:{index}')
            obj_list = id_items[id_key]
        # Search narrowed down to list of objects and the index
        # The return statement
        if index is not None:
            return obj_list[index]
        elif len(obj_list) == 1:
            return obj_list[0]
        raise KeyError(f'{str(path_key)}:{id_key}:{index}')

    def reload_objects(self) -> None:
        for fp in self.path.glob(self.__class__.file_pattern):
            if not fp.is_file():
                continue
            try:
                obj: MCFILE = self._make_collection_object(fp)
            except AttributeError:
                continue
            self.add(obj)

    # Different for _McFileMulti and _McFileSingle collections
    @abstractmethod
    def _quick_access_list_views(
    self) -> Tuple[Dict[Path, List[str]], Dict[str, List[MCFILE]]]: ...

    # METHODS THAT REQUIRE FURTHER SPECIFICATION IN SUBCLASSES (for their
    # content or type annotations)
    @abstractclassmethod
    def _init_from_objects(cls, objects: List[MCFILE]):
        '''
        Needs subclass type annotation
        :returns: self.__class__
        '''

    @abstractmethod
    def _make_collection_object(self, path: Path) -> MCFILE:
        '''Create an object connected to self from path'''

    @abstractclassmethod
    def combined_collections(cls, collections: List):
        '''
        Needs subclass type annotation
        :collections: List[self.__class__]
        :returns: self.__class___
        '''
        objects: List[MCFILE] = []
        for collection in collections:
            objects.extend(collection.objects)
        return cls._init_from_objects(objects=objects)

# OBJECTS (GENERIC)
class _McFile(Generic[MCFILE_COLLECTION], ABC):
    def __init__(
            self, path: Path,
            owning_collection: Optional[MCFILE_COLLECTION]=None
    ) -> None:
        self._owning_collection: Optional[
            MCFILE_COLLECTION] = owning_collection
        self.path: Path = path

    @property
    def owning_collection(self) -> Optional[MCFILE_COLLECTION]:
        return self._owning_collection

class _McFileSingle(_McFile[MCFILE_COLLECTION]):
    '''McFile with single Minecraft object'''
    @abstractproperty
    def identifier(self) -> str: ...

class _JsonMcFileSingle(_McFileSingle[MCFILE_COLLECTION]):
    '''McFile that has JSON in it, with single Minecraft object'''
    def __init__(
            self, path: Path,
            owning_collection: Optional[MCFILE_COLLECTION]=None
    ) -> None:
        super().__init__(path, owning_collection=owning_collection)
        with path.open('r') as f:
            self._json: JSONWalker = JSONWalker.load(
                f, cls=JSONCDecoder)  # read only (use json)

    @property
    def json(self) -> JSONWalker:
        return self._json

class _McFileMulti(_McFile[MCFILE_COLLECTION]):
    '''McFile with multiple Minecraft objects'''
    @abstractproperty
    def identifiers(self) -> Tuple[str, ...]: ...

class _JsonMcFileMulti(_McFileMulti[MCFILE_COLLECTION]):
    '''McFile that has JSON in it, with multiple Minecraft objects'''
    def __init__(
            self, path: Path,
            owning_collection: Optional[MCFILE_COLLECTION]=None
    ) -> None:
        super().__init__(path, owning_collection=owning_collection)
        with path.open('r') as f:
            self._json: JSONWalker = JSONWalker.load(
                f, cls=JSONCDecoder)  # read only (use json)

    @property
    def json(self) -> JSONWalker:
        return self._json

    @abstractmethod
    def __getitem__(self, key: str) -> JSONWalker: ...

# OBJECTS (IMPLEMENTATION)
class BpEntity(_JsonMcFileSingle['BpEntities']):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:entity" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class RpEntity(_JsonMcFileSingle['RpEntities']):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:client_entity" / "description" /
            "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class _AnimationController(_JsonMcFileMulti[MCFILE_COLLECTION]):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "animation_controllers")
        if isinstance(id_walker, JSONWalkerDict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        raise AttributeError("Can't get identifier attribute.")

    def __getitem__(self, key: str) -> JSONWalker:
        id_walker = (self.json / "animation_controllers")
        if isinstance(id_walker, JSONWalkerDict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)
class BpAnimationController(_AnimationController['BpAnimationControllers']): ...
class RpAnimationController(_AnimationController['RpAnimationControllers']): ...

class _Animation(_JsonMcFileMulti[MCFILE_COLLECTION]):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "animations")
        if isinstance(id_walker, JSONWalkerDict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        raise AttributeError("Can't get identifier attribute.")

    def __getitem__(self, key: str) -> JSONWalker:
        id_walker = (self.json / "animations")
        if isinstance(id_walker, JSONWalkerDict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)
class BpAnimation(_Animation['BpAnimations']): ...
class RpAnimation(_Animation['RpAnimations']): ...

class BpBlock(_JsonMcFileSingle['BpBlocks']):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:block" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class BpItem(_JsonMcFileSingle['BpItems']):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class RpItem(_JsonMcFileSingle['RpItems']):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class BpLootTable(_JsonMcFileSingle['BpLootTables']):
    @property
    def identifier(self) -> str:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            raise AttributeError("Can't get identifier attribute.")
        return self.path.relative_to(
            self.owning_collection.pack.path).as_posix()

class BpFunction(_McFileSingle['BpFunctions']):
    @property
    def identifier(self) -> str:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            raise AttributeError("Can't get identifier attribute.")
        return self.path.relative_to(
            self.owning_collection.pack.path / 'functions'
        ).with_suffix('').as_posix()

class BpSpawnRule(_JsonMcFileSingle['BpSpawnRules']):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:spawn_rules" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class BpTrade(_JsonMcFileSingle['BpTrades']):
    @property
    def identifier(self) -> str:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            raise AttributeError("Can't get identifier attribute.")
        return self.path.relative_to(
            self.owning_collection.pack.path).as_posix()

class RpModel(_JsonMcFileMulti['RpModels']):
    @property
    def format_version(self) -> Tuple[int, ...]:
        '''
        Return the format version of the model or guess the version based
        on the file structure if it's missing.

        :returns: format version of the model file
        '''
        format_version: Tuple[int, ...] = (1, 8, 0)
        try:
            id_walker = self.json / 'format_version'
            if isinstance(id_walker, JSONWalkerStr):
                format_version = tuple(
                    [int(i) for i in id_walker.data.split('.')])
        except:  # Guessing the format version instead
            id_walker = self.json / 'minecraft:geometry'
            if isinstance(id_walker, JSONWalkerList):
                format_version = (1, 16, 0)
        return format_version

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        if self.format_version <= (1, 10, 0):
            if isinstance(self.json, JSONWalkerDict):
                for k in self.json.data.keys():
                    if isinstance(k, str) and k.startswith('geometry.'):
                        result.append(k)
        else:  # Probably something <= 1.16.0
            id_walker = (
                self.json / 'minecraft:geometry' // int / 'description' /
                'identifier')
            for i in id_walker:
                if isinstance(i, JSONWalkerStr):
                    if i.data.startswith('geometry.'):
                        result.append(i.data)
        return tuple(result)

    def __getitem__(self, key: str) -> JSONWalker:
        if not key.startswith('.geometry'):
            raise AttributeError("Key must start with '.geometry'")
        if self.format_version <= (1, 10, 0):
            if isinstance(self.json, JSONWalkerDict):
                return self.json / key
        else:  # Probably something <= 1.16.0
            id_walker = (
                self.json / 'minecraft:geometry' // int)
            for model in id_walker:
                if not isinstance(
                        model / 'description' / 'identifier' / key,
                        JSONWalkerInvalidPath):
                    return model
        raise AttributeError("Can't get identifier attribute.")


# OBJECT COLLECTIONS (IMPLEMENTATIONS)
class _McPackCollectionSingle(_McFileCollection[MCPACK, MCFILE_SINGLE]):
    '''A collection of :class:`_McFileSingle` objects.'''
    def _quick_access_list_views(
            self) -> Tuple[Dict[Path, List[str]], Dict[str, List[MCFILE_SINGLE]]]:
        '''
        Creates and returns dictionaries with summary of the objects contained
        in this collection. Used by __getitem__ to find specific objects.

        :returns: Two dictionaries - first dict uses paths for keys and
            identifiers for values, second dict uses identifiers for keys and
            objects from this collection for values.
        '''
        path_ids: Dict[Path, List[str]] = {}
        id_items: Dict[str, List[MCFILE_SINGLE]] = {}
        for obj in self.objects:
            try:
                identifier = obj.identifier
            except AttributeError:
                continue  # Skip items with invalid identifier
            # path -> identifier
            if identifier in path_ids:
                path_ids[obj.path].append(identifier)
            else:
                path_ids[obj.path] = [identifier]
            # identifier -> item
            if obj.path in id_items:
                id_items[identifier].append(obj)
            else:
                id_items[identifier] = [obj]
        return (path_ids, id_items)

class _McPackCollectionMulti(_McFileCollection[MCPACK, MCFILE_MULTI]):
    '''A collection of :class:`_McFileMulti` objects.'''
    def _quick_access_list_views(
            self) -> Tuple[Dict[Path, List[str]], Dict[str, List[MCFILE_MULTI]]]:
        '''
        Creates and returns dictionaries with summary of the objects contained
        in this collection. Used by __getitem__ to find specific objects.

        :returns: Two dictionaries - first dict uses paths for keys and
            identifiers for values, second dict uses identifiers for keys and
            objects from this collection for values.
        '''
        path_ids: Dict[Path, List[str]] = {}
        id_items: Dict[str, List[MCFILE_MULTI]] = {}
        for obj in self.objects:
            try:
                identifiers = obj.identifiers
            except AttributeError:
                continue  # Skip items with invalid identifier
            # path -> identifier
            for identifier in identifiers:
                if identifier in path_ids:
                    path_ids[obj.path].append(identifier)
                else:
                    path_ids[obj.path] = [identifier]
                # identifier -> item
                if obj.path in id_items:
                    id_items[identifier].append(obj)
                else:
                    id_items[identifier] = [obj]
        return (path_ids, id_items)

class BpEntities(_McPackCollectionSingle[BehaviorPack, BpEntity]):
    pack_path = 'entities'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpEntity]) -> BpEntities:
        return BpEntities(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpEntities]) -> BpEntities:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpEntity:
        return BpEntity(path, self)

class RpEntities(_McPackCollectionSingle[ResourcePack, RpEntity]):
    pack_path = 'entity'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[RpEntity]) -> RpEntities:
        return RpEntities(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[RpEntities]) -> RpEntities:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> RpEntity:
        return RpEntity(path, self)

class BpAnimationControllers(_McPackCollectionMulti[BehaviorPack, BpAnimationController]):
    pack_path = 'animation_controllers'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpAnimationController]) -> BpAnimationControllers:
        return BpAnimationControllers(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpAnimationControllers]) -> BpAnimationControllers:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpAnimationController:
        return BpAnimationController(path, self)

class RpAnimationControllers(_McPackCollectionMulti[ResourcePack, RpAnimationController]):
    pack_path = 'animation_controllers'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[RpAnimationController]) -> RpAnimationControllers:
        return RpAnimationControllers(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[RpAnimationControllers]) -> RpAnimationControllers:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> RpAnimationController:
        return RpAnimationController(path, self)

class BpAnimations(_McPackCollectionMulti[BehaviorPack, BpAnimation]):
    pack_path = 'animations'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpAnimation]) -> BpAnimations:
        return BpAnimations(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpAnimations]) -> BpAnimations:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpAnimation:
        return BpAnimation(path, self)

class RpAnimations(_McPackCollectionMulti[ResourcePack, RpAnimation]):
    pack_path = 'animations'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[RpAnimation]) -> RpAnimations:
        return RpAnimations(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[RpAnimations]) -> RpAnimations:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> RpAnimation:
        return RpAnimation(path, self)

class BpBlocks(_McPackCollectionSingle[BehaviorPack, BpBlock]):
    pack_path = 'blocks'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpBlock]) -> BpBlocks:
        return BpBlocks(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpBlocks]) -> BpBlocks:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpBlock:
        return BpBlock(path, self)

class BpItems(_McPackCollectionSingle[BehaviorPack, BpItem]):
    pack_path = 'items'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpItem]) -> BpItems:
        return BpItems(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpItems]) -> BpItems:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpItem:
        return BpItem(path, self)

class RpItems(_McPackCollectionSingle[ResourcePack, RpItem]):
    pack_path = 'items'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[RpItem]) -> RpItems:
        return RpItems(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[RpItems]) -> RpItems:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> RpItem:
        return RpItem(path, self)

class BpLootTables(_McPackCollectionSingle[BehaviorPack, BpLootTable]):
    pack_path = 'loot_tables'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpLootTable]) -> BpLootTables:
        return BpLootTables(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpLootTables]) -> BpLootTables:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpLootTable:
        return BpLootTable(path, self)

class BpFunctions(_McPackCollectionSingle[BehaviorPack, BpFunction]):
    pack_path = 'functions'
    file_pattern = '**/*.mcfunction'
    @classmethod
    def _init_from_objects(cls, objects: List[BpFunction]) -> BpFunctions:
        return BpFunctions(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpFunctions]) -> BpFunctions:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpFunction:
        return BpFunction(path, self)

class BpSpawnRules(_McPackCollectionSingle[BehaviorPack, BpSpawnRule]):
    pack_path = 'spawn_rules'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpSpawnRule]) -> BpSpawnRules:
        return BpSpawnRules(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpSpawnRules]) -> BpSpawnRules:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpSpawnRule:
        return BpSpawnRule(path, self)

class BpTrades(_McPackCollectionSingle[BehaviorPack, BpTrade]):
    pack_path = 'trading'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[BpTrade]) -> BpTrades:
        return BpTrades(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[BpTrades]) -> BpTrades:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> BpTrade:
        return BpTrade(path, self)

class RpModels(_McPackCollectionMulti[ResourcePack, RpModel]):
    pack_path = 'models'
    file_pattern = '**/*.json'
    @classmethod
    def _init_from_objects(cls, objects: List[RpModel]) -> RpModels:
        return RpModels(objects=objects)
    @classmethod
    def combined_collections(cls, collections: List[RpModels]) -> RpModels:
        return super().combined_collections(collections)  # type: ignore
    def _make_collection_object(self, path: Path) -> RpModel:
        return RpModel(path, self)
