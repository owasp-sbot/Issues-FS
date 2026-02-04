# ═══════════════════════════════════════════════════════════════════════════════
# test_Safe_Str__Issue_Id - Tests for issue ID primitive
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe__Primitive                                     import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                                 import Safe_Str
from osbot_utils.utils.Objects                                                      import base_types
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Issue_Id import Safe_Str__Issue_Id


class test_Safe_Str__Issue_Id(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test basic initialization
        with Safe_Str__Issue_Id('Issue-001') as _:
            assert type(_)       is Safe_Str__Issue_Id
            assert base_types(_) == [Safe_Str, Type_Safe__Primitive, str, object, object ]
            assert str(_)        == 'Issue-001'

    def test__init____empty(self):                                               # Test empty initialization
        with Safe_Str__Issue_Id('') as _:
            assert str(_) == ''

    def test__init____case_insensitive(self):                                    # Test lowercase 'issue' works
        with Safe_Str__Issue_Id('issue-001') as _:
            assert str(_) == 'issue-001'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Format Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__valid_formats(self):                                               # Test valid ID formats
        valid_ids = ['Issue-001', 'Issue-1', 'Issue-999', 'Issue-12345', 'issue-42']
        for issue_id in valid_ids:
            with Safe_Str__Issue_Id(issue_id) as _:
                assert str(_) == issue_id


    # ═══════════════════════════════════════════════════════════════════════════════
    # Comparison Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__equality(self):                                                    # Test equality comparison
        id1 = Safe_Str__Issue_Id('Issue-001')
        id2 = Safe_Str__Issue_Id('Issue-001')
        id3 = Safe_Str__Issue_Id('Issue-002')

        assert id1 == id2
        assert id1 != id3
        assert id1 == 'Issue-001'
