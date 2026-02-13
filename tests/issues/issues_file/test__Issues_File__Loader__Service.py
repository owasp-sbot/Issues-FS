# ═══════════════════════════════════════════════════════════════════════════════
# test__Issues_File__Loader__Service - Tests for the top-level loader
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Issues_File__Loader__Service                  import Issues_File__Loader__Service
from issues_fs.issues.issues_file.Issues_File__Loader__Service                  import Schema__Issues_File__Load__Result


class test__Issues_File__Loader__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loader = Issues_File__Loader__Service()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.loader as _:
            assert type(_)         is Issues_File__Loader__Service
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Single File Loading
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_content__simple(self):
        content = ('Task-1 | todo | Enable CloudFront logs\n'
                   'Task-2 | done | Enable S3 logging')
        result = self.loader.load_content(content, 'test.issues')

        assert type(result)        is Schema__Issues_File__Load__Result
        assert result.total_issues == 2
        assert len(result.nodes)   == 2
        assert len(result.errors)  == 0
        assert result.files_loaded == ['test.issues']
        assert str(result.nodes[0].label)  == 'Task-1'
        assert str(result.nodes[1].label)  == 'Task-2'

    def test__load_content__with_hierarchy(self):
        content = ('Workstream-1 | todo | Observability\n'
                   '\tTask-1 | todo | Enable logs\n'
                   '\tTask-2 | done | Enable S3')
        result = self.loader.load_content(content, 'ws.issues')

        assert result.total_issues == 3
        assert len(result.errors)  == 0

        workstream = result.nodes[0]
        assert len(workstream.links)              == 2
        assert str(workstream.links[0].verb)      == 'has-task'
        assert str(workstream.links[0].target_label) == 'Task-1'

    def test__load_content__with_errors(self):
        content = ('Task-1 | todo | Good line\n'
                   'bad line no pipes\n'
                   'Task-2 | done | Another good line')
        result = self.loader.load_content(content, 'mixed.issues')

        assert result.total_issues == 2
        assert len(result.errors)  == 1

    def test__load_content__with_cross_refs(self):
        content = ('Task-1 | todo | Fix login -> Bug-1\n'
                   'Bug-1 | confirmed | Login broken')
        result = self.loader.load_content(content, 'refs.issues')

        assert result.total_issues == 2
        task = result.nodes[0]
        assert len(task.links)              == 1
        assert str(task.links[0].verb)      == 'relates-to'
        assert str(task.links[0].target_label) == 'Bug-1'

    def test__load_content__empty(self):
        result = self.loader.load_content('', 'empty.issues')
        assert result.total_issues == 0
        assert len(result.nodes)   == 0
        assert len(result.errors)  == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Full Example from Brief
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_content__workstream_example(self):
        content = ('Workstream-1 | todo | Enable full AWS observability and build analytics\n'
                   '\tTask-1 | todo | Enable CloudFront access logs with IP masking\n'
                   '\tTask-2 | todo | Enable S3 object access logging\n'
                   '\tTask-3 | todo | Create dashboards from collected data\n'
                   '\t\tSub-Task-1 | todo | Real-time traffic dashboard\n'
                   '\t\tSub-Task-2 | todo | Error rate and type dashboard\n'
                   '\t\tSub-Task-3 | todo | AWS cost tracking dashboard')
        result = self.loader.load_content(content, 'workstream-observability.issues')

        assert result.total_issues == 7
        assert len(result.errors)  == 0

        workstream = result.nodes[0]
        assert str(workstream.label)     == 'Workstream-1'
        assert str(workstream.node_type) == 'workstream'
        assert len(workstream.links)     == 3                                   # Task-1, Task-2, Task-3

        task3 = result.nodes[3]
        assert str(task3.label) == 'Task-3'
        assert len(task3.links) == 3                                            # Sub-Task-1, -2, -3

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple File Loading
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_multiple(self):
        files = [
            ('Task-1 | todo | First\nTask-2 | done | Second',        'a.issues'),
            ('Bug-1 | confirmed | A bug\nBug-2 | resolved | Fixed',  'b.issues'),
        ]
        result = self.loader.load_multiple(files)

        assert result.total_issues  == 4
        assert len(result.nodes)    == 4
        assert len(result.errors)   == 0
        assert result.files_loaded  == ['a.issues', 'b.issues']
        assert str(result.nodes[0].label) == 'Task-1'
        assert str(result.nodes[2].label) == 'Bug-1'

    def test__load_multiple__with_mixed_errors(self):
        files = [
            ('Task-1 | todo | Good\nbad line',   'a.issues'),
            ('Bug-1 | confirmed | Also good',     'b.issues'),
        ]
        result = self.loader.load_multiple(files)

        assert result.total_issues == 2
        assert len(result.errors)  == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Question/Answer Pattern from Brief
    # ═══════════════════════════════════════════════════════════════════════════

    def test__load_content__question_answer(self):
        content = ('Question-1 | open | Does the URL hash fragment ever leave the client?\n'
                   '\tAnswer-1 | answered | Hash fragment is not included per RFC 3986 -> Question-1')
        result = self.loader.load_content(content, 'questions.issues')

        assert result.total_issues == 2
        question = result.nodes[0]
        answer   = result.nodes[1]

        assert str(question.node_type) == 'question'
        assert str(answer.node_type)   == 'answer'

        # question has child link to answer
        assert len(question.links)              == 1
        assert str(question.links[0].verb)      == 'has-task'
        assert str(question.links[0].target_label) == 'Answer-1'

        # answer has cross-ref link to question
        assert len(answer.links)                == 1
        assert str(answer.links[0].verb)        == 'relates-to'
        assert str(answer.links[0].target_label) == 'Question-1'
