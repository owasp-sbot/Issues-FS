# ═══════════════════════════════════════════════════════════════════════════════
# test_Path__Handler__Issues - Tests for issue path handler
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                import TestCase
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                          import Safe_Str
from osbot_utils.utils.Objects                                                               import base_types
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Issue_Id          import Safe_Str__Issue_Id
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Issues import Path__Handler__Issues


class test_Path__Handler__Issues(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared test setup
        cls.handler = Path__Handler__Issues()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test initialization
        with Path__Handler__Issues() as _:
            assert type(_)       is Path__Handler__Issues
            assert base_types(_) == [Type_Safe, object]
            assert str(_.base_path) == ''

    def test__init____with_base_path(self):                                      # Test with base path
        with Path__Handler__Issues(base_path='.issues') as _:
            assert str(_.base_path) == '.issues'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Issue Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_path_for_issue(self):                                               # Test issue path without base
        path = self.handler.path_for_issue(Safe_Str__Issue_Id('Issue-001'))
        assert str(path) == 'Issue-001.json'

    def test_path_for_issue__with_base_path(self):                               # Test issue path with base
        handler = Path__Handler__Issues(base_path='.issues')
        path = handler.path_for_issue('Issue-042')
        assert str(path) == '.issues/Issue-042.json'

    def test_path_for_issues_index(self):                                        # Test index path without base
        path = self.handler.path_for_issues_index()
        assert str(path) == 'issues.json'

    def test_path_for_issues_index__with_base_path(self):                        # Test index path with base
        handler = Path__Handler__Issues(base_path=Safe_Str('data'))
        path = handler.path_for_issues_index()
        assert str(path) == 'data/issues.json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_path_for_labels(self):                                              # Test labels path without base
        path = self.handler.path_for_labels()
        assert str(path) == 'labels.json'

    def test_path_for_labels__with_base_path(self):                              # Test labels path with base
        handler = Path__Handler__Issues(base_path=Safe_Str('config'))
        path = handler.path_for_labels()
        assert str(path) == 'config/labels.json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Attachment Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_path_for_attachment(self):                                          # Test attachment path
        path = self.handler.path_for_attachment(issue_id = 'Issue-001'    ,
                                                filename = 'screenshot.png')
        assert path == 'attachments/Issue-001/screenshot.png'

    def test_path_for_attachment__with_base_path(self):                          # Test attachment path with base
        handler = Path__Handler__Issues(base_path='.issues')
        path = handler.path_for_attachment(issue_id = 'Issue-005',
                                           filename = 'error-log.txt')
        assert str(path) == '.issues/attachments/Issue-005/error-log.txt'
