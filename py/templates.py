"""
* Plugin: [Gavin]
"""
from functools import cached_property
# Standard Library
from typing import Optional, Union

# Third Party
from PIL import Image
# noinspection PyProtectedMember
from photoshop.api import AnchorPosition

# Local
import src.text_layers as text_classes
from src import CFG
from src.enums.layers import LAYERS
from src.enums.mtg import (
    MagicIcons,
    LayoutType,
)
from src.enums.settings import (
    CollectorMode
)
from src.helpers import get_line_count, set_text_size
from src.templates import ClassMod, NormalTemplate
from src.templates.saga import SagaMod
from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextArea,
    FormattedTextField,
    ScaledWidthTextField
)
from src.utils.adobe import ReferenceLayer
# Plugin imports
from utilities import *
from cardinfo import *

# TODO
# Nyx
# Legend Crown
# Battles
# Split Cards, rooms, aftermath and meld
# Flip Cards
# Adventure, Prototype, Mutate, Level Up

# planeswalker dashes are thinner than I'd like, but hyphens are too short
# not sure how to fix that

# historically accurate set symbols?
# boomerification of rules text?
# boomer mdfc text
# old basic land watermarks
# color options
# improve color indicators and saga chapter icons

# Gatherer scraper for printed card text (you can get a multiverse id from scryfall)
# and use it to scrape the printed text from gatherer

class RetroTemplate(NormalTemplate):
    """Old border card frames with modern features"""
    frame_suffix = 'Retro'

    # region    Settings

    # General
    @property
    def cfg_tombstone_setting(self):
        return CFG.get_setting(
            section="GENERAL",
            key="tombstone",
            is_bool=False)

    @property
    def cfg_textbox_size(self):
        return CFG.get_setting(
            section="GENERAL",
            key="textbox_size",
            is_bool=False)

    @property
    def cfg_irregular_textboxes(self):
        return CFG.get_setting(
            section="GENERAL",
            key="use_irregular_textboxes")

    @property
    def cfg_colorless_transparent(self):
        return CFG.get_setting(
            section="GENERAL",
            key="colorless_transparent")

    @property
    def cfg_colored_bevels_on_devoid(self):
        return CFG.get_setting(
            section="GENERAL",
            key="use_colored_bevels_on_devoid")

    @property
    def cfg_transparent_opacity(self):
        return float(CFG.get_setting(
            section="GENERAL",
            key="transparent_opacity",
            is_bool=False))

    @property
    def cfg_floating_frame(self):
        return CFG.get_setting(
            section="GENERAL",
            key="use_floating_frame")

    @property
    def cfg_split_hybrid(self):
        return CFG.get_setting(
            section="GENERAL",
            key="split_hybrid")

    @property
    def cfg_split_all(self):
        return CFG.get_setting(
            section="GENERAL",
            key="split_all")

    @property
    def cfg_dual_textbox_bevels(self):
        return not CFG.get_setting(
            section="GENERAL",
            key="standardize_dual_fade_bevels")

    @property
    def cfg_disable_textbox_bevels(self):
        return CFG.get_setting(
            section="GENERAL",
            key="disable_textbox_bevels")

    # Pinlines

    @property
    def cfg_pinlines_on_multicolored(self):
        return CFG.get_setting(
            section="PINLINES",
            key="multicolored")

    @property
    def cfg_pinlines_on_artifacts(self):
        return CFG.get_setting(
            section="PINLINES",
            key="artifacts")

    @property
    def cfg_pinlines_on_all_cards(self):
        return CFG.get_setting(
            section="PINLINES",
            key="all")

    @property
    def cfg_color_all_pinlines(self):
        return CFG.get_setting(
            section="PINLINES",
            key="color_all")

    @property
    def cfg_max_pinline_colors(self):
        return int(CFG.get_setting(
            section="PINLINES",
            key="max_colors",
            is_bool=False))

    # Lands

    @property
    def cfg_legends_style_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="legends_style_lands")

    @property
    def cfg_gold_textbox_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="gold_textbox_lands")

    @property
    def cfg_gold_textbox_pinline_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="gold_textbox_pinline_lands")

    @property
    def cfg_textbox_bevels_on_gold_lands(self):
        return CFG.get_setting(
            section="LANDS",
            key="textbox_bevels_on_gold_lands")

    # Planeswalker

    @property
    def cfg_verbose_planeswalkers(self):
        return CFG.get_setting(
            section="PLANESWALKER",
            key="verbose")

    # MDFC

    @property
    def cfg_has_mdfc_notch(self):
        return CFG.get_setting(
            section="MDFC",
            key="mdfc_notch")

    # Transform

    @property
    def cfg_has_tf_notch(self):
        return CFG.get_setting(
            section="TF",
            key="notch")

    @property
    def cfg_tf_icon_on_right_side(self):
        return CFG.get_setting(
            section="TF",
            key="icon_side")

    @property
    def cfg_set_symbol_on_back(self):
        return CFG.get_setting(
            section="TF",
            key="set_symbol_on_back")

    # Copied from ClassicTemplate

    @cached_property
    def is_promo_star(self) -> bool:
        return CFG.get_setting(
            section='GENERAL',
            key='add_promo_star')

    # @cached_property
    # def is_extended(self) -> bool:
    #     """bool: Whether to render using Extended Art framing."""
    #     return CFG.get_setting(
    #         section='FRAME',
    #         key='Extended.Art',
    #         default=False)

    @cached_property
    def is_align_collector_left(self) -> bool:
        return CFG.get_setting(
            section='GENERAL',
            key='align_collector_left')

    # endregion

    # region    Layers
    @cached_property
    def pinlines_layer(self) -> LayerSet:
        return psd.getLayerSet("Pinlines")

    @cached_property
    def card_frame_group(self) -> LayerSet:
        return psd.getLayerSet("Card Frame")

    @cached_property
    def art_frames_group(self) -> LayerSet:
        return psd.getLayerSet("Art Frames")

    @cached_property
    def art_pinlines_group(self) -> LayerSet:
        return psd.getLayerSet("Art", self.pinlines_layer)

    @cached_property
    def art_pinlines_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Art Masks", self.pinlines_layer)

    @cached_property
    def art_pinlines_background_group(self) -> LayerSet:
        return psd.getLayerSet("Art Background", self.pinlines_layer)

    @cached_property
    def textbox_pinlines_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox", self.pinlines_layer)

    @cached_property
    def textbox_pinlines_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Masks", self.pinlines_layer)

    @cached_property
    def textbox_pinlines_background_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Background", self.pinlines_layer)

    @cached_property
    def outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Outlines")

    @cached_property
    def art_outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Art Outlines", self.outlines_group)

    @cached_property
    def textbox_outlines_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Outlines", self.outlines_group)

    @cached_property
    def textbox_bevels_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox Bevels", self.card_frame_group)

    @cached_property
    def textbox_bevels_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.textbox_bevels_group)

    @cached_property
    def textbox_group(self) -> LayerSet:
        return psd.getLayerSet("Textbox", self.card_frame_group)

    @cached_property
    def textbox_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.textbox_group)

    @cached_property
    def textbox_effects_group(self) -> LayerSet:
        return psd.getLayerSet("Effects", self.textbox_group)

    @cached_property
    def bevels_group(self) -> LayerSet:
        return psd.getLayerSet("Bevels", self.card_frame_group)

    @cached_property
    def bevels_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.bevels_group)

    @cached_property
    def bevels_light_group(self) -> LayerSet:
        return psd.getLayerSet("Light", self.bevels_group)

    @cached_property
    def bevels_dark_group(self) -> LayerSet:
        return psd.getLayerSet("Dark", self.bevels_group)

    @cached_property
    def frame_texture_group(self) -> LayerSet:
        return psd.getLayerSet("Frame Texture", self.card_frame_group)

    @cached_property
    def frame_masks_group(self) -> LayerSet:
        return psd.getLayerSet("Masks", self.frame_texture_group)

    @cached_property
    def transform_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.TRANSFORM, self.text_group)

    @cached_property
    def mdfc_group(self) -> LayerSet:
        return psd.getLayerSet("MDFC", self.text_group)

    @cached_property
    def mdfc_bottom_group(self) -> LayerSet:
        return psd.getLayerSet("Bottom", self.mdfc_group)

    @cached_property
    def adventure_group(self) -> LayerSet:
        return psd.getLayerSet("Adventure", self.text_group)
    # endregion

    # region    Text Layers
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
    def nickname_shape_layer(self) -> ArtLayer:
        return psd.getLayer("Nickname Box", self.text_group)

    # endregion

    # region    Properties

    @cached_property
    def pt_length(self) -> int:
        return len(f'{self.layout.power}{self.layout.toughness}')

    @cached_property
    def is_leveler(self) -> bool:
        return self.layout.card_class == LayoutType.Leveler

    @cached_property
    def is_prototype(self) -> bool:
        return self.layout.card_class == LayoutType.Prototype

    @cached_property
    def is_adventure(self) -> bool:
        return self.layout.card_class == LayoutType.Adventure

    @cached_property
    def is_mutate(self) -> bool:
        return self.layout.card_class == LayoutType.Mutate

    @cached_property
    def template_suffix(self) -> str:
        """Add Promo if promo star enabled."""
        return 'Promo' if self.is_promo_star else ''

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
        if (self.is_transform or self.is_mdfc) and self.cfg_has_tf_notch:
            return False
        if not self.cfg_irregular_textboxes:
            return False
        if self.has_pinlines:
            return False
        if self.identity_advanced == "G":
            return True
        if self.identity_advanced == "B":
            return True
        return False

    @cached_property
    def identity_advanced(self) -> str:
        if self.is_land:
            return LAYERS.LAND
        if self.is_split_fade:
            return LAYERS.HYBRID
        if self.is_artifact:
            return LAYERS.ARTIFACT
        if self.is_colorless:
            return LAYERS.COLORLESS
        if len(self.identity) > 1:
            return LAYERS.GOLD
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
        if self.is_land:
            if self.cfg_legends_style_lands:
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
    def is_planeswalker(self) -> bool:
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
    def artref_size_from_art_aspect(self) -> str:
        """Currently same as the function above it, but may be changed"""
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
    def textbox_size(self) -> str:
        if self.is_saga:
            return "Saga"
        if self.is_class:
            return "Class"
        # Adventure templating is only supported on normal textbox size
        if self.is_adventure:
            return "Normal"
        if self.cfg_textbox_size == "Automatic":
            return get_bigger_textbox_size(
                self.textbox_size_from_text,
                self.textbox_size_from_art_aspect)
        return self.cfg_textbox_size

    @cached_property
    def has_different_adventure_color(self) -> bool:
        colors = self.layout.adventure_colors
        # Hybrid adventure cards use the land coloration, so we convert back to hybrid
        if colors == LAYERS.LAND: colors = LAYERS.HYBRID

        return colors != self.identity_advanced

    @cached_property
    def dual_fade_order(self) -> tuple[str, str, str, str] | None:
        """Returned values are: top mask, bottom mask, top layer identity, bottom layer identity"""
        return fade_mappings.get(self.identity)

    @cached_property
    def adventure_mask_info(self) -> tuple[str, str, str, str]:
        left, right = self.layout.adventure_colors, self.identity_advanced
        top, bottom = sort_frame_textures([left, right])
        if left == top:
            # Use a mask to cut out part of the top layer to be used for the adventure frame
            return "", top, " Inverted", bottom
        else:
            # Use a mask to remove the selected area, so the bottom layer shows through for the adventure frame
            return " Inverted", top, "", bottom

    @cached_property
    def pinline_colors(self) -> dict:
        if self.is_land:
            if len(self.identity) == 2:
                return dual_land_color_map
            return land_color_map
        return nonland_color_map

    @cached_property
    def textbox_bevel_thickness(self) -> Optional[str]:
        if self.has_pinlines:
            return "Land"
        thickness_mappings = {
            "W": "Small",
            "U": "Large",
            "B": "Small",
            "R": "Large",
            "G": "Medium",
            "Gold": "Large",
            "Hybrid": "Medium",
            "Artifact": "Medium",
            "Colorless": "Medium"
        }
        return thickness_mappings.get(self.identity_advanced)

    #endregion

    # region    Collector Info Methods
    # Copied from ClassicTemplate
    def process_layout_data(self) -> None:
        """Remove rarity letter from collector data."""
        super().process_layout_data()
        self.layout.collector_data = self.layout.collector_data[:-2] if (
                '/' in self.layout.collector_data
        ) else self.layout.collector_data[2:]

    def collector_info(self) -> None:
        """Format and add the collector info at the bottom."""

        # Which collector info mode?
        if CFG.collector_mode in [
            CollectorMode.Default, CollectorMode.Modern
        ] and self.layout.collector_data:
            layers = self.collector_info_authentic()
        elif CFG.collector_mode == CollectorMode.ArtistOnly:
            layers = self.collector_info_artist_only()
        else:
            layers = self.collector_info_basic()

        # Shift collector text
        if self.is_align_collector_left:
            [psd.align_left(n, ref=self.collector_reference.dims) for n in layers]

    # noinspection DuplicatedCode
    def collector_info_basic(self) -> list[ArtLayer]:
        """Called to generate basic collector info."""

        # Get artist and info layers
        artist = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        info = psd.getLayer(LAYERS.SET, self.legal_group)

        # Fill optional promo star
        if self.is_collector_promo:
            psd.replace_text(info, "•", MagicIcons.COLLECTOR_STAR)

        # Apply the collector info
        if self.layout.lang != 'en':
            psd.replace_text(info, 'EN', self.layout.lang.upper())
        psd.replace_text(artist, "Artist", self.layout.artist)
        psd.replace_text(info, 'SET', self.layout.set)
        return [artist, info]

    # noinspection DuplicatedCode
    def collector_info_authentic(self) -> list[ArtLayer]:
        """Classic presents authentic collector info differently."""

        # Hide basic 'Set' layer
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Get artist and info layers, reveal info layer
        artist = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        info = psd.getLayer(LAYERS.COLLECTOR, self.legal_group)
        info.visible = True

        # Fill optional promo star
        if self.is_collector_promo:
            psd.replace_text(info, "•", MagicIcons.COLLECTOR_STAR)

        # Apply the collector info
        psd.replace_text(artist, 'Artist', self.layout.artist)
        psd.replace_text(info, 'SET', self.layout.set)
        psd.replace_text(info, 'NUM', self.layout.collector_data)
        return [artist, info]

    def collector_info_artist_only(self) -> list[ArtLayer]:
        """Called to generate 'Artist Only' collector info."""

        # Collector layers
        artist = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Apply the collector info
        psd.replace_text(artist, "Artist", self.layout.artist)
        return [artist]
    # endregion

    # region    Layout logic
    @cached_property
    def flavor_name(self) -> Optional[str]:
        """Display name for nicknamed cards"""
        return self.layout.card.get('flavor_name')

    @cached_property
    def is_tombstone_scryfall(self) -> bool:
        return bool('tombstone' in self.layout.frame_effects)

    # Equivilent scryfall search:
    # o:"this card is in your graveyard" or o:"return this card from your graveyard" or o:"cast this card from your graveyard" or o:"put this card from your graveyard" or o:"exile this card from your graveyard" or o:"~ is in your graveyard" or o:"return ~ from your graveyard" or o:"cast ~ from your graveyard" or o:"put ~ from your graveyard" or o:"exile ~ from your graveyard" or keyword:disturb or keyword:flashback or keyword:Dredge or keyword:Scavenge or keyword:Embalm or keyword:Eternalize or keyword:Aftermath or keyword:Encore or keyword:Escape or keyword:Jump-start or keyword:Recover or keyword:Retrace or keyword:Unearth
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
    # endregion

    # region    Layer logic
    @cached_property
    def frame_texture(self) -> ArtLayer:
        if self.is_land and self.cfg_legends_style_lands:
            return psd.getLayer("Legends Land", self.frame_texture_group)
        return psd.getLayer(self.identity_advanced, self.frame_texture_group)

    @cached_property
    def frame_mask(self) -> ArtLayer:
        return psd.getLayer(self.textbox_size, self.frame_masks_group)

    @cached_property
    def textbox_texture(self) -> ArtLayer:
        if self.is_land:
            if self.cfg_legends_style_lands:
                return psd.getLayer("Legends", self.textbox_group)
            if self.is_gold_land:
                return psd.getLayer("Land", self.textbox_group)
            return psd.getLayer(self.identity + "L", self.textbox_group)
        return psd.getLayer(self.identity_advanced, self.textbox_group)

    @cached_property
    def textbox_shape(self) -> Optional[ArtLayer]:
        if self.textbox_size == "Textless": return None
        textbox_name = self.textbox_size
        if self.has_irregular_textbox:
            textbox_name = f"{self.identity_advanced} {self.textbox_size}"
        # if self.is_transform and self.is_front:
        #     textbox_name = textbox_name + " TF Front"
        if self.is_adventure:
            textbox_name = "Adventure"
        return psd.getLayer(textbox_name, self.textbox_masks_group)

    @cached_property
    def art_reference(self) -> ReferenceLayer:
        if self.cfg_floating_frame:
            return psd.get_reference_layer("Floating Frame", self.art_frames_group)
        if self.is_transparent:
            return psd.get_reference_layer("Transparent Frame", self.art_frames_group)
        # This intentionally makes the artbox larger than it should be given the textbox,
        # so that the art gets cut off at the bottom instead of at the top
        if self.is_normal:
            bigger_art_size = get_smaller_textbox_size(self.artref_size_from_art_aspect, self.textbox_size)
            return psd.get_reference_layer(bigger_art_size, self.art_frames_group)
        return psd.get_reference_layer(self.textbox_size, self.art_frames_group)

    @cached_property
    def textbox_reference(self) -> ReferenceLayer:
        layer_name = f"Textbox Reference {self.textbox_size}"
        if self.is_mdfc: layer_name += " MDFC"
        return psd.get_reference_layer(layer_name, self.text_group)

    @cached_property
    def collector_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer(LAYERS.COLLECTOR_REFERENCE, self.legal_group)

    @cached_property
    def expansion_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer("Expansion Reference", self.text_group)

    @cached_property
    def art_outlines(self) -> LayerSet:
        return psd.getLayerSet(self.textbox_size, self.art_outlines_group)

    @cached_property
    def textbox_outlines(self) -> Optional[ArtLayer]:
        if self.has_irregular_textbox:
            return None
        if self.textbox_size == "Textless":
            return None
        # if self.is_transform and self.is_front:
        #     return psd.getLayer(self.textbox_size + " TF Front", self.textbox_outlines_layer)
        return psd.getLayer(self.textbox_size, self.textbox_outlines_group)
    # endregion

    # region    Text Functions

    def planeswalker_rules_text(self) -> str:
        rules_text = self.layout.oracle_text
        rules_text = replace_hyphens_regex(rules_text)

        if self.cfg_verbose_planeswalkers:

            if self.layout.name == "The Aetherspark":
                return rules_text

            # The wanderer has no planeswalker type
            if self.layout.name == "The Wanderer" or self.layout.name == "The Eternal Wanderer":
                pw_name = "The Wanderer"
                pw_gender = "fem"
            else:
                pw_name = self.layout.type_line.split()[3]
                pw_gender = planeswalker_genders.get(pw_name)

            # Gendered verb conjugations end with s while non-gendered don't
            s = "s" if pw_gender == "masc" or pw_gender == "fem" else ""

            pronoun = "they"
            if pw_gender == "masc": pronoun = "he"
            if pw_gender == "fem": pronoun = "she"

            rules_text = (
                f"Put {self.layout.loyalty} loyalty (use counters) on {pw_name}. "
                f"Opponents can attack {pw_name} as though {pronoun} were you. "
                f"Any damage {pronoun} suffer{s} depletes that much loyalty. "
                f"If {pw_name} has no loyalty, {pronoun} abandon{s} you.\n"
                f"Once during each of your turns, you may add or spend loyalty "
                f"as indicated for the desired effect —\n"
                f"{rules_text}"
            )
        return rules_text

    def leveler_rules_text(self) -> str:
        """Makes boomerified rules text for level up cards.
        Revisit this function if they ever print more level up cards -
        It has assumptions that may not hold up on new cards
        """
        if self.layout.leveler_match is None:
            print("Error: failed to match leveler rules text")
            return ""

        rules_text: str = self.layout.level_up_text + "\n"

        n1, n2 = self.layout.middle_level.split('-')
        m_pt = self.layout.middle_power_toughness
        a_an = indefinite_article_for_number(m_pt.split("/")[0])
        m_abilities = format_leveler_abilities(self.layout.middle_text)

        if m_abilities is None: rules_text += (
            f"As long as this card has at least {n1} and at most {n2} level counters, "
            f"it's {a_an} {m_pt}.\n")
        else: rules_text += (
            f"As long as this card has at least {n1} and at most {n2} level counters, "
            f"it's {a_an} {m_pt} with {m_abilities}\n")

        n3 = self.layout.bottom_level[:-1] #Removes + after number
        b_pt = self.layout.bottom_power_toughness
        a_an_2 = indefinite_article_for_number(b_pt.split("/")[0])
        b_abilities = format_leveler_abilities(self.layout.bottom_text)

        if b_abilities is None: rules_text += (
            f"As long as this card has at least {n3} level counters, "
            f"it's {a_an_2} {b_pt}.")
        else: rules_text += (
            f"As long as this card has at least {n3} level counters, "
            f"it's {a_an_2} {b_pt} with {b_abilities}")

        return rules_text

    def prototype_rules_text(self):
        a_an = indefinite_article_for_number(self.layout.proto_pt[0])
        color = color_word_map.get(self.layout.proto_color)

        rules_text = (
            f"Prototype — You may cast this spell for {self.layout.proto_mana_cost}. "
            f"If you do, it's {color} and is {a_an} {self.layout.proto_pt}. "
            f"It keeps its abilities and types.\n"
            f"{self.layout.oracle_text}"
        )
        return rules_text

    def mutate_rules_text(self):
        return self.layout.oracle_text_unprocessed

    def add_adventure_rules_text(self):
        left_ref, right_ref = \
            (psd.get_reference_layer("Left Textbox Ref", self.adventure_group),
             psd.get_reference_layer("Right Textbox Ref", self.adventure_group))

        # Adventure Side
        self.text.append(FormattedTextArea(
            layer=psd.getLayer("Rules Text Left", self.adventure_group),
            contents=self.layout.oracle_text_adventure,
            flavor=self.layout.flavor_text_adventure,
            centered=False,
            reference=left_ref,
            divider=None))

        # Normal Side
        self.text.append(FormattedTextArea(
            layer=psd.getLayer("Rules Text Right", self.adventure_group),
            contents=self.layout.oracle_text,
            flavor=self.layout.flavor_text,
            centered=False,
            reference=right_ref,
            divider=None))

    def rules_text_and_pt_layers(self):
        if self.is_creature:
            self.text.append(TextField(
                layer=self.text_layer_pt,
                contents=f'{self.layout.power}/{self.layout.toughness}'))

        elif self.is_planeswalker:
            self.text.append(TextField(
                layer=self.text_layer_pt,
                contents=f'{self.layout.loyalty}'))

        # Make P/T a little smaller if it's two double digits to prevent touching outer card bevel
        # default size is 11.25
        if self.pt_length >= 4:
            set_text_size(psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_group), 10.0)

        if self.is_flipside_creature and self.cfg_has_tf_notch:
            self.text.append(TextField(
                layer=psd.getLayer(LAYERS.POWER_TOUGHNESS, self.transform_group),
                contents=f'{self.layout.other_face_power}/{self.layout.other_face_toughness}'))

        if self.textbox_size == "Textless":
            return
        if self.is_saga or self.is_class:
            return

        if self.is_planeswalker:
            rules_text = self.planeswalker_rules_text()
        elif self.is_leveler:
            rules_text = self.leveler_rules_text()
        elif self.is_prototype:
            rules_text = self.prototype_rules_text()
        elif self.is_mutate:
            rules_text = self.mutate_rules_text()
        else:
            rules_text = self.layout.oracle_text

        if self.is_adventure:
            self.add_adventure_rules_text()
        else:
            self.text.append(FormattedTextArea(
                layer=self.text_layer_rules,
                contents=rules_text,
                flavor=self.layout.flavor_text,
                centered=self.is_centered,
                reference=self.textbox_reference,
                divider=self.divider_layer))

    def add_nickname_text(self):
        self.text.extend([
            ScaledWidthTextField(
                layer=self.text_layer_nickname,
                contents=self.layout.name,
                reference=self.nickname_shape_layer
            ),
            ScaledTextField(
                layer=self.text_layer_name,
                contents=self.flavor_name,
                reference=self.name_reference
            )])

    def add_mdfc_text(self):
        """Adds text at the bottom of mdfc cards indicating the name and cost
        of the card on the other face"""
        self.text.extend([
            FormattedTextField(
                layer=psd.getLayer("Right", self.mdfc_bottom_group),
                contents=self.layout.other_face_right),
            ScaledTextField(
                layer=psd.getLayer("Left", self.mdfc_bottom_group),
                contents=self.layout.other_face.get("name"),
                reference=psd.getLayer("Right", self.mdfc_bottom_group))])

        if self.has_pinlines:
            psd.getLayer("Right", self.mdfc_bottom_group).translate(0, -6)
            psd.getLayer("Left", self.mdfc_bottom_group).translate(0, -6)

    def adjust_mana_cost(self):
        """Adjusts the size and position of the mana cost depending
        on if hybrid symbols are present and whether pinlines are enabled"""
        if 'P' in self.layout.mana_cost or '/' in self.layout.mana_cost:
            if self.has_pinlines:
                set_text_size(self.text_layer_mana, 9.0)
                self.text_layer_mana.translate(0, -15)
            else:
                self.text_layer_mana.translate(0, -12)
        elif self.has_pinlines:
            self.text_layer_mana.translate(0,-3)

    def adventure_basic_text_layers(self) -> None:
        self.text.append(FormattedTextField(
            layer=psd.getLayer(LAYERS.MANA_COST, self.adventure_group),
            contents=self.layout.mana_adventure))

        self.text.append(ScaledTextField(
            layer=psd.getLayer(LAYERS.TYPE_LINE, self.adventure_group),
            contents=self.layout.type_line_adventure,
            reference=psd.getLayer("Divider", self.adventure_group)))

        self.text.append(ScaledTextField(
            layer=psd.getLayer(LAYERS.NAME, self.adventure_group),
            contents=self.layout.name_adventure,
            reference=psd.getLayer(LAYERS.MANA_COST, self.adventure_group)))

        # Make mana cost smaller if it contains hybrid mana
        if 'P' in self.layout.mana_adventure or '/' in self.layout.mana_adventure:
            set_text_size(psd.getLayer(LAYERS.MANA_COST, self.adventure_group), 7.0)

    def basic_text_layers(self) -> None:
        self.text.append(FormattedTextField(
            layer=self.text_layer_mana,
            contents=self.layout.mana_cost))

        self.adjust_mana_cost()

        if self.has_textbox:
            if self.is_mdfc: self.add_mdfc_text()

            self.text.append(ScaledTextField(
                layer=self.text_layer_type,
                contents=self.layout.type_line,
                reference=self.type_reference))

        if self.has_nickname:
            self.add_nickname_text()
        else:
            self.text.append(ScaledTextField(
                layer=self.text_layer_name,
                contents=self.layout.name,
                reference=self.name_reference))

        if self.is_adventure: self.adventure_basic_text_layers()
    # endregion

    # region    Layer adding functions
    def load_expansion_symbol(self) -> None:
        """Import and loads the expansion symbol, except on textless cards"""
        if not self.has_textbox:
            return
        super().load_expansion_symbol()

    @cached_property
    def textbox_pinlines_colors(self) -> Union[list[int], list[dict]]:
        if self.is_land:
            if (not self.is_basic_land and self.cfg_gold_textbox_lands) or (len(self.identity) > self.cfg_max_pinline_colors):
                return psd.get_pinline_gradient("Land", color_map=self.pinline_colors)
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) <= self.cfg_max_pinline_colors else self.pinlines,
            color_map=self.pinline_colors)

    @cached_property
    def non_textbox_pinlines_colors(self) -> Union[list[int], list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        if not self.cfg_color_all_pinlines:
            if self.is_land and not self.is_basic_land:
                return psd.get_pinline_gradient("Land", color_map=self.pinline_colors)
            if len(self.identity) > 1:
                if self.is_artifact:
                    return psd.get_pinline_gradient("Artifact", color_map=self.pinline_colors)
                if self.is_colorless:
                    return psd.get_pinline_gradient("Colorless", color_map=self.pinline_colors)
                return psd.get_pinline_gradient("Gold", color_map=self.pinline_colors)
        return self.textbox_pinlines_colors

    def add_pinlines(self):
        enable(self.pinlines_layer)
        enable(self.textbox_size, self.art_pinlines_background_group)

        if self.cfg_legends_style_lands and self.is_land:
            enable(f"Legends {self.textbox_size}", psd.getLayerSet("Legends", self.pinlines_layer))

        self.generate_layer(group=psd.getLayerSet("Outer", self.pinlines_layer),
                            colors=self.non_textbox_pinlines_colors)

        self.generate_layer(group=psd.getLayerSet("Art", self.pinlines_layer), colors=self.non_textbox_pinlines_colors)
        art_mask = psd.getLayer(self.textbox_size, self.art_pinlines_masks_group)
        psd.copy_vector_mask(art_mask, self.art_pinlines_group)

        if not self.has_textbox: return

        enable(self.textbox_size, self.textbox_pinlines_background_group)
        self.generate_layer(group=psd.getLayerSet("Textbox", self.pinlines_layer), colors=self.textbox_pinlines_colors)
        textbox_mask = psd.getLayer(self.textbox_size, self.textbox_pinlines_masks_group)
        psd.copy_vector_mask(textbox_mask, self.textbox_pinlines_group)

    def add_outer_and_art_bevels(self):
        light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_group)
        dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_group)

        for (mask, layer) in [
            (light_mask, self.bevels_light_group),
            (dark_mask, self.bevels_dark_group)
        ]:
            psd.copy_vector_mask(mask, layer)
            enable(self.identity_advanced, layer)

    def add_textbox_bevels(self, identity=None):
        if not self.has_textbox_bevels: return

        if identity is None:
            identity = self.identity_advanced

        tr, bl, textbox_bevel = self.copy_textbox_bevel_masks(identity)

        # Enables lines which exist on white, blue, and red textbox bevels
        # They don't look good on hybrid cards, and I haven't implemented
        # The right size and placements for cards with pinlines
        if self.is_split_fade: return
        if self.has_pinlines: return
        if identity == "W" or identity == "U" or identity == "R":
            enable(self.textbox_size, textbox_bevel)

    def add_land_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        bevel_color = self.identity
        if self.is_gold_land:
            bevel_color = "Gold"

        tr, bl, _ = self.copy_textbox_bevel_masks("Land")

        enable(bevel_color, tr)
        enable(bevel_color, bl)

    def copy_textbox_bevel_masks(self, identity) -> tuple[LayerSet, LayerSet, LayerSet]:
        sized_bevel_masks = psd.getLayerSet(self.textbox_size, self.textbox_bevels_masks_group)
        textbox_bevel = psd.getLayerSet(identity, self.textbox_bevels_group)

        enable(textbox_bevel)

        (top_right, bottom_left) = \
            (psd.getLayerSet("TR", textbox_bevel), psd.getLayerSet("BL", textbox_bevel))

        top_right_mask = psd.getLayer(self.textbox_bevel_thickness + " TR", sized_bevel_masks)
        bottom_left_mask = psd.getLayer(self.textbox_bevel_thickness + " BL", sized_bevel_masks)

        psd.copy_vector_mask(top_right_mask, top_right)
        psd.copy_vector_mask(bottom_left_mask, bottom_left)

        return top_right, bottom_left, textbox_bevel

    def dual_fade_frame_texture(self):
        (top_mask_name, _, top_layer, bottom_layer) = self.dual_fade_order

        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        top_frame_layer = psd.getLayer(top_layer, self.frame_texture_group)
        bottom_frame_layer = psd.getLayer(bottom_layer, self.frame_texture_group)

        psd.copy_layer_mask(top_mask, top_frame_layer)

        enable(top_frame_layer)
        enable(bottom_frame_layer)

    def dual_fade_nonland_textbox(self, colors_override = None):
        color_source = self.dual_fade_order if colors_override is None else colors_override
        (top_mask_name, _, top_layer, bottom_layer) = color_source

        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        top_textbox_layer = psd.getLayer(top_layer, self.textbox_group)
        bottom_textbox_layer = psd.getLayer(bottom_layer, self.textbox_group)

        psd.copy_layer_mask(top_mask, top_textbox_layer)

        enable(top_textbox_layer)
        enable(bottom_textbox_layer)

    def add_dual_fade_land_textbox(self):
        (top_mask_name, _, top_layer, bottom_layer) = self.dual_fade_order

        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        top_textbox_layer = psd.getLayer(f"{top_layer}L Dual", self.textbox_group)
        bottom_textbox_layer = psd.getLayer(f"{bottom_layer}L Dual", self.textbox_group)

        psd.copy_layer_mask(top_mask, top_textbox_layer)

        enable(top_textbox_layer)
        enable(bottom_textbox_layer)

    def add_dual_fade_land_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_order

        top_mask = psd.getLayer(top_mask_name, self.mask_group)
        bottom_mask = psd.getLayer(bottom_mask_name, self.mask_group)

        top_right, bottom_left, _ = self.copy_textbox_bevel_masks("Land")

        for mask_layer, layer, group in [
            (top_mask, top_layer, top_right),
            (top_mask, top_layer, bottom_left),
            (bottom_mask, bottom_layer, top_right),
            (bottom_mask, bottom_layer, bottom_left)
        ]:
            enable(layer, group)
            psd.copy_layer_mask(mask_layer, psd.getLayer(layer, group))

    def dual_fade_textbox_bevels(self):
        if not self.has_textbox_bevels: return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_order

        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)

        for mask_layer, layer in [
            (top_mask, top_layer),
            (bottom_mask, bottom_layer),
        ]:
            self.add_textbox_bevels(identity=layer)
            psd.copy_layer_mask(mask_layer, psd.getLayerSet(layer, self.textbox_bevels_group))

    def dual_fade_bevels(self):

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = self.dual_fade_order

        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)
        light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_group)
        dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_group)

        psd.copy_vector_mask(light_mask, self.bevels_light_group)
        psd.copy_vector_mask(dark_mask, self.bevels_dark_group)

        for (mask, layer, group) in [
            (top_mask, top_layer, self.bevels_light_group),
            (top_mask, top_layer, self.bevels_dark_group),
            (bottom_mask, bottom_layer, self.bevels_light_group),
            (bottom_mask, bottom_layer, self.bevels_dark_group),
        ]:
            enable(layer, group)
            psd.copy_layer_mask(mask, psd.getLayer(layer, group))

    def position_type_line(self):
        """Positions the type line elements vertically based on the textbox size"""
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
            if self.expansion_symbol_layer:
                self.expansion_symbol_layer.resize(90, 90, AnchorPosition.MiddleCenter)
            offset += 4

        self.text_layer_type.translate(0, offset)
        if self.expansion_symbol_layer:
            self.expansion_symbol_layer.translate(0, offset)
        if self.color_indicator_layer:
            self.color_indicator_layer.translate(0, offset)

        if self.is_type_shifted:
            self.text_layer_type.translate(100, 0)

    def add_tombstone(self):
        # Enables smaller tombstone icon which sits below the transform icon
        if self.is_transform and self.is_front:
            icon_name = "Tombstone Small"
        else:
            icon_name = "Tombstone"

        enable(icon_name, self.text_group)

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
                    (top, _, top_color, bottom_color) = self.dual_fade_order
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

    def add_land_textbox(self):
        if self.is_dual_land:
            self.add_dual_fade_land_textbox()
            self.add_dual_fade_land_textbox_bevels()
        else:
            enable(self.textbox_texture)
            self.add_land_textbox_bevels()

    def add_nonland_frame_texture(self):
        if self.is_split_fade:
            self.dual_fade_frame_texture()
            self.dual_fade_bevels()
        elif self.is_adventure and self.has_different_adventure_color:
            mask, layer, _, _ = self.adventure_mask_info

            psd.copy_vector_mask(
                psd.getLayer(f"Adventure Frame{mask}", self.mask_group),
                psd.getLayer(layer, self.frame_texture_group))

            enable(self.layout.adventure_colors, self.frame_texture_group)
            enable(self.identity_advanced, self.frame_texture_group)
        else:
            enable(self.frame_texture)
            self.add_outer_and_art_bevels()

    def add_nonland_textbox(self):
        if self.is_split_fade:
            self.dual_fade_nonland_textbox()
            if self.cfg_dual_textbox_bevels:
                self.dual_fade_textbox_bevels()
            else:
                self.add_textbox_bevels()

        elif self.is_adventure and self.has_different_adventure_color:

            mask, top_layer, _, _ = self.adventure_mask_info

            psd.copy_vector_mask(
                psd.getLayer(f"Adventure Textbox{mask}", self.mask_group),
                psd.getLayer(top_layer, self.textbox_group))

            enable(self.layout.adventure_colors, self.textbox_group)
            enable(self.identity_advanced, self.textbox_group)

            #self.dual_fade_nonland_textbox(colors_override=self.dual_fade_order_adventure)
            #self.add_textbox_bevels()
        else:
            enable(self.textbox_texture)
            self.add_textbox_bevels()

    def apply_textbox_shape(self):
        if not (self.identity_advanced == "B" and self.is_normal and self.has_irregular_textbox):
            # Enables vector mask for vectorized textboxes (including green)
            enable(self.textbox_shape)
        else:
            # Enables rasterized textbox for black textboxes
            enable(f"B {self.textbox_size}", self.textbox_group)

    def apply_devoid(self):
        color = self.identity if len(self.identity) == 1 else "Gold"
        color_layer = psd.getLayer(color, self.frame_texture_group)
        enable(color_layer.visible)
        psd.copy_layer_mask(psd.getLayer("Devoid Color", self.mask_group), color_layer)

        if self.is_transparent:
            psd.copy_layer_mask(psd.getLayer("Devoid", self.mask_group), self.card_frame_group)

        if self.cfg_colored_bevels_on_devoid:
            enable(color, self.bevels_light_group)
            enable(color, self.bevels_dark_group)

            psd.copy_layer_mask(
                psd.getLayer("Devoid Color", self.mask_group),
                psd.getLayer(color, self.bevels_light_group))

            psd.copy_layer_mask(
                psd.getLayer("Devoid Color", self.mask_group),
                psd.getLayer(color, self.bevels_dark_group))

    def add_outlines(self):
        enable(self.art_outlines)
        if self.textbox_outlines is not None:
            enable(self.textbox_outlines)

    def add_nickname_plate(self):
        enable("Nickname", self.text_group)
        enable("Nickname Box", self.text_group)

        masks = psd.getLayerSet("Masks", self.frame_texture_group)
        enable("Nickname", masks)

        nickname_mask = psd.getLayer("Nickname", self.mask_group)
        psd.copy_vector_mask(nickname_mask, self.outlines_group)
        psd.copy_vector_mask(nickname_mask, self.bevels_group)

    def add_textbox_decorations(self):
        """Adds the color indicator and fx to textboxes when appropriate"""
        if self.is_type_shifted and self.color_indicator_layer:
            enable(self.color_indicator_layer)

        # Applies dropshadow effect to green textbox
        if self.identity_advanced == "G":
            psd.copy_layer_fx(psd.getLayer("G", self.textbox_effects_group), self.textbox_group)

    def add_textbox(self):
        if self.is_land: self.add_land_textbox()
        if not self.is_land: self.add_nonland_textbox()
        self.apply_textbox_shape()
        self.add_textbox_decorations()

    def enable_frame_layers(self):
        enable(self.frame_mask)
        self.add_outlines()

        if self.is_land: self.add_land_frame_texture()
        if not self.is_land: self.add_nonland_frame_texture()

        if self.cfg_floating_frame: disable(self.border_group)
        if self.is_devoid: self.apply_devoid()
        if self.has_textbox:
            self.add_textbox()
            self.position_type_line()
        # if not self.has_textbox: disable(self.expansion_symbol_layer)
        if self.has_pinlines: self.add_pinlines()
        if self.has_nickname: self.add_nickname_plate()
        if self.is_promo_star: enable("Promo Star", self.text_group)
        if self.has_tombstone: self.add_tombstone()
        if self.is_adventure: enable(self.adventure_group)
    # endregion

class RetroAdventureTemplate(RetroTemplate):
    ...
class RetroPrototypeTemplate(RetroTemplate):
    ...
class RetroMutateTemplate(RetroTemplate):
    ...
class RetroLevelerTemplate(RetroTemplate):
    ...

class RetroPWTemplate(RetroTemplate):
    """Template for Planeswalkers"""

    @cached_property
    def is_planeswalker(self) -> bool:
        return True

class RetroTFTemplate(RetroTemplate):
    """Template for TransForming cards"""

    def load_expansion_symbol(self) -> None:
        """Import and loads the expansion symbol, except on textless cards"""
        if not self.has_textbox:
            return
        if self.is_transform and not self.is_front and not self.cfg_set_symbol_on_back:
            return
        super().load_expansion_symbol()

    def has_tf_notch(self) -> bool:
        if self.has_textbox and self.is_front and self.cfg_has_tf_notch:
            return True
        return False

    def add_transform_icon(self):
        """Adds transform icons to the top left and right of cards"""
        if self.is_front:
            if self.has_tombstone: # Cards with tombstones use a smaller transform icon which is placed above it
                icon_name = "Front Small"
            else:
                icon_name = "Front"
        else:
            icon_name = "Back"
            if self.cfg_tf_icon_on_right_side:
                self.transform_group.translate(1675, 0)

        enable(icon_name, self.transform_group)

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Sagas inherit from TFTemplate since they can be transforming cards
        # but not all of them are, so we have the following guard
        if not self.is_transform: return

        self.add_transform_icon()
        if self.has_tf_notch():
            self.add_textbox_notch()
            if self.is_flipside_creature:
                enable(LAYERS.POWER_TOUGHNESS, self.transform_group)

class RetroMDFCTemplate(RetroTemplate):
    """Template for Modal Double Faced cards"""

    def has_mdfc_notch(self) -> bool:
        """MDFCs have placards in the bottom left on both faces which show the cost and types
        of the other face. I use a notch on the bottom left of the text box and a dividing line
        to accomplish this. Since I have more space to work with, I decided to put the card name
        instead of the type, since it fills the space better and looks better, in my opinion
        """
        if self.has_textbox and self.cfg_has_mdfc_notch:
            return True
        return False

    def add_mdfc_icon(self):
        """Adds modal double faced icons to the top left of cards"""
        enable(self.mdfc_group)
        if self.is_front:
            enable("Front", self.mdfc_group)
        else:
            enable("Back", self.mdfc_group)

    def adjust_mdfc_text_position(self):
        """Move the mdfc backside card info text up a bit on cards with larger textbox bevels"""
        if self.textbox_bevel_thickness == "Land" or self.textbox_bevel_thickness == "Large":
            self.mdfc_bottom_group.translate(0, -5)

    def enable_frame_layers(self):
        super().enable_frame_layers()
        self.add_mdfc_icon()
        self.adjust_mdfc_text_position()
        if self.has_mdfc_notch():
            self.add_textbox_notch()

class RetroPWTFTemplate(RetroTFTemplate):
    """Transforming Planeswalkers"""

class RetroPWMDFCTemplate(RetroMDFCTemplate):
    """Modal Double Faced Planeswalkers"""

class RetroSagaTemplate(RetroTFTemplate, SagaMod):

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

    # noinspection DuplicatedCode
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