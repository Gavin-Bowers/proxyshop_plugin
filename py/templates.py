"""
* Plugin: [Gavin]
"""
# Standard Library
from typing import Optional, Union
from functools import cached_property

# Third Party
from PIL import Image
from photoshop.api import AnchorPosition
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local
import src.helpers as psd
import src.text_layers as text_classes
from src import CFG

from src.enums.layers import LAYERS
from src.utils.adobe import ReferenceLayer, LayerContainerTypes
from src.helpers import get_line_count, set_text_size
from src.templates import ClassicTemplate, ClassMod
from src.templates.saga import SagaMod
from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextArea,
    FormattedTextField,
    ScaledWidthTextField
)

# TODO
# Nyx, colored artifacts
# Legend Crown
# Battles
# Split Cards, rooms, aftermath and meld
# Flip Cards
# Replace en dashes in planeswalker loyalty abilities with em dashes (−)

# Make Retro inherit from core or normal instead of classic?

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

class RetroTemplate(ClassicTemplate):
    """Retro frames from MM3, MH3, and RVR."""
    frame_suffix = 'Retro'


    ##################################################
    # Settings
    ##################################################

    # General

    @property
    def cfg_tombstone_setting(self):
        return CFG.get_setting(
            section="GENERAL",
            key="tombstone",
            is_bool=False
        )

    @property
    def cfg_textbox_size(self):
        return CFG.get_setting(
            section="GENERAL",
            key="textbox_size",
            is_bool=False
        )

    @property
    def cfg_irregular_textboxes(self):
        return CFG.get_setting(
            section="GENERAL",
            key="use_irregular_textboxes",
        )

    @property
    def cfg_colorless_transparent(self):
        return CFG.get_setting(
            section="GENERAL",
            key="colorless_transparent",
        )

    @property
    def cfg_colored_bevels_on_devoid(self):
        return CFG.get_setting(
            section="GENERAL",
            key="use_colored_bevels_on_devoid",
        )

    @property
    def cfg_all_transparent(self):
        return CFG.get_setting(
            section="GENERAL",
            key="all_transparent",
        )

    @property
    def cfg_transparent_opacity(self):
        return float(CFG.get_setting(
            section="GENERAL",
            key="transparent_opacity",
            is_bool=False
        ))

    @property
    def cfg_floating_frame(self):
        return CFG.get_setting(
            section="GENERAL",
            key="use_floating_frame",
        )

    @property
    def cfg_split_hybrid(self):
        return CFG.get_setting(
            section="GENERAL",
            key="split_hybrid",
        )

    @property
    def cfg_split_all(self):
        return CFG.get_setting(
            section="GENERAL",
            key="split_all",
        )

    @property
    def cfg_dual_textbox_bevels(self):
        return not CFG.get_setting(
            section="GENERAL",
            key="standardize_dual_fade_bevels",
        )

    @property
    def cfg_disable_textbox_bevels(self):
        return CFG.get_setting(
            section="GENERAL",
            key="disable_textbox_bevels",
        )

    # Pinlines

    @property
    def cfg_pinlines_on_multicolored(self):
        return CFG.get_setting(
            section="PINLINES",
            key="multicolored",
        )

    @property
    def cfg_pinlines_on_artifacts(self):
        return CFG.get_setting(
            section="PINLINES",
            key="artifacts",
        )

    @property
    def cfg_pinlines_on_all_cards(self):
        return CFG.get_setting(
            section="PINLINES",
            key="all",
        )

    @property
    def cfg_color_all_pinlines(self):
        return CFG.get_setting(
            section="PINLINES",
            key="color_all",
        )

    @property
    def cfg_max_pinline_colors(self):
        return int(CFG.get_setting(
            section="PINLINES",
            key="max_colors",
            is_bool=False
        ))

    # Lands

    @property
    def cfg_legends_style_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="legends_style_lands",
        )

    @property
    def cfg_gold_textbox_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="gold_textbox_lands",
        )

    @property
    def cfg_gold_textbox_pinline_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="gold_textbox_pinline_lands",
        )

    @property
    def cfg_textbox_bevels_on_gold_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="textbox_bevels_on_gold_lands",
        )

    # Planeswalker

    @property
    def cfg_verbose_planeswalkers(self):
        return CFG.get_setting(
            section="PLANESWALKER",
            key="verbose",
        )

    # Double Faced

    @property
    def cfg_has_notch(self):
        return CFG.get_setting(
            section="DOUBLEFACED",
            key="notch",
            is_bool=True,
            default=False,
        )

    ##################################################
    # Layers and Groups
    ##################################################

    @cached_property
    def card_frame_group(self) -> LayerSet:
        return psd.getLayerSet("Card Frame")

    @cached_property
    def art_frames_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Frames")

    @cached_property
    def pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Pinlines")

    @cached_property
    def art_pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Art", self.pinlines_layer)

    @cached_property
    def art_pinlines_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Masks", self.pinlines_layer)

    @cached_property
    def art_pinlines_background_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Background", self.pinlines_layer)

    @cached_property
    def textbox_pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox", self.pinlines_layer)

    @cached_property
    def textbox_pinlines_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox Masks", self.pinlines_layer)

    @cached_property
    def textbox_pinlines_background_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox Background", self.pinlines_layer)

    @cached_property
    def outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Outlines")

    @cached_property
    def art_outlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Outlines", self.outlines_group)

    @cached_property
    def textbox_outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Outlines", self.outlines_group)

    @cached_property
    def textbox_bevels_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Bevels", self.card_frame_group)

    @cached_property
    def textbox_bevels_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.textbox_bevels_group)

    @cached_property
    def textbox_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox", self.card_frame_group)

    @cached_property
    def textbox_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.textbox_layer)

    @cached_property
    def textbox_effects_layer(self) -> LayerSet:
        return psd.getLayerSet("Effects", self.textbox_layer)

    @cached_property
    def bevels_layer(self) -> LayerSet:
        return psd.getLayerSet("Bevels", self.card_frame_group)

    @cached_property
    def bevels_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.bevels_layer)

    @cached_property
    def bevels_light_layer(self) -> LayerSet:
        return psd.getLayerSet("Light", self.bevels_layer)

    @cached_property
    def bevels_dark_layer(self) -> LayerSet:
        return psd.getLayerSet("Dark", self.bevels_layer)

    @cached_property
    def frame_texture_layer(self) -> LayerSet:
        return psd.getLayerSet("Frame Texture", self.card_frame_group)

    @cached_property
    def frame_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.frame_texture_layer)

    @cached_property
    def transform_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.TRANSFORM, self.text_group)

    @cached_property
    def mdfc_group(self) -> LayerSet:
        return psd.getLayerSet("MDFC", self.text_group)

    ##################################################
    # Added layout logic
    ##################################################

    @cached_property
    def flavor_name(self) -> Optional[str]:
        """Display name for nicknamed cards"""
        return self.layout.card.get('flavor_name')

    @cached_property
    def is_tombstone_scryfall(self) -> bool:
        return bool('tombstone' in self.layout.frame_effects)

# Equivilent scryfall search:
# o:"this card is in your graveyard" or o:"return this card from your graveyard" or o:"cast this card from your graveyard'" or o:"put this card from your graveyard" or o:"exile this card from your graveyard" or o:"~ is in your graveyard" or o:"return ~ from your graveyard" or o:"cast ~ from your graveyard'" or o:"put ~ from your graveyard" or o:"exile ~ from your graveyard" or keyword:disturb or keyword:flashback or keyword:Dredge or keyword:Scavenge or keyword:Embalm or keyword:Eternalize or keyword:Aftermath or keyword:Encore or keyword:Escape or keyword:Jump-start or keyword:Recover or keyword:Retrace or keyword:Unearth
# (Excluding named cards)

    @cached_property
    def is_tombstone_auto(self) -> bool:
        keyword_list = [
            'Flashback',
            'Dredge',
            'Scavenge',
            'Embalm',
            'Eternalize',
            'Aftermath',
            'Disturb',
            'Encore',
            'Escape',
            'Jump-start',
            'Recover',
            'Retrace',
            'Unearth',
        ]
        for keyword in keyword_list:
            if keyword in self.layout.keywords: return True

        cardname = self.layout.name_raw.lower()
        oracle_text = self.layout.oracle_text.lower()

        key_phrase_list = [
            f'{cardname} is in your graveyard',
            f'return {cardname} from your graveyard',
            f'cast {cardname} from your graveyard',
            f'put {cardname} from your graveyard',
            f'exile {cardname} from your graveyard',
        ]
        for phrase in key_phrase_list:
            if phrase in oracle_text: return True

        key_phrase_list_generic = [
            f'this card is in your graveyard',
            f'return this card from your graveyard',
            f'cast this card from your graveyard',
            f'put this card from your graveyard',
            f'exile this card from your graveyard',
        ]
        for phrase in key_phrase_list_generic:
            if phrase in oracle_text: return True

        name_list = [
            "Say Its Name",
            "Skyblade's Boon",
            "Nether Spirit",
        ]
        for name in name_list:
            if name == self.layout.name_raw: return True
        return False

    @cached_property
    def has_tombstone(self) -> bool:
        setting = self.cfg_tombstone_setting
        match setting:
            case "Automatic":
                return self.is_tombstone_auto
            case "Scryfall":
                return self.is_tombstone_scryfall
        return False

    ##################################################
    # Layer logic
    ##################################################

    @cached_property
    def frame_texture(self) -> ArtLayer:
        if self.is_land and self.cfg_legends_style_lands:
            return psd.getLayer("Legends Land", self.frame_texture_layer)
        return psd.getLayer(self.identity_advanced, self.frame_texture_layer)

    @cached_property
    def frame_mask(self) -> ArtLayer:
        return psd.getLayer(self.textbox_size, self.frame_masks_layer)

    @cached_property
    def textbox_texture(self) -> ArtLayer:
        if self.is_land:
            if self.cfg_legends_style_lands:
                return psd.getLayer("Legends", self.textbox_layer)
            if self.is_gold_land:
                return psd.getLayer("Land", self.textbox_layer)
            return psd.getLayer(self.identity + "L", self.textbox_layer)
        return psd.getLayer(self.identity_advanced, self.textbox_layer)

    @cached_property
    def textbox_mask(self) -> Optional[ArtLayer]:
        if self.textbox_size == "Textless": return None
        textbox_name = self.textbox_size
        if self.has_irregular_textbox:
            textbox_name = f"{self.identity_advanced} {self.textbox_size}"
        # if self.is_transform and self.is_front:
        #     textbox_name = textbox_name + " TF Front"

        return psd.getLayer(textbox_name, self.textbox_masks_group)

    @cached_property
    def art_reference(self) -> ReferenceLayer:
        if self.cfg_floating_frame:
            return psd.get_reference_layer("Floating Frame", self.art_frames_layer)
        if self.is_transparent:
            return psd.get_reference_layer("Transparent Frame", self.art_frames_layer)
        return psd.get_reference_layer(self.textbox_size, self.art_frames_layer)

    @cached_property
    def textbox_reference(self) -> ReferenceLayer:
        if self.is_mdfc:
            return psd.get_reference_layer(f"Textbox Reference {self.textbox_size} TF", self.text_group)
        return psd.get_reference_layer(f"Textbox Reference {self.textbox_size}", self.text_group)

    @cached_property
    def expansion_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer("Expansion Reference", self.text_group)

    @cached_property
    def art_outlines(self) -> LayerSet:
        return psd.getLayerSet(self.textbox_size, self.art_outlines_layer)

    @cached_property
    def textbox_outlines(self) -> Optional[ArtLayer]:
        if self.has_irregular_textbox:
            return None
        if self.textbox_size == "Textless":
            return None
        # if self.is_transform and self.is_front:
        #     return psd.getLayer(self.textbox_size + " TF Front", self.textbox_outlines_layer)
        return psd.getLayer(self.textbox_size, self.textbox_outlines_group)

    ##################################################
    # Properties
    ##################################################

    @cached_property
    def has_nickname(self) -> bool:
        """Return True if this a nickname render."""
        if self.flavor_name is not None:
            return True
        return False

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        # if self.cfg_floating_frame:
        #     return True
        return False

    @cached_property
    def has_irregular_textbox(self) -> bool:
        if self.is_saga or self.is_class:
            return False
        if (self.is_transform or self.is_mdfc) and self.cfg_has_notch:
            return False
        if not self.cfg_irregular_textboxes:
            return False
        if self.identity_advanced == "G":
            return True
        if self.identity_advanced == "B":
            return True
        return False

    @cached_property
    def identity_advanced(self) -> str:
        if self.is_land:
            return "Land"
        if self.is_split_fade:
            return "Hybrid"
        if self.is_artifact:
            return "Artifact"
        if self.is_colorless:
            return "Colorless"
        if len(self.identity) > 1:
            return "Gold"
        return self.identity

    @cached_property
    def has_pinlines(self) -> bool:
        if self.is_land:
            return True
        if len(self.identity) > 1 and self.cfg_pinlines_on_multicolored:
            return True
        if self.is_artifact and self.cfg_pinlines_on_artifacts:
            return True
        if self.cfg_pinlines_on_all_cards:
            return True
        return False

    @cached_property
    def has_textbox(self) -> bool:
        if self.textbox_size == "Textless":
            return False
        return True

    @cached_property
    def has_textbox_bevels(self) -> bool:
        if not self.has_textbox:
            return False
        if self.cfg_disable_textbox_bevels:
            return False
        if self.has_irregular_textbox:
            return False
        if self.is_land and self.cfg_legends_style_lands:
            return False
        if self.is_gold_land:
            if self.cfg_textbox_bevels_on_gold_lands:
                return True
            return False
        return True

    @cached_property
    def is_gold_land(self) -> bool:
        """ Whether the textbox of the card is the gold land textbox"""
        if not self.is_land:
            return False
        if self.is_basic_land:
            return False
        if self.cfg_gold_textbox_lands:
            return True
        if len(self.identity) < 1 or len(self.identity) > 2:
            return True
        return False

    @cached_property
    def is_dual_land(self) -> bool:
        if not self.is_land:
            return False
        if self.is_gold_land:
            return False
        if self.cfg_legends_style_lands:
            return False
        if len(self.identity) == 2:
            return True
        return False

    @cached_property
    def is_split_fade(self) -> bool:
        if len(self.identity) != 2:
            return False
        if self.cfg_split_all:
            return True
        if self.is_hybrid and self.cfg_split_hybrid:
            return True
        return False

    @cached_property
    def is_transparent(self) -> bool:
        if self.is_colorless and self.cfg_colorless_transparent:
            return True
        if self.cfg_all_transparent:
            return True
        return False

    @cached_property
    def is_devoid(self) -> bool:
        # For some reason true colorless cards have "Colorless" as their color identity while
        # artifacts have an empty string.
        if self.identity == "Colorless":
            return False
        if self.is_colorless and (len(self.identity) > 0):
            return True
        return False

    @cached_property
    def is_saga(self) -> bool:
        return False

    @cached_property
    def is_class(self) -> bool:
        return False

    @cached_property
    def is_normal(self) -> bool:
        if self.is_saga:
            return False
        if self.is_class:
            return False
        return True

    @cached_property
    def art_aspect(self) -> float:
        art_file = self.layout.art_file
        with Image.open(art_file) as img:
            width, height = img.size
            return width / height

    @cached_property
    def textbox_size_from_art_aspect(self) -> str:
        if self.art_aspect > 1.25:
            return "Normal"
        if self.art_aspect > 1.06:
            return "Medium"
        if self.art_aspect > 0.96:
            return "Small"
        return "Small"

    @cached_property
    def textbox_size_from_text(self) -> str:
        """Returns an appropriate textbox size for the amount of text"""
        # Set up our test text layer
        test_layer = self.text_layer_rules
        test_text = self.layout.oracle_text
        if self.layout.flavor_text:
            test_text += f'\r{self.layout.flavor_text}'
        test_layer.textItem.contents = test_text.replace('\n', '\r')
        # Get the number of lines in our test text and decide what size
        num = get_line_count(test_layer)
        if num < 5:
            return "Small"
        if num < 7:
            return "Medium"
        return "Normal"

    @cached_property
    def auto_textbox_size(self) -> str:

        def rank_textbox_size(size: str) -> int:
            match size:
                case "Small":
                    return 0
                case "Medium":
                    return 1
                case "Normal":
                    return 2

        match max(
            rank_textbox_size(self.textbox_size_from_text),
            rank_textbox_size(self.textbox_size_from_art_aspect)
        ):
            case 0:
                return "Small"
            case 1:
                return "Medium"
            case 2:
                return "Normal"
        return "Normal"  # Failsafe

    @cached_property
    def textbox_size(self) -> str:
        if self.is_saga:
            return "Saga"
        if self.is_class:
            return "Class"
        if self.cfg_textbox_size == "Automatic":
            return self.auto_textbox_size
        return self.cfg_textbox_size

    ##################################################
    # Text Layers
    ##################################################

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        if not self.has_textbox:
            return None
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    @cached_property
    def text_layer_name(self) -> ArtLayer:
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_nickname(self) -> ArtLayer:
        return psd.getLayer("Nickname", self.text_group)

    @cached_property
    def text_layer_rules(self) -> ArtLayer:
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @cached_property
    def nickname_shape(self) -> ArtLayer:
        return psd.getLayer("Nickname Box", self.text_group)

    @cached_property
    def pt_length(self) -> int:
        return len(f'{self.layout.power}{self.layout.toughness}')

    ##################################################
    # Layer adding functions
    ##################################################

    def rules_text_and_pt_layers(self):
        if self.is_creature:
            self.text.append(
                TextField(
                    layer=self.text_layer_pt,
                    contents=f'{self.layout.power}/{self.layout.toughness}'))

        if "Planeswalker" in self.layout.type_line:
            self.text.append(
                TextField(
                    layer=self.text_layer_pt,
                    contents=f'{self.layout.loyalty}'))

        # Make P/T a little smaller if it's two double digits to prevent touching outer card bevel
        pt_size = 11.25
        if self.pt_length >= 4:
            pt_size = 10.0
        set_text_size(psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_group), pt_size)

        if self.is_flipside_creature and self.cfg_has_notch:
            self.text.append(
                TextField(
                    layer=psd.getLayer(LAYERS.POWER_TOUGHNESS, self.transform_group),
                    contents=f'{self.layout.other_face_power}/{self.layout.other_face_toughness}'))

        if self.textbox_size == "Textless":
            return
        if self.is_saga or self.is_class:
            return

        rules_text = self.layout.oracle_text

        if "Planeswalker" in self.layout.type_line and self.cfg_verbose_planeswalkers:
            pw_name = self.layout.type_line.split()[3]
            rules_text = f"Put {self.layout.loyalty} loyalty (use counters) on {pw_name}. Opponents can attack {pw_name} as though they were you. Any damage they suffer depletes that much loyalty. If {pw_name} has no loyalty, they abandon you.\n Once during each of your turns, you may add or spend loyalty as indicated for the desired effect—\n{self.layout.oracle_text}"

        self.text.append(
            FormattedTextArea(
                layer=self.text_layer_rules,
                contents=rules_text,
                flavor=self.layout.flavor_text,
                centered=self.is_centered,
                reference=self.textbox_reference,
                divider=self.divider_layer))

    def basic_text_layers(self) -> None:
        self.text.append(
            FormattedTextField(
                layer=self.text_layer_mana,
                contents=self.layout.mana_cost
            ))

        if self.has_textbox:
            self.text.append(
                ScaledTextField(
                    layer=self.text_layer_type,
                    contents=self.layout.type_line,
                    reference=self.type_reference
                ))
            if self.is_mdfc:
                # Add mdfc text layers
                self.text.extend([
                    FormattedTextField(
                        layer=psd.getLayer("Right", self.mdfc_group),
                        contents=self.layout.other_face_right),
                    ScaledTextField(
                        layer=psd.getLayer("Left", self.mdfc_group),
                        contents=self.layout.other_face.get("name"),
                        reference=psd.getLayer("Right", self.mdfc_group))])

                if self.has_pinlines:
                    psd.getLayer("Right", self.mdfc_group).translate(0, -6)
                    psd.getLayer("Left", self.mdfc_group).translate(0, -6)

        if self.has_nickname:
            self.text.extend([
                ScaledWidthTextField(
                    layer=self.text_layer_nickname,
                    contents=self.layout.name,
                    reference=self.nickname_shape
                ),
                ScaledTextField(
                    layer=self.text_layer_name,
                    contents=self.flavor_name,  # I added flavor_name to layouts.py to make this work
                    reference=self.name_reference
                )])
        else:
            self.text.append(
                ScaledTextField(
                    layer=self.text_layer_name,
                    contents=self.layout.name,
                    reference=self.name_reference
                )
            )

    @cached_property
    def land_color_map(self) -> dict:
        return {
            'W': [217, 206, 200],
            'U': [12, 97, 122],
            'B': [76, 72, 71],
            'R': [199, 78, 49],  # Changed from CMM to 7ED for more saturation
            'G': [99, 142, 85],
            'Land': [244, 172, 38],
        }

    @cached_property
    def dual_land_color_map(self) -> dict:
        return {
            'W': [224, 217, 215],
            'U': [0, 119, 158],
            'B': [82, 81, 74],
            'R': [237, 97, 59],
            'G': [146, 192, 48],
            'Land': [244, 172, 38],
        }

    @cached_property
    def nonland_color_map(self) -> dict:
        return {
            'W': [217, 206, 200],
            'U': [12, 97, 122],
            'B': [76, 72, 71],
            'R': [198, 118, 89],
            'G': [99, 142, 85],
            'Gold': [184, 165, 110],
            'Artifact': [139, 124, 108],
            'Colorless': [198, 198, 198]
        }

    @cached_property
    def pinlines_color_map(self) -> dict:
        if self.is_land:
            if len(self.identity) == 2:
                return self.dual_land_color_map
            return self.land_color_map
        return self.nonland_color_map

    @cached_property
    def textbox_pinlines_colors(self) -> Union[list[int], list[dict]]:
        if self.is_land:
            if (not self.is_basic_land and self.cfg_gold_textbox_lands) or (len(self.identity) > self.cfg_max_pinline_colors):
                return psd.get_pinline_gradient("Land", color_map=self.pinlines_color_map)
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) <= self.cfg_max_pinline_colors else self.pinlines,
            color_map=self.pinlines_color_map)

    @cached_property
    def non_textbox_pinlines_colors(self) -> Union[list[int], list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        if not self.cfg_color_all_pinlines:
            if self.is_land and not self.is_basic_land:
                return psd.get_pinline_gradient("Land", color_map=self.pinlines_color_map)
            if len(self.identity) > 1:
                if self.is_artifact:
                    return psd.get_pinline_gradient("Artifact", color_map=self.pinlines_color_map)
                if self.is_colorless:
                    return psd.get_pinline_gradient("Colorless", color_map=self.pinlines_color_map)
                return psd.get_pinline_gradient("Gold", color_map=self.pinlines_color_map)
        return self.textbox_pinlines_colors

    def add_pinlines(self):
        enable(self.pinlines_layer)
        enable(self.textbox_size, self.art_pinlines_background_layer)

        if self.cfg_legends_style_lands and self.is_land:
            enable(f"Legends {self.textbox_size}", psd.getLayerSet("Legends", self.pinlines_layer))

        self.generate_layer(group=psd.getLayerSet("Outer", self.pinlines_layer),
                            colors=self.non_textbox_pinlines_colors)

        self.generate_layer(group=psd.getLayerSet("Art", self.pinlines_layer), colors=self.non_textbox_pinlines_colors)
        art_mask = psd.getLayer(self.textbox_size, self.art_pinlines_masks_layer)
        psd.copy_vector_mask(art_mask, self.art_pinlines_layer)

        if not self.has_textbox: return

        enable(self.textbox_size, self.textbox_pinlines_background_layer)
        self.generate_layer(group=psd.getLayerSet("Textbox", self.pinlines_layer), colors=self.textbox_pinlines_colors)
        textbox_mask = psd.getLayer(self.textbox_size, self.textbox_pinlines_masks_layer)
        psd.copy_vector_mask(textbox_mask, self.textbox_pinlines_layer)

    def add_outer_and_art_bevels(self):
        light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_layer)
        dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_layer)
        psd.copy_vector_mask(light_mask, self.bevels_light_layer)
        psd.copy_vector_mask(dark_mask, self.bevels_dark_layer)
        enable(self.identity_advanced, self.bevels_light_layer)
        enable(self.identity_advanced, self.bevels_dark_layer)

    @cached_property
    def textbox_bevel_thickness(self) -> Optional[str]:
        if self.has_pinlines:
            return "Land"
        match self.identity_advanced:
            case "W":
                return "Small"
            case "U":
                return "Large"
            case "B":
                return "Small"
            case "R":
                return "Large"
            case "G":
                return "Medium"
            case "Gold":
                return "Large"
            case "Hybrid":
                return "Medium"
            case "Artifact":
                return "Medium"
            case "Colorless":
                return "Medium"
            case _:
                return None

    def add_textbox_bevels(self, identity=None):
        if not self.has_textbox_bevels: return

        if identity is None:
            identity = self.identity_advanced

        sized_bevel_masks = psd.getLayerSet(self.textbox_size, self.textbox_bevels_masks_layer)
        textbox_bevel = psd.getLayerSet(identity, self.textbox_bevels_group)
        enable(textbox_bevel)
        (tr, bl) = (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))
        tr_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bl_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)
        psd.copy_vector_mask(tr_mask, tr)
        psd.copy_vector_mask(bl_mask, bl)

        # Enables lines which exist on white, blue, and red textbox bevels
        if (identity == "W" or identity == "U" or identity == "R"):# and not self.is_split_fade:
            enable(self.textbox_size, textbox_bevel)

    def add_land_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        bevel_color = self.identity
        if self.is_gold_land:
            bevel_color = "Gold"

        sized_bevel_masks = psd.getLayerSet(self.textbox_size, self.textbox_bevels_masks_layer)
        textbox_bevel = psd.getLayerSet("Land", self.textbox_bevels_group)
        enable(textbox_bevel)
        (tr, bl) = (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))
        tr_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bl_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)
        psd.copy_vector_mask(tr_mask, tr)
        psd.copy_vector_mask(bl_mask, bl)
        enable(bevel_color, tr)
        enable(bevel_color, bl)

    @cached_property
    def dual_fade_info(self) -> tuple[str, str, str, str]:
        """Returned values are: top mask, bottom mask, top layer identity, bottom layer identity"""
        match self.identity:
            case "WU":
                return "Left", "Right", "W", "U"
            case "WB":
                return "Left", "Right", "W", "B"
            case "RW":
                return "Right", "Left", "W", "R"
            case "GW":
                return "Right", "Left", "W", "G"
            case "UB":
                return "Left", "Right", "U", "B"
            case "UR":
                return "Left", "Right", "U", "R"
            case "GU":
                return "Right", "Left", "U", "G"
            case "BR":
                return "Left", "Right", "B", "R"
            case "BG":
                return "Left", "Right", "B", "G"
            case "RG":
                return "Left", "Right", "R", "G"
            case _:
                return "Left", "Right", "W", "W"

    def dual_fade(self):
        (top_mask_name, _, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)

        top_frame_layer = psd.getLayer(top_layer, self.frame_texture_layer)
        bottom_frame_layer = psd.getLayer(bottom_layer, self.frame_texture_layer)
        psd.copy_layer_mask(top_mask, top_frame_layer)
        enable(top_frame_layer)
        enable(bottom_frame_layer)

        if not self.has_textbox: return
        top_textbox_layer = psd.getLayer(top_layer, self.textbox_layer)
        bottom_textbox_layer = psd.getLayer(bottom_layer, self.textbox_layer)
        psd.copy_layer_mask(top_mask, top_textbox_layer)
        enable(top_textbox_layer)
        enable(bottom_textbox_layer)

    def add_dual_fade_land_textbox(self):
        if not self.has_textbox: return

        (top_mask_name, _, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        top_textbox_layer = psd.getLayer(f"{top_layer}L Dual", self.textbox_layer)
        bottom_textbox_layer = psd.getLayer(f"{bottom_layer}L Dual", self.textbox_layer)
        psd.copy_layer_mask(top_mask, top_textbox_layer)
        enable(top_textbox_layer)
        enable(bottom_textbox_layer)

    def add_dual_fade_land_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)

        sized_bevel_masks = psd.getLayerSet(self.textbox_size, self.textbox_bevels_masks_layer)
        textbox_bevel = psd.getLayerSet("Land", self.textbox_bevels_group)
        enable(textbox_bevel)
        (tr, bl) = (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))
        tr_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bl_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)
        psd.copy_vector_mask(tr_mask, tr)
        psd.copy_vector_mask(bl_mask, bl)

        enable(psd.getLayer(top_layer, tr))
        enable(psd.getLayer(top_layer, bl))
        enable(psd.getLayer(bottom_layer, tr))
        enable(psd.getLayer(bottom_layer, bl))

        psd.copy_layer_mask(top_mask, psd.getLayer(top_layer, tr))
        psd.copy_layer_mask(top_mask, psd.getLayer(top_layer, bl))
        psd.copy_layer_mask(bottom_mask, psd.getLayer(bottom_layer, tr))
        psd.copy_layer_mask(bottom_mask, psd.getLayer(bottom_layer, bl))

    def dual_fade_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)

        self.add_textbox_bevels(identity=top_layer)
        self.add_textbox_bevels(identity=bottom_layer)

        psd.copy_layer_mask(top_mask, psd.getLayerSet(top_layer, self.textbox_bevels_group))
        psd.copy_layer_mask(bottom_mask, psd.getLayerSet(bottom_layer, self.textbox_bevels_group))

    def dual_fade_bevels(self):
        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)

        light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_layer)
        dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_layer)
        psd.copy_vector_mask(light_mask, self.bevels_light_layer)
        psd.copy_vector_mask(dark_mask, self.bevels_dark_layer)

        enable(psd.getLayer(top_layer, self.bevels_light_layer))
        enable(psd.getLayer(top_layer, self.bevels_dark_layer))
        enable(psd.getLayer(bottom_layer, self.bevels_light_layer))
        enable(psd.getLayer(bottom_layer, self.bevels_dark_layer))

        psd.copy_layer_mask(top_mask, psd.getLayer(top_layer, self.bevels_light_layer))
        psd.copy_layer_mask(top_mask, psd.getLayer(top_layer, self.bevels_dark_layer))
        psd.copy_layer_mask(bottom_mask, psd.getLayer(bottom_layer, self.bevels_light_layer))
        psd.copy_layer_mask(bottom_mask, psd.getLayer(bottom_layer, self.bevels_dark_layer))

    def position_type_line(self):
        if not self.has_textbox: return

        match self.textbox_size:
            case "Medium":
                offset = 220
            case "Small":
                offset = 365
            case "Saga":
                offset = 587
            case "Class":
                offset = 587
            case _:
                offset = 0

        if self.has_pinlines:
            self.expansion_symbol_layer.resize(90, 90, AnchorPosition.MiddleCenter)
            offset += 4

        self.text_layer_type.translate(0, offset)
        self.expansion_symbol_layer.translate(0, offset)
        if self.color_indicator_layer:
            self.color_indicator_layer.translate(0, offset)

        if self.is_type_shifted:
            self.text_layer_type.translate(100, 0)

    def add_tf_elements(self):
        """Adds elements for transform and mdfc cards (also tombstone)"""
        if self.is_transform:
            # Enables the front or back icon depending on the card face
            # Enables smaller, shifted transform icon to coexist with tombstone icon
            face = LAYERS.FRONT if self.is_front else LAYERS.BACK
            if self.has_tombstone and self.is_front:
                face = "Front Small"

            enable(face, self.transform_group)

            if self.is_front:
                if self.has_textbox and self.cfg_has_notch:
                    self.add_textbox_notch()

                    if self.is_flipside_creature:
                        enable(LAYERS.POWER_TOUGHNESS, self.transform_group)
            else:
                # Transforms backside icon to right side
                # TODO This should respond to a setting to have the icon on the left
                self.transform_group.translate(1675, 0)

        if self.is_mdfc:
            enable(self.mdfc_group)

            if self.is_front:
                enable("Front", self.mdfc_group)
            else:
                enable("Back", self.mdfc_group)
            if self.has_textbox and self.cfg_has_notch:
                self.add_textbox_notch()
            return

        if self.has_tombstone:
            if self.is_transform and self.is_front:
                # Enables smaller, shifted tombstone icon to coexist with transform icon
                enable("Tombstone Small", self.text_group)
            else:
                enable("Tombstone", self.text_group)

    def add_textbox_notch(self):
        cardtype = ""
        if self.is_mdfc:
            cardtype = "MDFC"
        if self.is_transform:
            cardtype = "TF"

        enable(f"{cardtype} Notch", self.textbox_masks_group)
        psd.copy_vector_mask(psd.getLayer(f"Textbox Outlines {cardtype}", self.mask_group), self.textbox_outlines_group)

        bevel_overlays = psd.getLayerSet(f"Textbox Bevel Overlays {cardtype}", self.card_frame_group)

        if self.has_textbox_bevels:
            color = self.identity_advanced

            if self.is_split_fade:
                color = "Hybrid"

            enable(color, bevel_overlays)
            psd.copy_vector_mask(psd.getLayer(f"Textbox Bevels {cardtype}", self.mask_group), self.textbox_bevels_group)

            if self.is_land:
                color = self.identity
                if len(color) > 2: color = "Gold"

                if self.is_dual_land:
                    (top, _, top_color, bottom_color) = self.dual_fade_info
                    notch_side = "Left" if cardtype == "MDFC" else "Right"
                    color = top_color if notch_side == top else bottom_color

                print(color)
                land_bevel_overlays = psd.getLayerSet("Land", bevel_overlays)
                enable(color, psd.getLayerSet("TR", land_bevel_overlays))
                enable(color, psd.getLayerSet("BL", land_bevel_overlays))

        if self.has_pinlines:
            enable("Pinlines", bevel_overlays)
            psd.copy_vector_mask(psd.getLayer(f"Pinlines {cardtype}", self.mask_group), self.pinlines_layer)
            self.generate_layer(
                group=psd.getLayerSet("Pinlines", psd.getLayerSet("Pinlines", bevel_overlays)),
                colors=self.textbox_pinlines_colors
            )
        else:
            enable(f"{cardtype} Notch", self.outlines_group)

    def add_land_frame_texture(self):
        enable(self.frame_texture)
        self.add_outer_and_art_bevels()

    def add_land_textbox_texture(self):
        if self.is_dual_land:
            self.add_dual_fade_land_textbox()
            self.add_dual_fade_land_textbox_bevels()
        else:
            enable(self.textbox_texture)
            self.add_land_textbox_bevels()

    def add_nonland_frame_texture(self):
        if self.is_split_fade:
            self.dual_fade()
            self.dual_fade_bevels()
        else:
            enable(self.frame_texture)
            self.add_outer_and_art_bevels()

    def add_nonland_textbox_texture(self):
        if self.is_split_fade:
            if self.cfg_dual_textbox_bevels:
                self.dual_fade_textbox_bevels()
            else:
                self.add_textbox_bevels()
        else:
            enable(self.textbox_texture)
            self.add_textbox_bevels()

    def apply_textbox_shape(self):
        if not (self.identity_advanced == "B" and self.is_normal and self.has_irregular_textbox):
            # Enables vector mask for vectorized textboxes (including green)
            enable(self.textbox_mask)
        else:
            # Enables rasterized textbox for black textboxes
            enable(f"B {self.textbox_size}", self.textbox_layer)

    def apply_devoid(self):
        color = self.identity if len(self.identity) == 1 else "Gold"
        color_layer = psd.getLayer(color, self.frame_texture_layer)
        enable(color_layer.visible)
        psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group), color_layer)

        if self.is_transparent:
            psd.copy_layer_mask(psd.getLayer("Devoid", self.mask_group), self.card_frame_group)

        if self.cfg_colored_bevels_on_devoid:
            enable(color, self.bevels_light_layer)
            enable(color, self.bevels_dark_layer)
            psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group),
                                psd.getLayer(color, self.bevels_light_layer))
            psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group),
                                psd.getLayer(color, self.bevels_dark_layer))

    def add_outlines(self):
        enable(self.art_outlines)
        if self.textbox_outlines is not None:
            enable(self.textbox_outlines)

    def add_nickname_plate(self):
        enable("Nickname", self.text_group)
        enable("Nickname Box", self.text_group)

        masks = psd.getLayerSet("Masks", self.frame_texture_layer)
        enable("Nickname", masks)

        nickname_mask = psd.getLayer("Nickname", self.mask_group)
        psd.copy_vector_mask(nickname_mask, self.outlines_group)
        psd.copy_vector_mask(nickname_mask, self.bevels_layer)

    def add_textbox_decorations(self):
        if self.is_type_shifted and self.color_indicator_layer:
            enable(self.color_indicator_layer)

        # Applies dropshadow effect to green textbox
        if self.identity_advanced == "G":
            psd.copy_layer_fx(psd.getLayer("G", self.textbox_effects_layer), self.textbox_layer)

    def add_textbox(self):
        if self.is_land: self.add_land_textbox_texture()
        if not self.is_land: self.add_nonland_textbox_texture()
        self.apply_textbox_shape()
        self.add_textbox_decorations()

    def enable_frame_layers(self):
        if self.is_land: self.add_land_frame_texture()
        if not self.is_land: self.add_nonland_frame_texture()
        enable(self.frame_mask)

        if self.is_devoid: self.apply_devoid()

        if (not self.is_devoid) and self.is_transparent:
            self.card_frame_group.opacity = self.cfg_transparent_opacity

        if self.cfg_floating_frame: disable(self.border_group)

        if self.has_textbox: self.add_textbox()
        # Hide expansion symbol (better to not add it in the first place, but I don't know how)
        if not self.has_textbox:
            disable(self.expansion_symbol_layer)

        self.add_outlines()
        if self.has_pinlines: self.add_pinlines()
        self.position_type_line()

        if self.has_nickname: self.add_nickname_plate()

        if self.is_promo_star:
            enable("Promo Star", self.text_group)

        self.add_tf_elements()

    def hook_large_mana(self) -> None:
        """Adjust mana cost position for large symbols."""
        self.text_layer_mana.translate(0, -12)

##################################################
# Child classes
##################################################

class RetroSagaTemplate(RetroTemplate, SagaMod):

    @cached_property
    def is_saga(self) -> bool:
        return True

    @cached_property
    def has_pinlines(self) -> bool:
        return False

    @cached_property
    def is_split_fade(self) -> bool:
        return False

    @cached_property
    def textbox_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.saga_group)

    def text_layers_saga(self):
        # The full read ahead reminder text is too large to comfortably fit in the textbox
        # So it gets swapped out for an abridged version that explains Read Ahead but not how Sagas work
        description = self.layout.saga_description
        if "Read ahead" in description:
            description = "Read ahead (Choose a chapter and start with that many lore counters. Skipped chapters don't trigger.)"

        # Add description text with reminder
        self.text.append(
            text_classes.FormattedTextArea(
                layer=self.text_layer_reminder,
                contents=description,
                reference=self.reminder_reference))

        # Iterate through each saga stage and add line to text layers
        for i, line in enumerate(self.layout.saga_lines):
            # Add icon layers for this ability
            self.icon_layers.append([psd.getLayer(n, self.saga_group).duplicate() for n in line['icons']])

            # Add ability text for this ability
            layer = self.text_layer_ability if i == 0 else self.text_layer_ability.duplicate()
            self.ability_layers.append(layer)
            self.text.append(
                text_classes.FormattedTextField(
                    layer=layer, contents=line['text']))

    def frame_layers_saga(self):
        enable(self.saga_group)


class RetroClassTemplate(RetroTemplate, ClassMod):
    @cached_property
    def is_class(self) -> bool:
        return True

    @cached_property
    def has_pinlines(self) -> bool:
        return False

    @cached_property
    def is_split_fade(self) -> bool:
        return False

    @cached_property
    def textbox_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.class_group)

    @cached_property
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STAGE, self.class_group)

    def frame_layers_classes(self) -> None:
        enable(self.class_group)

class RetroPWTemplate(RetroTemplate):
    """Exists to have a different picture and settings"""

class RetroPWMDFCTemplate(RetroTemplate):
    """Exists to have a different picture and settings"""

class RetroPWTFTemplate(RetroTemplate):
    """Exists to have a different picture and settings"""

class RetroMDFCTemplate(RetroTemplate):
    """Exists to have a different picture and settings"""

class RetroTFTemplate(RetroTemplate):
    """Exists to have a different picture and settings"""