# ═══════════════════════════════════════════════════════════════════════════════
# test_Issue__Path__Config - Tests for issue path configuration
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                                     import Safe_Str
from osbot_utils.utils.Files                                                                            import folder_create, folder_delete_all, folder_exists
from osbot_utils.utils.Objects                                                                          import base_types
from mgraph_ai_ui_html_transformation_workbench.service.issues.Issue__Path__Config                      import Issue__Path__Config


class test_Issue__Path__Config(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test initialization
        with Issue__Path__Config() as _:
            assert type(_)       is Issue__Path__Config
            assert base_types(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_default_issues_path(self):                                          # Test default path generation
        path = Issue__Path__Config.default_issues_path()

        assert type(path)        is str
        assert 'docs/dev-briefs/issues' in str(path)

    def test_ensure_issues_directory(self):                                      # Test directory creation
        test_path = Safe_Str('/tmp/test-issue-path-config')

        folder_delete_all(test_path)
        assert folder_exists(test_path) is False

        result = Issue__Path__Config.ensure_issues_directory(test_path)

        assert result == test_path
        assert folder_exists(test_path) is True

        folder_delete_all(test_path)

    def test_ensure_issues_directory__already_exists(self):                      # Test with existing directory
        test_path = Safe_Str('/tmp/test-issue-path-exists')

        folder_create(test_path)
        assert folder_exists(test_path) is True

        result = Issue__Path__Config.ensure_issues_directory(test_path)

        assert result == test_path
        assert folder_exists(test_path) is True

        folder_delete_all(test_path)
