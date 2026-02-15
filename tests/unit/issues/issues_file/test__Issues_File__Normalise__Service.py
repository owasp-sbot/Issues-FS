# ═══════════════════════════════════════════════════════════════════════════════
# test__Issues_File__Normalise__Service - Tests for JSON export
# ═══════════════════════════════════════════════════════════════════════════════

import json
from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Issues_File__Normalise__Service               import Issues_File__Normalise__Service


class test__Issues_File__Normalise__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.normaliser = Issues_File__Normalise__Service()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.normaliser as _:
            assert type(_)         is Issues_File__Normalise__Service
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Path Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__paths(self):
        content = ('Task-1 | todo | A task\n'
                   'Bug-1 | confirmed | A bug')
        file_map, errors = self.normaliser.normalise_to_dict(content)

        assert len(errors)   == 0
        assert len(file_map) == 2
        assert 'data/task/Task-1/issue.json' in file_map
        assert 'data/bug/Bug-1/issue.json'   in file_map

    def test__normalise__hyphenated_type_path(self):
        content = 'User-Journey-1 | todo | Onboarding flow'
        file_map, errors = self.normaliser.normalise_to_dict(content)

        assert 'data/user-journey/User-Journey-1/issue.json' in file_map

    # ═══════════════════════════════════════════════════════════════════════════
    # JSON Content
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__json_content(self):
        content = 'Task-1 | todo | Enable CloudFront logs'
        file_map, errors = self.normaliser.normalise_to_dict(content)

        json_str = file_map['data/task/Task-1/issue.json']
        data     = json.loads(json_str)

        assert data['label']       == 'Task-1'
        assert data['node_type']   == 'task'
        assert data['node_index']  == 1
        assert data['status']      == 'todo'
        assert data['title']       == 'Enable CloudFront logs'
        assert data['description'] == 'Enable CloudFront logs'
        assert data['tags']        == []
        assert data['links']       == []
        assert data['properties']  == {}
        assert 'node_id'           in data
        assert 'created_at'        in data

    def test__normalise__json_with_links(self):
        content = ('Workstream-1 | todo | Parent\n'
                   '\tTask-1 | todo | Child')
        file_map, errors = self.normaliser.normalise_to_dict(content)

        parent_json = file_map['data/workstream/Workstream-1/issue.json']
        parent      = json.loads(parent_json)

        assert len(parent['links']) == 1
        assert parent['links'][0]['verb']         == 'has-task'
        assert parent['links'][0]['target_label'] == 'Task-1'

    def test__normalise__json_with_cross_refs(self):
        content = ('Task-1 | todo | Fix login -> Bug-1\n'
                   'Bug-1 | confirmed | Login broken')
        file_map, errors = self.normaliser.normalise_to_dict(content)

        task_json = file_map['data/task/Task-1/issue.json']
        task      = json.loads(task_json)

        assert len(task['links']) == 1
        assert task['links'][0]['verb']         == 'relates-to'
        assert task['links'][0]['target_label'] == 'Bug-1'

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise_multiple(self):
        files = [
            ('Task-1 | todo | First',  'a.issues'),
            ('Bug-1 | confirmed | Bug', 'b.issues'),
        ]
        file_map, errors = self.normaliser.normalise_multiple(files)

        assert len(errors)   == 0
        assert len(file_map) == 2
        assert 'data/task/Task-1/issue.json' in file_map
        assert 'data/bug/Bug-1/issue.json'   in file_map

    # ═══════════════════════════════════════════════════════════════════════════
    # Full Example
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__workstream_example(self):
        content = ('Workstream-1 | todo | Observability\n'
                   '\tTask-1 | todo | CloudFront logs\n'
                   '\tTask-2 | done | S3 logging\n'
                   '\tTask-3 | todo | Dashboards')
        file_map, errors = self.normaliser.normalise_to_dict(content, 'ws.issues')

        assert len(errors)   == 0
        assert len(file_map) == 4

        paths = sorted(file_map.keys())
        assert paths == ['data/task/Task-1/issue.json',
                         'data/task/Task-2/issue.json',
                         'data/task/Task-3/issue.json',
                         'data/workstream/Workstream-1/issue.json']

        # verify parent has links
        ws = json.loads(file_map['data/workstream/Workstream-1/issue.json'])
        assert len(ws['links']) == 3

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__with_parse_errors(self):
        content = ('Task-1 | todo | Good line\n'
                   'bad line\n'
                   'Task-2 | done | Also good')
        file_map, errors = self.normaliser.normalise_to_dict(content)

        assert len(file_map) == 2                                               # 2 valid nodes exported
        assert len(errors)   == 1                                               # 1 parse error

    def test__normalise__empty(self):
        file_map, errors = self.normaliser.normalise_to_dict('')
        assert len(file_map) == 0
        assert len(errors)   == 0
