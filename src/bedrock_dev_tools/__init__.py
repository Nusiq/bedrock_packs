'''
Python module for working with Minecraft bedrock edition projects.
'''
from __future__ import annotations
from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty

from typing import Callable, ClassVar, Dict, List, Optional, Tuple, TypeVar, Generic, Type, Union, cast
from copy import copy
from uuid import UUID
from pathlib import Path

from bedrock_dev_tools.json import JSONCDecoder, JSONWalker, JSONWalkerDict, JSONWalkerStr

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

# OBJECT COLLECTIONS (GENERIC)
class _McFileCollection(Generic[MCPACK, MCFILE], ABC):
    '''
    Collection of :class:`_McFile`s.
    '''
    pack_path: ClassVar[str]

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

    @abstractmethod
    def _quick_access_list_views(
    self) -> Tuple[Dict[Path, List[str]], Dict[str, List[MCFILE]]]: ...

    @abstractmethod
    def reload_objects(self) -> None: ...

    @abstractmethod
    def __add__(self, other): ...

    @abstractclassmethod
    def combined_collections(cls, collections): ...

# Additional method definitions form McFileCollection which couldn't be added
# to the class due to Typing limitations
def _mc_object_collection_reload_objects(
        self: _McFileCollection,
        pattern: str,
        collected_type: Type[MCFILE]):
    '''Reducing boilerplate code...'''
    for fp in self.path.glob(pattern):
        if not fp.is_file():
            continue
        try:
            obj = collected_type(fp, owning_collection=self)
        except AttributeError:
            continue
        self.add(obj)

def _mc_object_collection__add__(
        self: _McFileCollection,
        other: _McFileCollection,
        self_type: Type[MCFILE_COLLECTION]) -> MCFILE_COLLECTION:
    '''Reducing boilerplate code...'''
    if not isinstance(other, type(self)):
        raise TypeError(
            "unsupported operand types for +: "
            f"'{type(self).__name__}' and '{type(other).__name__}'")
    result = self_type(objects=self.objects + other.objects)
    return result

def _mc_object_collection_combined_collections(
        cls: Type[MCFILE_COLLECTION],
        collections: List[MCFILE_COLLECTION]) -> MCFILE_COLLECTION:
    '''Reducing boilerplate code'''
    objects: List[MCFILE_COLLECTION] = []
    for collection in collections:
        objects.extend(collection.objects)
    return cls(objects=objects)

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

class JsonMcFileMulti(_McFileMulti[MCFILE_COLLECTION]):
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

# OBJECT COLLECTIONS (IMPLEMENTATIONS)
class BpEntities(_McPackCollectionSingle[BehaviorPack, 'BpEntity']):
    pack_path = 'entities'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(self, '**/*.json', BpEntity)
    def __add__(self, other: BpEntities) -> BpEntities:
        return _mc_object_collection__add__(self, other, BpEntities)
    @classmethod
    def combined_collections(cls, collections: List[BpEntities]) -> BpEntities:
        return _mc_object_collection_combined_collections(cls, collections)

class RpEntities(_McPackCollectionSingle[ResourcePack, 'RpEntity']):
    pack_path = 'entity'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(self, '**/*.json', RpEntity)
    def __add__(self, other: RpEntities) -> RpEntities:
        return _mc_object_collection__add__(self, other, RpEntities)
    @classmethod
    def combined_collections(cls, collections: List[RpEntities]) -> RpEntities:
        return _mc_object_collection_combined_collections(cls, collections)

class BpAnimationControllers(_McPackCollectionMulti[
        BehaviorPack, 'BpAnimationController']):  # TODO - there can be multiple animaton controllers in one file.
    pack_path = 'animation_controllers'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpAnimationController)
    def __add__(self, other: BpAnimationControllers) -> BpAnimationControllers:
        return _mc_object_collection__add__(
            self, other, BpAnimationControllers)
    @classmethod
    def combined_collections(
        cls, collections: List[BpAnimationControllers]
    ) -> BpAnimationControllers:
        return _mc_object_collection_combined_collections(cls, collections)

class RpAnimationControllers(_McPackCollectionMulti[
        ResourcePack, 'RpAnimationController']):  # TODO - there can be multiple animaton controllers in one file.
    pack_path = 'animation_controllers'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', RpAnimationController)
    def __add__(self, other: RpAnimationControllers) -> RpAnimationControllers:
        return _mc_object_collection__add__(
            self, other, RpAnimationControllers)
    @classmethod
    def combined_collections(
        cls, collections: List[RpAnimationControllers]
    ) -> RpAnimationControllers:
        return _mc_object_collection_combined_collections(cls, collections)

class BpAnimations(_McPackCollectionMulti[
        BehaviorPack, 'BpAnimation']):  # TODO - there can be multiple animaton controllers in one file.
    pack_path = 'animations'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpAnimation)
    def __add__(self, other: BpAnimations) -> BpAnimations:
        return _mc_object_collection__add__(
            self, other, BpAnimations)
    @classmethod
    def combined_collections(
        cls, collections: List[BpAnimations]
    ) -> BpAnimations:
        return _mc_object_collection_combined_collections(cls, collections)

class RpAnimations(_McPackCollectionMulti[
        ResourcePack, 'RpAnimation']):  # TODO - there can be multiple animaton controllers in one file.
    pack_path = 'animations'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', RpAnimation)
    def __add__(self, other: RpAnimations) -> RpAnimations:
        return _mc_object_collection__add__(
            self, other, RpAnimations)
    @classmethod
    def combined_collections(
        cls, collections: List[RpAnimations]
    ) -> RpAnimations:
        return _mc_object_collection_combined_collections(cls, collections)

class BpBlocks(_McPackCollectionSingle[
        BehaviorPack, 'BpBlock']):
    pack_path = 'blocks'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpBlock)
    def __add__(self, other: BpBlocks) -> BpBlocks:
        return _mc_object_collection__add__(
            self, other, BpBlocks)
    @classmethod
    def combined_collections(
        cls, collections: List[BpBlocks]
    ) -> BpBlocks:
        return _mc_object_collection_combined_collections(cls, collections)

class BpItems(_McPackCollectionSingle[
        BehaviorPack, 'BpItem']):
    pack_path = 'items'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpItem)
    def __add__(self, other: BpItems) -> BpItems:
        return _mc_object_collection__add__(
            self, other, BpItems)
    @classmethod
    def combined_collections(
        cls, collections: List[BpItems]
    ) -> BpItems:
        return _mc_object_collection_combined_collections(cls, collections)

class BpLootTables(_McPackCollectionSingle[
        BehaviorPack, 'BpLootTable']):
    pack_path = 'loot_tables'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpLootTable)
    def __add__(self, other: BpLootTables) -> BpLootTables:
        return _mc_object_collection__add__(
            self, other, BpLootTables)
    @classmethod
    def combined_collections(
        cls, collections: List[BpLootTables]
    ) -> BpLootTables:
        return _mc_object_collection_combined_collections(cls, collections)

class BpFunctions(_McPackCollectionSingle[
        BehaviorPack, 'BpFunction']):
    pack_path = 'functions'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.mcfunction', BpFunction)
    def __add__(self, other: BpFunctions) -> BpFunctions:
        return _mc_object_collection__add__(
            self, other, BpFunctions)
    @classmethod
    def combined_collections(
        cls, collections: List[BpFunctions]
    ) -> BpFunctions:
        return _mc_object_collection_combined_collections(cls, collections)

class BpSpawnRules(_McPackCollectionSingle[
        BehaviorPack, 'BpSpawnRule']):
    pack_path = 'spawn_rules'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpSpawnRule)
    def __add__(self, other: BpSpawnRules) -> BpSpawnRules:
        return _mc_object_collection__add__(
            self, other, BpSpawnRules)
    @classmethod
    def combined_collections(
        cls, collections: List[BpSpawnRules]
    ) -> BpSpawnRules:
        return _mc_object_collection_combined_collections(cls, collections)

class BpTrades(_McPackCollectionSingle[
        BehaviorPack, 'BpTrade']):
    pack_path = 'trading'
    def reload_objects(self) -> None:
        _mc_object_collection_reload_objects(
            self, '**/*.json', BpTrade)
    def __add__(self, other: BpTrades) -> BpTrades:
        return _mc_object_collection__add__(
            self, other, BpTrades)
    @classmethod
    def combined_collections(
        cls, collections: List[BpTrades]
    ) -> BpTrades:
        return _mc_object_collection_combined_collections(cls, collections)

# OBJECTS (IMPLEMENTATION)
class BpEntity(_JsonMcFileSingle[BpEntities]):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:entity" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class RpEntity(_JsonMcFileSingle[RpEntities]):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:client_entity" / "description" /
            "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class _AnimationController(JsonMcFileMulti[MCFILE_COLLECTION]):  # GENERIC
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

class BpAnimationController(_AnimationController[BpAnimationControllers]): ...
class RpAnimationController(_AnimationController[RpAnimationControllers]): ...

class _Animation(JsonMcFileMulti[MCFILE_COLLECTION]):  # GENERIC
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

class BpAnimation(_Animation[BpAnimations]): ...
class RpAnimation(_Animation[RpAnimations]): ...

class BpBlock(_JsonMcFileSingle[BpBlocks]):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:block" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class BpItem(_JsonMcFileSingle[BpItems]):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class BpLootTable(_JsonMcFileSingle[BpLootTables]):
    @property
    def identifier(self) -> str:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            raise AttributeError("Can't get identifier attribute.")
        return self.path.relative_to(
            self.owning_collection.pack.path).as_posix()

class BpFunction(_McFileSingle[BpFunctions]):
    @property
    def identifier(self) -> str:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            raise AttributeError("Can't get identifier attribute.")
        return self.path.relative_to(
            self.owning_collection.pack.path / 'functions'
        ).with_suffix('').as_posix()

class BpSpawnRule(_JsonMcFileSingle[BpSpawnRules]):
    @property
    def identifier(self) -> str:
        id_walker = (
            self.json / "minecraft:spawn_rules" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        raise AttributeError("Can't get identifier attribute.")

class BpTrade(_JsonMcFileSingle[BpTrades]):
    @property
    def identifier(self) -> str:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            raise AttributeError("Can't get identifier attribute.")
        return self.path.relative_to(
            self.owning_collection.pack.path).as_posix()
