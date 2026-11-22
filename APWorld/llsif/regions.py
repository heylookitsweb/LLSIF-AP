from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import LLSIFWorld

def create_and_connect_regions(world: LLSIFWorld) -> None:
    menu: Region = Region("Menu", world.player, world.multiworld)
    world.multiworld.regions.append(menu)