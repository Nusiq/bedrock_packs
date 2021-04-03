'''
Python module for working with Minecraft bedrock edition projects.
'''
from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty

from typing import (
    ClassVar, Dict, List, Optional, Reversible, Sequence, Tuple, Type, TypeVar,
    Generic, Union)
from pathlib import Path

from .json import JSONCDecoder, JsonWalker

# Package version
VERSION = (0, 1)
__version__ = '.'.join([str(x) for x in VERSION])



# Type variables
MCPACK = TypeVar('MCPACK', bound='_Pack')
MCFILE_COLLECTION = TypeVar('MCFILE_COLLECTION', bound='_McFileCollection')
MCFILE = TypeVar('MCFILE', bound='_McFile')
MCFILE_SINGLE = TypeVar('MCFILE_SINGLE', bound='_McFileSingle')
MCFILE_MULTI = TypeVar('MCFILE_MULTI', bound='_McFileMulti')
UNIQUE_MC_FILE_JSON_MULTI = TypeVar(
    'UNIQUE_MC_FILE_JSON_MULTI',
    bound='_UniqueMcFileJsonMulti')
RP_SOUNDS_JSON_PART = TypeVar('RP_SOUNDS_JSON_PART', bound='_RpSoundsJsonPart')
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
        '''Tuple with behavior packs from this :class:`Project`'''
        return tuple(self._bps)

    @property
    def rps(self) -> Tuple[ResourcePack, ...]:
        '''Tuple with resource packs from this :class:`Project`'''
        return tuple(self._rps)

    def uuid_bps(self) -> Dict[str, BehaviorPack]:
        '''
        Returns a dictionary that maps :class:`BehaviorPack` objects that
        belong to this :class:`Project` to their UUIDs (the UUIDS are used
        as dict keys). The packs without UUID are skipped.
        '''
        result: Dict[str, BehaviorPack] = {}
        for bp in self.bps:
            if bp.uuid is not None:
                result[bp.uuid] = bp
        return result

    def uuid_rps(self) -> Dict[str, ResourcePack]:
        '''
        Returns a dictionary that maps :class:`ResourcePack` objects that
        belong to this :class:`Project` to their UUIDs (the UUIDS are used
        as dict keys). The packs without UUID are skipped.
        '''
        result: Dict[str, ResourcePack] = {}
        for rp in self.rps:
            if rp.uuid is not None:
                result[rp.uuid] = rp
        return result

    def path_bps(self) -> Dict[Path, BehaviorPack]:
        '''
        Returns a dictionary that maps :class:`BehaviorPack` objects that
        belong to this :class:`Project` to their paths (the paths are used
        as dict keys).
        '''
        result: Dict[Path, BehaviorPack] = {}
        for bp in self.bps:
            result[bp.path] = bp
        return result

    def path_rps(self) -> Dict[Path, ResourcePack]:
        '''
        Returns a dictionary that maps :class:`ResourcePack` objects that
        belong to this :class:`Project` to their paths (the paths are used
        as dict keys).
        '''
        result: Dict[Path, ResourcePack] = {}
        for rp in self.rps:
            result[rp.path] = rp
        return result

    def add_bp(self, pack: BehaviorPack) -> None:
        '''
        Adds behavior pack to this project.

        :param pack: the behavior pack
        '''
        self._bps.append(pack)
        pack.project = self

    def add_rp(self, pack: ResourcePack) -> None:
        '''
        Adds resource pack to this project

        :param pack: the resource pack
        '''
        self._rps.append(pack)
        pack.project = self

    @property
    def bp_entities(
            self) -> _McFileCollectionQuery[BpEntity]:
        '''
        Returns a file collection of all behavior pack entities from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            BpEntities, [i.entities for i in self.bps])

    @property
    def rp_entities(
            self) -> _McFileCollectionQuery[RpEntity]:
        '''
        Returns a file collection of all resource pack entities from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            RpEntities, [i.entities for i in self.rps])

    @property
    def bp_animation_controllers(
            self) -> _McFileCollectionQuery[BpAnimationController]:
        '''
        Returns a file collection of all behavior pack animation controllers
        from this :class:`Project`.
        '''
        return _McFileCollectionQuery(
            BpAnimationControllers,
            [i.animation_controllers for i in self.bps])

    @property
    def rp_animation_controllers(
            self) -> _McFileCollectionQuery[RpAnimationController]:
        '''
        Returns a file collection of all resource pack animation controllers
        from this :class:`Project`.
        '''
        return _McFileCollectionQuery(
            RpAnimationControllers,
            [i.animation_controllers for i in self.rps])

    @property
    def bp_blocks(
            self) -> _McFileCollectionQuery[BpBlock]:
        '''
        Returns a file collection of all behavior pack blocks from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(BpBlocks, [i.blocks for i in self.bps])

    @property
    def bp_items(
            self) -> _McFileCollectionQuery[BpItem]:
        '''
        Returns a file collection of all behavior pack items from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(BpItems, [i.items for i in self.bps])

    @property
    def rp_items(
            self) -> _McFileCollectionQuery[RpItem]:
        '''
        Returns a file collection of all resource pack items from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(RpItems, [i.items for i in self.rps])

    @property
    def bp_loot_tables(
            self) -> _McFileCollectionQuery[BpLootTable]:
        '''
        Returns a file collection of all behavior pack loot tables from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            BpLootTables, [i.loot_tables for i in self.bps])

    @property
    def bp_functions(
            self) -> _McFileCollectionQuery[BpFunction]:
        '''
        Returns a file collection of all behavior pack functions from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            BpFunctions, [i.functions for i in self.bps])

    @property
    def rp_sound_files(
            self) -> _McFileCollectionQuery[RpSoundFile]:
        '''
        Returns a file collection of all resource pack sound files from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            RpSoundFiles, [i.sound_files for i in self.rps])

    @property
    def rp_texture_files(
            self) -> _McFileCollectionQuery[RpTextureFile]:
        '''
        Returns a file collection of all resource pack texture files from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            RpTextureFiles, [i.texture_files for i in self.rps])

    @property
    def bp_spawn_rules(
            self) -> _McFileCollectionQuery[BpSpawnRule]:
        '''
        Returns a file collection of all behavior pack spawn rules from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            BpSpawnRules, [i.spawn_rules for i in self.bps])

    @property
    def bp_trades(
            self) -> _McFileCollectionQuery[BpTrade]:
        '''
        Returns a file collection of all behavior pack trades from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(BpTrades, [i.trades for i in self.bps])

    @property
    def bp_recipes(
            self) -> _McFileCollectionQuery[BpRecipe]:
        '''
        Returns a file collection of all behavior pack recipes from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(BpRecipes, [i.recipes for i in self.bps])

    @property
    def rp_models(
            self) -> _McFileCollectionQuery[RpModel]:
        '''
        Returns a file collection of all resource pack models from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(RpModels, [i.models for i in self.rps])

    @property
    def rp_particles(
            self) -> _McFileCollectionQuery[RpParticle]:
        '''
        Returns a file collection of all resource pack particles from this
        :class:`Project`.
        '''
        return _McFileCollectionQuery(
            RpParticles, [i.particles for i in self.rps])

    @property
    def rp_render_controllers(
            self) -> _McFileCollectionQuery[RpRenderController]:
        '''
        Returns a file collection of all resource pack render controllers
        from this :class:`Project`.
        '''
        return  _McFileCollectionQuery(
            RpRenderControllers, [i.render_controllers for i in self.rps])

    @property
    def rp_sound_definitions_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpSoundDefinitionsJson]:
        '''
        Returns a unique file collection of all resource pack
        sound_definitions.json files from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery(
            [i.sound_definitions_json for i in self.rps])

    @property
    def rp_blocks_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpBlocksJson]:
        '''
        Returns a unique file collection of all resource pack blocks.json files
        from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery([i.blocks_json for i in self.rps])

    @property
    def rp_music_definitions_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpMusicDefinitionsJson]:
        '''
        Returns a unique file collection of all resource pack
        music_definitions.json files from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery(
            [i.music_definitions_json for i in self.rps])

    @property
    def rp_biomes_client_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpBiomesClientJson]:
        '''
        Returns a unique file collection of all resource pack
        biomes_client.json files from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery(
            [i.biomes_client_json for i in self.rps])

    @property
    def rp_item_texture_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpItemTextureJson]:
        '''
        Returns a unique file collection of all resource pack
        item_texture.json files from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery(
            [i.item_texture_json for i in self.rps])

    @property
    def rp_flipbook_textures_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpFlipbookTexturesJson]:
        '''
        Returns a unique file collection of all resource pack
        flipbook_textures.json files from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery(
            [i.flipbook_textures_json for i in self.rps])

    @property
    def rp_terrain_texture_json(
            self) -> _UniqueMcFileJsonMultiQuery[RpTerrainTextureJson]:
        '''
        Returns a unique file collection of all resource pack
        terrain_texture.json files from this :class:`Project`.
        '''
        return _UniqueMcFileJsonMultiQuery(
            [i.terrain_texture_json for i in self.rps])


# PACKS
class _Pack(ABC):
    '''
    Behavior pack or resource pack. A collection of
    :class:`_McFileCollection`.
    '''
    def __init__(self, path: Path, project: Optional[Project]=None) -> None:
        self.project: Optional[Project] = project
        self.path: Path = path
        self._manifest: Optional[JsonWalker] = None

    @property
    def manifest(self) -> Optional[JsonWalker]:
        ''':class:`JsonWalker` for manifest file'''
        if self._manifest is None:
            manifest_path = self.path / 'manifest.json'
            try:
                with manifest_path.open('r') as f:
                    self._manifest = JsonWalker.load(f)
            except:
                return None
        return self._manifest

    @property
    def uuid(self) -> Optional[str]:
        '''the UUID from manifest.'''
        if self.manifest is not None:
            uuid_walker = (self.manifest / 'header' / 'uuid')
            if isinstance(uuid_walker.data, str):
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
        self._sound_definitions_json: Optional[RpSoundDefinitionsJson] = None
        self._sounds_json: Optional[RpSoundsJson] = None
        self._blocks_json: Optional[RpBlocksJson] = None
        self._music_definitions_json: Optional[RpMusicDefinitionsJson] = None
        self._biomes_client_json: Optional[RpBiomesClientJson] = None
        self._item_texture_json: Optional[RpItemTextureJson] = None
        self._flipbook_textures_json: Optional[RpFlipbookTexturesJson] = None
        self._terrain_texture_json: Optional[RpTerrainTextureJson] = None
        self._sound_files: Optional[RpSoundFiles] = None
        self._texture_files: Optional[RpTextureFiles] = None

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
    def sound_definitions_json(self) -> RpSoundDefinitionsJson:
        if self._sound_definitions_json is None:
            self._sound_definitions_json = RpSoundDefinitionsJson(pack=self)
        return self._sound_definitions_json

    @property
    def sounds_json(self) -> RpSoundsJson:
        if self._sounds_json is None:
            self._sounds_json = RpSoundsJson(pack=self)
        return self._sounds_json

    @property
    def blocks_json(self) -> RpBlocksJson:
        if self._blocks_json is None:
            self._blocks_json = RpBlocksJson(pack=self)
        return self._blocks_json

    @property
    def music_definitions_json(self) -> RpMusicDefinitionsJson:
        if self._music_definitions_json is None:
            self._music_definitions_json = RpMusicDefinitionsJson(pack=self)
        return self._music_definitions_json

    @property
    def biomes_client_json(self) -> RpBiomesClientJson:
        if self._biomes_client_json is None:
            self._biomes_client_json = RpBiomesClientJson(pack=self)
        return self._biomes_client_json

    @property
    def item_texture_json(self) -> RpItemTextureJson:
        if self._item_texture_json is None:
            self._item_texture_json = RpItemTextureJson(pack=self)
        return self._item_texture_json

    @property
    def flipbook_textures_json(self) -> RpFlipbookTexturesJson:
        if self._flipbook_textures_json is None:
            self._flipbook_textures_json = RpFlipbookTexturesJson(pack=self)
        return self._flipbook_textures_json

    @property
    def terrain_texture_json(self) -> RpTerrainTextureJson:
        if self._terrain_texture_json is None:
            self._terrain_texture_json = RpTerrainTextureJson(pack=self)
        return self._terrain_texture_json

    @property
    def sound_files(self) -> RpSoundFiles:
        if self._sound_files is None:
            self._sound_files = RpSoundFiles(pack=self)
        return self._sound_files

    @property
    def texture_files(self) -> RpTextureFiles:
        if self._texture_files is None:
            self._texture_files = RpTextureFiles(pack=self)
        return self._texture_files

# OBJECT COLLECTIONS (GENERIC)
class _McFileCollection(Generic[MCPACK, MCFILE], ABC):
    '''
    Collection of files that contain objects of a certain type (collection of :class:`_McFile`).
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
            for file_pattern in self.__class__.file_patterns:
                for fp in self.path.glob(file_pattern):
                    if not fp.is_file():
                        continue
                    try:
                        obj: MCFILE = self._make_collection_object(fp)
                    except AttributeError:
                        continue
                    self._objects.append(obj)
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

    # Different for _McFileMulti and _McFileSingle collections
    @abstractmethod
    def keys(self) -> Tuple[str, ...]: ...

    @classmethod
    def _get_item_from_combined_collections(
            cls, collections: Reversible[_McFileCollection[MCPACK, MCFILE]],
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

    @abstractmethod
    def _quick_access_list_views(
    self) -> Tuple[Dict[Path, List[str]], Dict[str, List[MCFILE]]]: ...

    @abstractmethod
    def _make_collection_object(self, path: Path) -> MCFILE:
        '''Create an object connected to self from path'''

# Query
class _McFileCollectionQuery(Generic[MCFILE]):
    '''
    Groups multiple file collections (sometimes from multiple packs).
    Used in :class:`Project` to provide methods for finding McFiles in
    :class:`McFileCollections` that belong to that project.
    '''
    def __init__(
            self,
            collections_type: Type[_McFileCollection[MCPACK, MCFILE]],
            collections: Sequence[_McFileCollection[MCPACK, MCFILE]]):
        self.collections = collections
        self.collections_type = collections_type

    def __getitem__(self, key: Union[str, slice]) -> MCFILE:
        return self.collections_type._get_item_from_combined_collections(
            self.collections, key)

    def __iter__(self):  # Apparently getitem automatically implements __iter__
        raise TypeError(f'{type(self).__name__} is not iterable.')

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
    '''
    A file that can contain only one object of certain type from a pack.
    :class:`McFile` with single Minecraft object
    '''
    @abstractproperty
    def identifier(self) -> Optional[str]: ...

class _McFileJsonSingle(_McFileSingle[MCFILE_COLLECTION]):
    '''
    A JSON file that can contain only one object of certain type from a pack.
    :class:`McFile` that has JSON in it, with single Minecraft object.
    '''
    def __init__(
            self, path: Path,
            owning_collection: Optional[MCFILE_COLLECTION]=None
    ) -> None:
        super().__init__(path, owning_collection=owning_collection)
        self._json: JsonWalker = JsonWalker(None)
        try:
            with path.open('r') as f:
                self._json = JsonWalker.load(f, cls=JSONCDecoder)
        except:
            pass  # self._json remains None walker

    @property
    def json(self) -> JsonWalker:
        return self._json

class _McFileMulti(_McFile[MCFILE_COLLECTION]):
    '''
    A file that can contain multiple objects of certain type from a pack.
    :class:`McFile` with multiple Minecraft objects.
    '''
    @abstractproperty
    def identifiers(self) -> Tuple[str, ...]: ...

class _McFileJsonMulti(_McFileMulti[MCFILE_COLLECTION]):
    '''
    A JSON file that can contain multiple objects of certain type from a pack.
    :class:`McFile` that has JSON in it, with multiple Minecraft objects.
    '''
    def __init__(
            self, path: Path,
            owning_collection: Optional[MCFILE_COLLECTION]=None
    ) -> None:
        super().__init__(path, owning_collection=owning_collection)
        self._json: JsonWalker = JsonWalker(None)
        try:
            with path.open('r') as f:
                self._json = JsonWalker.load(f, cls=JSONCDecoder)
        except:
            pass  # self._json remains None walker

    @property
    def json(self) -> JsonWalker:
        return self._json

    @abstractmethod
    def __getitem__(self, key: str) -> JsonWalker: ...

# OBJECTS (IMPLEMENTATION)
class BpEntity(_McFileJsonSingle['BpEntities']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:entity" / "description" / "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class RpEntity(_McFileJsonSingle['RpEntities']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:client_entity" / "description" /
            "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class _AnimationController(_McFileJsonMulti[MCFILE_COLLECTION]):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "animation_controllers")
        if isinstance(id_walker.data, dict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        return tuple()

    def __getitem__(self, key: str) -> JsonWalker:
        id_walker = (self.json / "animation_controllers")
        if isinstance(id_walker.data, dict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)
class BpAnimationController(_AnimationController['BpAnimationControllers']): ...
class RpAnimationController(_AnimationController['RpAnimationControllers']): ...

class _Animation(_McFileJsonMulti[MCFILE_COLLECTION]):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "animations")
        if isinstance(id_walker.data, dict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        return tuple()

    def __getitem__(self, key: str) -> JsonWalker:
        id_walker = (self.json / "animations")
        if isinstance(id_walker.data, dict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)
class BpAnimation(_Animation['BpAnimations']): ...
class RpAnimation(_Animation['RpAnimations']): ...

class BpBlock(_McFileJsonSingle['BpBlocks']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:block" / "description" / "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class BpItem(_McFileJsonSingle['BpItems']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class RpItem(_McFileJsonSingle['RpItems']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:item" / "description" / "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class BpLootTable(_McFileJsonSingle['BpLootTables']):
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

class RpSoundFile(_McFileSingle['RpSoundFiles']):
    @property
    def identifier(self) -> Optional[str]:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            return None
        return self.path.relative_to(
            self.owning_collection.pack.path
        ).with_suffix('').as_posix()

class RpTextureFile(_McFileSingle['RpTextureFiles']):
    @property
    def identifier(self) -> Optional[str]:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            return None
        return self.path.relative_to(
            self.owning_collection.pack.path
        ).with_suffix('').as_posix()

class BpSpawnRule(_McFileJsonSingle['BpSpawnRules']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "minecraft:spawn_rules" / "description" / "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class BpTrade(_McFileJsonSingle['BpTrades']):
    @property
    def identifier(self) -> Optional[str]:
        if (
                self.owning_collection is None or
                self.owning_collection.pack is None):
            return None
        return self.path.relative_to(
            self.owning_collection.pack.path).as_posix()

class RpModel(_McFileJsonMulti['RpModels']):
    @property
    def format_version(self) -> Tuple[int, ...]:
        '''
        Return the format version of the model or guess the version based
        on the file structure if it's missing.
        '''
        format_version: Tuple[int, ...] = (1, 8, 0)
        try:
            id_walker = self.json / 'format_version'
            if isinstance(id_walker.data, str):
                format_version = tuple(
                    [int(i) for i in id_walker.data.split('.')])
        except:  # Guessing the format version instead
            id_walker = self.json / 'minecraft:geometry'
            if isinstance(id_walker.data, list):
                format_version = (1, 16, 0)
        return format_version

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        if self.format_version <= (1, 10, 0):
            if isinstance(self.json.data, dict):
                for k in self.json.data.keys():
                    if isinstance(k, str) and k.startswith('geometry.'):
                        result.append(k)
        else:  # Probably something <= 1.16.0
            id_walker = (
                self.json / 'minecraft:geometry' // int / 'description' /
                'identifier')
            for i in id_walker:
                if isinstance(i.data, str):
                    if i.data.startswith('geometry.'):
                        result.append(i.data)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        if not key.startswith('.geometry'):
            raise AttributeError("Key must start with '.geometry'")
        if self.format_version <= (1, 10, 0):
            if isinstance(self.json.data, dict):
                return self.json / key
        else:  # Probably something <= 1.16.0
            id_walker = (
                self.json / 'minecraft:geometry' // int)
            for model in id_walker:
                if not isinstance(
                        (model / 'description' / 'identifier' / key).data,
                        Exception):
                    return model
        raise KeyError(key)

class RpParticle(_McFileJsonSingle['RpParticles']):
    @property
    def identifier(self) -> Optional[str]:
        id_walker = (
            self.json / "particle_effect" / "description" / "identifier")
        if isinstance(id_walker.data, str):
            return id_walker.data
        return None

class RpRenderController(_McFileJsonMulti['RpRenderControllers']):  # GENERIC
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (self.json / "render_controllers")
        if isinstance(id_walker.data, dict):
            return tuple(
                [k for k in id_walker.data.keys() if isinstance(k, str)])
        return tuple()

    def __getitem__(self, key: str) -> JsonWalker:
        id_walker = (self.json / "render_controllers")
        if isinstance(id_walker.data, dict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)

class BpRecipe(_McFileJsonMulti['BpRecipes']):
    @property
    def identifiers(self) -> Tuple[str, ...]:
        id_walker = (
            self.json // '(minecraft:recipe_shaped)|(minecraft:recipe_furnace)'
            '|(minecraft:recipe_shapeless)|(minecraft:recipe_brewing_mix)|'
            '(minecraft:recipe_brewing_container)' / "description"  /
            "identifier")
        result: List[str] = []
        for identifier_walker in id_walker.data:
            if isinstance(identifier_walker.data, str):
                result.append(identifier_walker.data)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        id_walker = (
            self.json // '(minecraft:recipe_shaped)|(minecraft:recipe_furnace)'
            '|(minecraft:recipe_shapeless)|(minecraft:recipe_brewing_mix)|'
            '(minecraft:recipe_brewing_container)' / "description"  /
            "identifier")
        if isinstance(id_walker.data, dict):
            if key in id_walker.data:
                return id_walker / key
        raise KeyError(key)

# OBJECT COLLECTIONS (IMPLEMENTATIONS)
class _McFileCollectionSingle(_McFileCollection[MCPACK, MCFILE_SINGLE]):
    '''
    Collection of files where each file represent exactly one object of certain type
    (a collection of :class:`_McFileSingle` objects).
    '''
    def keys(self) -> Tuple[str, ...]:
        result: List[str] = []
        for obj in self.objects:
            if obj.identifier is not None:
                result.append(obj.identifier)
        return tuple(set(result))

    def _quick_access_list_views(self) -> Tuple[
            Dict[Path, List[str]], Dict[str, List[MCFILE_SINGLE]]]:
        '''
        Creates and returns dictionaries with summary of the objects contained
        in this collection. Used by __getitem__ to find specific objects.

        First dict maps identifiers (values) to paths (keys),
        second dict maps objects from this collection (values) to
        identifiers (keys).
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

class _McFileCollectionMulti(_McFileCollection[MCPACK, MCFILE_MULTI]):
    '''
    Collection of files where each file can represent multiple objects of certain type
    (a collection of :class:`_McFileMulti` objects).
    '''
    def keys(self) -> Tuple[str, ...]:
        result: List[str] = []
        for obj in self.objects:
            result.extend(obj.identifiers)
        return tuple(set(result))

    def _quick_access_list_views(self) -> Tuple[
            Dict[Path, List[str]], Dict[str, List[MCFILE_MULTI]]]:
        '''
        Creates and returns two dictionaries with summary of the objects
        contained in this collection. Used by __getitem__ to find specific
        objects.

        First dict maps identifiers (values) to paths (keys),
        second mapsobjects from this collection (values) to identifiers (keys).
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

class BpEntities(_McFileCollectionSingle[BehaviorPack, BpEntity]):
    pack_path = 'entities'
    file_patterns = ('**/*.json',)

    def _make_collection_object(self, path: Path) -> BpEntity:
        return BpEntity(path, self)

class RpEntities(_McFileCollectionSingle[ResourcePack, RpEntity]):
    pack_path = 'entity'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpEntity:
        return RpEntity(path, self)

class BpAnimationControllers(
        _McFileCollectionMulti[BehaviorPack, BpAnimationController]):
    pack_path = 'animation_controllers'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpAnimationController:
        return BpAnimationController(path, self)

class RpAnimationControllers(
        _McFileCollectionMulti[ResourcePack, RpAnimationController]):
    pack_path = 'animation_controllers'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpAnimationController:
        return RpAnimationController(path, self)

class BpAnimations(_McFileCollectionMulti[BehaviorPack, BpAnimation]):
    pack_path = 'animations'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpAnimation:
        return BpAnimation(path, self)

class RpAnimations(_McFileCollectionMulti[ResourcePack, RpAnimation]):
    pack_path = 'animations'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpAnimation:
        return RpAnimation(path, self)

class BpBlocks(_McFileCollectionSingle[BehaviorPack, BpBlock]):
    pack_path = 'blocks'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpBlock:
        return BpBlock(path, self)

class BpItems(_McFileCollectionSingle[BehaviorPack, BpItem]):
    pack_path = 'items'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpItem:
        return BpItem(path, self)

class RpItems(_McFileCollectionSingle[ResourcePack, RpItem]):
    pack_path = 'items'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpItem:
        return RpItem(path, self)

class BpLootTables(_McFileCollectionSingle[BehaviorPack, BpLootTable]):
    pack_path = 'loot_tables'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpLootTable:
        return BpLootTable(path, self)

class BpFunctions(_McFileCollectionSingle[BehaviorPack, BpFunction]):
    pack_path = 'functions'
    file_patterns = ('**/*.mcfunction',)
    def _make_collection_object(self, path: Path) -> BpFunction:
        return BpFunction(path, self)

class RpSoundFiles(_McFileCollectionSingle[ResourcePack, RpSoundFile]):
    pack_path = 'sounds'
    file_patterns = ('**/*.ogg', '**/*.wav', '**/*.mp3', '**/*.fsb',)
    def _make_collection_object(self, path: Path) -> RpSoundFile:
        return RpSoundFile(path, self)

class RpTextureFiles(_McFileCollectionSingle[ResourcePack, RpTextureFile]):
    pack_path = 'textures'

    file_patterns = ('**/*.tga', '**/*.png', '**/*.jpg',)
    def _make_collection_object(self, path: Path) -> RpTextureFile:
        return RpTextureFile(path, self)

class BpSpawnRules(_McFileCollectionSingle[BehaviorPack, BpSpawnRule]):
    pack_path = 'spawn_rules'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpSpawnRule:
        return BpSpawnRule(path, self)

class BpTrades(_McFileCollectionSingle[BehaviorPack, BpTrade]):
    pack_path = 'trading'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpTrade:
        return BpTrade(path, self)

class RpModels(_McFileCollectionMulti[ResourcePack, RpModel]):
    pack_path = 'models'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpModel:
        return RpModel(path, self)

class RpParticles(_McFileCollectionSingle[ResourcePack, RpParticle]):
    pack_path = 'particles'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpParticle:
        return RpParticle(path, self)

class RpRenderControllers(
        _McFileCollectionMulti[ResourcePack, RpRenderController]):
    pack_path = 'render_controllers'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> RpRenderController:
        return RpRenderController(path, self)

class BpRecipes(_McFileCollectionMulti[BehaviorPack, BpRecipe]):
    pack_path = 'recipes'
    file_patterns = ('**/*.json',)
    def _make_collection_object(self, path: Path) -> BpRecipe:
        return BpRecipe(path, self)

# SPECIAL PACK FILES - ONE FILE PER PACK (GENERICS)
class _UniqueMcFile(Generic[MCPACK], ABC):
    '''
    A file which is unique for the pack. E.g. You can have only one blocks.json file in
    a resource pack.
    '''
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

class _UniqueMcFileJson(_UniqueMcFile[MCPACK]):
    def __init__(
            self,  *,
            path: Optional[Path]=None,
            pack: Optional[MCPACK]=None) -> None:
        super().__init__(path=path, pack=pack)
        self._json: JsonWalker = JsonWalker(None)
        try:
            with self.path.open('r') as f:
                self._json = JsonWalker.load(f, cls=JSONCDecoder)
        except:
            pass  # self._json remains None walker

    @property
    def json(self) -> JsonWalker:
        return self._json

class _UniqueMcFileJsonMulti(_UniqueMcFileJson[MCPACK]):
    @abstractproperty
    def identifiers(self) -> Tuple[str, ...]: ...

    @abstractmethod
    def __getitem__(self, key: str) -> JsonWalker: ...

# Query
class _UniqueMcFileJsonMultiQuery(Generic[UNIQUE_MC_FILE_JSON_MULTI]):
    '''
    Groups multiple unique files (often from multiple packs).
    Used in :class:`Project` to provide methods for finding McSpecialPackFiles
    that belong to the project.
    '''
    def __init__(self, pack_files: Sequence[UNIQUE_MC_FILE_JSON_MULTI]):
        self.pack_files = pack_files

    def __getitem__(self, key: str) -> JsonWalker:
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
class RpSoundDefinitionsJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'sounds/sound_definitions.json'

    @property
    def format_version(self) -> Tuple[int, ...]:
        '''
        Return the format version of the sounds.json file or guess the version
        based on the file structure if it's missing.
        '''
        # Legacy format (no format_version)
        format_version: Tuple[int, ...] = tuple()
        try:
            id_walker = self.json / 'format_version'
            if isinstance(id_walker.data, str):
                format_version = tuple(
                    [int(i) for i in id_walker.data.split('.')])
        except:  # Guessing the format version instead
            id_walker = self.json / 'sound_definitions'
            if isinstance(id_walker.data, dict):
                format_version = (1, 14, 0)
        return format_version

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        if self.format_version <= (1, 14, 0):
            id_walker = self.json / 'sound_definitions'
            if isinstance(id_walker.data, dict):
                for key in id_walker.data.keys():
                    if isinstance(key, str):
                        result.append(key)
        else:
            if isinstance(self.json.data, dict):
                for key in self.json.data.keys():
                    if isinstance(key, str) and key != 'format_version':
                        result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        if key != 'format_version':
            if self.format_version <= (1, 14, 0):
                walker = self.json / 'sound_definitions' / key
                if not isinstance(walker.data, Exception):
                    return walker
            else:
                walker = self.json / key
                if not isinstance(walker.data, Exception):
                    return walker
        raise KeyError(key)

class RpBiomesClientJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'biomes_client.json'

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        walker = self.json / 'biomes'
        if isinstance(walker.data, dict):
            for key in walker.data.keys():
                if isinstance(key, str):
                    result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        result = self.json / 'biomes' / key
        if isinstance(result.data, Exception):
            raise KeyError(key)
        return result

class RpItemTextureJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'textures/item_texture.json'

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        walker = self.json / 'texture_data'
        if isinstance(walker.data, dict):
            for key in walker.data.keys():
                if isinstance(key, str):
                    result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        result = self.json / 'texture_data' / key
        if isinstance(result.data, Exception):
            raise KeyError(key)
        return result

class RpFlipbookTexturesJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'textures/flipbook_textures.json'

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        walkers = self.json // int / 'flipbook_texture'
        for walker in walkers:
            if isinstance(walker.data, str):
                result.append(walker.data)
        return tuple(set(result))

    def __getitem__(self, key: str) -> JsonWalker:
        walkers = self.json // int / 'flipbook_texture'
        for walker in walkers:
            if isinstance(walker.data, str) and walker.data == key:
                return walker.parent
        raise KeyError(key)

class RpTerrainTextureJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'textures/terrain_texture.json'

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        walker = self.json / 'texture_data'
        if isinstance(walker.data, dict):
            for key in walker.data.keys():
                if isinstance(key, str):
                    result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        result = self.json / 'texture_data' / key
        if isinstance(result.data, Exception):
            raise KeyError(key)
        return result

class RpBlocksJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'blocks.json'

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        if isinstance(self.json.data, dict):
            for key in self.json.data.keys():
                if isinstance(key, str):
                    result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        result = self.json / key
        if isinstance(result.data, Exception):
            raise KeyError(key)
        return result

class RpMusicDefinitionsJson(_UniqueMcFileJsonMulti[ResourcePack]):
    pack_path: ClassVar[str] = 'sounds/music_definitions.json'

    @property
    def identifiers(self) -> Tuple[str, ...]:
        result: List[str] = []
        if isinstance(self.json.data, dict):
            for key in self.json.data.keys():
                if isinstance(key, str):
                    result.append(key)
        return tuple(result)

    def __getitem__(self, key: str) -> JsonWalker:
        result = self.json / key
        if isinstance(result.data, Exception):
            raise KeyError(key)
        return result


# SOUNDS.JSON
def get_float_tuple_range(
        data: Union[JsonWalker, float, List[float]], default: Tuple[float, float]
) -> Optional[Tuple[float, float]]:
    '''
    Takes a value which can be a single number or a range (list with two numbers)
    and returns a tuple with two numbers to represent the range.
    '''
    if isinstance(data, JsonWalker):
        data = data.data
    if isinstance(data, list):
        data = data
        if (
                len(data) == 2 and isinstance(data[0], (float, int)) and
                isinstance(data[1], (float, int))):
            return (data[0], data[1])
    elif isinstance(data, (float, int)):
        return (data, data)
    return None


class RpSoundsJson(_UniqueMcFileJson[ResourcePack]):
    pack_path: ClassVar[str] = 'sounds.json'

    def __init__(
            self, *,
            path: Optional[Path]=None,
            pack: Optional[ResourcePack]=None) -> None:
        super().__init__(path=path, pack=pack)
        self.block_sounds = SjBlockSounds(self)
        self.entity_sounds = SjEntitySounds(self)
        self.individual_event_sounds = SjIndividualEventSounds(self)
        self.interactive_block_sounds = SjInteractiveBlockSounds(self)
        self.interactive_entity_sounds = SjInteractiveEntitySounds(self)

# Various parts of the sounds.json file
class _RpSoundsJsonPart(ABC):
    '''
    A part of sounds.json file. The sounds.json file is a special case
    because it holds 5 different types of the objects.
    '''
    def __init__(self, sounds_json: RpSoundsJson):
        self.sounds_json = sounds_json

class _PermanentJsonWalkerContainer:
    '''
    Holds reference to JsonWalker which can't be changed.
    '''
    def __init__(self, json: JsonWalker) -> None:
        self._json: JsonWalker = json

    @property
    def json(self):
        return self._json

# Sounds.JSON -> Block Sounds
class SjBlockSounds(_RpSoundsJsonPart):
    @property
    def json(self):
        return self.sounds_json.json / "block_sounds"

    def keys(self) -> Tuple[str]:
        if isinstance(self.json.data, dict):
            return tuple(self.json.data.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjBlockSoundsBlock:
        if key not in self.keys():
            raise KeyError()
        return SjBlockSoundsBlock(self.json / key, self)

class SjBlockSoundsBlock(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, block_sounds: SjBlockSounds) -> None:
        super().__init__(json)
        self._block_sounds: SjBlockSounds = block_sounds

    def keys(self) -> Tuple[str]:
        events = self.json / 'events'
        if isinstance(events.data, dict):
            return tuple([k for k in events.data.keys() if k != 'default'])
        return tuple()

    def __getitem__(self, key: str) -> SjBlockSoundsBlockEvent:
        if not key in self.keys():
            raise KeyError()
        return SjBlockSoundsBlockEvent(self.json / 'events' / key, self)

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    @property
    def block_sounds(self) -> SjBlockSounds:
        return self._block_sounds

    @property
    def sound(self):
        result = self.json / 'events' / 'default'
        if isinstance(result.data, str):
            return result.data
        return ''

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / "pitch")
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / "volume")
        if volume is None:
            return (1, 1)
        return volume

class SjBlockSoundsBlockEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, block_sounds_block: SjBlockSoundsBlock) -> None:
        super().__init__(json)
        self._block_sounds_block: SjBlockSoundsBlock = block_sounds_block

    @property
    def block_sounds_block(self):
        return self._block_sounds_block

    @property
    def sound(self):
        sound = (self.json / "sound").data
        if not isinstance(sound, str):
            return self.block_sounds_block.sound
        return sound

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / "pitch")
        if pitch is None:
            return self.block_sounds_block.pitch
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / "volume")
        if volume is None:
            return self.block_sounds_block.volume
        return volume

# Sounds.JSON -> Entity Sounds
class SjEntitySounds(_RpSoundsJsonPart):
    @property
    def json(self):
        return self.sounds_json.json / "entity_sounds"

    @property
    def defaults(self):
        return SjEntitySoundsDefaults(self.json / "defaults", self)

    def keys(self) -> Tuple[str]:
        entities = self.json / 'entities'
        if isinstance(entities.data, dict):
            return tuple(entities.data.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjEntitySoundsEntity:
        if key in self.keys():
            return SjEntitySoundsEntity(self.json / 'entities' / key, self)
        raise KeyError()

class SjEntitySoundsDefaults(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds: SjEntitySounds) -> None:
        super().__init__(json)
        self._entity_sounds = entity_sounds

    @property
    def entity_sounds(self) -> SjEntitySounds:
        return self._entity_sounds

    def keys(self) -> Tuple[str]:
        events = self.json / 'events'
        if isinstance(events.data, dict):
            return tuple(events.data.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjEntitySoundsDefaultsEvent:
        if key in self.keys():
            return SjEntitySoundsDefaultsEvent(self.json / 'events' / key, self)
        raise KeyError()

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / "pitch")
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / "volume")
        if volume is None:
            return (1, 1)
        return volume

class SjEntitySoundsDefaultsEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds_defaults: SjEntitySoundsDefaults) -> None:
        super().__init__(json)
        self._entity_sounds_defaults = entity_sounds_defaults

    @property
    def entity_sounds_defaults(self) -> SjEntitySoundsDefaults:
        return self._entity_sounds_defaults

    @property
    def pitch(self):
        if isinstance(self.json.data, str):
            return self.entity_sounds_defaults.pitch
        elif isinstance(self.json.data, dict):
            pitch = get_float_tuple_range(self.json / 'pitch')
            if pitch is None:
                return self.entity_sounds_defaults.pitch
            return pitch

    @property
    def volume(self):
        if isinstance(self.json.data, str):
            return self.entity_sounds_defaults.volume
        elif isinstance(self.json.data, dict):
            volume = get_float_tuple_range(self.json / 'volume')
            if volume is None:
                return self.entity_sounds_defaults.volume
            return volume

    @property
    def sound(self):
        if isinstance(self.json.data, str):
            return self.json.data
        elif isinstance(self.json.data, dict):
            sound = (self.json / 'sound').data
            if isinstance(sound, str):
                return sound
            return ""

class SjEntitySoundsEntity(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds: SjEntitySounds) -> None:
        super().__init__(json)
        self._entity_sounds = entity_sounds

    @property
    def entity_sounds(self) -> SjEntitySounds:
        return self._entity_sounds

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / "pitch")
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / "volume")
        if volume is None:
            return (1, 1)
        return volume

    def keys(self) -> Tuple[str]:
        events = (self.json / 'events').data
        if isinstance(events, dict):
            return tuple(events.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjEntitySoundsEntityEvent:
        if key not in self.keys():
            raise KeyError()
        return SjEntitySoundsEntityEvent(self.json / 'events' / key, self)

class SjEntitySoundsEntityEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds_entity: SjEntitySoundsEntity) -> None:
        super().__init__(json)
        self._entity_sounds_entity = entity_sounds_entity

    @property
    def entity_sounds_entity(self) -> SjEntitySoundsEntity:
        return self._entity_sounds_entity

    @property
    def pitch(self):
        if isinstance(self.json.data, str):
            return self.entity_sounds_entity.pitch
        elif isinstance(self.json.data, dict):
            pitch = get_float_tuple_range(self.json / 'pitch')
            if pitch is None:
                return self.entity_sounds_entity.pitch
            return pitch

    @property
    def volume(self):
        if isinstance(self.json.data, str):
            return self.entity_sounds_entity.volume
        elif isinstance(self.json.data, dict):
            volume = get_float_tuple_range(self.json / 'volume')
            if volume is None:
                return self.entity_sounds_entity.volume
            return volume

    @property
    def sound(self):
        if isinstance(self.json.data, str):
            return self.json.data
        elif isinstance(self.json.data, dict):
            sound = (self.json / 'sound').data
            if isinstance(sound, str):
                return sound
            return ""

# Sounds.JSON -> Individual Event Sounds
class SjIndividualEventSounds(_RpSoundsJsonPart):
    @property
    def json(self):
        return self.sounds_json.json / "individual_event_sounds"

    def keys(self) -> Tuple[str]:
        events = (self.json / 'events').data
        if isinstance(events, dict):
            return tuple(events.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjIndividualEventSoundsEvent:
        if key not in self.keys():
            raise KeyError()
        return SjIndividualEventSoundsEvent(self.json / 'events' / key, self)

class SjIndividualEventSoundsEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, individual_event_sounds_event: SjIndividualEventSoundsEvent) -> None:
        super().__init__(json)
        self._individual_event_sounds_event = individual_event_sounds_event
    
    @property
    def individual_event_sounds_event(self) -> SjIndividualEventSoundsEvent:
        return self._individual_event_sounds_event

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / 'pitch')
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / 'volume')
        if volume is None:
            return (1, 1)
        return volume

    @property
    def sound(self):
        sound = (self.json / 'sound').data
        if isinstance(sound, str):
            return sound
        return ""

# Sounds.JSON -> Interactive Block Sounds
class SjInteractiveBlockSounds(_RpSoundsJsonPart):
    @property
    def json(self):
        return self.sounds_json.json / "interactive_sounds" / "block_sounds"

    def keys(self) -> Tuple[str]:
        if isinstance(self.json.data, dict):
            return tuple(self.json.data.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjInteractiveBlockSoundsBlock:
        if key in self.keys():
            return SjInteractiveBlockSoundsBlock(self.json / key, self)
        raise KeyError()

class SjInteractiveBlockSoundsBlock(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, interactive_block_sounds: SjInteractiveBlockSounds) -> None:
        super().__init__(json)
        self._interactive_block_sounds = interactive_block_sounds

    @property
    def interactive_block_sounds(self) -> SjInteractiveBlockSounds:
        return self._interactive_block_sounds

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / 'pitch')
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / 'volume')
        if volume is None:
            return (1, 1)
        return volume

    @property
    def sound(self):
        sound = (self.json / 'events' / 'default').data
        if isinstance(sound, str):
            return sound
        return ""


    def keys(self) -> Tuple[str]:
        events = self.json / 'events'
        if isinstance(events.data, dict):
            return tuple([k for k in events.data.keys() if k != 'default'])
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjInteractiveBlockSoundsBlockEvent:
        if not key in self.keys():
            raise KeyError()
        return SjInteractiveBlockSoundsBlockEvent(self.json / 'events' / key, self)


class SjInteractiveBlockSoundsBlockEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, interactive_block_sounds_block: SjInteractiveBlockSoundsBlock) -> None:
        super().__init__(json)
        self._interactive_block_sounds_block = interactive_block_sounds_block

    @property
    def interactive_block_sounds_block(self) -> SjInteractiveBlockSoundsBlock:
        return self._interactive_block_sounds_block

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / 'pitch')
        if pitch is None:
            return self.interactive_block_sounds_block.pitch
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / 'volume')
        if volume is None:
            return self.interactive_block_sounds_block.volume
        return volume

    @property
    def sound(self):
        sound = (self.json / 'events' / 'default').data
        if isinstance(sound, str):
            return sound
        return ""

# Sounds.JSON -> Interactive Entity Sounds
class SjInteractiveEntitySounds(_RpSoundsJsonPart):
    @property
    def json(self):
        return self.sounds_json.json / "interactive_sounds" / "entity_sounds"

    @property
    def defaults(self) -> SjInteractiveEntitySoundsDefaults:
        return SjInteractiveEntitySoundsDefaults(self.json / "defaults", self)
    
    def keys(self) -> Tuple[str]:
        entities = self.json / 'entities'
        if isinstance(entities.data, dict):
            return tuple(entities.data.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjInteractiveEntitySoundsEntity:
        if key in self.keys():
            return SjInteractiveEntitySoundsEntity(self.json / 'entities' / key, self)
        raise KeyError()

class SjInteractiveEntitySoundsDefaults(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds: SjInteractiveEntitySounds) -> None:
        super().__init__(json)
        self._entity_sounds = entity_sounds

    def entity_sounds(self) -> SjInteractiveEntitySounds:
        return self._entity_sounds

    def keys(self) -> Tuple[str]:
        events = self.json / 'events'
        if isinstance(events.data, dict):
            return tuple(events.data.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjInteractiveEntitySoundsDefaultsEvent:
        if key in self.keys():
            return SjInteractiveEntitySoundsDefaultsEvent(self.json / 'events' / key, self)
        raise KeyError()

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / "pitch")
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / "volume")
        if volume is None:
            return (1, 1)
        return volume

class SjInteractiveEntitySoundsDefaultsEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds_defaults: SjInteractiveEntitySoundsDefaults) -> None:
        super().__init__(json)
        self._entity_sounds_defaults = entity_sounds_defaults

    @property
    def entity_sounds_defaults(self) -> SjInteractiveEntitySoundsDefaults:
        return self._entity_sounds_defaults

    @property
    def pitch(self):
        if isinstance(self.json.data, str):
            return self.entity_sounds_defaults.pitch
        elif isinstance(self.json.data, dict):
            pitch = get_float_tuple_range(self.json / 'default' / 'pitch')
            if pitch is None:
                return self.entity_sounds_defaults.pitch
            return pitch

    @property
    def volume(self):
        if isinstance(self.json.data, str):
            return self.entity_sounds_defaults.volume
        elif isinstance(self.json.data, dict):
            volume = get_float_tuple_range(self.json / 'default' / 'volume')
            if volume is None:
                return self.entity_sounds_defaults.volume
            return volume

    @property
    def sound(self):
        if isinstance(self.json.data, str):
            return self.json.data
        elif isinstance(self.json.data, dict):
            sound = (self.json / 'default' / 'sound').data
            if isinstance(sound, str):
                return sound
            return ""

class SjInteractiveEntitySoundsEntity(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds: SjInteractiveEntitySounds) -> None:
        super().__init__(json)
        self._entity_sounds = entity_sounds

    def entity_sounds(self) -> SjInteractiveEntitySounds:
        return self._entity_sounds

    @property
    def pitch(self):
        pitch = get_float_tuple_range(self.json / "pitch")
        if pitch is None:
            return (1, 1)
        return pitch

    @property
    def volume(self):
        volume = get_float_tuple_range(self.json / "volume")
        if volume is None:
            return (1, 1)
        return volume

    def keys(self) -> Tuple[str]:
        events = (self.json / 'events').data
        if isinstance(events, dict):
            return tuple(events.keys())
        return tuple()

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjInteractiveEntitySoundsEntityEvent:
        if key not in self.keys():
            raise KeyError()
        return SjInteractiveEntitySoundsEntityEvent(self.json / 'events' / key, self)

class SjInteractiveEntitySoundsEntityEvent(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds_entity: SjInteractiveEntitySoundsEntity) -> None:
        super().__init__(json)
        self._entity_sounds_entity = entity_sounds_entity

    @property
    def entity_sounds_entity(self) -> SjInteractiveEntitySoundsEntity:
        return self._entity_sounds_entity

    @property
    def sound(self):
        if isinstance(self.json.data, dict):
            sound = (self.json / 'default').data
            if isinstance(sound, str):
                return sound
        return ""

    def keys(self) -> Tuple[str]:
        if isinstance(self.json.data, dict):
            return tuple([i for i in self.json.data.keys() if i != 'default'])
        return ""

    def __iter__(self):
        for k in self.keys():
            yield self[k]

    def __getitem__(self, key: str) -> SjInteractiveEntitySoundsEntityEventBlock:
        if key not in self.keys():
            raise KeyError()
        return SjInteractiveEntitySoundsEntityEventBlock(self.json / key, self)

class SjInteractiveEntitySoundsEntityEventBlock(_PermanentJsonWalkerContainer):
    def __init__(self, json: JsonWalker, entity_sounds_entity_event: SjInteractiveEntitySoundsEntityEvent) -> None:
        super().__init__(json)
        self._entity_sounds_entity_event = entity_sounds_entity_event

    @property
    def entity_sounds_entity_event(self) -> SjInteractiveEntitySoundsEntityEvent:
        return self._entity_sounds_entity_event

    @property
    def sound(self):
        if isinstance(self.json.data, str):
            return self.json.data
        return ""
