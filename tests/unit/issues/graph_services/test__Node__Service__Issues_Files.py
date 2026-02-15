# ═══════════════════════════════════════════════════════════════════════════════
# test__Node__Service__Issues_Files - Tests that Node__Service.list_nodes()
# includes nodes from .issues files alongside JSON-backed nodes
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from issues_fs.issues.graph_services.Graph__Repository__Factory                 import Graph__Repository__Factory
from issues_fs.issues.graph_services.Node__Service                              import Node__Service
from issues_fs.issues.graph_services.Type__Service                              import Type__Service


class test__Node__Service__Issues_Files(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repository   = Graph__Repository__Factory.create_memory()
        cls.type_service = Type__Service(repository=cls.repository)
        cls.node_service = Node__Service(repository=cls.repository)

    def setUp(self):
        self.repository.clear_storage()
        self.type_service.initialize_default_types()

    # ═══════════════════════════════════════════════════════════════════════════
    # list_nodes includes .issues file nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def test__list_nodes__includes_issues_file_tasks(self):
        self.repository.storage_fs.file__save('tasks.issues',
            b'Task-1 | todo | From .issues file')

        response = self.node_service.list_nodes()

        assert response.success is True
        labels = [str(n.label) for n in response.nodes]
        assert 'Task-1' in labels

    def test__list_nodes__issues_file_with_hierarchy(self):
        self.repository.storage_fs.file__save('ws.issues',
            b'Workstream-1 | in-progress | Main stream\n\tTask-1 | todo | A task')

        response = self.node_service.list_nodes()

        labels = [str(n.label) for n in response.nodes]
        assert 'Task-1'       in labels
        assert 'Workstream-1' in labels

    def test__list_nodes__includes_unregistered_types(self):
        self.repository.storage_fs.file__save('ws.issues',
            b'Workstream-1 | todo | Not a registered type')

        response = self.node_service.list_nodes()

        labels = [str(n.label) for n in response.nodes]
        assert 'Workstream-1' in labels

    def test__list_nodes__by_type_from_issues_file(self):
        self.repository.storage_fs.file__save('mixed.issues',
            b'Task-1 | todo | A task\nBug-1 | confirmed | A bug')

        response = self.node_service.list_nodes(node_type='task')

        labels = [str(n.label) for n in response.nodes]
        assert 'Task-1' in labels
        assert 'Bug-1'  not in labels

    def test__list_nodes__mixed_json_and_issues_file(self):
        from issues_fs.schemas.graph.Schema__Node__Create__Request              import Schema__Node__Create__Request

        create_req = Schema__Node__Create__Request(node_type='bug', title='JSON bug')
        self.node_service.create_node(create_req)

        self.repository.storage_fs.file__save('tasks.issues',
            b'Task-10 | todo | Issues file task')
        self.repository.issues_files_invalidate_cache()

        response = self.node_service.list_nodes()

        labels = [str(n.label) for n in response.nodes]
        assert 'Bug-1'   in labels                                              # from JSON
        assert 'Task-10' in labels                                              # from .issues file

    def test__list_nodes__json_takes_precedence_in_listing(self):
        from issues_fs.schemas.graph.Schema__Node__Create__Request              import Schema__Node__Create__Request

        create_req = Schema__Node__Create__Request(node_type='task', title='JSON task')
        self.node_service.create_node(create_req)

        self.repository.storage_fs.file__save('tasks.issues',
            b'Task-1 | todo | Issues file version')
        self.repository.issues_files_invalidate_cache()

        response = self.node_service.list_nodes(node_type='task')

        task_1_entries = [n for n in response.nodes if str(n.label) == 'Task-1']
        assert len(task_1_entries) == 1                                          # no duplicates
        assert str(task_1_entries[0].title) == 'JSON task'                       # JSON version wins
