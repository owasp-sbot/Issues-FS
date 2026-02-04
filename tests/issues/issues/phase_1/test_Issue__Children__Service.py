# ═══════════════════════════════════════════════════════════════════════════════
# test_Issue__Children__Service - Tests for Phase 1 child issue operations
# Tests add_child_issue, convert_to_new_structure, and list_children
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from memory_fs.helpers.Memory_FS__In_Memory                                                             import Memory_FS__In_Memory
from osbot_utils.utils.Json                                                                             import json_dumps
from issues_fs.schemas.issues.phase_1.Schema__Issue__Children          import Schema__Issue__Child__Create
from issues_fs.issues.graph_services.Graph__Repository         import Graph__Repository
from issues_fs.issues.phase_1.Issue__Children__Service         import Issue__Children__Service
from issues_fs.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


class test_Issue__Children__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup for all tests
        cls.memory_fs    = Memory_FS__In_Memory()
        cls.path_handler = Path__Handler__Graph_Node()
        cls.repository   = Graph__Repository(memory_fs    = cls.memory_fs   ,
                                             path_handler = cls.path_handler)
        cls.service      = Issue__Children__Service(repository   = cls.repository  ,
                                                    path_handler = cls.path_handler)

    def setUp(self):                                                             # Reset storage before each test
        self.repository.clear_storage()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_issue_at_path(self                             ,
                             path       : str                 ,
                             label      : str = 'Test-1'      ,
                             title      : str = 'Test Issue'  ,
                             node_type  : str = 'task'
                        ) -> None:
        data    = {'label': label, 'title': title, 'node_type': node_type, 'status': 'backlog'}
        content = json_dumps(data, indent=2)
        self.repository.storage_fs.file__save(path, content.encode('utf-8'))

    def create_parent_issue(self                              ,
                            node_type  : str = 'feature'      ,
                            label      : str = 'Feature-1'
                       ) -> str:
        path = f".issues/data/{node_type}/{label}/issue.json"
        self.create_issue_at_path(path, label=label, node_type=node_type)
        return f"data/{node_type}/{label}"

    # ═══════════════════════════════════════════════════════════════════════════════
    # add_child_issue Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__add_child_issue__creates_child(self):                              # Test basic child creation
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-1')

        child_data = Schema__Issue__Child__Create(issue_type = 'task'      ,
                                                  title      = 'Child Task')

        response = self.service.add_child_issue(parent_path = parent_path,
                                                child_data  = child_data )

        assert response.success         is True
        assert str(response.label)      == 'Task-1'
        assert str(response.issue_type) == 'task'
        assert str(response.title)      == 'Child Task'
        assert 'issues/Task-1'          in str(response.path)

    def test__add_child_issue__creates_issues_folder(self):                      # Test issues/ folder created
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-2')

        child_data = Schema__Issue__Child__Create(issue_type = 'bug'       ,
                                                  title      = 'Child Bug' )

        self.service.add_child_issue(parent_path = parent_path,
                                     child_data  = child_data )

        issues_folder = f".issues/{parent_path}/issues"
        child_file    = f"{issues_folder}/Bug-1/issue.json"

        assert self.repository.storage_fs.file__exists(child_file) is True

    def test__add_child_issue__increments_label(self):                           # Test label auto-increment
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-3')

        child1 = Schema__Issue__Child__Create(issue_type='task', title='Task 1')
        child2 = Schema__Issue__Child__Create(issue_type='task', title='Task 2')
        child3 = Schema__Issue__Child__Create(issue_type='task', title='Task 3')

        response1 = self.service.add_child_issue(parent_path, child1)
        response2 = self.service.add_child_issue(parent_path, child2)
        response3 = self.service.add_child_issue(parent_path, child3)

        assert str(response1.label) == 'Task-1'
        assert str(response2.label) == 'Task-2'
        assert str(response3.label) == 'Task-3'

    def test__add_child_issue__multiple_types(self):                             # Test different child types
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-4')

        task_data = Schema__Issue__Child__Create(issue_type='task', title='A Task')
        bug_data  = Schema__Issue__Child__Create(issue_type='bug',  title='A Bug')

        task_response = self.service.add_child_issue(parent_path, task_data)
        bug_response  = self.service.add_child_issue(parent_path, bug_data)

        assert str(task_response.label) == 'Task-1'
        assert str(bug_response.label)  == 'Bug-1'

    def test__add_child_issue__with_description(self):                           # Test with optional fields
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-5')

        child_data = Schema__Issue__Child__Create(issue_type  = 'task'               ,
                                                  title       = 'Detailed Task'      ,
                                                  description = 'Task description'   ,
                                                  status      = 'in-progress'        )

        response = self.service.add_child_issue(parent_path, child_data)

        assert response.success is True

        child_file = f".issues/{parent_path}/issues/Task-1/issue.json"           # Verify content was saved
        content    = self.repository.storage_fs.file__str(child_file)

        assert 'Task description' in content
        assert 'in-progress'      in content

    def test__add_child_issue__parent_not_found(self):                           # Test error for missing parent
        child_data = Schema__Issue__Child__Create(issue_type='task', title='Orphan')

        response = self.service.add_child_issue(parent_path = 'nonexistent/path',
                                                child_data  = child_data        )

        assert response.success     is False
        assert 'not found'          in str(response.message).lower()

    def test__add_child_issue__root_as_parent(self):                             # Test adding child to root
        child_data = Schema__Issue__Child__Create(issue_type = 'feature'     ,
                                                  title      = 'Root Feature')

        response = self.service.add_child_issue(parent_path = '',
                                                child_data  = child_data)

        assert response.success         is True
        assert str(response.label)      == 'Feature-1'
        assert 'issues/Feature-1'       in str(response.path)

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert_to_new_structure Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__convert_to_new_structure__creates_folder(self):                    # Test creates issues/ folder
        issue_path = self.create_parent_issue(node_type='task', label='Task-1')

        response = self.service.convert_to_new_structure(issue_path)

        assert response.success   is True
        assert response.converted is True
        assert 'issues'           in str(response.issues_path)

    def test__convert_to_new_structure__idempotent(self):                        # Test doesn't recreate folder
        issue_path = self.create_parent_issue(node_type='task', label='Task-2')

        response1 = self.service.convert_to_new_structure(issue_path)            # First conversion
        response2 = self.service.convert_to_new_structure(issue_path)            # Second conversion

        assert response1.converted is True
        assert response2.converted is False                                      # Already had issues/
        assert 'Already'           in str(response2.message)

    def test__convert_to_new_structure__issue_not_found(self):                   # Test error for missing issue
        response = self.service.convert_to_new_structure('nonexistent/path')

        assert response.success is False
        assert 'not found'      in str(response.message).lower()

    def test__convert_to_new_structure__creates_gitkeep(self):                   # Test creates placeholder file
        issue_path = self.create_parent_issue(node_type='feature', label='Feature-10')

        self.service.convert_to_new_structure(issue_path)

        gitkeep_path = f".issues/{issue_path}/issues/.gitkeep"
        assert self.repository.storage_fs.file__exists(gitkeep_path) is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # list_children Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_children__empty_no_folder(self):                              # Test empty when no issues/ folder
        issue_path = self.create_parent_issue(node_type='task', label='Task-10')

        response = self.service.list_children(issue_path)

        assert response.success    is True
        assert int(response.total) == 0
        assert len(response.children) == 0

    def test__list_children__finds_children(self):                               # Test finds child issues
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-20')

        child1 = Schema__Issue__Child__Create(issue_type='task', title='Task One')
        child2 = Schema__Issue__Child__Create(issue_type='task', title='Task Two')
        child3 = Schema__Issue__Child__Create(issue_type='bug',  title='Bug One' )

        self.service.add_child_issue(parent_path, child1)
        self.service.add_child_issue(parent_path, child2)
        self.service.add_child_issue(parent_path, child3)

        response = self.service.list_children(parent_path)

        assert response.success    is True
        assert int(response.total) == 3

        labels = [c.get('label') for c in response.children]
        assert 'Task-1' in labels
        assert 'Task-2' in labels
        assert 'Bug-1'  in labels

    def test__list_children__includes_metadata(self):                            # Test children have metadata
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-21')

        child_data = Schema__Issue__Child__Create(issue_type = 'task'       ,
                                                  title      = 'Test Task'  ,
                                                  status     = 'in-progress')
        self.service.add_child_issue(parent_path, child_data)

        response = self.service.list_children(parent_path)

        assert len(response.children) == 1

        child = response.children[0]
        assert child.get('label')      == 'Task-1'
        assert child.get('title')      == 'Test Task'
        assert child.get('node_type')  == 'task'

    def test__list_children__sorted(self):                                       # Test children are sorted
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-22')

        for i in range(5, 0, -1):                                                # Create in reverse order
            child = Schema__Issue__Child__Create(issue_type='task', title=f'Task {i}')
            self.service.add_child_issue(parent_path, child)

        response = self.service.list_children(parent_path)

        labels = [c.get('label') for c in response.children]
        assert labels == ['Task-1', 'Task-2', 'Task-3', 'Task-4', 'Task-5']       # Should be sorted

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__generate_child_label__first_of_type(self):                         # Test first label for type
        label = self.service.generate_child_label('.issues/data/feature/F1/issues', 'task')
        assert label == 'Task-1'

    def test__generate_child_label__git_repo_type(self):                         # Test hyphenated type
        label = self.service.generate_child_label('.issues/data/feature/F1/issues', 'git-repo')
        assert label == 'GitRepo-1'

    def test__extract_index_from_label(self):                                    # Test index extraction
        assert int(self.service.extract_index_from_label('Task-1'))    == 1
        assert int(self.service.extract_index_from_label('Task-42'))   == 42
        assert int(self.service.extract_index_from_label('Bug-100'))   == 100
        assert int(self.service.extract_index_from_label('Invalid'))   == 1      # Default

    # ═══════════════════════════════════════════════════════════════════════════════
    # Path Resolution Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__resolve_full_path__empty(self):                                    # Test empty path
        result = self.service.resolve_full_path('')
        assert result == '.issues'

    def test__resolve_full_path__relative(self):                                 # Test relative path
        result = self.service.resolve_full_path('data/task/Task-1')
        assert result == '.issues/data/task/Task-1'

    def test__resolve_full_path__already_full(self):                             # Test already full path
        result = self.service.resolve_full_path('.issues/data/task/Task-1')
        assert result == '.issues/data/task/Task-1'

    def test__make_relative_path(self):                                          # Test making relative
        result = self.service.make_relative_path('.issues/data/task/Task-1')
        assert result == 'data/task/Task-1'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__full_workflow__convert_then_add_children(self):                    # Test full workflow
        parent_path = self.create_parent_issue(node_type='feature', label='Feature-100')

        convert_response = self.service.convert_to_new_structure(parent_path)    # Convert to new structure
        assert convert_response.converted is True

        child1 = Schema__Issue__Child__Create(issue_type='task', title='Task A')  # Add children
        child2 = Schema__Issue__Child__Create(issue_type='bug',  title='Bug A')

        self.service.add_child_issue(parent_path, child1)
        self.service.add_child_issue(parent_path, child2)

        list_response = self.service.list_children(parent_path)                  # List children
        assert int(list_response.total) == 2

    def test__nested_children__two_levels(self):                                 # Test two levels of nesting
        root_path = self.create_parent_issue(node_type='feature', label='Feature-200')

        task_data = Schema__Issue__Child__Create(issue_type='task', title='Task A')   # Add child to root
        task_response = self.service.add_child_issue(root_path, task_data)
        task_path = str(task_response.path)

        bug_data = Schema__Issue__Child__Create(issue_type='bug', title='Bug under Task')  # Add grandchild
        bug_response = self.service.add_child_issue(task_path, bug_data)

        assert bug_response.success    is True
        assert str(bug_response.label) == 'Bug-1'

        task_children = self.service.list_children(task_path)                    # List grandchildren
        assert int(task_children.total) == 1
        assert task_children.children[0].get('label') == 'Bug-1'