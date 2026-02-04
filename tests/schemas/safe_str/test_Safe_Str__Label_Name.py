# ═══════════════════════════════════════════════════════════════════════════════
# test_Safe_Str__Label_Name - Tests for label name primitive
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe__Primitive                                         import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                                     import Safe_Str
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id         import Safe_Str__Id
from osbot_utils.utils.Objects                                                          import base_types
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Label_Name   import Safe_Str__Label_Name


class test_Safe_Str__Label_Name(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test basic initialization
        with Safe_Str__Label_Name('bug') as _:
            assert type(_)       is Safe_Str__Label_Name
            assert base_types(_) == [Safe_Str__Id, Safe_Str, Type_Safe__Primitive, str, object, object]
            assert str(_)        == 'bug'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__valid_names(self):                                                 # Test valid label names
        valid_names = ['bug', 'feature', 'high-priority', 'v2-release', 'API']
        for name in valid_names:
            with Safe_Str__Label_Name(name) as _:
                assert str(_) == name

    def test__sanitization(self):                                                # Test special chars removed
        with Safe_Str__Label_Name('bug!@#fix') as _:
            assert str(_) == 'bug___fix'                                         # Special chars replaced

        with Safe_Str__Label_Name('feature request') as _:
            assert str(_) == 'feature_request'                                   # Spaces replaced

    def test__hyphen_preserved(self):                                            # Test hyphens kept
        with Safe_Str__Label_Name('high-priority') as _:
            assert str(_) == 'high-priority'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Comparison Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__equality(self):                                                    # Test equality comparison
        name1 = Safe_Str__Label_Name('bug')
        name2 = Safe_Str__Label_Name('bug')
        name3 = Safe_Str__Label_Name('feature')

        assert name1 == name2
        assert name1 != name3
        assert name1 == 'bug'
