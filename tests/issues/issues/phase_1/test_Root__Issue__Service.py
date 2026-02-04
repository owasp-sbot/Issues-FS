# ═══════════════════════════════════════════════════════════════════════════════
# test_Root__Issue__Service - Tests for Phase 1 root issue (GitRepo-1) creation
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository         import Graph__Repository
from mgraph_ai_ui_html_transformation_workbench.service.issues.phase_1.Root__Issue__Service             import Root__Issue__Service, ROOT_ISSUE_TYPE, ROOT_ISSUE_LABEL, ROOT_ISSUE_DEFAULT_TITLE, ROOT_ISSUE_STATUS
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


class test_Root__Issue__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)
        cls.service      = Root__Issue__Service(repository   = cls.repository  ,
                                                path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Constants Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__constants__values(self):                                           # Test constant values
        assert ROOT_ISSUE_TYPE          == 'git-repo'
        assert ROOT_ISSUE_LABEL         == 'Gitrepo-1'
        assert ROOT_ISSUE_DEFAULT_TITLE == 'Project Issues'
        assert ROOT_ISSUE_STATUS        == 'active'

    # ═══════════════════════════════════════════════════════════════════════════════
    # create_root_issue Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_root_issue__creates_file(self):                             # Test creates .issues/issue.json
        result = self.service.create_root_issue()

        assert result is True

        path = self.path_handler.path_for_root_issue()
        assert self.repository.storage_fs.file__exists(path) is True

    def test__create_root_issue__default_values(self):                           # Test default field values
        self.service.create_root_issue()

        root_issue = self.service.load_root_issue()

        assert root_issue                 is not None
        assert str(root_issue.node_type)  == 'git-repo'
        assert str(root_issue.label)      == 'Gitrepo-1'
        assert str(root_issue.title)      == 'Project Issues'
        assert str(root_issue.status)     == 'active'
        assert int(root_issue.node_index) == 1

    def test__create_root_issue__custom_title(self):                             # Test custom title
        self.service.create_root_issue(title='My Custom Project')

        root_issue = self.service.load_root_issue()

        assert str(root_issue.title) == 'My Custom Project'

    def test__create_root_issue__does_not_overwrite(self):                       # Test doesn't overwrite existing
        self.service.create_root_issue(title='First Title')
        result = self.service.create_root_issue(title='Second Title')

        assert result is False                                                   # Should not overwrite

        root_issue = self.service.load_root_issue()
        assert str(root_issue.title) == 'First Title'                            # Original preserved

    def test__create_root_issue__has_node_id(self):                              # Test has valid node_id
        create_result = self.service.create_root_issue()
        root_issue    = self.service.load_root_issue()

        assert create_result      is True
        assert root_issue.node_id is not None
        assert root_issue.node_id != ''

    def test__create_root_issue__has_timestamps(self):                           # Test has timestamps
        self.service.create_root_issue()

        root_issue = self.service.load_root_issue()

        assert root_issue.created_at is not None
        assert root_issue.updated_at is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # ensure_root_issue_exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__ensure_root_issue_exists__creates_if_missing(self):                # Test creates when missing
        assert self.service.root_issue_exists() is False

        result = self.service.ensure_root_issue_exists()

        assert result is True
        assert self.service.root_issue_exists() is True

    def test__ensure_root_issue_exists__skips_if_exists(self):                   # Test skips if already exists
        self.service.create_root_issue(title='Original Title')
        original_issue = self.service.load_root_issue()

        result = self.service.ensure_root_issue_exists(title='New Title')

        assert result is True

        current_issue = self.service.load_root_issue()
        assert str(current_issue.title)   == 'Original Title'                    # Title unchanged
        assert str(current_issue.node_id) == str(original_issue.node_id)         # Same issue

    def test__ensure_root_issue_exists__custom_title_on_create(self):            # Test custom title when creating
        result = self.service.ensure_root_issue_exists(title='Custom Title')

        assert result is True

        root_issue = self.service.load_root_issue()
        assert str(root_issue.title) == 'Custom Title'

    # ═══════════════════════════════════════════════════════════════════════════════
    # root_issue_exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__root_issue_exists__false_when_missing(self):                       # Test returns False when missing
        assert self.service.root_issue_exists() is False

    def test__root_issue_exists__true_after_create(self):                        # Test returns True after create
        self.service.create_root_issue()

        assert self.service.root_issue_exists() is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # load_root_issue Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__load_root_issue__returns_none_when_missing(self):                  # Test returns None when missing
        result = self.service.load_root_issue()

        assert result is None

    def test__load_root_issue__returns_schema(self):                             # Test returns Schema__Node
        self.service.create_root_issue()

        result = self.service.load_root_issue()

        assert result is not None
        assert hasattr(result, 'node_id')
        assert hasattr(result, 'node_type')
        assert hasattr(result, 'label')
        assert hasattr(result, 'title')

    # ═══════════════════════════════════════════════════════════════════════════════
    # update_root_issue_title Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update_root_issue_title__updates(self):                            # Test title update works
        self.service.create_root_issue(title='Original')

        result = self.service.update_root_issue_title('Updated Title')

        assert result is True

        root_issue = self.service.load_root_issue()
        assert str(root_issue.title) == 'Updated Title'

    def test__update_root_issue_title__returns_false_when_missing(self):         # Test returns False when no root
        result = self.service.update_root_issue_title('New Title')

        assert result is False

    def test__update_root_issue_title__updates_timestamp(self):                  # Test updated_at changes
        self.service.create_root_issue()
        original = self.service.load_root_issue()
        original_updated_at = original.updated_at

        import time
        time.sleep(0.01)                                                         # Small delay

        self.service.update_root_issue_title('New Title')
        updated = self.service.load_root_issue()

        assert updated.updated_at != original_updated_at                         # Timestamp changed

    # ═══════════════════════════════════════════════════════════════════════════════
    # update_root_issue_description Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update_root_issue_description__updates(self):                      # Test description update works
        self.service.create_root_issue()

        result = self.service.update_root_issue_description('New description')

        assert result is True

        root_issue = self.service.load_root_issue()
        assert str(root_issue.description) == 'New description'

    def test__update_root_issue_description__returns_false_when_missing(self):   # Test returns False when no root
        result = self.service.update_root_issue_description('Description')

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # delete_root_issue Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_root_issue__removes_file(self):                             # Test deletion removes file
        self.service.create_root_issue()
        assert self.service.root_issue_exists() is True

        result = self.service.delete_root_issue()

        assert result is True
        assert self.service.root_issue_exists() is False

    def test__delete_root_issue__returns_false_when_missing(self):               # Test returns False when no file
        result = self.service.delete_root_issue()

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # File Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__root_issue_path__correct(self):                                    # Test root issue path
        expected_path = '.issues/issue.json'

        assert self.path_handler.path_for_root_issue() == expected_path

    def test__root_issue_path__custom_base(self):                                # Test with custom base path
        custom_handler = Path__Handler__Graph_Node(base_path='custom/.issues')

        expected_path = 'custom/.issues/issue.json'

        assert custom_handler.path_for_root_issue() == expected_path