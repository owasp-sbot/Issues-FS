# ═══════════════════════════════════════════════════════════════════════════════
# test_Path__Handler__Graph_Node__Phase1 - Tests for Phase 1 path handler changes
# Tests issue.json path methods and issues/ folder paths
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from issues_fs.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node, FILE_NAME__ISSUE_JSON, FILE_NAME__NODE_JSON


class test_Path__Handler__Graph_Node__Phase_1(TestCase):

    def setUp(self):
        self.path_handler = Path__Handler__Graph_Node()

    # ═══════════════════════════════════════════════════════════════════════════════
    # File Name Constants
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__file_name_constants(self):                                         # Test file name constants
        assert FILE_NAME__ISSUE_JSON == 'issue.json'
        assert FILE_NAME__NODE_JSON  == 'node.json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # path_for_issue_json Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_issue_json(self):                                         # Test issue.json path generation
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        result = self.path_handler.path_for_issue_json(node_type, label)

        assert result == 'data/bug/Bug-1/issue.json'

    def test__path_for_issue_json__task(self):                                   # Test issue.json for task
        node_type = Safe_Str__Node_Type('task')
        label     = Safe_Str__Node_Label('Task-42')

        result = self.path_handler.path_for_issue_json(node_type, label)

        assert result == 'data/task/Task-42/issue.json'

    def test__path_for_issue_json__git_repo(self):                               # Test issue.json for git-repo type
        node_type = Safe_Str__Node_Type('git-repo')
        label     = Safe_Str__Node_Label('Gitrepo-1')

        result = self.path_handler.path_for_issue_json(node_type, label)

        assert result == 'data/git-repo/Gitrepo-1/issue.json'

    # ═══════════════════════════════════════════════════════════════════════════════
    # path_for_node_json Tests (Legacy)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_node_json(self):                                          # Test node.json path generation
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        result = self.path_handler.path_for_node_json(node_type, label)

        assert result == 'data/bug/Bug-1/node.json'

    def test__path_for_node__returns_node_json(self):                            # Test deprecated method returns node.json
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        result = self.path_handler.path_for_node(node_type, label)

        assert result == 'data/bug/Bug-1/node.json'                              # Should match path_for_node_json

    # ═══════════════════════════════════════════════════════════════════════════════
    # path_for_root_issue Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_root_issue(self):                                         # Test root issue.json path
        result = self.path_handler.path_for_root_issue()

        assert result == 'issue.json'

    def test__path_for_root_issue__custom_base(self):                            # Test root issue with custom base
        handler = Path__Handler__Graph_Node(base_path='my-issues')

        result = handler.path_for_root_issue()

        assert result == 'issue.json'                                            # base_path no longer affects paths

    # ═══════════════════════════════════════════════════════════════════════════════
    # path_for_issues_folder Tests (Hierarchical Structure)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_issues_folder(self):                                      # Test issues/ subfolder path
        node_type = Safe_Str__Node_Type('feature')
        label     = Safe_Str__Node_Label('Feature-1')

        result = self.path_handler.path_for_issues_folder(node_type, label)

        assert result == 'data/feature/Feature-1/issues'

    def test__path_for_issues_folder__git_repo(self):                            # Test issues/ folder for git-repo
        node_type = Safe_Str__Node_Type('git-repo')
        label     = Safe_Str__Node_Label('Gitrepo-1')

        result = self.path_handler.path_for_issues_folder(node_type, label)

        assert result == 'data/git-repo/Gitrepo-1/issues'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Path Consistency Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__issue_and_node_paths_in_same_folder(self):                         # Test both files in same folder
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        path_issue = self.path_handler.path_for_issue_json(node_type, label)
        path_node  = self.path_handler.path_for_node_json(node_type, label)
        path_folder = self.path_handler.path_for_node_folder(node_type, label)

        assert path_issue.startswith(path_folder)                                # issue.json in node folder
        assert path_node.startswith(path_folder)                                 # node.json in node folder
        assert path_issue != path_node                                           # Different files

    def test__issues_folder_inside_node_folder(self):                            # Test issues/ is inside node folder
        node_type = Safe_Str__Node_Type('feature')
        label     = Safe_Str__Node_Label('Feature-1')

        path_folder = self.path_handler.path_for_node_folder(node_type, label)
        path_issues = self.path_handler.path_for_issues_folder(node_type, label)

        assert path_issues.startswith(path_folder)                               # issues/ inside node folder
        assert path_issues == f"{path_folder}/issues"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Custom Base Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__custom_base_path__issue_json(self):                                # Test issue.json with custom base
        handler   = Path__Handler__Graph_Node(base_path='custom/.issues')
        node_type = Safe_Str__Node_Type('bug')
        label     = Safe_Str__Node_Label('Bug-1')

        result = handler.path_for_issue_json(node_type, label)

        assert result == 'data/bug/Bug-1/issue.json'                             # base_path no longer affects paths

    def test__custom_base_path__issues_folder(self):                             # Test issues/ with custom base
        handler   = Path__Handler__Graph_Node(base_path='custom/.issues')
        node_type = Safe_Str__Node_Type('feature')
        label     = Safe_Str__Node_Label('Feature-1')

        result = handler.path_for_issues_folder(node_type, label)

        assert result == 'data/feature/Feature-1/issues'                         # base_path no longer affects paths
