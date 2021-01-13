'''
Python module for working with Minecraft bedrock edition projects.
'''

# Package version
VERSION = (0, 1)
__version__ = '.'.join([str(x) for x in VERSION])

from ._content import (
    # Project and packs
    Project, BehaviorPack, ResourcePack,

    # Files
    BpAnimation, BpAnimationController, BpBlock, BpEntity, BpFunction, BpItem,
    BpLootTable, BpRecipe, BpSpawnRule, BpTrade,
    
    RpAnimation, RpAnimationController, RpEntity, RpItem, RpModel, RpParticle,
    RpRenderController, RpSoundFile, RpTextureFile,

    # File collections
    BpAnimationControllers, BpAnimations, BpBlocks, BpEntities, BpFunctions,
    BpItems, BpLootTables, BpRecipes, BpSpawnRules, BpTrades,

    RpAnimationControllers, RpAnimations, RpEntities, RpItems, RpModels,
    RpParticles, RpRenderControllers, RpSoundFiles, RpTextureFiles,

    # Unique files
    RpBiomesClientJson, RpBlocksJson, RpFlipbookTexturesJson,
    RpItemTextureJson, RpMusicDefinitionsJson, RpSoundDefinitionsJson,
    RpSoundsJson, RpTerrainTextureJson,

    # sounds.json parts
    BlockSoundEvent, EntitySoundEvent, IndividualSoundEvent,
    InteractiveBlockSoundEvent, InteractiveEntitySoundEvent,
)

