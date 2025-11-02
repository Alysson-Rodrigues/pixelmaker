"""Pixel art generation routines (pure processing code).

Este módulo implementa o algoritmo de processamento principal.
Depende de: PIL, numpy, colormath
"""

import numpy as np
from PIL import Image
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# Compatibility shim: older colormath versions expect numpy.asscalar which
# was removed in recent NumPy. Provide a small fallback.
if not hasattr(np, 'asscalar'):
    def _asscalar(x):
        try:
            return x.item()
        except Exception:
            return x
    np.asscalar = _asscalar


def hex_to_rgb(hex_str):
    """Converte uma string hex #RRGGBB para uma tupla (R, G, B)."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_lab(rgb_tuple):
    """Converte uma tupla (R, G, B) (0-255) ou floats para um objeto LabColor."""
    r, g, b = rgb_tuple
    try:
        rn = float(r) / 255.0
        gn = float(g) / 255.0
        bn = float(b) / 255.0
    except Exception:
        rn, gn, bn = r, g, b
    srgb = sRGBColor(rn, gn, bn)
    return convert_color(srgb, LabColor)


def get_color_diff(lab1, lab2):
    """Calcula a diferença perceptual (Delta E 2000) entre duas cores Lab."""
    return delta_e_cie2000(lab1, lab2)


def generate_pixel_art(original_image, segmentation_maps, palettes, block_size):
    """Gera a imagem de pixel art com base nos dados fornecidos.

    Args:
        original_image: PIL.Image (RGBA) - A imagem original.
        segmentation_maps: dict[str, PIL.Image] - Dicionário de {assunto: PIL.Image (mapa)}.
        palettes: dict[str, list[str]] - Dicionário de {assunto -> ["#RRGGBB", ...]}.
        block_size: int - O tamanho do "super pixel" (ex: 10).

    Returns:
        PIL.Image: A imagem de pixel art gerada.
    """
    print(f"Iniciando geração: block_size={block_size}")
    lab_palettes = {}
    for subject, hex_colors in palettes.items():
        if not hex_colors:
            continue
        try:
            lab_palettes[subject] = [rgb_to_lab(hex_to_rgb(h)) for h in hex_colors]
        except Exception as e:
            print(f"Aviso: Falha ao processar paleta para '{subject}': {e}")

    if not lab_palettes:
        raise ValueError("Nenhuma paleta válida foi processada. Abortando.")

    combined_lab_list = []
    combined_hex_list = []
    for subject, hex_colors in palettes.items():
        if not hex_colors:
            continue
        for h in hex_colors:
            try:
                combined_lab_list.append(rgb_to_lab(hex_to_rgb(h)))
                combined_hex_list.append(h)
            except Exception:
                # ignora entradas inválidas
                pass

    if not combined_lab_list:
        raise ValueError("Nenhuma cor disponível nas paletas para fallback.")

    original_array = np.array(original_image.convert('RGBA'))
    orig_h, orig_w, _ = original_array.shape

    seg_arrays = {}
    for subject, img in segmentation_maps.items():
        map_w, map_h = img.size
        if map_w != (orig_w // block_size) or map_h != (orig_h // block_size):
            raise ValueError(f"Mapa '{subject}' tem dimensões erradas ({map_w}x{map_h}). Esperado ({orig_w // block_size}x{orig_h // block_size})")
        seg_arrays[subject] = np.array(img.convert('RGBA'))[:, :, 3]

    out_w = orig_w // block_size
    out_h = orig_h // block_size
    output_image = Image.new('RGBA', (out_w, out_h))
    output_pixels = output_image.load()

    print(f"Dimensões de saída: {out_w} x {out_h}")

    for y in range(out_h):
        for x in range(out_w):
            current_subject = None
            for subject, alpha_arr in seg_arrays.items():
                if alpha_arr[y, x] > 128:
                    current_subject = subject
                    break

            use_combined = False
            if current_subject is None or current_subject not in lab_palettes:
                use_combined = True

            y_start, x_start = y * block_size, x * block_size
            y_end, x_end = y_start + block_size, x_start + block_size
            block_array = original_array[y_start:y_end, x_start:x_end]

            try:
                block_image = Image.fromarray(block_array, 'RGBA').convert('RGB')
            except Exception as e:
                print(f"Aviso: Falha ao criar imagem do bloco (x={x}, y={y}): {e}")
                output_pixels[x, y] = (0, 0, 0, 0)
                continue

            quantized_block = block_image.quantize(colors=1)
            palette = quantized_block.getpalette()
            if not palette:
                output_pixels[x, y] = (0, 0, 0, 0)
                continue

            dominant_rgb_tuple = tuple(palette[0:3])
            target_lab_color = rgb_to_lab(dominant_rgb_tuple)

            if use_combined:
                target_palette_lab = combined_lab_list
                original_palette_hex = combined_hex_list
            else:
                target_palette_lab = lab_palettes[current_subject]
                original_palette_hex = palettes[current_subject]

            min_diff = float('inf')
            best_color_hex = "#000000"
            for i, pal_lab in enumerate(target_palette_lab):
                diff = get_color_diff(target_lab_color, pal_lab)
                if diff < min_diff:
                    min_diff = diff
                    best_color_hex = original_palette_hex[i]

            best_rgb_tuple = hex_to_rgb(best_color_hex)
            output_pixels[x, y] = (int(best_rgb_tuple[0]), int(best_rgb_tuple[1]), int(best_rgb_tuple[2]), 255)

        if out_h > 0 and y % max(1, (out_h // 10)) == 0:
            print(f"Progresso: {int((y / out_h) * 100)}%")

    print("Geração concluída.")
    return output_image
