"""
* Plugin: [Gavin]
"""

from enum import StrEnum
from functools import cached_property
from typing import override

from cardinfo import *
from photoshop.api.enumerations import AnchorPosition
from PIL import Image
from utilities import *

import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.enums.mtg import MagicIcons
from src.enums.settings import CollectorMode
from src.helpers import get_line_count, set_text_size
from src.layouts import (
    AdventureLayout,
    BattleLayout,
    LevelerLayout,
    MutateLayout,
    PlaneswalkerLayout,
    PlaneswalkerMDFCLayout,
    PlaneswalkerTransformLayout,
    PrototypeLayout,
    SagaLayout,
)
from src.schema.colors import ColorObject, GradientConfig
from src.templates import ClassMod, NormalTemplate
from src.templates.saga import SagaMod
from src.text_layers import (
    FormattedTextArea,
    FormattedTextField,
    ScaledTextField,
    ScaledWidthTextField,
    TextField,
)
from src.utils.adobe import ReferenceLayer
from src.utils.scryfall import ScryfallCard


class TombstoneOption(StrEnum):
    AUTOMATIC = "Automatic"
    SCRYFALL = "Scryfall"
    NONE = "None"


class TextboxSizeOption(StrEnum):
    AUTOMATIC = "Automatic"
    NORMAL = "Normal"
    MEDIUM = "Medium"
    SMALL = "Small"
    TEXTLESS = "Textless"


# TODO
# Nyx
# Legend Crown
# Battles
# Split Cards, rooms, aftermath and meld
# Flip Cards

# planeswalker dashes are thinner than I'd like, but hyphens are too short

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

    frame_suffix = "Retro"

    # region    Settings

    # General
    @cached_property
    def cfg_tombstone_setting(self) -> TombstoneOption:
        return self.config.get_option(
            section="GENERAL",
            key="tombstone",
            enum_class=TombstoneOption,
            default=TombstoneOption.AUTOMATIC,
        )

    @property
    def cfg_textbox_size(self) -> TextboxSizeOption:
        return self.config.get_option(
            section="GENERAL",
            key="textbox_size",
            enum_class=TextboxSizeOption,
            default=TextboxSizeOption.AUTOMATIC,
        )

    @property
    def cfg_irregular_textboxes(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="use_irregular_textboxes", default=True
        )

    @property
    def cfg_colorless_transparent(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="colorless_transparent", default=True
        )

    @property
    def cfg_colored_bevels_on_devoid(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="use_colored_bevels_on_devoid", default=True
        )

    @property
    def cfg_transparent_opacity(self) -> float:
        return float(
            self.config.get_float_setting(
                section="GENERAL", key="transparent_opacity", default=45
            )
        )

    @property
    def cfg_floating_frame(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="use_floating_frame", default=False
        )

    @property
    def cfg_split_hybrid(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="split_hybrid", default=True
        )

    @property
    def cfg_split_all(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="split_all", default=False
        )

    @property
    def cfg_dual_textbox_bevels(self) -> bool:
        return not self.config.get_bool_setting(
            section="GENERAL", key="standardize_dual_fade_bevels", default=True
        )

    @property
    def cfg_disable_textbox_bevels(self) -> bool:
        return self.config.get_bool_setting(
            section="GENERAL", key="disable_textbox_bevels", default=False
        )

    # Pinlines

    @property
    def cfg_pinlines_on_multicolored(self) -> bool:
        return self.config.get_bool_setting(
            section="PINLINES", key="multicolored", default=False
        )

    @property
    def cfg_pinlines_on_artifacts(self) -> bool:
        return self.config.get_bool_setting(
            section="PINLINES", key="artifacts", default=False
        )

    @property
    def cfg_pinlines_on_all_cards(self) -> bool:
        return self.config.get_bool_setting(
            section="PINLINES", key="all", default=False
        )

    @property
    def cfg_color_all_pinlines(self) -> bool:
        return self.config.get_bool_setting(
            section="PINLINES", key="color_all", default=False
        )

    @property
    def cfg_max_pinline_colors(self) -> int:
        return self.config.get_int_setting(
            section="PINLINES", key="max_colors", default=2
        )

    # Lands

    @property
    def cfg_legends_style_lands(self) -> bool:
        return self.config.get_bool_setting(
            section="LANDS", key="legends_style_lands", default=False
        )

    @property
    def cfg_gold_textbox_lands(self) -> bool:
        return self.config.get_bool_setting(
            section="LANDS", key="gold_textbox_lands", default=False
        )

    @property
    def cfg_gold_textbox_pinline_lands(self) -> bool:
        return self.config.get_bool_setting(
            section="LANDS", key="gold_textbox_pinline_lands", default=False
        )

    @property
    def cfg_textbox_bevels_on_gold_lands(self) -> bool:
        return self.config.get_bool_setting(
            section="LANDS", key="textbox_bevels_on_gold_lands", default=True
        )

    # Planeswalker

    @property
    def cfg_verbose_planeswalkers(self) -> bool:
        return self.config.get_bool_setting(
            section="PLANESWALKER", key="verbose", default=False
        )

    # MDFC

    @property
    def cfg_has_mdfc_notch(self) -> bool:
        return self.config.get_bool_setting(
            section="MDFC", key="mdfc_notch", default=True
        )

    # Transform

    @property
    def cfg_has_tf_notch(self) -> bool:
        return self.config.get_bool_setting(section="TF", key="notch", default=False)

    @property
    def cfg_tf_icon_on_right_side(self) -> bool:
        return self.config.get_bool_setting(section="TF", key="icon_side", default=True)

    @property
    def cfg_set_symbol_on_back(self) -> bool:
        return self.config.get_bool_setting(
            section="TF", key="set_symbol_on_back", default=False
        )

    # Copied from ClassicTemplate

    @cached_property
    def is_promo_star(self) -> bool:
        # TODO not specified in config files
        return self.config.get_bool_setting(
            section="GENERAL", key="add_promo_star", default=False
        )

    # @cached_property
    # def is_extended(self) -> bool:
    #     """bool: Whether to render using Extended Art framing."""
    #     return self.config.get_setting(
    #         section='FRAME',
    #         key='Extended.Art',
    #         default=False)

    @cached_property
    def is_align_collector_left(self) -> bool:
        # TODO not specified in config files
        return self.config.get_bool_setting(
            section="GENERAL", key="align_collector_left", default=False
        )

    # endregion

    # region    Layers
    @cached_property
    def pinlines_group(self) -> LayerSet | None:
        return psd.getLayerSet("Pinlines")

    @cached_property
    def card_frame_group(self) -> LayerSet | None:
        return psd.getLayerSet("Card Frame")

    @cached_property
    def art_frames_group(self) -> LayerSet | None:
        return psd.getLayerSet("Art Frames")

    @cached_property
    def art_pinlines_group(self) -> LayerSet | None:
        return psd.getLayerSet("Art", self.pinlines_group)

    @cached_property
    def art_pinlines_masks_group(self) -> LayerSet | None:
        return psd.getLayerSet("Art Masks", self.pinlines_group)

    @cached_property
    def art_pinlines_background_group(self) -> LayerSet | None:
        return psd.getLayerSet("Art Background", self.pinlines_group)

    @cached_property
    def textbox_pinlines_group(self) -> LayerSet | None:
        return psd.getLayerSet("Textbox", self.pinlines_group)

    @cached_property
    def textbox_pinlines_masks_group(self) -> LayerSet | None:
        return psd.getLayerSet("Textbox Masks", self.pinlines_group)

    @cached_property
    def textbox_pinlines_background_group(self) -> LayerSet | None:
        return psd.getLayerSet("Textbox Background", self.pinlines_group)

    @cached_property
    def outlines_group(self) -> LayerSet | None:
        return psd.getLayerSet("Outlines")

    @cached_property
    def art_outlines_group(self) -> LayerSet | None:
        return psd.getLayerSet("Art Outlines", self.outlines_group)

    @cached_property
    def textbox_outlines_group(self) -> LayerSet | None:
        return psd.getLayerSet("Textbox Outlines", self.outlines_group)

    @cached_property
    def textbox_bevels_group(self) -> LayerSet | None:
        return psd.getLayerSet("Textbox Bevels", self.card_frame_group)

    @cached_property
    def textbox_bevels_masks_group(self) -> LayerSet | None:
        return psd.getLayerSet("Masks", self.textbox_bevels_group)

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        return psd.getLayerSet("Textbox", self.card_frame_group)

    @cached_property
    def textbox_masks_group(self) -> LayerSet | None:
        return psd.getLayerSet("Masks", self.textbox_group)

    @cached_property
    def textbox_effects_group(self) -> LayerSet | None:
        return psd.getLayerSet("Effects", self.textbox_group)

    @cached_property
    def bevels_group(self) -> LayerSet | None:
        return psd.getLayerSet("Bevels", self.card_frame_group)

    @cached_property
    def bevels_masks_group(self) -> LayerSet | None:
        return psd.getLayerSet("Masks", self.bevels_group)

    @cached_property
    def bevels_light_group(self) -> LayerSet | None:
        return psd.getLayerSet("Light", self.bevels_group)

    @cached_property
    def bevels_dark_group(self) -> LayerSet | None:
        return psd.getLayerSet("Dark", self.bevels_group)

    @cached_property
    def frame_texture_group(self) -> LayerSet | None:
        return psd.getLayerSet("Frame Texture", self.card_frame_group)

    @cached_property
    def frame_masks_group(self) -> LayerSet | None:
        return psd.getLayerSet("Masks", self.frame_texture_group)

    @cached_property
    def transform_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.TRANSFORM, self.text_group)

    @cached_property
    def mdfc_group(self) -> LayerSet | None:
        return psd.getLayerSet("MDFC", self.text_group)

    @cached_property
    def mdfc_bottom_group(self) -> LayerSet | None:
        return psd.getLayerSet("Bottom", self.mdfc_group)

    @cached_property
    def adventure_group(self) -> LayerSet | None:
        return psd.getLayerSet("Adventure", self.text_group)

    # endregion

    # region    Text Layers

    @cached_property
    def text_layer_collector_first(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.COLLECTOR, self.legal_group)

    @cached_property
    def text_layer_type(self) -> ArtLayer | None:
        if not self.has_textbox:
            return None
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_nickname(self) -> ArtLayer | None:
        return psd.getLayer("Nickname", self.text_group)

    @cached_property
    def text_layer_rules(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @cached_property
    def nickname_shape_layer(self) -> ArtLayer | None:
        return psd.getLayer("Nickname Box", self.text_group)

    # endregion

    # region    Properties

    @cached_property
    def pt_length(self) -> int:
        return len(f"{self.layout.power}{self.layout.toughness}")

    @cached_property
    def is_leveler(self) -> bool:
        return isinstance(self.layout, LevelerLayout)

    @cached_property
    def is_prototype(self) -> bool:
        return isinstance(self.layout, PrototypeLayout)

    @cached_property
    def is_adventure(self) -> bool:
        return isinstance(self.layout, AdventureLayout)

    @cached_property
    def is_mutate(self) -> bool:
        return isinstance(self.layout, MutateLayout)

    @cached_property
    def is_battle(self):
        return isinstance(self.layout, BattleLayout)

    @cached_property
    def template_suffix(self) -> str:
        """Add Promo if promo star enabled."""
        return "Promo" if self.is_promo_star else ""

    @cached_property
    def has_nickname(self) -> bool:
        """Return True if this a nickname render."""
        return self.flavor_name is not None

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        # if self.cfg_floating_frame:
        #     return True
        return False

    @cached_property
    def has_irregular_textbox(self) -> bool:
        if self.is_saga or self.is_class:
            return False
        # if self.is_adventure:
        #     return False
        if (self.is_transform or self.is_mdfc) and self.cfg_has_tf_notch:
            return False
        if not self.cfg_irregular_textboxes:
            return False
        if self.has_pinlines:
            return False
        if self.identity_advanced == "G":
            return True
        return self.identity_advanced == "B"

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
        return self.cfg_pinlines_on_all_cards

    @cached_property
    def has_textbox(self) -> bool:
        return self.textbox_size != "Textless"

    @cached_property
    def has_textbox_bevels(self) -> bool:
        if not self.has_textbox:
            return False
        if self.cfg_disable_textbox_bevels:
            return False
        if self.has_irregular_textbox:
            return False
        # if self.is_adventure:
        #     return False
        if self.is_land:
            if self.cfg_legends_style_lands:
                return False
            if self.is_gold_land:
                return self.cfg_textbox_bevels_on_gold_lands

        return True

    @cached_property
    def is_gold_land(self) -> bool:
        """Whether the textbox of the card is the gold land textbox"""
        if not self.is_land:
            return False
        if self.is_basic_land:
            return False
        if self.cfg_gold_textbox_lands:
            return True
        return len(self.identity) < 1 or len(self.identity) > 2

    @cached_property
    def is_dual_land(self) -> bool:
        if not self.is_land:
            return False
        if self.is_gold_land:
            return False
        if self.cfg_legends_style_lands:
            return False
        return len(self.identity) == 2

    @cached_property
    def is_split_fade(self) -> bool:
        if len(self.identity) != 2:
            return False
        if self.cfg_split_all:
            return True
        return self.is_hybrid and self.cfg_split_hybrid

    @cached_property
    def is_transparent(self) -> bool:
        return self.is_colorless and self.cfg_colorless_transparent

    @cached_property
    def is_devoid(self) -> bool:
        # For some reason true colorless cards have "Colorless" as their color identity while
        # artifacts have an empty string.
        if self.identity == "Colorless":
            return False
        return self.is_colorless and len(self.identity) > 0

    @cached_property
    def is_saga(self) -> bool:
        return False

    @cached_property
    def is_class(self) -> bool:
        return False

    @cached_property
    def is_planeswalker(self) -> bool:
        return isinstance(
            self.layout,
            (
                PlaneswalkerLayout,
                PlaneswalkerTransformLayout,
                PlaneswalkerMDFCLayout,
            ),
        )

    @cached_property
    def is_normal(self) -> bool:
        if self.is_saga:
            return False
        return not self.is_class

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
        if test_layer := self.text_layer_rules:
            test_text = self.layout.oracle_text
            if self.layout.flavor_text:
                test_text += f"\r{self.layout.flavor_text}"
            test_layer.textItem.contents = test_text.replace("\n", "\r")
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
        # if self.is_adventure:
        #     return "Normal"
        if self.cfg_textbox_size == "Automatic":
            print("Using automatic textbox size")
            return get_bigger_textbox_size(
                self.textbox_size_from_text, self.textbox_size_from_art_aspect
            )
        return self.cfg_textbox_size

    @cached_property
    def has_different_adventure_color(self) -> bool:
        if isinstance(self.layout, AdventureLayout):
            colors = self.layout.adventure_colors
            # Hybrid adventure cards use the land coloration, so we convert back to hybrid
            if colors == LAYERS.LAND:
                colors = LAYERS.HYBRID

            return colors != self.identity_advanced
        return False

    @cached_property
    def dual_fade_order(self) -> tuple[str, str, str, str] | None:
        """Returned values are: top mask, bottom mask, top layer identity, bottom layer identity"""
        return fade_mappings.get(self.identity)

    @cached_property
    def adventure_mask_info(self) -> tuple[str, str, str, str] | None:
        if isinstance(self.layout, AdventureLayout):
            left, right = self.layout.adventure_colors, self.identity_advanced
            top, bottom = sort_frame_textures([left, right])
            if left == top:
                # Use a mask to cut out part of the top layer to be used for the adventure frame
                return "", top, " Inverted", bottom
            else:
                # Use a mask to remove the selected area, so the bottom layer shows through for the adventure frame
                return " Inverted", top, "", bottom

    @cached_property
    def pinline_colors(self) -> dict[str, tuple[float, float, float]]:
        if self.is_land:
            if len(self.identity) == 2:
                return dual_land_color_map
            return land_color_map
        return nonland_color_map

    @cached_property
    def textbox_bevel_thickness(self) -> str:
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
            "Colorless": "Medium",
        }
        return thickness_mappings.get(self.identity_advanced, "Medium")

    @cached_property
    def is_centered(self) -> bool:
        """bool: Governs whether rules text is centered."""
        if self.is_adventure:
            return False
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
        )

    # endregion

    # region    Collector Info Methods
    # Copied from ClassicTemplate
    def process_layout_data(self) -> None:
        """Remove rarity letter from collector data."""
        super().process_layout_data()
        self.layout.collector_data = (
            self.layout.collector_data[:-2]
            if ("/" in self.layout.collector_data)
            else self.layout.collector_data[2:]
        )

    def collector_info(self) -> None:
        """Format and add the collector info at the bottom."""

        # Which collector info mode?
        if (
            self.config.collector_mode in [CollectorMode.Normal, CollectorMode.Modern]
            and self.layout.collector_data
        ):
            self.collector_info_authentic()
            layers = (self.text_layer_artist, self.text_layer_collector_first)
        elif self.config.collector_mode == CollectorMode.ArtistOnly:
            self.collector_info_artist_only()
            layers = (self.text_layer_artist,)
        else:
            self.collector_info_basic()
            layers = (self.text_layer_artist, self.text_layer_set)

        # Shift collector text
        if self.is_align_collector_left and self.collector_reference:
            [psd.align_left(n, ref=self.collector_reference.dims) for n in layers]

    # noinspection DuplicatedCode
    def collector_info_basic(self) -> None:
        """Called to generate basic collector info."""
        if info := self.text_layer_set:
            # Fill optional promo star
            if self.is_collector_promo:
                psd.replace_text(info, "•", MagicIcons.COLLECTOR_STAR)

            # Apply the collector info
            if self.layout.lang != "en":
                psd.replace_text(info, "EN", self.layout.lang.upper())

            psd.replace_text(info, "SET", self.layout.set)

        if self.text_layer_artist:
            psd.replace_text(self.text_layer_artist, "Artist", self.layout.artist)

    # noinspection DuplicatedCode
    def collector_info_authentic(self) -> None:
        """Classic presents authentic collector info differently."""

        # Hide basic 'Set' layer
        if self.text_layer_set:
            self.text_layer_set.visible = False

        if info := psd.getLayer(LAYERS.COLLECTOR, self.legal_group):
            info.visible = True

            # Fill optional promo star
            if self.is_collector_promo:
                psd.replace_text(info, "•", MagicIcons.COLLECTOR_STAR)

            psd.replace_text(info, "SET", self.layout.set)
            psd.replace_text(info, "NUM", self.layout.collector_data)

        if self.text_layer_artist:
            psd.replace_text(self.text_layer_artist, "Artist", self.layout.artist)

    def collector_info_artist_only(self) -> None:
        """Called to generate 'Artist Only' collector info."""

        # Hide basic 'Set' layer
        if self.text_layer_set:
            self.text_layer_set.visible = False

        if self.text_layer_artist:
            psd.replace_text(self.text_layer_artist, "Artist", self.layout.artist)

    # endregion

    # region    Layout logic
    @cached_property
    def flavor_name(self) -> str | None:
        """Display name for nicknamed cards"""
        if isinstance(self.layout.card, ScryfallCard):
            return self.layout.card.flavor_name

    @cached_property
    def is_tombstone_scryfall(self) -> bool:
        return bool("tombstone" in self.layout.frame_effects)

    # Equivilent scryfall search:
    # o:"this card is in your graveyard" or o:"return this card from your graveyard" or o:"cast this card from your graveyard" or o:"put this card from your graveyard" or o:"exile this card from your graveyard" or o:"~ is in your graveyard" or o:"return ~ from your graveyard" or o:"cast ~ from your graveyard" or o:"put ~ from your graveyard" or o:"exile ~ from your graveyard" or keyword:disturb or keyword:flashback or keyword:Dredge or keyword:Scavenge or keyword:Embalm or keyword:Eternalize or keyword:Aftermath or keyword:Encore or keyword:Escape or keyword:Jump-start or keyword:Recover or keyword:Retrace or keyword:Unearth
    # (Excluding named cards)

    @cached_property
    def is_tombstone_auto(self) -> bool:
        keyword_list = [
            "Flashback",
            "Dredge",
            "Scavenge",
            "Embalm",
            "Eternalize",
            "Aftermath",
            "Disturb",
            "Encore",
            "Escape",
            "Jump-start",
            "Recover",
            "Retrace",
            "Unearth",
        ]
        for keyword in keyword_list:
            if keyword in self.layout.keywords:
                return True

        cardname = self.layout.name_raw.lower()
        oracle_text = self.layout.oracle_text.lower()

        key_phrase_list = [
            f"{cardname} is in your graveyard",
            f"return {cardname} from your graveyard",
            f"cast {cardname} from your graveyard",
            f"put {cardname} from your graveyard",
            f"exile {cardname} from your graveyard",
        ]
        for phrase in key_phrase_list:
            if phrase in oracle_text:
                return True

        key_phrase_list_generic = [
            "this card is in your graveyard",
            "return this card from your graveyard",
            "cast this card from your graveyard",
            "put this card from your graveyard",
            "exile this card from your graveyard",
        ]
        for phrase in key_phrase_list_generic:
            if phrase in oracle_text:
                return True

        name_list = [
            "Say Its Name",
            "Skyblade's Boon",
            "Nether Spirit",
        ]
        for name in name_list:
            if name == self.layout.name_raw:
                return True
        return False

    @cached_property
    def has_tombstone(self) -> bool:
        setting = self.cfg_tombstone_setting
        match setting:
            case "Automatic":
                return self.is_tombstone_auto
            case "Scryfall":
                return self.is_tombstone_scryfall
            case _:
                return False

    # endregion

    # region    Layer logic
    @cached_property
    def frame_texture(self) -> ArtLayer | None:
        if self.is_land and self.cfg_legends_style_lands:
            return psd.getLayer("Legends Land", self.frame_texture_group)
        return psd.getLayer(self.identity_advanced, self.frame_texture_group)

    @cached_property
    def frame_mask(self) -> ArtLayer | None:
        return psd.getLayer(self.textbox_size, self.frame_masks_group)

    @cached_property
    def textbox_texture(self) -> ArtLayer | None:
        if self.is_land:
            if self.cfg_legends_style_lands:
                return psd.getLayer("Legends", self.textbox_group)
            if self.is_gold_land:
                return psd.getLayer("Land", self.textbox_group)
            return psd.getLayer(self.identity + "L", self.textbox_group)
        return psd.getLayer(self.identity_advanced, self.textbox_group)

    @cached_property
    def textbox_shape(self) -> ArtLayer | None:
        if self.textbox_size == "Textless":
            return None
        textbox_name = self.textbox_size
        if self.has_irregular_textbox:
            textbox_name = f"{self.identity_advanced} {self.textbox_size}"
        # if self.is_transform and self.is_front:
        #     textbox_name = textbox_name + " TF Front"
        # if self.is_adventure:
        #     textbox_name = "Adventure"
        return psd.getLayer(textbox_name, self.textbox_masks_group)

    @cached_property
    def art_reference(self) -> ReferenceLayer | None:
        if self.cfg_floating_frame:
            return psd.get_reference_layer("Floating Frame", self.art_frames_group)
        if self.is_transparent:
            return psd.get_reference_layer("Transparent Frame", self.art_frames_group)
        # This intentionally makes the artbox larger than it should be given the textbox,
        # so that the art gets cut off at the bottom instead of at the top
        if self.is_normal:
            bigger_art_size = get_smaller_textbox_size(
                self.artref_size_from_art_aspect, self.textbox_size
            )
            return psd.get_reference_layer(bigger_art_size, self.art_frames_group)
        return psd.get_reference_layer(self.textbox_size, self.art_frames_group)

    @cached_property
    def textbox_reference(self) -> ReferenceLayer | None:
        layer_name = f"Textbox Reference {self.textbox_size}"
        if self.is_mdfc:
            layer_name += " MDFC"
        return psd.get_reference_layer(layer_name, self.text_group)

    @cached_property
    def collector_reference(self) -> ReferenceLayer | None:
        return psd.get_reference_layer(LAYERS.COLLECTOR_REFERENCE, self.legal_group)

    @cached_property
    def expansion_reference(self) -> ReferenceLayer | None:
        return psd.get_reference_layer("Expansion Reference", self.text_group)

    @cached_property
    def art_outlines(self) -> LayerSet | None:
        return psd.getLayerSet(self.textbox_size, self.art_outlines_group)

    @cached_property
    def textbox_outlines(self) -> ArtLayer | None:
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

        if isinstance(self.layout, PlaneswalkerLayout):
            rules_text = replace_hyphens_regex(rules_text)

            if self.cfg_verbose_planeswalkers:
                if self.layout.name == "The Aetherspark":
                    return rules_text

                # The wanderer has no planeswalker type
                if (
                    self.layout.name == "The Wanderer"
                    or self.layout.name == "The Eternal Wanderer"
                ):
                    pw_name = "The Wanderer"
                    pw_gender = "fem"
                else:
                    pw_name = self.layout.type_line.split()[3]
                    pw_gender = planeswalker_genders.get(pw_name)

                # Gendered verb conjugations end with s while non-gendered don't
                s = "s" if pw_gender == "masc" or pw_gender == "fem" else ""

                pronoun = "they"
                if pw_gender == "masc":
                    pronoun = "he"
                if pw_gender == "fem":
                    pronoun = "she"

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
        if isinstance(self.layout, LevelerLayout):
            if self.layout.leveler_match is None:
                print("Error: failed to match leveler rules text")
                return ""

            rules_text: str = self.layout.level_up_text + "\n"

            n1, n2 = self.layout.middle_level.split("-")
            m_pt = self.layout.middle_power_toughness
            a_an = indefinite_article_for_number(m_pt.split("/")[0])
            m_abilities = format_leveler_abilities(self.layout.middle_text)

            if m_abilities is None:
                rules_text += (
                    f"As long as this card has at least {n1} and at most {n2} level counters, "
                    f"it's {a_an} {m_pt}.\n"
                )
            else:
                rules_text += (
                    f"As long as this card has at least {n1} and at most {n2} level counters, "
                    f"it's {a_an} {m_pt} with {m_abilities}\n"
                )

            n3 = self.layout.bottom_level[:-1]  # Removes + after number
            b_pt = self.layout.bottom_power_toughness
            a_an_2 = indefinite_article_for_number(b_pt.split("/")[0])
            b_abilities = format_leveler_abilities(self.layout.bottom_text)

            if b_abilities is None:
                rules_text += (
                    f"As long as this card has at least {n3} level counters, "
                    f"it's {a_an_2} {b_pt}."
                )
            else:
                rules_text += (
                    f"As long as this card has at least {n3} level counters, "
                    f"it's {a_an_2} {b_pt} with {b_abilities}"
                )

            return rules_text
        return ""

    def prototype_rules_text(self) -> str:
        if isinstance(self.layout, PrototypeLayout):
            a_an = indefinite_article_for_number(self.layout.proto_pt[0])
            color = color_word_map.get(self.layout.proto_color)

            rules_text = (
                f"Prototype — You may cast this spell for {self.layout.proto_mana_cost}. "
                f"If you do, it's {color} and is {a_an} {self.layout.proto_pt}. "
                f"It keeps its abilities and types.\n"
                f"{self.layout.oracle_text}"
            )
            return rules_text
        return ""

    def mutate_rules_text(self) -> str:
        return self.layout.oracle_text_raw

    def adventure_rules_text(self) -> str:
        """
        Handles adventure, omen, and prepared, which are all treated as adventure template by Proxyshop
        """
        if isinstance(self.layout, AdventureLayout):
            adventure_type = self.layout.type_line_adventure.split(" ")[0].lower()
            # a_an = "a" if adventure_type == "sorcery" else "an"

            supertypes_and_types, _subtypes = self.layout.type_line.split("—")
            card_type = supertypes_and_types.split(" ")[-2].lower()
            a_an_2 = "a" if card_type == "creature" else "an"

            adventure_text_no_reminder = re.sub(
                r"\s\([^)]*\)", "", self.layout.oracle_text_adventure
            )
            # maybe_colors = a_an

            # if self.has_different_adventure_color:
            colors = self.layout.color_identity_adventure
            color_words = [color_word_map[color] for color in colors]
            color_list = list_to_text(color_words)
            maybe_colors = f"a {color_list}"

            if "prepared" in self.layout.oracle_text:
                return (
                    f"When this {card_type} becomes prepared, create a copy of its spell in exile. "
                    f"While it's prepared, you may cast that spell. Doing so unprepares it. "
                    f"This card's spell is {self.layout.name_adventure}. "
                    f"It's {maybe_colors} {adventure_type} for {self.layout.mana_adventure} "
                    f'with "{adventure_text_no_reminder}"\n'
                    f"{self.layout.oracle_text}"
                )

            if "Omen" in self.layout.type_line_adventure:
                return (
                    f"{self.layout.name} can be heralded by an omen. "
                    f"You may cast this card as {maybe_colors} Omen {adventure_type} "
                    f"named {self.layout.name_adventure} for {self.layout.mana_adventure}. "
                    f'It has "{adventure_text_no_reminder} '
                    f"Then shuffle this card into its owner's library.\"\n"
                    f"{self.layout.oracle_text}"
                )

            # This templating is functionally similar to the rules for adventure cards,
            # However, there are things spelled out as rules text that are handled by game rules in reality
            # This distinction doensn't matter unless something modifies the card text or game rules in certain ways
            # Which nothing does, as far as I'm aware
            # The templating only fails on one card, Twice Upon a Time
            # Since it has the same card type (sorcery) for the adventure and non-adventure sides

            return (
                f"{self.layout.name} can go on an adventure. "
                f"You may cast this card as {maybe_colors} Adventure {adventure_type} "
                f"named {self.layout.name_adventure} for {self.layout.mana_adventure}. "
                f'It has "{adventure_text_no_reminder} '
                f"Then exile this card. You may cast it as {a_an_2} {card_type} "
                f'for as long as it remains exiled."\n'
                f"{self.layout.oracle_text}"
            )
        return ""

    def add_adventure_rules_text(self) -> None:
        if isinstance(self.layout, AdventureLayout):
            left_ref, right_ref = (
                psd.get_reference_layer("Left Textbox Ref", self.adventure_group),
                psd.get_reference_layer("Right Textbox Ref", self.adventure_group),
            )

            # Adventure Side
            if layer := psd.getLayer("Rules Text Left", self.adventure_group):
                self.text.append(
                    FormattedTextArea(
                        layer=layer,
                        contents=self.layout.oracle_text_adventure,
                        flavor=self.layout.flavor_text_adventure,
                        centered=False,
                        reference=left_ref,
                        divider=None,
                    )
                )

            # Normal Side
            if layer := psd.getLayer("Rules Text Right", self.adventure_group):
                self.text.append(
                    FormattedTextArea(
                        layer=layer,
                        contents=self.layout.oracle_text,
                        flavor=self.layout.flavor_text,
                        centered=False,
                        reference=right_ref,
                        divider=None,
                    )
                )

    def rules_text_and_pt_layers(self) -> None:
        if self.is_creature and self.text_layer_pt:
            self.text.append(
                TextField(
                    layer=self.text_layer_pt,
                    contents=f"{self.layout.power}/{self.layout.toughness}",
                )
            )

        elif (
            isinstance(
                self.layout,
                (
                    PlaneswalkerLayout,
                    PlaneswalkerTransformLayout,
                    PlaneswalkerMDFCLayout,
                ),
            )
            and self.text_layer_pt
        ):
            self.text.append(
                TextField(layer=self.text_layer_pt, contents=f"{self.layout.loyalty}")
            )

        elif isinstance(self.layout, BattleLayout) and self.text_layer_pt:
            self.text.append(
                TextField(layer=self.text_layer_pt, contents=f"{self.layout.defense}")
            )

        # Make P/T a little smaller if it's two double digits to prevent touching outer card bevel
        # default size is 11.25
        if self.pt_length >= 4 and (
            layer := psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_group)
        ):
            set_text_size(layer, 10.0)

        if (
            self.is_flipside_creature
            and self.cfg_has_tf_notch
            and (layer := psd.getLayer(LAYERS.POWER_TOUGHNESS, self.transform_group))
        ):
            self.text.append(
                TextField(
                    layer=layer,
                    contents=f"{self.layout.other_face_power}/{self.layout.other_face_toughness}",
                )
            )

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
        elif self.is_adventure:
            rules_text = self.adventure_rules_text()
        else:
            rules_text = self.layout.oracle_text

        # if self.is_adventure:
        #     self.add_adventure_rules_text()
        # else:
        if self.text_layer_rules:
            self.text.append(
                FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=rules_text,
                    flavor=self.layout.flavor_text,
                    centered=self.is_centered,
                    reference=self.textbox_reference,
                    divider=self.divider_layer,
                )
            )

    def add_nickname_text(self) -> None:
        if self.text_layer_nickname:
            self.text.append(
                ScaledWidthTextField(
                    layer=self.text_layer_nickname,
                    contents=self.layout.name,
                    reference=self.nickname_shape_layer,
                )
            )
        if self.flavor_name and self.text_layer_name:
            self.text.append(
                ScaledTextField(
                    layer=self.text_layer_name,
                    contents=self.flavor_name,
                    reference=self.name_reference,
                )
            )

    def add_mdfc_text(self) -> None:
        """Adds text at the bottom of mdfc cards indicating the name and cost
        of the card on the other face"""
        if layer := psd.getLayer("Right", self.mdfc_bottom_group):
            self.text.append(
                FormattedTextField(layer=layer, contents=self.layout.other_face_right)
            )
        if (
            layer := psd.getLayer("Left", self.mdfc_bottom_group)
        ) and self.layout.other_face:
            self.text.append(
                ScaledTextField(
                    layer=layer,
                    contents=self.layout.other_face.name,
                    reference=psd.getLayer("Right", self.mdfc_bottom_group),
                )
            )

        if self.has_pinlines:
            if layer := psd.getLayer("Right", self.mdfc_bottom_group):
                layer.translate(0, -6)
            if layer := psd.getLayer("Left", self.mdfc_bottom_group):
                layer.translate(0, -6)

    def adjust_mana_cost(self) -> None:
        """Adjusts the size and position of the mana cost depending
        on if hybrid symbols are present and whether pinlines are enabled"""
        if self.text_layer_mana:
            if "P" in self.layout.mana_cost or "/" in self.layout.mana_cost:
                if self.has_pinlines:
                    set_text_size(self.text_layer_mana, 9.0)
                    self.text_layer_mana.translate(0, -15)
                else:
                    self.text_layer_mana.translate(0, -12)
            elif self.has_pinlines:
                self.text_layer_mana.translate(0, -3)

    def adventure_basic_text_layers(self) -> None:
        if isinstance(self.layout, AdventureLayout):
            if layer := psd.getLayer(LAYERS.MANA_COST, self.adventure_group):
                self.text.append(
                    FormattedTextField(layer=layer, contents=self.layout.mana_adventure)
                )

            if layer := psd.getLayer(LAYERS.TYPE_LINE, self.adventure_group):
                self.text.append(
                    ScaledTextField(
                        layer=layer,
                        contents=self.layout.type_line_adventure,
                        reference=psd.getLayer("Divider", self.adventure_group),
                    )
                )

            if layer := psd.getLayer(LAYERS.NAME, self.adventure_group):
                self.text.append(
                    ScaledTextField(
                        layer=layer,
                        contents=self.layout.name_adventure,
                        reference=psd.getLayer(LAYERS.MANA_COST, self.adventure_group),
                    )
                )

            # Make mana cost smaller if it contains hybrid mana
            if (
                "P" in self.layout.mana_adventure or "/" in self.layout.mana_adventure
            ) and (layer := psd.getLayer(LAYERS.MANA_COST, self.adventure_group)):
                set_text_size(layer, 7.0)

    def basic_text_layers(self) -> None:
        if self.text_layer_mana:
            self.text.append(
                FormattedTextField(
                    layer=self.text_layer_mana, contents=self.layout.mana_cost
                )
            )

        self.adjust_mana_cost()

        if self.has_textbox:
            if self.is_mdfc:
                self.add_mdfc_text()

            if self.text_layer_type:
                self.text.append(
                    ScaledTextField(
                        layer=self.text_layer_type,
                        contents=self.layout.type_line,
                        reference=self.type_reference,
                    )
                )

        if self.has_nickname:
            self.add_nickname_text()
        elif self.text_layer_name:
            self.text.append(
                ScaledTextField(
                    layer=self.text_layer_name,
                    contents=self.layout.name,
                    reference=self.name_reference,
                )
            )

        # if self.is_adventure: self.adventure_basic_text_layers()

    # endregion

    # region    Layer adding functions
    def load_expansion_symbol(self) -> None:
        """Import and loads the expansion symbol, except on textless cards"""
        if not self.has_textbox:
            return
        super().load_expansion_symbol()

    @cached_property
    def textbox_pinlines_colors(self) -> ColorObject | list[GradientConfig]:
        if self.is_land and (
            (not self.is_basic_land and self.cfg_gold_textbox_lands)
            or (len(self.identity) > self.cfg_max_pinline_colors)
        ):
            return psd.get_pinline_gradient("Land", color_map=self.pinline_colors)
        return psd.get_pinline_gradient(
            self.identity
            if 1 < len(self.identity) <= self.cfg_max_pinline_colors
            else self.pinlines,
            color_map=self.pinline_colors,
        )

    @cached_property
    def non_textbox_pinlines_colors(self) -> ColorObject | list[GradientConfig]:
        """Must be returned as SolidColor or gradient notation."""
        if not self.cfg_color_all_pinlines:
            if self.is_land and not self.is_basic_land:
                return psd.get_pinline_gradient("Land", color_map=self.pinline_colors)
            if len(self.identity) > 1:
                if self.is_artifact:
                    return psd.get_pinline_gradient(
                        "Artifact", color_map=self.pinline_colors
                    )
                if self.is_colorless:
                    return psd.get_pinline_gradient(
                        "Colorless", color_map=self.pinline_colors
                    )
                return psd.get_pinline_gradient("Gold", color_map=self.pinline_colors)
        return self.textbox_pinlines_colors

    def add_pinlines(self) -> None:
        if self.pinlines_group:
            enable(self.pinlines_group)
        enable(self.textbox_size, self.art_pinlines_background_group)

        if self.cfg_legends_style_lands and self.is_land:
            enable(f"Legends {self.textbox_size}", psd.getLayerSet("Legends", self.pinlines_group))

        if group := psd.getLayerSet("Outer", self.pinlines_group):
            self.generate_layer(group=group,
                                colors=self.non_textbox_pinlines_colors)

        if group := psd.getLayerSet("Art", self.pinlines_group):
            self.generate_layer(group=group, colors=self.non_textbox_pinlines_colors)
        if (art_mask := psd.getLayer(self.textbox_size, self.art_pinlines_masks_group)) and self.art_pinlines_group:
            psd.copy_vector_mask(art_mask, self.art_pinlines_group)

        if not self.has_textbox: return

        enable(self.textbox_size, self.textbox_pinlines_background_group)
        if group := psd.getLayerSet("Textbox", self.pinlines_group):
            self.generate_layer(group=group, colors=self.textbox_pinlines_colors)
        if (textbox_mask := psd.getLayer(self.textbox_size, self.textbox_pinlines_masks_group)) and self.textbox_pinlines_group:
            psd.copy_vector_mask(textbox_mask, self.textbox_pinlines_group)

    def add_outer_and_art_bevels(self) -> None:
        light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_group)
        dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_group)

        for mask, layer in [
            (light_mask, self.bevels_light_group),
            (dark_mask, self.bevels_dark_group),
        ]:
            if mask and layer:
                psd.copy_vector_mask(mask, layer)
            enable(self.identity_advanced, layer)

    def add_textbox_bevels(self, identity: str | None = None) -> None:
        if not self.has_textbox_bevels:
            return

        if identity is None:
            identity = self.identity_advanced

        _, _, textbox_bevel = self.copy_textbox_bevel_masks(identity)

        # Enables lines which exist on white, blue, and red textbox bevels
        # They don't look good on hybrid cards, and I haven't implemented
        # The right size and placements for cards with pinlines
        if self.is_split_fade or self.has_pinlines:
            return
        if identity == "W" or identity == "U" or identity == "R":
            enable(self.textbox_size, textbox_bevel)

    def add_land_textbox_bevels(self) -> None:
        if not self.has_textbox_bevels:
            return

        bevel_color = self.identity
        if self.is_gold_land:
            bevel_color = "Gold"

        tr, bl, _ = self.copy_textbox_bevel_masks("Land")

        enable(bevel_color, tr)
        enable(bevel_color, bl)

    def copy_textbox_bevel_masks(self, identity: str) -> tuple[LayerSet | None, LayerSet | None, LayerSet | None]:
        sized_bevel_masks = psd.getLayerSet(
            self.textbox_size, self.textbox_bevels_masks_group
        )
        if textbox_bevel := psd.getLayerSet(identity, self.textbox_bevels_group):
            enable(textbox_bevel)

        (top_right, bottom_left) = (
            psd.getLayerSet("TR", textbox_bevel),
            psd.getLayerSet("BL", textbox_bevel),
        )

        top_right_mask = psd.getLayer(
            self.textbox_bevel_thickness + " TR", sized_bevel_masks
        )
        bottom_left_mask = psd.getLayer(
            self.textbox_bevel_thickness + " BL", sized_bevel_masks
        )

        if top_right_mask and top_right:
            psd.copy_vector_mask(top_right_mask, top_right)
        if bottom_left_mask and bottom_left:
            psd.copy_vector_mask(bottom_left_mask, bottom_left)

        return top_right, bottom_left, textbox_bevel

    def dual_fade_frame_texture(self) -> None:
        if self.dual_fade_order:
            top_mask_name, _, top_layer, bottom_layer = self.dual_fade_order

            top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
            top_frame_layer = psd.getLayer(top_layer, self.frame_texture_group)
            bottom_frame_layer = psd.getLayer(bottom_layer, self.frame_texture_group)

            if top_mask and top_frame_layer:
                psd.copy_layer_mask(top_mask, top_frame_layer)

            if top_frame_layer:
                enable(top_frame_layer)
            if bottom_frame_layer:
                enable(bottom_frame_layer)

    def dual_fade_nonland_textbox(self, colors_override: tuple[str,str,str,str] | None = None) -> None:
        if color_source := (
            self.dual_fade_order if colors_override is None else colors_override
        ):
            (top_mask_name, _, top_layer, bottom_layer) = color_source

            top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
            top_textbox_layer = psd.getLayer(top_layer, self.textbox_group)
            bottom_textbox_layer = psd.getLayer(bottom_layer, self.textbox_group)

            if top_mask and top_textbox_layer:
                psd.copy_layer_mask(top_mask, top_textbox_layer)

            if top_textbox_layer:
                enable(top_textbox_layer)
            if bottom_textbox_layer:
                enable(bottom_textbox_layer)

    def add_dual_fade_land_textbox(self) -> None:
        if self.dual_fade_order:
            (top_mask_name, _, top_layer, bottom_layer) = self.dual_fade_order

            top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
            top_textbox_layer = psd.getLayer(f"{top_layer}L Dual", self.textbox_group)
            bottom_textbox_layer = psd.getLayer(f"{bottom_layer}L Dual", self.textbox_group)

            if top_mask and top_textbox_layer:
                psd.copy_layer_mask(top_mask, top_textbox_layer)

            if top_textbox_layer:
                enable(top_textbox_layer)
            if bottom_textbox_layer:
                enable(bottom_textbox_layer)

    def add_dual_fade_land_textbox_bevels(self) -> None:
        if not (self.has_textbox_bevels and self.dual_fade_order):
            return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = (
            self.dual_fade_order
        )

        top_mask = psd.getLayer(top_mask_name, self.mask_group)
        bottom_mask = psd.getLayer(bottom_mask_name, self.mask_group)

        top_right, bottom_left, _ = self.copy_textbox_bevel_masks("Land")

        for mask_layer, layer, group in [
            (top_mask, top_layer, top_right),
            (top_mask, top_layer, bottom_left),
            (bottom_mask, bottom_layer, top_right),
            (bottom_mask, bottom_layer, bottom_left),
        ]:
            enable(layer, group)
            if mask_layer and (layer := psd.getLayer(layer, group)):
                psd.copy_layer_mask(mask_layer, layer)

    def dual_fade_textbox_bevels(self) -> None:
        if not (self.has_textbox_bevels and self.dual_fade_order):
            return

        (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = (
            self.dual_fade_order
        )

        top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
        bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)

        for mask_layer, layer in [
            (top_mask, top_layer),
            (bottom_mask, bottom_layer),
        ]:
            self.add_textbox_bevels(identity=layer)
            if mask_layer and (group :=  psd.getLayerSet(layer, self.textbox_bevels_group)):
                psd.copy_layer_mask(
                    mask_layer, group
                )

    def dual_fade_bevels(self) -> None:
        if self.dual_fade_order:
            (top_mask_name, bottom_mask_name, top_layer, bottom_layer) = (
                self.dual_fade_order
            )

            top_mask = psd.getLayer(top_mask_name, LAYERS.MASKS)
            bottom_mask = psd.getLayer(bottom_mask_name, LAYERS.MASKS)
            light_mask = psd.getLayer(self.textbox_size + " Light", self.bevels_masks_group)
            dark_mask = psd.getLayer(self.textbox_size + " Dark", self.bevels_masks_group)

            if light_mask and self.bevels_light_group:
                psd.copy_vector_mask(light_mask, self.bevels_light_group)
            if dark_mask and self.bevels_dark_group:
                psd.copy_vector_mask(dark_mask, self.bevels_dark_group)

            for mask, layer, group in [
                (top_mask, top_layer, self.bevels_light_group),
                (top_mask, top_layer, self.bevels_dark_group),
                (bottom_mask, bottom_layer, self.bevels_light_group),
                (bottom_mask, bottom_layer, self.bevels_dark_group),
            ]:
                enable(layer, group)
                if mask and (layer := psd.getLayer(layer, group)):
                    psd.copy_layer_mask(mask, layer)

    def position_type_line(self) -> None:
        """Positions the type line elements vertically based on the textbox size"""
        if not self.has_textbox:
            return

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

        if self.text_layer_type:
            self.text_layer_type.translate(0, offset)
        if self.expansion_symbol_layer:
            self.expansion_symbol_layer.translate(0, offset)
        if self.color_indicator_layer:
            self.color_indicator_layer.translate(0, offset)

        if self.is_type_shifted and self.text_layer_type:
            self.text_layer_type.translate(100, 0)

    def add_tombstone(self) -> None:
        # Enables smaller tombstone icon which sits below the transform icon
        if self.is_transform and self.is_front:
            icon_name = "Tombstone Small"
        else:
            icon_name = "Tombstone"

        enable(icon_name, self.text_group)

    def add_textbox_notch(self) -> None:
        cardtype = ""
        if self.is_mdfc:
            cardtype = "MDFC"
        if self.is_transform:
            cardtype = "TF"

        enable(f"{cardtype} Notch", self.textbox_masks_group)
        if self.textbox_outlines_group and (layer := psd.getLayer(f"Textbox Outlines {cardtype}", self.mask_group)):
            psd.copy_vector_mask(layer, self.textbox_outlines_group)

        bevel_overlays = psd.getLayerSet(
            f"Textbox Bevel Overlays {cardtype}", self.card_frame_group
        )

        if self.has_textbox_bevels:
            color = self.identity_advanced

            if self.is_split_fade:
                color = "Hybrid"

            enable(color, bevel_overlays)
            if self.textbox_bevels_group and (layer := psd.getLayer(f"Textbox Bevels {cardtype}", self.mask_group)):
                psd.copy_vector_mask(
                    layer,
                    self.textbox_bevels_group,
                )

            if self.is_land:
                color = self.identity
                if len(color) > 2:
                    color = "Gold"

                if self.is_dual_land and self.dual_fade_order:
                    (top, _, top_color, bottom_color) = self.dual_fade_order
                    notch_side = "Left" if cardtype == "MDFC" else "Right"
                    color = top_color if notch_side == top else bottom_color

                land_bevel_overlays = psd.getLayerSet("Land", bevel_overlays)
                enable(color, psd.getLayerSet("TR", land_bevel_overlays))
                enable(color, psd.getLayerSet("BL", land_bevel_overlays))

        if self.has_pinlines:
            enable("Pinlines", bevel_overlays)
            if self.pinlines_layer and (layer := psd.getLayer(f"Pinlines {cardtype}", self.mask_group)):
                psd.copy_vector_mask(layer, self.pinlines_layer)
            if group := psd.getLayerSet(
                    "Pinlines", psd.getLayerSet("Pinlines", bevel_overlays)
            ):
                self.generate_layer(
                    group=group,
                    colors=self.textbox_pinlines_colors,
                )
        else:
            enable(f"{cardtype} Notch", self.outlines_group)

    def add_land_frame_texture(self) -> None:
        if self.frame_texture:
            enable(self.frame_texture)
        self.add_outer_and_art_bevels()

    def add_land_textbox(self) -> None:
        if self.is_dual_land:
            self.add_dual_fade_land_textbox()
            self.add_dual_fade_land_textbox_bevels()
        else:
            if self.textbox_texture:
                enable(self.textbox_texture)
            self.add_land_textbox_bevels()

    def add_nonland_frame_texture(self) -> None:
        if self.is_split_fade:
            self.dual_fade_frame_texture()
            self.dual_fade_bevels()
        # elif self.is_adventure and self.has_different_adventure_color:
        #     mask, layer, _, _ = self.adventure_mask_info
        #
        #     psd.copy_vector_mask(
        #         psd.getLayer(f"Adventure Frame{mask}", self.mask_group),
        #         psd.getLayer(layer, self.frame_texture_group))
        #
        #     enable(self.layout.adventure_colors, self.frame_texture_group)
        #     enable(self.identity_advanced, self.frame_texture_group)
        #     self.add_outer_and_art_bevels()
        else:
            if self.frame_texture:
                enable(self.frame_texture)
            self.add_outer_and_art_bevels()

    def add_nonland_textbox(self) -> None:
        if self.is_split_fade:
            self.dual_fade_nonland_textbox()
            if self.cfg_dual_textbox_bevels:
                self.dual_fade_textbox_bevels()
            else:
                self.add_textbox_bevels()

        # elif self.is_adventure and self.has_different_adventure_color:
        #
        #     mask, top_layer, _, _ = self.adventure_mask_info
        #
        #     psd.copy_vector_mask(
        #         psd.getLayer(f"Adventure Textbox{mask}", self.mask_group),
        #         psd.getLayer(top_layer, self.textbox_group))
        #
        #     enable(self.layout.adventure_colors, self.textbox_group)
        #     enable(self.identity_advanced, self.textbox_group)
        #
        # self.dual_fade_nonland_textbox(colors_override=self.dual_fade_order_adventure)
        # self.add_textbox_bevels()
        else:
            if self.textbox_texture:
                enable(self.textbox_texture)
            self.add_textbox_bevels()

    def apply_textbox_shape(self) -> None:
        if not (
            self.identity_advanced == "B"
            and self.is_normal
            and self.has_irregular_textbox
        ) and self.textbox_shape:
            # Enables vector mask for vectorized textboxes (including green)
            enable(self.textbox_shape)
        else:
            # Enables rasterized textbox for black textboxes
            enable(f"B {self.textbox_size}", self.textbox_group)

    def apply_devoid(self) -> None:
        color = self.identity if len(self.identity) == 1 else "Gold"
        if color_layer := psd.getLayer(color, self.frame_texture_group):
            enable(color_layer)
            if layer := psd.getLayer("Devoid Color", self.mask_group):
                psd.copy_layer_mask(layer, color_layer)

        if self.is_transparent and self.card_frame_group and (layer := psd.getLayer("Devoid", self.mask_group)):
            psd.copy_layer_mask(
                layer, self.card_frame_group
            )

        if self.cfg_colored_bevels_on_devoid:
            enable(color, self.bevels_light_group)
            enable(color, self.bevels_dark_group)

            if (layer_a := psd.getLayer("Devoid Color", self.mask_group)) and (layer_b := psd.getLayer(color, self.bevels_light_group)):
                psd.copy_layer_mask(
                    layer_a,
                    layer_b,
                )

            if (layer_a := psd.getLayer("Devoid Color", self.mask_group)) and (layer_b := psd.getLayer(color, self.bevels_dark_group)):
                psd.copy_layer_mask(
                    layer_a,
                    layer_b,
                )

    def add_outlines(self) -> None:
        if self.art_outlines:
            enable(self.art_outlines)
        if self.textbox_outlines is not None:
            enable(self.textbox_outlines)

    def add_nickname_plate(self) -> None:
        enable("Nickname", self.text_group)
        enable("Nickname Box", self.text_group)

        masks = psd.getLayerSet("Masks", self.frame_texture_group)
        enable("Nickname", masks)

        if nickname_mask := psd.getLayer("Nickname", self.mask_group):
            if self.outlines_group:
                psd.copy_vector_mask(nickname_mask, self.outlines_group)
            if self.bevels_group:
                psd.copy_vector_mask(nickname_mask, self.bevels_group)

    def add_textbox_decorations(self) -> None:
        """Adds the color indicator and fx to textboxes when appropriate"""
        if self.is_type_shifted and self.color_indicator_layer:
            enable(self.color_indicator_layer)

        # Applies dropshadow effect to green textbox
        if self.identity_advanced == "G" and self.textbox_group and (layer := psd.getLayer("G", self.textbox_effects_group)):
            psd.copy_layer_fx(
                layer, self.textbox_group
            )

    def add_textbox(self) -> None:
        if self.is_land:
            self.add_land_textbox()
        if not self.is_land:
            self.add_nonland_textbox()
        self.apply_textbox_shape()
        self.add_textbox_decorations()

    @override
    def enable_frame_layers(self) -> None:
        if self.frame_mask:
            enable(self.frame_mask)
        self.add_outlines()

        if self.is_land:
            self.add_land_frame_texture()
        if not self.is_land:
            self.add_nonland_frame_texture()

        if self.cfg_floating_frame and self.border_group:
            disable(self.border_group)
        if self.is_devoid:
            self.apply_devoid()
        if self.has_textbox:
            self.add_textbox()
            self.position_type_line()
        # if not self.has_textbox: disable(self.expansion_symbol_layer)
        if self.has_pinlines:
            self.add_pinlines()
        if self.has_nickname:
            self.add_nickname_plate()
        if self.is_promo_star:
            enable("Promo Star", self.text_group)
        if self.has_tombstone:
            self.add_tombstone()
        # if self.is_adventure: enable(self.adventure_group)

    # endregion


class RetroAdventureTemplate(RetroTemplate): ...


class RetroPrototypeTemplate(RetroTemplate): ...


class RetroMutateTemplate(RetroTemplate): ...


class RetroLevelerTemplate(RetroTemplate): ...


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
        return self.has_textbox and self.is_front and self.cfg_has_tf_notch

    def add_transform_icon(self) -> None:
        """Adds transform icons to the top left and right of cards"""
        if self.is_front:
            if self.has_tombstone:  # Cards with tombstones use a smaller transform icon which is placed above it
                icon_name = "Front Small"
            else:
                icon_name = "Front"
        else:
            icon_name = "Back"
            if self.cfg_tf_icon_on_right_side and self.transform_group:
                self.transform_group.translate(1675, 0)

        enable(icon_name, self.transform_group)

    @override
    def enable_frame_layers(self) -> None:
        super().enable_frame_layers()

        # Sagas inherit from TFTemplate since they can be transforming cards
        # but not all of them are, so we have the following guard
        if not self.is_transform:
            return

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
        return self.has_textbox and self.cfg_has_mdfc_notch

    def add_mdfc_icon(self) -> None:
        """Adds modal double faced icons to the top left of cards"""
        if self.mdfc_group:
            enable(self.mdfc_group)
        if self.is_front:
            enable("Front", self.mdfc_group)
        else:
            enable("Back", self.mdfc_group)

    def adjust_mdfc_text_position(self) -> None:
        """Move the mdfc backside card info text up a bit on cards with larger textbox bevels"""
        if (
            self.textbox_bevel_thickness == "Land"
            or self.textbox_bevel_thickness == "Large"
        ) and self.mdfc_bottom_group:
            self.mdfc_bottom_group.translate(0, -5)

    @override
    def enable_frame_layers(self) -> None:
        super().enable_frame_layers()
        self.add_mdfc_icon()
        self.adjust_mdfc_text_position()
        if self.has_mdfc_notch():
            self.add_textbox_notch()


class RetroBattleTemplate(RetroTFTemplate):
    ...
    # Battles are always transform
    # @property
    # def is_transform(self) -> bool:
    #     return True


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
    def textbox_reference(self) -> ReferenceLayer | None:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.saga_group)

    @override
    def text_layers_saga(self) -> None:
        if isinstance(self.layout, SagaLayout):
            # The full read ahead reminder text is too large to comfortably fit in the textbox
            # So it gets swapped out for an abridged version that explains Read Ahead but not how Sagas work
            description = self.layout.saga_description
            if "Read ahead" in description:
                description = "Read ahead (Choose a chapter and start with that many lore counters. Skipped chapters don't trigger.)"

            # Add description text with reminder
            if self.text_layer_reminder:
                self.text.append(
                    text_classes.FormattedTextArea(
                        layer=self.text_layer_reminder,
                        contents=description,
                        reference=self.reminder_reference,
                    )
                )

            # Iterate through each saga stage and add line to text layers
            for i, line in enumerate(self.layout.saga_lines):
                # Add icon layers for this ability
                for n in line["icons"]:
                    if layer := psd.getLayer(n, self.saga_group):
                        self._saga_icons.append([layer.duplicate()])

                # Add ability text for this ability
                if layer := (
                    self.text_layer_ability
                    if i == 0
                    else self.text_layer_ability.duplicate() if self.text_layer_ability else None
                ):
                    self._saga_abilities.append(layer)
                    self.text.append(
                        text_classes.FormattedTextField(layer=layer, contents=line["text"])
                    )

    @override
    def frame_layers_saga(self) -> None:
        if self.saga_group:
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
    def textbox_reference(self) -> ReferenceLayer | None:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.class_group)

    @cached_property
    def stage_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.STAGE, self.class_group)

    @override
    def frame_layers_classes(self) -> None:
        if self.class_group:
            enable(self.class_group)
