"""
* Plugin: [Gavin]
"""
# Standard Library
from enum import Enum
from typing import Optional, Union

# Third Party
from PIL import Image
from photoshop.api import AnchorPosition, SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local
import src.helpers as psd
import src.text_layers as text_classes

from src import CFG, CON
from src.enums.layers import LAYERS
from src.utils.adobe import ReferenceLayer
from src.utils.properties import auto_prop_cached
from src.helpers import get_line_count, set_text_size, enable_layer_fx
from src.layouts import SagaLayout
from src.templates import ClassicTemplate, ClassMod
from src.templates.saga import SagaMod, SagaVectorTemplate

from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextArea,
    FormattedTextField,
    ScaledWidthTextField
)



# TODO
# MDFC
# Planeswalkers
# Nyx, colored artifacts
# Legend Crown
# Battles
# Split Cards, rooms, aftermath and meld
# Flip Cards

# Move the layout methods to here (should be possible because I don't think anything is protected)
# That will be necessary for distributing the plugin.

# Make Retro inherit from core or normal instead of classic?

def rank_textbox_size(size: str) -> int:
    match size:
        case "Small":
            return 0
        case "Medium":
            return 1
        case "Normal":
            return 2


class RetroTemplate(ClassicTemplate):
    """Retro frames from MM3, MH3, and RVR."""
    frame_suffix = 'Retro'

    # Settings

    # Auto looks for certain phrases in the oracle text
    # to determine which cards should have the tombstone icon
    # on_flashback only checks for flashback so it doesn't have false positives like auto
    # The last setting checks if the exact version of the card given has a tombstone icon
    # So new border cards and cards before the creation of tombstone don't have it
    auto_add_tombstone = True
    tombstone_on_flashback = True
    tombstone_on_tombstone = True

    # Makes planeswalker explain the mechanics, like the secret lair planeswalkers
    verbose_planeswalkers = False

    # Controls size of textbox and art. Options are Normal (default), Medium, Small, and Textless
    # Medium is about 70% of normal size and Small is about 55%
    # Textless still has Power/Toughness, Name, and Mana cost, but all other text (and the set symbol) are removed

    # Set to None to enable automatic textbox size based on the amount of text
    textbox_size_override = None

    # Gives lands a lighter color-grading, golden textbox color, and shiny golden pinlines like the lands from Legends
    legends_style_lands = False

    # Use nonstandard textboxes (wooden plank and tattered scroll respectively) on green and black cards
    use_irregular_textboxes = True
    use_black_raster_textbox = True

    # Pinlines

    # Adds multicolored/gold pinlines to multicolored cards
    pinlines_on_multicolored = False

    # Adds colored pinlines to colored artifacts and light brown pinlines to colorless ones
    pinlines_on_artifacts = False

    # Enables pinlines on all nonland cards. Monocolored cards have pinline colors inherited from basic lands
    pinlines_on_all_cards = False

    # Applies card color to pinlines other than the textbox on multicolored and artifact cards
    # Monocolored and basic land cards always use card color for all pinlines
    color_all_pinlines = False

    # Range: 2-4, default: 2
    # Pinlines are gold if colors > max_pinline_colors
    max_pinline_colors = 2

    # Art Size

    # Makes colorless cardframes transparent
    # Requires full art
    colorless_transparent = True

    # Makes the colored part at the top of devoid cards include a colored art bevel
    # The colorless bevel is very subtle, so this setting makes the name bar more pronounced
    use_colored_bevels_on_devoid = True

    # Makes all cards transparent
    all_transparent = False

    # The opacity value for the card frame when transparent. Range: 0.0 - 100.0, Default: 35.0
    transparent_opacity = 45.0

    # Makes the card borderless, so the frame floats on top of the art. Requires very large art to work properly
    use_floating_frame = False

    # Lands

    # Makes the textbox pinlines on all nonbasic lands gold, like in fifth edition
    gold_textbox_pinline_lands = False

    # Makes the textbox on all nonbasic lands gold, like in fifth edition
    gold_textbox_lands = False

    # Makes gold lands have textbox bevels. They don't for some reason
    textbox_bevels_on_gold_lands = False

    # Split fade cards

    # Makes hybrid cards a horizontal fade between the colors
    split_hybrid = True

    # Split fade on all two colored cards.
    split_all = False

    # Uses normal textbox bevels and applies a dual fade to them on split fade cards.
    # Looks weird because red cards have inverted bevels to other colors, and blue, white and red cards have lines in their bevels
    # The alternative (default) is a standarized bevel color
    # The bevel size is always standardized because it would look goofy otherwise
    use_dual_textbox_bevels = False

    # Misc

    # Does what it sounds like. Turns off all textbox bevels
    disable_textbox_bevels = False

    #################################################################################

    @auto_prop_cached
    def card_frame_group(self) -> LayerSet:
        return psd.getLayerSet("Card Frame")

    @auto_prop_cached
    def art_frames_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Frames")

    @auto_prop_cached
    def pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Pinlines")

    @auto_prop_cached
    def art_pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Art", self.pinlines_layer)

    @auto_prop_cached
    def art_pinlines_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Masks", self.pinlines_layer)

    @auto_prop_cached
    def art_pinlines_background_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Background", self.pinlines_layer)

    @auto_prop_cached
    def textbox_pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox", self.pinlines_layer)

    @auto_prop_cached
    def textbox_pinlines_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox Masks", self.pinlines_layer)

    @auto_prop_cached
    def textbox_pinlines_background_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox Background", self.pinlines_layer)

    @auto_prop_cached
    def outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Outlines")

    @auto_prop_cached
    def art_outlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Art Outlines", self.outlines_group)

    @auto_prop_cached
    def textbox_outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Outlines", self.outlines_group)

    @auto_prop_cached
    def textbox_bevels_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Bevels", self.card_frame_group)

    @auto_prop_cached
    def textbox_bevels_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.textbox_bevels_group)

    @auto_prop_cached
    def textbox_layer(self) -> LayerSet:
        return psd.getLayerSet("Textbox", self.card_frame_group)

    @auto_prop_cached
    def textbox_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.textbox_layer)

    @auto_prop_cached
    def textbox_effects_layer(self) -> LayerSet:
        return psd.getLayerSet("Effects", self.textbox_layer)

    @auto_prop_cached
    def bevels_layer(self) -> LayerSet:
        return psd.getLayerSet("Bevels", self.card_frame_group)

    @auto_prop_cached
    def bevels_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.bevels_layer)

    @auto_prop_cached
    def bevels_light_layer(self) -> LayerSet:
        return psd.getLayerSet("Light", self.bevels_layer)

    @auto_prop_cached
    def bevels_dark_layer(self) -> LayerSet:
        return psd.getLayerSet("Dark", self.bevels_layer)

    @auto_prop_cached
    def frame_texture_layer(self) -> LayerSet:
        return psd.getLayerSet("Frame Texture", self.card_frame_group)

    @auto_prop_cached
    def frame_masks_layer(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.frame_texture_layer)

    @auto_prop_cached
    def transform_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.TRANSFORM, self.text_group)

    @auto_prop_cached
    def mdfc_group(self) -> LayerSet:
        return psd.getLayerSet("MDFC", self.text_group)

    # Added layout logic

    @auto_prop_cached
    def flavor_name(self) -> Optional[str]:
        """Display name for nicknamed cards"""
        return self.layout.card.get('flavor_name')

    @auto_prop_cached
    def is_tombstone(self) -> bool:
        return bool('tombstone' in self.layout.frame_effects)

    @auto_prop_cached
    def is_flashback(self) -> bool:
        return bool('flashback' in self.layout.oracle_text)

    @auto_prop_cached
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

        key_phrase_list = [
            f'{self.layout.name_raw} is in your graveyard',
            f'return {self.layout.name_raw} from your graveyard',
            f'cast {self.layout.name_raw} from your graveyard',
            f'put {self.layout.name_raw} from your graveyard',
            f'exile {self.layout.name_raw} from your graveyard',
        ]
        for phrase in key_phrase_list:
            if phrase in self.layout.oracle_text_raw: return True

        name_list = [
            "Say Its Name",
            "Skyblade's Boon",
            "Nether Spirit",
        ]
        for name in name_list:
            if name == self.layout.name_raw: return True

        return False

    # Layer logic

    @auto_prop_cached
    def frame_texture(self) -> ArtLayer:
        if self.is_land and self.legends_style_lands:
            return psd.getLayer("Legends Land", self.frame_texture_layer)
        return psd.getLayer(self.identity_advanced, self.frame_texture_layer)

    @auto_prop_cached
    def frame_mask(self) -> ArtLayer:
        return psd.getLayer(self.textbox_size, self.frame_masks_layer)

    @auto_prop_cached
    def textbox_texture(self) -> ArtLayer:
        if self.is_land:
            if self.legends_style_lands:
                return psd.getLayer("Legends", self.textbox_layer)
            if self.is_gold_land:
                return psd.getLayer("Land", self.textbox_layer)
            return psd.getLayer(self.identity + "L", self.textbox_layer)
        return psd.getLayer(self.identity_advanced, self.textbox_layer)

    @auto_prop_cached
    def textbox_mask(self) -> Optional[ArtLayer]:
        if self.textbox_size == "Textless": return None
        textbox_name = self.textbox_size
        if self.has_irregular_textbox:
            textbox_name = f"{self.identity_advanced} {self.textbox_size}"
        # if self.is_transform and self.is_front:
        #     textbox_name = textbox_name + " TF Front"

        return psd.getLayer(textbox_name, self.textbox_masks_group)

    @auto_prop_cached
    def art_reference(self) -> ReferenceLayer:
        if self.use_floating_frame:
            return psd.get_reference_layer("Floating Frame", self.art_frames_layer)
        if self.is_transparent:
            return psd.get_reference_layer("Transparent Frame", self.art_frames_layer)
        return psd.get_reference_layer(self.textbox_size, self.art_frames_layer)

    @auto_prop_cached
    def textbox_reference(self) -> ReferenceLayer:
        if self.is_mdfc:
            return psd.get_reference_layer(f"Textbox Reference {self.textbox_size} TF", self.text_group)
        return psd.get_reference_layer(f"Textbox Reference {self.textbox_size}", self.text_group)

    @auto_prop_cached
    def expansion_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer("Expansion Reference", self.text_group)

    @auto_prop_cached
    def art_outlines(self) -> LayerSet:
        return psd.getLayerSet(self.textbox_size, self.art_outlines_layer)

    @auto_prop_cached
    def textbox_outlines(self) -> Optional[ArtLayer]:
        if self.has_irregular_textbox:
            return None
        if self.textbox_size == "Textless":
            return None
        # if self.is_transform and self.is_front:
        #     return psd.getLayer(self.textbox_size + " TF Front", self.textbox_outlines_layer)
        return psd.getLayer(self.textbox_size, self.textbox_outlines_group)

    # Properties

    @auto_prop_cached
    def has_nickname(self) -> bool:
        """Return True if this a nickname render."""
        if self.flavor_name is not None:
            return True
        return False

    @auto_prop_cached
    def is_content_aware_enabled(self) -> bool:
        if self.use_floating_frame:
            return True
        return False

    @auto_prop_cached
    def has_irregular_textbox(self) -> bool:
        if self.is_saga or self.is_class:
            return False
        if self.is_transform or self.is_mdfc:
            return False
        if not self.use_irregular_textboxes:
            return False
        if self.identity_advanced == "G":
            return True
        if self.identity_advanced == "B":
            return True
        return False

    @auto_prop_cached
    def identity_advanced(self) -> str:
        if self.is_land:
            return "Land"
        if self.is_split:
            return "Hybrid"
        if self.is_artifact:
            return "Artifact"
        if self.is_colorless:
            return "Colorless"
        if len(self.identity) > 1:
            return "Gold"
        return self.identity

    @auto_prop_cached
    def has_pinlines(self) -> bool:
        if self.is_land:
            return True
        if len(self.identity) > 1 and self.pinlines_on_multicolored:
            return True
        if self.is_artifact and self.pinlines_on_artifacts:
            return True
        if self.pinlines_on_all_cards:
            return True
        return False

    @auto_prop_cached
    def has_textbox(self) -> bool:
        if self.textbox_size == "Textless":
            return False
        return True

    @auto_prop_cached
    def has_textbox_bevels(self) -> bool:
        if not self.has_textbox:
            return False
        if self.disable_textbox_bevels:
            return False
        if self.has_irregular_textbox:
            return False
        if self.is_land and self.legends_style_lands:
            return False
        if self.is_gold_land:
            if self.textbox_bevels_on_gold_lands:
                return True
            return False
        return True

    @auto_prop_cached
    def is_gold_land(self) -> bool:
        """ Whether the textbox of the card is the gold land textbox"""
        if not self.is_land:
            return False
        if self.is_basic_land:
            return False
        if self.gold_textbox_lands:
            return True
        if len(self.identity) < 1 or len(self.identity) > 2:
            return True
        return False

    @auto_prop_cached
    def is_dual_land(self) -> bool:
        if not self.is_land:
            return False
        if self.is_gold_land:
            return False
        if len(self.identity) == 2:
            return True
        return False

    @auto_prop_cached
    def is_split(self) -> bool:
        if len(self.identity) != 2:
            return False
        if self.split_all:
            return True
        if self.is_hybrid and self.split_hybrid:
            return True
        return False

    @auto_prop_cached
    def is_transparent(self) -> bool:
        if self.is_colorless and self.colorless_transparent:
            return True
        if self.all_transparent:
            return True
        return False

    @auto_prop_cached
    def is_devoid(self) -> bool:
        # For some reason true colorless cards have "Colorless" as their color identity while
        # artifacts have an empty string.
        if self.identity == "Colorless":
            return False
        if self.is_colorless and (len(self.identity) > 0):
            return True
        return False

    @auto_prop_cached
    def is_saga(self) -> bool:
        return False

    @auto_prop_cached
    def is_class(self) -> bool:
        return False

    @auto_prop_cached
    def art_aspect(self) -> float:
        art_file = self.layout.art_file
        with Image.open(art_file) as img:
            width, height = img.size
            return width / height

    @auto_prop_cached
    def textbox_size_from_art_aspect(self) -> str:
        if self.art_aspect > 1.25:
            return "Normal"
        if self.art_aspect > 1.06:
            return "Medium"
        if self.art_aspect > 0.96:
            return "Small"
        return "Small"

    @auto_prop_cached
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

    @auto_prop_cached
    def auto_textbox_size(self) -> str:
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

    @auto_prop_cached
    def textbox_size(self) -> str:
        if self.is_saga:
            return "Saga"
        if self.is_class:
            return "Class"
        if self.textbox_size_override is not None:
            return self.textbox_size_override
        return self.auto_textbox_size

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_type(self) -> ArtLayer:
        if not self.has_textbox:
            return None
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    @auto_prop_cached
    def text_layer_name(self) -> ArtLayer:
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @auto_prop_cached
    def text_layer_nickname(self) -> ArtLayer:
        return psd.getLayer("Nickname", self.text_group)

    @auto_prop_cached
    def text_layer_rules(self) -> ArtLayer:
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @auto_prop_cached
    def nickname_shape(self) -> ArtLayer:
        return psd.getLayer("Nickname Box", self.text_group)

    @auto_prop_cached
    def pt_length(self) -> int:
        return len(f'{self.layout.power}{self.layout.toughness}')

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

        if self.is_flipside_creature:
            self.text.append(
                TextField(
                    layer=psd.getLayer(LAYERS.POWER_TOUGHNESS, self.transform_group),
                    contents=f'{self.layout.other_face_power}/{self.layout.other_face_toughness}'))

        if self.textbox_size == "Textless":
            return
        if self.is_saga or self.is_class:
            return

        rules_text = self.layout.oracle_text

        if "Planeswalker" in self.layout.type_line and self.verbose_planeswalkers:
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

    @auto_prop_cached
    def land_color_map(self) -> dict:
        return {
            'W': [217, 206, 200],
            'U': [12, 97, 122],
            'B': [76, 72, 71],
            'R': [199, 78, 49],  # Changed from CMM to 7ED for more saturation
            'G': [99, 142, 85],
            'Land': [244, 172, 38],
        }

    @auto_prop_cached
    def dual_land_color_map(self) -> dict:
        return {
            'W': [224, 217, 215],
            'U': [0, 119, 158],
            'B': [82, 81, 74],
            'R': [237, 97, 59],
            'G': [146, 192, 48],
            'Land': [244, 172, 38],
        }

    @auto_prop_cached
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

    @auto_prop_cached
    def pinlines_color_map(self) -> dict:
        if self.is_land:
            if len(self.identity) == 2:
                return self.dual_land_color_map
            return self.land_color_map
        return self.nonland_color_map

    @auto_prop_cached
    def textbox_pinlines_colors(self) -> Union[list[int], list[dict]]:
        if self.is_land:
            if (not self.is_basic_land and self.gold_textbox_lands) or (len(self.identity) > self.max_pinline_colors):
                return psd.get_pinline_gradient("Land", color_map=self.pinlines_color_map)
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) <= self.max_pinline_colors else self.pinlines,
            color_map=self.pinlines_color_map)

    @auto_prop_cached
    def non_textbox_pinlines_colors(self) -> Union[list[int], list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        if self.is_land and not self.is_basic_land:
            return psd.get_pinline_gradient("Land", color_map=self.pinlines_color_map)
        if not self.color_all_pinlines and len(self.identity) > 1:
            if self.is_artifact:
                return psd.get_pinline_gradient("Artifact", color_map=self.pinlines_color_map)
            if self.is_colorless:
                return psd.get_pinline_gradient("Colorless", color_map=self.pinlines_color_map)
            return psd.get_pinline_gradient("Gold", color_map=self.pinlines_color_map)
        return self.textbox_pinlines_colors

    def add_pinlines(self):
        if not self.has_pinlines: return

        self.pinlines_layer.visible = True
        psd.getLayer(self.textbox_size, self.art_pinlines_background_layer).visible = True

        if self.legends_style_lands and self.is_land:
            psd.getLayer(f"Legends {self.textbox_size}", psd.getLayerSet("Legends", self.pinlines_layer)).visible = True

        self.generate_layer(group=psd.getLayerSet("Outer", self.pinlines_layer),
                            colors=self.non_textbox_pinlines_colors)

        self.generate_layer(group=psd.getLayerSet("Art", self.pinlines_layer), colors=self.non_textbox_pinlines_colors)
        art_mask = psd.getLayer(self.textbox_size, self.art_pinlines_masks_layer)
        psd.copy_vector_mask(art_mask, self.art_pinlines_layer)

        if not self.has_textbox: return

        psd.getLayer(self.textbox_size, self.textbox_pinlines_background_layer).visible = True
        self.generate_layer(group=psd.getLayerSet("Textbox", self.pinlines_layer), colors=self.textbox_pinlines_colors)
        textbox_mask = psd.getLayer(self.textbox_size, self.textbox_pinlines_masks_layer)
        psd.copy_vector_mask(textbox_mask, self.textbox_pinlines_layer)

    def add_bevels(self):
        light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_layer)
        dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_layer)
        psd.copy_vector_mask(light_mask, self.bevels_light_layer)
        psd.copy_vector_mask(dark_mask, self.bevels_dark_layer)
        psd.getLayer(self.identity_advanced, self.bevels_light_layer).visible = True
        psd.getLayer(self.identity_advanced, self.bevels_dark_layer).visible = True

    @auto_prop_cached
    def textbox_bevel_thickness(self) -> str:
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
        textbox_bevel.visible = True
        (tr, bl) = (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))
        tr_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bl_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)
        psd.copy_vector_mask(tr_mask, tr)
        psd.copy_vector_mask(bl_mask, bl)

        if (identity == "W" or identity == "U" or identity == "R") and not self.is_split:
            psd.getLayerSet(self.textbox_size, textbox_bevel).visible = True

    def add_land_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        bevel_color = self.identity
        if self.is_gold_land:
            bevel_color = "Gold"

        sized_bevel_masks = psd.getLayerSet(self.textbox_size, self.textbox_bevels_masks_layer)
        textbox_bevel = psd.getLayerSet("Land", self.textbox_bevels_group)
        textbox_bevel.visible = True
        (tr, bl) = (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))
        tr_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bl_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)
        psd.copy_vector_mask(tr_mask, tr)
        psd.copy_vector_mask(bl_mask, bl)
        psd.getLayer(bevel_color, tr).visible = True
        psd.getLayer(bevel_color, bl).visible = True

    @auto_prop_cached
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
        top_frame_layer.visible = True
        bottom_frame_layer.visible = True

        if not self.has_textbox: return
        top_textbox_layer = psd.getLayer(top_layer, self.textbox_layer)
        bottom_textbox_layer = psd.getLayer(bottom_layer, self.textbox_layer)
        psd.copy_layer_mask(top_mask, top_textbox_layer)
        top_textbox_layer.visible = True
        bottom_textbox_layer.visible = True

    def dual_fade_land_textbox(self):
        if not self.has_textbox: return

        (top_mask_name, _, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        top_textbox_layer = psd.getLayer(f"{top_layer}L Dual", self.textbox_layer)
        bottom_textbox_layer = psd.getLayer(f"{bottom_layer}L Dual", self.textbox_layer)
        psd.copy_layer_mask(top_mask, top_textbox_layer)
        top_textbox_layer.visible = True
        bottom_textbox_layer.visible = True

    def dual_fade_land_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_info
        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)

        sized_bevel_masks = psd.getLayerSet(self.textbox_size, self.textbox_bevels_masks_layer)
        textbox_bevel = psd.getLayerSet("Land", self.textbox_bevels_group)
        textbox_bevel.visible = True
        (tr, bl) = (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))
        tr_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bl_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)
        psd.copy_vector_mask(tr_mask, tr)
        psd.copy_vector_mask(bl_mask, bl)

        psd.getLayer(top_layer, tr).visible = True
        psd.getLayer(top_layer, bl).visible = True
        psd.getLayer(bottom_layer, tr).visible = True
        psd.getLayer(bottom_layer, bl).visible = True

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

        psd.getLayer(top_layer, self.bevels_light_layer).visible = True
        psd.getLayer(top_layer, self.bevels_dark_layer).visible = True
        psd.getLayer(bottom_layer, self.bevels_light_layer).visible = True
        psd.getLayer(bottom_layer, self.bevels_dark_layer).visible = True

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

    @auto_prop_cached
    def has_tombstone(self) -> bool:
        if self.is_tombstone_auto and self.auto_add_tombstone:
            return True
        if self.is_flashback and self.tombstone_on_flashback:
            return True
        if self.is_tombstone and self.tombstone_on_tombstone:
            return True
        return False

    def add_tf_elements(self):
        """Adds elements for transform and mdfc cards (also tombstone)"""
        if self.is_transform:
            self.transform_group.visible = True

            if self.transform_icon_layer:
                self.transform_icon_layer.visible = True

            if self.is_front:
                # Move Cardname to the right slightly
                psd.getLayer(LAYERS.NAME, self.text_group).translate(40, 0)

                if self.has_textbox:
                    self.add_textbox_notch()

                if self.is_flipside_creature:
                    psd.getLayer(LAYERS.POWER_TOUGHNESS, self.transform_group).visible = True
            else:
                self.transform_group.translate(1658, 0)
            return

        if self.is_mdfc:
            self.mdfc_group.visible = True

            if self.is_front:
                psd.getLayerSet("Front", self.mdfc_group).visible = True
            else:
                psd.getLayerSet("Back", self.mdfc_group).visible = True
                # Move card name on back because back icon is wider
                psd.getLayer(LAYERS.NAME, self.text_group).translate(60, 0)
            if self.has_textbox:
                self.add_textbox_notch()
            return

        if self.has_tombstone:
            psd.getLayer("Tombstone", self.text_group).visible = True

    def add_textbox_notch(self):
        type = ""
        if self.is_mdfc:
            type = "MDFC"
        if self.is_transform:
            type = "TF"

        psd.getLayer(f"{type} Notch", self.textbox_masks_group).visible = True
        psd.copy_vector_mask(psd.getLayer(f"Textbox Outlines {type}", self.mask_group), self.textbox_outlines_group)

        bevel_overlays = psd.getLayerSet(f"Textbox Bevel Overlays {type}", self.card_frame_group)

        if self.has_textbox_bevels:
            color = self.identity_advanced

            if self.is_split:
                color = "Hybrid"

            psd.getLayerSet(color, bevel_overlays).visible = True
            psd.copy_vector_mask(psd.getLayer(f"Textbox Bevels {type}", self.mask_group), self.textbox_bevels_group)

            if self.is_land:
                color = self.identity
                if len(color) > 2: color = "Gold"

                if self.is_dual_land:
                    (top, _, top_color, bottom_color) = self.dual_fade_info
                    notch_side = "Left" if type == "MDFC" else "Right"
                    color = top_color if notch_side == top else bottom_color

                print(color)
                land_bevel_overlays = psd.getLayerSet("Land", bevel_overlays)
                psd.getLayer(color, psd.getLayerSet("TR", land_bevel_overlays)).visible = True
                psd.getLayer(color, psd.getLayerSet("BL", land_bevel_overlays)).visible = True

        if self.has_pinlines:
            psd.getLayerSet("Pinlines", bevel_overlays).visible = True
            psd.copy_vector_mask(psd.getLayer(f"Pinlines {type}", self.mask_group), self.pinlines_layer)
            self.generate_layer(
                group=psd.getLayerSet("Pinlines", psd.getLayerSet("Pinlines", bevel_overlays)),
                colors=self.textbox_pinlines_colors
            )
        else:
            psd.getLayer(f"{type} Notch", self.outlines_group).visible = True

    def enable_frame_layers(self):
        if self.is_land:
            self.frame_texture.visible = True
            self.add_bevels()
            if self.is_dual_land and not self.legends_style_lands:
                self.dual_fade_land_textbox()
                self.dual_fade_land_textbox_bevels()
            else:
                self.textbox_texture.visible = True
                self.add_land_textbox_bevels()
        else:
            if self.is_split:
                self.dual_fade()
                self.dual_fade_bevels()
                if self.use_dual_textbox_bevels:
                    self.dual_fade_textbox_bevels()
                else:
                    self.add_textbox_bevels()
            else:
                self.frame_texture.visible = True
                self.textbox_texture.visible = True
                self.add_bevels()
                self.add_textbox_bevels()

        self.frame_mask.visible = True
        if self.has_textbox:
            if self.identity_advanced == "B" and self.use_black_raster_textbox:
                psd.getLayer(f"B {self.textbox_size}", self.textbox_layer).visible = True
            else:
                self.textbox_mask.visible = True

        if self.has_irregular_textbox and not (self.identity_advanced == "B" and self.use_black_raster_textbox):
            psd.copy_layer_fx(psd.getLayer(self.identity_advanced, self.textbox_effects_layer), self.textbox_layer)

        self.art_outlines.visible = True
        if self.textbox_outlines is not None:
            self.textbox_outlines.visible = True

        self.add_pinlines()

        if self.is_devoid:
            color = self.identity if len(self.identity) == 1 else "Gold"
            color_layer = psd.getLayer(color, self.frame_texture_layer)
            color_layer.visible = True
            psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group), color_layer)

            if self.is_transparent:
                psd.copy_layer_mask(psd.getLayer("Devoid", self.mask_group), self.card_frame_group)

            if self.use_colored_bevels_on_devoid:
                psd.getLayer(color, self.bevels_light_layer).visible = True
                psd.getLayer(color, self.bevels_dark_layer).visible = True
                psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group),
                                    psd.getLayer(color, self.bevels_light_layer))
                psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group),
                                    psd.getLayer(color, self.bevels_dark_layer))

        elif self.is_transparent:
            self.card_frame_group.opacity = self.transparent_opacity

        if self.use_floating_frame:
            self.border_group.visible = False

        if self.is_type_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

        if not self.has_textbox:  # Replace with not adding it in the first place
            self.expansion_symbol_layer.visible = False

            if self.color_indicator_layer:
                self.color_indicator_layer.visible = False

        self.position_type_line()

        if self.has_nickname:
            psd.getLayer("Nickname", self.text_group).visible = True
            psd.getLayer("Nickname Box", self.text_group).visible = True
            psd.getLayer("Nickname", psd.getLayerSet("Masks", self.frame_texture_layer)).visible = True
            nickname_mask = psd.getLayer("Nickname", self.mask_group)
            psd.copy_vector_mask(nickname_mask, self.outlines_group)
            psd.copy_vector_mask(nickname_mask, self.bevels_layer)

        # Add the promo star
        if self.is_promo_star:
            psd.getLayerSet("Promo Star", LAYERS.TEXT_AND_ICONS).visible = True

        self.add_tf_elements()

    def hook_large_mana(self) -> None:
        """Adjust mana cost position for large symbols."""
        self.text_layer_mana.translate(0, -12)


class RetroSagaTemplate(RetroTemplate, SagaMod):

    @auto_prop_cached
    def is_saga(self) -> bool:
        return True

    @auto_prop_cached
    def has_pinlines(self) -> bool:
        return False

    @auto_prop_cached
    def is_split(self) -> bool:
        return False

    @auto_prop_cached
    def textbox_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.saga_group)

    def text_layers_saga(self):
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
        self.saga_group.visible = True


class RetroClassTemplate(RetroTemplate, ClassMod):
    @auto_prop_cached
    def is_class(self) -> bool:
        return True

    @auto_prop_cached
    def has_pinlines(self) -> bool:
        return False

    @auto_prop_cached
    def is_split(self) -> bool:
        return False

    @auto_prop_cached
    def textbox_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.class_group)

    @auto_prop_cached
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STAGE, self.class_group)

    def frame_layers_classes(self) -> None:
        self.class_group.visible = True
