import re

# Third Party
# noinspection PyProtectedMember
from photoshop.api._artlayer import ArtLayer
# noinspection PyProtectedMember
from photoshop.api._layerSet import LayerSet

# Local
import src.helpers as psd
from src.utils.adobe import LayerContainerTypes
# Plugin imports
import cardinfo

# region Layer Visibility Functions

def set_layer_visibility(
    visible: bool,
    layer: ArtLayer | LayerSet | str,
    group: LayerContainerTypes | None = None,
):
    if layer is None: return

    if isinstance(layer, (ArtLayer, LayerSet)):
        layer.visible = visible
        return

    target: ArtLayer | LayerSet = psd.getLayerSet(layer, group)
    if target is None: # If a group is not found, look for a layer instead
        target = psd.getLayer(layer, group)

    # If neither are found, print an error and give up
    if target is None:
        print(f"Error: layer/group {layer} was not found in {group}")
        return

    target.visible = visible

def enable(
    layer: ArtLayer | LayerSet | str,
    group: LayerContainerTypes | None = None,
):
    set_layer_visibility(True, layer, group)

def disable(
    layer: ArtLayer | LayerSet | str,
    group: LayerContainerTypes | None = None,
):
    set_layer_visibility(False, layer, group)

# endregion

# region    Text Processing functions

def replace_hyphens_regex(text: str) -> str:
    """
    Replace hyphens with em-dashes in patterns like "-1:" or "-12:"
    Used for planeswalker rules text
    """
    pattern = r'-(\d{1,2}:)'
    return re.sub(pattern, '–\\1', text)

def indefinite_article_for_number(number: str) -> str:
    if number.startswith(('8', '11', '18')) or number == '18':
        return "an"
    else:
        return "a"

def is_keyword_section(input_string: str) -> bool:
    for keyword in cardinfo.KEYWORDS:
        if input_string.startswith(keyword):
            return True
    return False

def lowercase_first_char(input_string: str) -> str:
    if not input_string:
        return ""
    return input_string[0].lower() + input_string[1:]

def add_and_to_list(text: str) -> str:
    """Adds and to lists, respecting Oxford comma"""
    comma_count = text.count(',')

    if comma_count == 0:
        return text
    elif comma_count == 1:
        return re.sub(r',\s*([^,]*)$', r' and \1', text)
    else:
        return re.sub(r',\s*([^,]*)$', r', and \1', text)


def list_to_text(items: list[str]) -> str:
    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(items[:-1]) + ", and " + items[-1]

def format_leveler_abilities(abilities) -> str | None:
    if abilities == "" or abilities is None:
        return None

    if "\n" in abilities:
        keywords, ability = abilities.split("\n")
        abilities = f"{lowercase_first_char(keywords)}, and \"{ability}\""
    else:
        if is_keyword_section(abilities):
            abilities = f"{add_and_to_list(lowercase_first_char(abilities))}."
        else:
            abilities = f"\"{abilities}\""

    return abilities

def get_bigger_textbox_size(size1, size2) -> str:
    sizes = ["Small", "Medium", "Normal"]
    size_ranks = {size: i for i, size in enumerate(sizes)}
    return sizes[max(size_ranks.get(size1), size_ranks.get(size2))]

def get_smaller_textbox_size(size1, size2) -> str:
    sizes = ["Small", "Medium", "Normal"]
    size_ranks = {size: i for i, size in enumerate(sizes)}
    return sizes[min(size_ranks.get(size1), size_ranks.get(size2))]

def sort_frame_textures(inputs: list[str]) -> list[str]:
    return sort_elements_by_position(inputs, cardinfo.ordered_frame_textures)

def sort_textbox_textures(inputs: list[str]) -> list[str]:
    return sort_elements_by_position(inputs, cardinfo.ordered_textbox_textures)

def sort_elements_by_position(inputs: list[str], positions: list[str]) -> list[str]:
    position_map = {item: i for i, item in enumerate(positions)}
    return sorted(inputs, key=lambda item: position_map.get(item, float('inf')))

# endregion