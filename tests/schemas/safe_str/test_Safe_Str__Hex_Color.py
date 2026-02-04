# ═══════════════════════════════════════════════════════════════════════════════
# test_Safe_Str__Hex_Color - Tests for hex color primitive
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase

from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                                                     import Safe_Str
from osbot_utils.utils.Objects                                                                          import base_types
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Hex_Color import Safe_Str__Hex_Color


class test_Safe_Str__Hex_Color(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test basic initialization
        with Safe_Str__Hex_Color('#22c55e') as _:
            assert type(_)       is Safe_Str__Hex_Color
            assert base_types(_) == [Safe_Str, Type_Safe__Primitive,  str, object, object]
            assert str(_)        == '#22c55e'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__valid_colors(self):                                                # Test valid hex colors
        valid_colors = ['#000000', '#FFFFFF', '#22c55e', '#ff0000', '#ABC123']
        for color in valid_colors:
            with Safe_Str__Hex_Color(color) as _:
                assert str(_) == color

    def test__lowercase_and_uppercase(self):                                     # Test case variations
        lower = Safe_Str__Hex_Color('#aabbcc')
        upper = Safe_Str__Hex_Color('#AABBCC')

        assert lower == '#aabbcc'
        assert upper == '#AABBCC'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Comparison Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__equality(self):                                                    # Test equality comparison
        color1 = Safe_Str__Hex_Color('#22c55e')
        color2 = Safe_Str__Hex_Color('#22c55e')
        color3 = Safe_Str__Hex_Color('#ff0000')

        assert color1 == color2
        assert color1 != color3
        assert color1 == '#22c55e'
