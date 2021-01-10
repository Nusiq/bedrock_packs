'''
Python module for working with Minecraft bedrock edition projects.
'''
from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty

from typing import (
    ClassVar, Dict, List, NamedTuple, Optional, Reversible, Sequence, Tuple, Type, TypeVar, Generic,
    Union)
from pathlib import Path

from .json import (
    JSONCDecoder, JSONWalker, JSONWalkerDict, JSONWalkerFloat, JSONWalkerInt, JSONWalkerInvalidPath,
    JSONWalkerList, JSONWalkerStr)

# Package version
VERSION = (0, 1)
__version__ = '.'.join([str(x) for x in VERSION])



# Type variables
MCPACK = TypeVar('MCPACK', bound='_Pack')
MCFILE_COLLECTION = TypeVar('MCFILE_COLLECTION', bound='_McFileCollection')
MCFILE = TypeVar('MCFILE', bound='_McFile')
MCFILE_SINGLE = TypeVar('MCFILE_SINGLE', bound='_McFileSingle')
MCFILE_MULTI = TypeVar('MCFILE_MULTI', bound='_McFileMulti')
JSON_MC_PACK_FILE_MULTI = TypeVar(
    'JSON_MC_PACK_FILE_MULTI',
    bound='_JsonMcPackFileMulti')
RP_SOUNDS_JSON_PART = TypeVar('RP_SOUNDS_JSON_PART', bound='RpSoundsJsonPart')
RP_SOUNDS_JSON_PART_KEY = TypeVar('RP_SOUNDS_JSON_PART_KEY')
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
            if bp.uuid is not None:
                result[bp.uuid] = bp
        return result

    def uuid_rps(self) -> Dict[str, ResourcePack]:
        '''
        A view of :class:`ResourcePack`s from this project. The packs
        without UUID are skipped.

        :returns: a dictionary with packs uuids for keys and packs for values
        '''
        result: Dict[str, ResourcePack] = {}
        for rp in self.rps:
            if rp.uuid is not None:
                result[rp.uuid] = rp
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
    def bp_entities(
            self) -> _MFCQuery[BpEntity]:
        return _MFCQuery(BpEntities, [i.entities for i in self.bps])

    @property
    def rp_entities(
            self) -> _MFCQuery[RpEntity]:
        return _MFCQuery(RpEntities, [i.entities for i in self.rps])

    @property
    def bp_animation_controllers(
            self) -> _MFCQuery[BpAnimationController]:
        return _MFCQuery(
            BpAnimationControllers,
            [i.animation_controllers for i in self.bps])

    @property
    def rp_animation_controllers(
            self) -> _MFCQuery[RpAnimationController]:
        return _MFCQuery(
            RpAnimationControllers,
            [i.animation_controllers for i in self.rps])

    @property
    def bp_blocks(
            self) -> _MFCQuery[BpBlock]:
        return _MFCQuery(BpBlocks, [i.blocks for i in self.bps])

    @property
    def bp_items(
            self) -> _MFCQuery[BpItem]:
        return _MFCQuery(BpItems, [i.items for i in self.bps])

    @property
    def rp_items(
            self) -> _MFCQuery[RpItem]:
        return _MFCQuery(RpItems, [i.items for i in self.rps])

    @property
    def bp_loot_tables(
            self) -> _MFCQuery[BpLootTable]:
        return _MFCQuery(BpLootTables, [i.loot_tables for i in self.bps])

    @property
    def bp_functions(
            self) -> _MFCQuery[BpFunction]:
        return _MFCQuery(BpFunctions, [i.functions for i in self.bps])

    @property
    def bp_spawn_rules(
            self) -> _MFCQuery[BpSpawnRule]:
        return _MFCQuery(BpSpawnRules, [i.spawn_rules for i in self.bps])

    @property
    def bp_trades(
            self) -> _MFCQuery[BpTrade]:
        return _MFCQuery(BpTrades, [i.trades for i in self.bps])

    @property
    def bp_recipes(
            self) -> _MFCQuery[BpRecipe]:
        return _MFCQuery(BpRecipes, [i.recipes for i in self.bps])

    @property
    def rp_models(
            self) -> _MFCQuery[RpModel]:
        return _MFCQuery(RpModels, [i.models for i in self.rps])

    @property
    def rp_particles(
            self) -> _MFCQuery[RpParticle]:
        return _MFCQuery(RpParticles, [i.particles for i in self.rps])

    @property
    def rp_render_controllers(
            self) -> _MFCQuery[RpRenderController]:
        return  _MFCQuery(
            RpRenderControllers, [i.render_controllers for i in self.rps])

    @property
    def rp_sound_definitions(
            self) -> _JMPFMQuery[RpSoundDefinitionsJson]:
        return _JMPFMQuery([i.sound_definitions for i in self.rps])

    @property
    def rp_sounds_json_block_sound_event(
            self) -> _BlockSoundEventQuery:
        return _BlockSoundEventQuery(
            [i.sounds_json for i in self.rps])

    @property
    def rp_sounds_json_entity_sound_event(
            self) -> _EntitySoundEventQuery:
        return _EntitySoundEventQuery(
            [i.sounds_json for i in self.rps])

    @property
    def rp_sounds_json_individual_sound_event(
            self) -> _IndividualSoundEventQuery:
        return _IndividualSoundEventQuery(
            [i.sounds_json for i in self.rps])

    @property
    def rp_sounds_json_interactive_block_sound_event(
            self) -> _InteractiveBlockSoundEventQuery:
        return _InteractiveBlockSoundEventQuery(
            [i.sounds_json for i in self.rps])

    @property
    def rp_sounds_json_interactive_entity_sound_event(
            self) -> _InteractiveEntitySoundEventQuery:
        return _InteractiveEntitySoundEventQuery(
            [i.sounds_json for i in self.rps])

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
    def manifest(self) -> Optional[JSONWalker]:
        ''':class:`JSONWalker` for manifest file'''
        if self._manifest is None:
            manifest_path = self.path / 'manifest.json'
            try:
                with manifest_path.open('r') as f:
                    self._manifest = JSONWalker.load(f)
            except:
                return None
        return self._manifest

    @property
    def uuid(self) -> Optional[str]:
        '''the UUID from manifest.'''
        if self.manifest is not None:
            uuid_walker = (self.manifest / 'header' / 'uuid')
            if isinstance(uuid_walker, JSONWalkerStr):
                return uuid_walker.data
        return None

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
        self._recipes: Optional[BpRecipes] = None

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

    @property
    def recipes(self) -> BpRecipes:
        if self._recipes is None:
            self._recipes = BpRecipes(pack=self)
        return self._recipes

class ResourcePack(_Pack):
    '''A part of a project or standalone resource pack.'''
    def __init__(self, path: Path, project: Optional[Project]=None) -> None:
        super().__init__(path, project=project)
        self._entities: Optional[RpEntities] = None
        self._animation_controllers: Optional[RpAnimationControllers] = None
        self._animations: Optional[RpAnimations] = None
        self._items: Optional[RpItems] = None
        self._models: Optional[RpModels] = None
        self._particles: Optional[RpParticles] = None
        self._render_controllers: Optional[RpRenderControllers] = None
        self._sound_definitions: Optional[RpSoundDefinitionsJson] = None
        self._sounds_json: Optional[RpSoundsJson] = None

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

    @property
    def particles(self) -> RpParticles:
        if self._particles is None:
            self._particles = RpParticles(pack=self)
        return self._particles

    @property
    def render_controllers(self) -> RpRenderControllers:
        if self._render_controllers is None:
            self._render_controllers = RpRenderControllers(pack=self)
        return self._render_controllers

    @property
    def sound_definitions(self) -> RpSoundDefinitionsJson:
        if self._sound_definitions is None:
            self._sound_definitions = RpSoundDefinitionsJson(pack=self)
        return self._sound_definitions

    @property
    def sounds_json(self) -> RpSoundsJson:
        if self._sounds_json is None:
            self._sounds_json = RpSoundsJson(pack=self)
        return self._sounds_json

# OBJECT COLLECTIONS (GENERIC)
class _McFileCollection(Generic[MCPACK, MCFILE], ABC):
    '''
    Collection of :class:`_McFile`s.
    '''
    pack_path: ClassVar[str]
    file_patterns: ClassVar[Tuple[str, ...]]

    def __init__(
            self, *,
            path: Optional[Path]=None,
            pack: Optional[MCPACK]=None) -> None:

        if pack is None and path is None:
            raise ValueError(
                'You must provide "path" or "pack" to '
                f'{type(self).__name__} constructor')
        if pack is not None and path is not None:
            raise ValueError(
                "You can't use both 'pack' and 'path' in "
                f'{type(self).__name__} constructor')

        self._objects: Optional[List[MCFILE]] = None  # Lazy evaluation
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
                    raise KeyError(key)
            elif id_key not in id_list:
                raise KeyError(key)
            obj_list = id_items[id_key]
        else:  # path_key is None
            if id_key is None:
                raise KeyError(key)
            obj_list = id_items[id_key]
        # Search narrowed down to list of objects and the index
        # The return statement
        if index is not None:
            return obj_list[index]
        elif len(obj_list) == 1:
            return obj_list[0]
        raise KeyError(key)

    def reload_objects(self) -> None:
        for file_pattern in self.__class__.file_patterns:
            for fp in self.path.glob(file_pattern):
                if not fp.is_file():
                    continue
                try:
                    obj: MCFILE = self._make_collection_object(fp)
                except AttributeError:
                    continue
                self.add(obj)

    @classmethod
    def get_item_from_combined_collections(
            self, collections: Reversible[_McFileCollection[MCPACK, MCFILE]],
            key: Union[str, slice]) -> MCFILE:
        '''
        Looks for _McFile in multiple _McFileCollections returns the result
        from the topmost collection.
        '''
        for collection in reversed(collections):
            try:
                return collection[key]
            except:
                pass
        raise KeyError(key)

    # Different for _McFileMulti and _McFileSingle collections
    @abstractmethod
    def keys(self) -> Tuple[str, ...]: ...

    @abstractmethod
    def _quick_access_list_views(
    self) -> Tuple[Dict[Path, List[str]], Dict[str, List[MCFILE]]]: ...

    @abstractmethod
    def _make_collection_object(self, path: Path) -> MCFILE:
        '''Create an object connected to self from path'''

# Query
class _MFCQuery(Generic[MCFILE]):
    '''
    "M - Mc, F - file, C - collection, query" - used in :class:`Project` to
    provide methods for finding McFiles in McFileCollections that belong to
    that project.
    '''
    def __init__(
            self,
            collections_type: Type[_McFileCollection[MCPACK, MCFILE]],
            collections: Sequence[_McFileCollection[MCPACK, MCFILE]]):
        self.collections = collections
        self.collections_type = collections_type

    def __getitem__(self, key: Union[str, slice]) -> MCFILE:
        return self.collections_type.get_item_from_combined_collections(
            self.collections, key)

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        for collection in self.collections:
            result.extend(collection.keys())
        return tuple(set(result))

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
    def identifier(self) -> Optional[str]: ...

class _JsonMcFileSingle(_McFileSingle[MCFILE_COLLECTION]):
    '''McFile that has JSON in it, with single Minecraft object'''
    def __init__(
            self, path: Path,
            owning_collection: Optional[MCFILE_COLLECTION]=None
    ) -> None:
        super().__init__(path, owning_collection=owning_collection)
        self._json: JSONWalker = JSONWalker.from_json(None)
        try:
            with path.open('r') as f:
                self._json = JSONWalker.load(f, cls=JSONCDecoder)
        except:
            pass  # self._json remains None walker

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
        self._json: JSONWalker = JSONWalker.from_json(None)
        try:
            with path.open('r') as f:
                self._json = JSONWalker.load(f, cls=JSONCDecoder)
        except:
            pass  # self._json remains None walker

    @property
    def json(self) -> JSONWalker:
        return self._json

    @abstractmethod
    def __getitem__(self, key: str) -> JSONWalker: ...

# OBJECTS (IMPLEMENTATION)
class BpEntity(_JsonMcFileSingle['BpEntities']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:entity" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class RpEntity(_JsonMcFileSingle['RpEntities']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:client_entity" / "description" /
            "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class _AnimationController(_JsonMcFileMulti[MCFILE_COLLECTION]):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "animation_controllers")
        if isinstance(id_walker, JSONWalkerDict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        return tuple()

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
        return tuple()

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
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:block" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class BpItem(_JsonMcFileSingle['BpItems']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class RpItem(_JsonMcFileSingle['RpItems']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class BpLootTable(_JsonMcFileSingle['BpLootTables']):
    @property
    def identifier(self) -> Optional[str]:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            return None
        return self.path.relative_to(
            self.owning_collection.pack.path).as_posix()

class BpFunction(_McFileSingle['BpFunctions']):
    @property
    def identifier(self) -> Optional[str]:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            return None
        return self.path.relative_to(
            self.owning_collection.pack.path / 'functions'
        ).with_suffix('').as_posix()

class BpSpawnRule(_JsonMcFileSingle['BpSpawnRules']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:spawn_rules" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class BpTrade(_JsonMcFileSingle['BpTrades']):
    @property
    def identifier(self) -> Optional[str]:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            return None
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
        raise KeyError(key)

class RpParticle(_JsonMcFileSingle['RpParticles']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "particle_effect" / "description" / "identifier")
        if isinstance(id_walker, JSONWalkerStr):
            return id_walker.data
        return None

class RpRenderController(_JsonMcFileMulti['RpRenderControllers']):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "render_controllers")
        if isinstance(id_walker, JSONWalkerDict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        return tuple()

    def __getitem__(self, key: str) -> JSONWalker:
        id_walker = (self.json / "render_controllers")
        if isinstance(id_walker, JSONWalkerDict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)

class BpRecipe(_JsonMcFileMulti['BpRecipes']):
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (
            self.json // '(minecraft:recipe_shaped)|(minecraft:recipe_furnace)'
            '|(minecraft:recipe_shapeless)|(minecraft:recipe_brewing_mix)|'
            '(minecraft:recipe_brewing_container)' / "description"  /
            "identifier")
        result: List[str] = []
        for identifier_walker in id_walker.data:
            if isinstance(identifier_walker, JSONWalkerStr):
                result.append(identifier_walker.data)
        return tuple(result)

    def __getitem__(self, key: str) -> JSONWalker:
        id_walker = (
            self.json // '(minecraft:recipe_shaped)|(minecraft:recipe_furnace)'
            '|(minecraft:recipe_shapeless)|(minecraft:recipe_brewing_mix)|'
            '(minecraft:recipe_brewing_container)' / "description"  /
            "identifier")
        if isinstance(id_walker, JSONWalkerDict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)

# OBJECT COLLECTIONS (IMPLEMENTATIONS)
class _McPackCollectionSingle(_McFileCollection[MCPACK, MCFILE_SINGLE]):
    '''A collection of :class:`_McFileSingle` objects.'''
    def keys(self) -> Tuple[str, ...]:
        result: List[str] = []
        for obj in self.objects:
            if not obj.identifier is None:
                result.append(obj.identifier)
        return tuple(set(result))

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
            if obj.identifier is None:
                continue
            # path -> identifier
            if obj.path in path_ids:
                path_ids[obj.path].append(obj.identifier)
            else:
                path_ids[obj.path] = [obj.identifier]
            # identifier -> item
            if obj.path in id_items:
                id_items[obj.identifier].append(obj)
            else:
                id_items[obj.identifier] = [obj]
        return (path_ids, id_items)

class _McPackCollectionMulti(_McFileCollection[MCPACK, MCFILE_MULTI]):
    '''A collection of :class:`_McFileMulti` objects.'''
    def keys(self) -> Tuple[str, ...]:
        result: List[str] = []
        for obj in self.objects:
            result.extend(obj.identifiers)
        return tuple(set(result))

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
            # path -> identifier
            for identifier in obj.identifiers:
                if obj.path in path_ids:
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
    file_patterns = ('**/*.json',)

    def _make_collection_object(self, path: Path) -> BpEntity:
        return BpEntity(path, self)

class RpEntities(_McPackCollectionSingle[ResourcePack, RpEntity]):
    pack_path = 'entity'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpEntity:
        return RpEntity(path, self)

class BpAnimationControllers(_McPackCollectionMulti[BehaviorPack, BpAnimationController]):
    pack_path = 'animation_controllers'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpAnimationController:
        return BpAnimationController(path, self)

class RpAnimationControllers(_McPackCollectionMulti[ResourcePack, RpAnimationController]):
    pack_path = 'animation_controllers'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpAnimationController:
        return RpAnimationController(path, self)

class BpAnimations(_McPackCollectionMulti[BehaviorPack, BpAnimation]):
    pack_path = 'animations'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpAnimation:
        return BpAnimation(path, self)

class RpAnimations(_McPackCollectionMulti[ResourcePack, RpAnimation]):
    pack_path = 'animations'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpAnimation:
        return RpAnimation(path, self)

class BpBlocks(_McPackCollectionSingle[BehaviorPack, BpBlock]):
    pack_path = 'blocks'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpBlock:
        return BpBlock(path, self)

class BpItems(_McPackCollectionSingle[BehaviorPack, BpItem]):
    pack_path = 'items'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpItem:
        return BpItem(path, self)

class RpItems(_McPackCollectionSingle[ResourcePack, RpItem]):
    pack_path = 'items'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpItem:
        return RpItem(path, self)

class BpLootTables(_McPackCollectionSingle[BehaviorPack, BpLootTable]):
    pack_path = 'loot_tables'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpLootTable:
        return BpLootTable(path, self)

class BpFunctions(_McPackCollectionSingle[BehaviorPack, BpFunction]):
    pack_path = 'functions'
    file_patterns = ('**/*.mcfunction',)
    def _make_collection_object(self, path: Path) -> BpFunction:
        return BpFunction(path, self)

class BpSpawnRules(_McPackCollectionSingle[BehaviorPack, BpSpawnRule]):
    pack_path = 'spawn_rules'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpSpawnRule:
        return BpSpawnRule(path, self)

class BpTrades(_McPackCollectionSingle[BehaviorPack, BpTrade]):
    pack_path = 'trading'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpTrade:
        return BpTrade(path, self)

class RpModels(_McPackCollectionMulti[ResourcePack, RpModel]):
    pack_path = 'models'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpModel:
        return RpModel(path, self)

class RpParticles(_McPackCollectionSingle[ResourcePack, RpParticle]):
    pack_path = 'particles'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpParticle:
        return RpParticle(path, self)

class RpRenderControllers(_McPackCollectionMulti[ResourcePack, RpRenderController]):
    pack_path = 'render_controllers'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpRenderController:
        return RpRenderController(path, self)

class BpRecipes(_McPackCollectionMulti[BehaviorPack, BpRecipe]):
    pack_path = 'recipes'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpRecipe:
        return BpRecipe(path, self)

# SPECIAL PACK FILES - ONE FILE PER PACK (GENERICS)
class _McPackFile(Generic[MCPACK], ABC):
    pack_path: ClassVar[str]

    def __init__(
            self, *,
            path: Optional[Path]=None,
            pack: Optional[MCPACK]=None) -> None:
        if pack is None and path is None:
            raise ValueError(
                'You must provide "path" or "pack" to '
                f'{type(self).__name__} constructor')
        if pack is not None and path is not None:
            raise ValueError(
                "You can't use both 'pack' and 'path' in "
                f'{type(self).__name__} constructor')

        self._pack: Optional[MCPACK] = pack  # read only (use pack)
        self._path: Optional[Path] = path  # read only (use path)

    @property
    def pack(self) -> Optional[MCPACK]:
        return self._pack

    @property
    def path(self) -> Path:
        if self.pack is not None:  # Get path from pack
            return self.pack.path / self.__class__.pack_path
        if self._path is None:
            raise AttributeError("Can't get 'path' attribute.")
        return self._path

class _JsonMcPackFile(_McPackFile[MCPACK]):
    def __init__(
            self,  *,
            path: Optional[Path]=None,
            pack: Optional[MCPACK]=None) -> None:
        super().__init__(path=path, pack=pack)
        self._json: JSONWalker = JSONWalker.from_json(None)
        try:
            with self.path.open('r') as f:
                self._json = JSONWalker.load(f, cls=JSONCDecoder)
        except:
            pass  # self._json remains None walker

    @property
    def json(self) -> JSONWalker:
        return self._json

class _JsonMcPackFileMulti(_JsonMcPackFile[MCPACK]):
    @abstractproperty
    def identifiers(self) -> Tuple[str, ...]: ...

    @abstractmethod
    def __getitem__(self, key: str) -> JSONWalker: ...

# Query
class _JMPFMQuery(Generic[JSON_MC_PACK_FILE_MULTI]):
    '''
    "J - Json, M -Mc, P - Pack, F- File, M -Multi, query" - used
    in :class:`Project` to provide methods for finding McSpecialPackFiles that
    belong to the project.
    '''
    def __init__(self, pack_files: Sequence[JSON_MC_PACK_FILE_MULTI]):
        self.pack_files = pack_files

    def __getitem__(self, key: str) -> JSONWalker:
        for pack_file in reversed(self.pack_files):
            try:
                aaa=  pack_file[key]
                return aaa
            except:
                pass
        raise KeyError(key)

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        for pack_file in self.pack_files:
            result.extend(pack_file.identifiers)
        return tuple(set(result))

# SPECIAL PACK FILES - ONE FILE/PACK (IMPLEMENTATIONS)
class RpSoundDefinitionsJson(_JsonMcPackFileMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'sounds/sound_definitions.json'

    @property
    def format_version(self) -> Tuple[int, ...]:
        '''
        Return the format version of the sounds.json file or guess the version
        based on the file structure if it's missing.

        :returns: format version of the sounds.json file file
        '''
        # Legacy format (no format_version)
        format_version: Tuple[int, ...] = tuple()
        try:
            id_walker = self.json / 'format_version'
            if isinstance(id_walker, JSONWalkerStr):
                format_version = tuple(
                    [int(i) for i in id_walker.data.split('.')])
        except:  # Guessing the format version instead
            id_walker = self.json / 'sound_definitions'
            if isinstance(id_walker, JSONWalkerDict):
                format_version = (1, 14, 0)
        return format_version

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        if self.format_version <= (1, 14, 0):
            id_walker = self.json / 'sound_definitions'
            if isinstance(id_walker, JSONWalkerDict):
                for key in id_walker.data.keys():
                    if isinstance(key, str):
                        result.append(key)
        else:
            if isinstance(self.json, JSONWalkerDict):
                for key in self.json.data.keys():
                    if isinstance(key, str) and key != 'format_version':
                        result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JSONWalker:
        if key != 'format_version':
            if self.format_version <= (1, 14, 0):
                walker = self.json / 'sound_definitions' / key
                if not isinstance(walker, JSONWalkerInvalidPath):
                    return walker
            else:
                walker = self.json / key
                if not isinstance(walker, JSONWalkerInvalidPath):
                    return walker
        raise KeyError(key)

# SOUNDS.JSON
class RpSoundsJson(_JsonMcPackFile[ResourcePack]):
    pack_path: ClassVar[str] = 'sounds.json'

    def __init__(
            self, *,
            path: Optional[Path]=None,
            pack: Optional[ResourcePack]=None) -> None:
        super().__init__(path=path, pack=pack)

    @property
    def block_sound_event(self) -> _BlockSoundEventQuery:
        return _BlockSoundEventQuery((self,))
    @property
    def entity_sound_event(self) -> _EntitySoundEventQuery:
        return _EntitySoundEventQuery((self,))
    @property
    def individual_sound_event(self) -> _IndividualSoundEventQuery:
        return _IndividualSoundEventQuery((self,))
    @property
    def interactive_block_sound_event(
            self) -> _InteractiveBlockSoundEventQuery:
        return _InteractiveBlockSoundEventQuery((self,))
    @property
    def interactive_entity_sound_event(
            self) -> _InteractiveEntitySoundEventQuery:
        return _InteractiveEntitySoundEventQuery((self,))

# Various parts of the sounds.json file
class RpSoundsJsonPart(ABC):
    def __init__(self, sounds_json: RpSoundsJson, json: JSONWalker):
        self.sounds_json = sounds_json
        self.json = json

    @staticmethod
    def _get_float_tuple(walker) -> Optional[Tuple[float, float]]:
        '''
        Used to access pitch and volume from walker.
        '''
        if isinstance(walker, JSONWalkerList):
            data = walker.data
            if (
                    len(data) == 2 and isinstance(data[0], (float, int)) and
                    isinstance(data[1], (float, int))):
                return (data[0], data[1])
        elif isinstance(walker, (JSONWalkerFloat, JSONWalkerInt)):
            return (walker.data, walker.data)
        return None

    @abstractproperty
    def pitch(self) -> Optional[Tuple[float, float]]: ...

    @abstractproperty
    def volume(self) -> Optional[Tuple[float, float]]: ...

class RpSoundsJsonPartWithSound(RpSoundsJsonPart):
    @abstractproperty
    def sound(self) -> Optional[str]: ...

class BlockSoundEvent(RpSoundsJsonPartWithSound):
    @property
    def sound(self) -> Optional[str]:
        walker = self.json / 'sound'
        if isinstance(walker, JSONWalkerStr):
            return walker.data
        # Try to get the value from defaults
        walker = self.json.parent / 'default'
        if isinstance(walker, JSONWalkerStr):
            return walker.data
        return None

    @property
    def pitch(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(self.json / 'pitch')
        if result is None:
            result = RpSoundsJsonPart._get_float_tuple(
                self.json.parent.parent / 'pitch')
        return result

    @property
    def volume(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(self.json / 'volume')
        if result is None:
            result = RpSoundsJsonPart._get_float_tuple(
                self.json.parent.parent / 'volume')
        return result

class EntitySoundEvent(RpSoundsJsonPartWithSound):
    @property
    def sound(self) -> Optional[str]:
        if isinstance(self.json, JSONWalkerStr):
            return self.json.data
        walker = self.json / 'sound'
        if isinstance(walker, JSONWalkerStr):
            return walker.data
        event_key = self.json.parent_key
        if isinstance(event_key, str):
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' / 'events' /
                event_key)
            if isinstance(walker, JSONWalkerStr):
                return walker.data
            walker = walker / 'sound'
            if isinstance(walker, JSONWalkerStr):
                return walker.data
        return None

    @property
    def pitch(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(self.json / 'volume')
        if result is not None:
            return result
        result = RpSoundsJsonPart._get_float_tuple(
            self.json.parent.parent / 'volume')
        if result is not None:
            return result
        event_key = self.json.parent_key
        if isinstance(event_key, str):
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' /
                'events' / event_key / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
        return None

    @property
    def volume(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(self.json / 'volume')
        if result is not None:
            return result
        result = RpSoundsJsonPart._get_float_tuple(
            self.json.parent.parent / 'volume')
        if result is not None:
            return result
        event_key = self.json.parent_key
        if isinstance(event_key, str):
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' /
                'events' / event_key / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
        return None

class IndividualSoundEvent(RpSoundsJsonPartWithSound):
    @property
    def sound(self) -> Optional[str]:
        walker = self.json / 'sound'
        if isinstance(walker, JSONWalkerStr):
            return walker.data
        return None

    @property
    def pitch(self) -> Optional[Tuple[float, float]]:
        return RpSoundsJsonPart._get_float_tuple(self.json / 'pitch')

    @property
    def volume(self) -> Optional[Tuple[float, float]]:
        return RpSoundsJsonPart._get_float_tuple(self.json / 'volume')

class InteractiveBlockSoundEvent(RpSoundsJsonPartWithSound):
    @property
    def sound(self) -> Optional[str]:
        walker = self.json / 'sound'
        if isinstance(walker, JSONWalkerStr):
            return walker.data
        # Try to get the value from defaults
        walker = self.json.parent / 'default'
        if isinstance(walker, JSONWalkerStr):
            return walker.data
        return None

    @property
    def pitch(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(self.json / 'pitch')
        if result is None:
            result = RpSoundsJsonPart._get_float_tuple(
                self.json.parent.parent / 'pitch')
        return result

    @property
    def volume(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(self.json / 'volume')
        if result is None:
            result = RpSoundsJsonPart._get_float_tuple(
                self.json.parent.parent / 'volume')
        return result

class InteractiveEntitySoundEvent(RpSoundsJsonPart):
    @property
    def sounds(self) -> Dict[str, str]:
        '''
        A dictionary with sounds used by this event where key is a block name
        and value is the sound name.
        '''
        result: Dict[str, str] = {}
        if isinstance(self.json, JSONWalkerDict):
            for k, v in self.json.data.items():
                if isinstance(k, str) and isinstance(v, str):
                    result[k] = v
        return result

    @property
    def pitch(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(
            self.json.parent.parent / 'volume')
        if result is not None:
            return result
        event_key = self.json.parent_key
        if isinstance(event_key, str):
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' /
                'events' / event_key / 'default' / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
        return None

    @property
    def volume(self) -> Optional[Tuple[float, float]]:
        result = RpSoundsJsonPart._get_float_tuple(
            self.json.parent.parent / 'volume')
        event_key = self.json.parent_key
        if isinstance(event_key, str):
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' /
                'events' / event_key / 'default' / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
            walker = (
                self.json.parent.parent.parent.parent / 'defaults' / 'volume')
            result = RpSoundsJsonPart._get_float_tuple(walker)
            if result is not None:
                return result
        return None


# sounds.json queries (used by )
class _RSJPQuery(Generic[RP_SOUNDS_JSON_PART, RP_SOUNDS_JSON_PART_KEY]):
    '''
    "R - Rp, S - Sounds, J - Json, P - Part, query" - used in :class:`Project`
    and :class:`RpSoundsJsonPart` to get info about parts of sounds.json
    file(s).
    '''
    def __init__(self, sounds_json_collection: Sequence[RpSoundsJson]) -> None:
        self.sounds_json_collection = sounds_json_collection

    def __getitem__(
        self, key: RP_SOUNDS_JSON_PART_KEY) -> RP_SOUNDS_JSON_PART: ...

    def keys(self) -> Tuple[RP_SOUNDS_JSON_PART_KEY, ...]: ...

class _BlockSoundEventQuery(_RSJPQuery[BlockSoundEvent, Tuple[str, str]]):
    def __getitem__(self, key: Tuple[str, str]) -> BlockSoundEvent:
        for collection in reversed(self.sounds_json_collection):
            if key[1] == 'default':
                raise KeyError(key)
            walker = (
                collection.json / 'block_sounds' / key[0] / 'events' / key[1])
            if not isinstance(walker, JSONWalkerInvalidPath):
                return BlockSoundEvent(collection, walker)
        raise KeyError(key)

    def keys(self) -> Tuple[Tuple[str, str], ...]:
        result: List[Tuple[str, str]] = []
        for collection in self.sounds_json_collection:
            walkers = (
                collection.json / 'block_sounds' // str / 'events' // str)
            for walker in walkers:
                k0 = walker.parent.parent.parent_key  # block_sounds/->[str]<-
                k1 = walker.parent_key  # block_sounds/[str]/events/->[str]<-
                if (
                        not isinstance(k0, str) or not isinstance(k1, str) or
                        k1 == 'default'):
                    continue
                result.append((k0, k1))
        return tuple(set(result))

class _EntitySoundEventQuery(_RSJPQuery[EntitySoundEvent, Tuple[str, str]]):
    def __getitem__(self, key: Tuple[str, str]) -> EntitySoundEvent:
        for collection in reversed(self.sounds_json_collection):
            walker = (
                collection.json / 'entity_sounds' / 'entities' / key[0] /
                'events' / key[1])
            if not isinstance(walker, JSONWalkerInvalidPath):
                return EntitySoundEvent(collection, walker)
        raise KeyError(key)

    def keys(self) -> Tuple[Tuple[str, str], ...]:
        result: List[Tuple[str, str]] = []
        for collection in self.sounds_json_collection:
            walkers = (
                collection.json / 'entity_sounds' / 'entities' // str /
                'events' // str)
            for walker in walkers:
                k0 = walker.parent.parent.parent_key  # entity_sounds/->[str]<-
                k1 = walker.parent_key  # entity_sounds/[str]/events/->[str]<-
                if not isinstance(k0, str) or not isinstance(k1, str):
                    continue
                result.append((k0, k1))
        return tuple(set(result))

class _IndividualSoundEventQuery(_RSJPQuery[IndividualSoundEvent, str]):
    def __getitem__(self, key: str) -> IndividualSoundEvent:
        for collection in reversed(self.sounds_json_collection):
            walker = (
                collection.json / 'individual_event_sounds' / 'events' / key)
            if not isinstance(walker, JSONWalkerInvalidPath):
                return IndividualSoundEvent(collection, walker)
        raise KeyError(key)

    def keys(self) -> Tuple[str, ...]:
        result: List[str] = []
        for collection in self.sounds_json_collection:
            walkers = (
                collection.json / 'individual_event_sounds' / 'events' // str)
            for walker in walkers:
                key = walker.parent_key  # block_sounds/[str]/events/->[str]<-
                if not isinstance(key, str):
                    continue
                result.append(key)
        return tuple(set(result))

class _InteractiveBlockSoundEventQuery(
        _RSJPQuery[InteractiveBlockSoundEvent, Tuple[str, str]]):
    def __getitem__(self, key: Tuple[str, str]) -> InteractiveBlockSoundEvent:
        for collection in reversed(self.sounds_json_collection):
            if key[1] == 'default':
                raise KeyError(key)
            walker = (
                collection.json / 'interactive_sounds' / 'block_sounds' /
                key[0] / 'events' / key[1])
            if not isinstance(walker, JSONWalkerInvalidPath):
                return InteractiveBlockSoundEvent(collection, walker)
        raise KeyError(key)

    def keys(self) -> Tuple[Tuple[str, str], ...]:
        result: List[Tuple[str, str]] = []
        for collection in self.sounds_json_collection:
            walkers = (
                collection.json / 'interactive_sounds' / 'block_sounds' //
                str / 'events' // str)
            for walker in walkers:
                k0 = walker.parent.parent.parent_key  # block_sounds/->[str]<-
                k1 = walker.parent_key  # block_sounds/[str]/events/->[str]<-
                if (
                        not isinstance(k0, str) or not isinstance(k1, str) or
                        k1 == 'default'):
                    continue
                result.append((k0, k1))
        return tuple(set(result))

class _InteractiveEntitySoundEventQuery(_RSJPQuery[InteractiveEntitySoundEvent, Tuple[str, str]]):
    def __getitem__(self, key: Tuple[str, str]) -> InteractiveEntitySoundEvent:
        for collection in reversed(self.sounds_json_collection):
            walker = (
                collection.json / 'interactive_sounds' / 'entity_sounds' /
                'entities' / key[0] / 'events' / key[1])
            if not isinstance(walker, JSONWalkerInvalidPath):
                return InteractiveEntitySoundEvent(collection, walker)
        raise KeyError(key)

    def keys(self) -> Tuple[Tuple[str, str], ...]:
        result: List[Tuple[str, str]] = []
        for collection in self.sounds_json_collection:
            walkers = (
                collection.json / 'interactive_sounds' / 'entity_sounds' /
                'entities' // str / 'events' // str)
            for walker in walkers:
                k0 = walker.path[-3]  # entity_sounds/->[str]<-
                k1 = walker.path[-1]  # entity_sounds/[str]/events/->[str]<-
                if not isinstance(k0, str) or not isinstance(k1, str):
                    continue
                result.append((k0, k1))
        return tuple(set(result))
