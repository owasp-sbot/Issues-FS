# ═══════════════════════════════════════════════════════════════════════════════
# test__Graph__Repository__Issues_Files - Tests for .issues file integration
# Uses in-memory storage via Graph__Repository__Factory
# ═══════════════════════════════════════════════════════════════════════════════

import json
from unittest                                                                   import TestCase
from issues_fs.issues.graph_services.Graph__Repository__Factory                 import Graph__Repository__Factory


class test__Graph__Repository__Issues_Files(TestCase):

    def setUp(self):
        self.repository = Graph__Repository__Factory.create_memory()

    # ═══════════════════════════════════════════════════════════════════════════
    # .issues File Discovery
    # ═══════════════════════════════════════════════════════════════════════════

    def test__issues_files_discover__none(self):
        result = self.repository.issues_files_discover()
        assert result == []

    def test__issues_files_discover__finds_issues_files(self):
        self.repository.storage_fs.file__save('workstream.issues', b'Task-1 | todo | Enable logs')

        result = self.repository.issues_files_discover()
        assert result == ['workstream.issues']

    def test__issues_files_discover__multiple(self):
        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | First')
        self.repository.storage_fs.file__save('bugs.issues',  b'Bug-1 | confirmed | A bug')

        result = sorted(self.repository.issues_files_discover())
        assert result == ['bugs.issues', 'tasks.issues']

    def test__issues_files_discover__ignores_json(self):
        self.repository.storage_fs.file__save('data/task/Task-1/issue.json', b'{}')
        self.repository.storage_fs.file__save('workstream.issues', b'Task-1 | todo | A task')

        result = self.repository.issues_files_discover()
        assert result == ['workstream.issues']

    # ═══════════════════════════════════════════════════════════════════════════
    # .issues File Loading
    # ═══════════════════════════════════════════════════════════════════════════

    def test__issues_files_load__single_file(self):
        self.repository.storage_fs.file__save('tasks.issues',
            b'Task-1 | todo | Enable logs\nTask-2 | done | Enable S3')

        nodes = self.repository.issues_files_load()
        assert len(nodes)          == 2
        assert str(nodes[0].label) == 'Task-1'
        assert str(nodes[1].label) == 'Task-2'

    def test__issues_files_load__with_hierarchy(self):
        self.repository.storage_fs.file__save('ws.issues',
            b'Workstream-1 | todo | Parent\n\tTask-1 | todo | Child')

        nodes = self.repository.issues_files_load()
        assert len(nodes)            == 2
        assert str(nodes[0].label)   == 'Workstream-1'
        assert len(nodes[0].links)   == 1
        assert str(nodes[0].links[0].target_label) == 'Task-1'

    def test__issues_files_load__empty_when_no_files(self):
        nodes = self.repository.issues_files_load()
        assert nodes == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Behaviour
    # ═══════════════════════════════════════════════════════════════════════════

    def test__issues_files_cache__loads_once(self):
        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | Cached')

        nodes1 = self.repository.issues_files_get_cached_nodes()
        nodes2 = self.repository.issues_files_get_cached_nodes()
        assert nodes1 is nodes2                                                 # same list object

    def test__issues_files_cache__invalidate(self):
        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | Version 1')

        nodes1 = self.repository.issues_files_get_cached_nodes()
        assert len(nodes1) == 1

        self.repository.storage_fs.file__save('tasks.issues',
            b'Task-1 | todo | Version 1\nTask-2 | done | Version 2')
        self.repository.issues_files_invalidate_cache()

        nodes2 = self.repository.issues_files_get_cached_nodes()
        assert len(nodes2) == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Find Node by Label
    # ═══════════════════════════════════════════════════════════════════════════

    def test__issues_files_find_node__exists(self):
        self.repository.storage_fs.file__save('mixed.issues',
            b'Task-1 | todo | Enable logs\nBug-1 | confirmed | A bug')

        node = self.repository.issues_files_find_node_by_label('Bug-1')
        assert node             is not None
        assert str(node.label)  == 'Bug-1'
        assert str(node.status) == 'confirmed'

    def test__issues_files_find_node__not_found(self):
        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | Enable logs')

        node = self.repository.issues_files_find_node_by_label('Ghost-1')
        assert node is None

    # ═══════════════════════════════════════════════════════════════════════════
    # nodes_list_all includes .issues nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def test__nodes_list_all__includes_issues_file_nodes(self):
        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | From .issues')

        all_nodes = self.repository.nodes_list_all()
        labels    = [str(n.label) for n in all_nodes]
        assert 'Task-1' in labels

    def test__nodes_list_all__json_takes_precedence(self):
        node_json = json.dumps({'node_id': 'abc', 'node_type': 'task', 'node_index': 1,
                                'label': 'Task-1', 'title': 'From JSON', 'description': '',
                                'status': 'done', 'created_at': '0', 'updated_at': '0',
                                'created_by': '', 'tags': [], 'links': [], 'properties': {}})
        self.repository.storage_fs.file__save('data/task/Task-1/issue.json', node_json.encode())

        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | From .issues')
        self.repository.issues_files_invalidate_cache()

        all_nodes = self.repository.nodes_list_all()
        task_1_entries = [n for n in all_nodes if str(n.label) == 'Task-1']
        assert len(task_1_entries) == 1                                          # no duplicates
        assert 'data/task/Task-1' in str(task_1_entries[0].path)                 # JSON path wins

    def test__nodes_list_all__exclude_issues_files(self):
        self.repository.storage_fs.file__save('tasks.issues', b'Task-1 | todo | From .issues')

        all_nodes = self.repository.nodes_list_all(include_issues_files=False)
        labels    = [str(n.label) for n in all_nodes]
        assert 'Task-1' not in labels
