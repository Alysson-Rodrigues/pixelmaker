"""Pixel art generation routines (pure processing code).

This module is intentionally GUI-free so it can be unit-tested.
"""

# Keep a simple stub for now; we'll implement a full algorithm next if you want.

def generate_pixel_art(original_image, segmentation_maps, palettes, block_size):
    """Stubbed generator.

    Args:
        original_image: PIL.Image (RGBA)
        segmentation_maps: dict[str, PIL.Image]  # reduced-size maps
        palettes: dict[str, list[str]]  # subject -> ["#RRGGBB", ...]
        block_size: int

    Returns:
        PIL.Image or None
    """
    # TODO: implement the algorithm described earlier (average block color -> nearest palette color)
    return None
