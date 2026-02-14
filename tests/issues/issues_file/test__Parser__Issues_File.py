# ═══════════════════════════════════════════════════════════════════════════════
# test__Parser__Issues_File - Tests for full .issues file parser
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Parser__Issues_File                           import Parser__Issues_File
from issues_fs.issues.issues_file.Schema__Issues_File__Result                   import Schema__Issues_File__Result


class test__Parser__Issues_File(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = Parser__Issues_File()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.parser as _:
            assert type(_)         is Parser__Issues_File
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Parsing
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__single_line(self):
        content = 'Task-1 | todo | Do something'
        result  = self.parser.parse(content, 'test.issues')

        assert type(result)      is Schema__Issues_File__Result
        assert result.source_file == 'test.issues'
        assert len(result.issues) == 1
        assert len(result.errors) == 0
        assert result.issues[0].label == 'Task-1'

    def test__parse__multiple_lines(self):
        content = ('Task-1 | todo | First task\n'
                   'Task-2 | done | Second task\n'
                   'Bug-1 | confirmed | A bug')
        result = self.parser.parse(content)

        assert len(result.issues) == 3
        assert result.issues[0].label == 'Task-1'
        assert result.issues[1].label == 'Task-2'
        assert result.issues[2].label == 'Bug-1'
        assert result.issues[2].issue_type == 'bug'

    # ═══════════════════════════════════════════════════════════════════════════
    # Comment and Blank Line Handling
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__skip_comments(self):
        content = ('# This is a comment\n'
                   'Task-1 | todo | Do something\n'
                   '# Another comment\n'
                   'Task-2 | done | Something else')
        result = self.parser.parse(content)

        assert len(result.issues) == 2
        assert result.issues[0].label == 'Task-1'
        assert result.issues[1].label == 'Task-2'

    def test__parse__skip_blank_lines(self):
        content = ('Task-1 | todo | First\n'
                   '\n'
                   '\n'
                   'Task-2 | done | Second')
        result = self.parser.parse(content)

        assert len(result.issues) == 2

    def test__parse__comment_with_leading_spaces(self):
        content = ('  # indented comment\n'
                   'Task-1 | todo | Something')
        result = self.parser.parse(content)

        assert len(result.issues) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Hierarchy via Indentation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__with_hierarchy__tabs(self):
        content = ('Workstream-1 | todo | Observability\n'
                   '\tTask-1 | todo | Enable CloudFront logs\n'
                   '\tTask-2 | todo | Enable S3 logging')
        result = self.parser.parse(content)

        assert len(result.issues)            == 3
        assert result.issues[0].indent_level == 0
        assert result.issues[0].parent_label == ''
        assert result.issues[1].indent_level == 1
        assert result.issues[1].parent_label == 'Workstream-1'
        assert result.issues[2].indent_level == 1
        assert result.issues[2].parent_label == 'Workstream-1'

    def test__parse__nested_hierarchy(self):
        content = ('Workstream-1 | todo | Top level\n'
                   '\tTask-1 | todo | Child\n'
                   '\t\tSub-Task-1 | todo | Grandchild\n'
                   '\t\tSub-Task-2 | done | Another grandchild')
        result = self.parser.parse(content)

        assert len(result.issues)            == 4
        assert result.issues[0].indent_level == 0
        assert result.issues[0].parent_label == ''
        assert result.issues[1].indent_level == 1
        assert result.issues[1].parent_label == 'Workstream-1'
        assert result.issues[2].indent_level == 2
        assert result.issues[2].parent_label == 'Task-1'
        assert result.issues[3].indent_level == 2
        assert result.issues[3].parent_label == 'Task-1'

    def test__parse__hierarchy_with_dedent(self):
        content = ('Workstream-1 | todo | Parent\n'
                   '\tTask-1 | todo | Child\n'
                   '\t\tSub-Task-1 | todo | Grandchild\n'
                   'Workstream-2 | todo | Back to top level')
        result = self.parser.parse(content)

        assert len(result.issues)            == 4
        assert result.issues[3].indent_level == 0
        assert result.issues[3].parent_label == ''

    def test__parse__hierarchy_with_spaces(self):
        content = ('Workstream-1 | todo | Parent\n'
                   '    Task-1 | todo | Child (4 spaces)\n'
                   '        Sub-Task-1 | todo | Grandchild (8 spaces)')
        result = self.parser.parse(content)

        assert len(result.issues)            == 3
        assert result.issues[0].indent_level == 0
        assert result.issues[1].indent_level == 1
        assert result.issues[1].parent_label == 'Workstream-1'
        assert result.issues[2].indent_level == 2
        assert result.issues[2].parent_label == 'Task-1'

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__mixed_valid_and_invalid(self):
        content = ('Task-1 | todo | Valid line\n'
                   'this is garbage\n'
                   'Task-2 | done | Another valid line')
        result = self.parser.parse(content)

        assert len(result.issues) == 2
        assert len(result.errors) == 1
        assert result.errors[0].line_number == 2
        assert 'Expected format' in result.errors[0].message

    def test__parse__multiple_errors(self):
        content = ('bad line one\n'
                   'bad line two\n'
                   'Task-1 | todo | The only valid line')
        result = self.parser.parse(content)

        assert len(result.issues) == 1
        assert len(result.errors) == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Full Example from Brief
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__workstream_observability_example(self):
        content = ('Task-1 | todo | Enable CloudFront access logs with IP masking\n'
                   'Task-2 | todo | Enable S3 object access logging\n'
                   'Task-3 | todo | Enable detailed Lambda execution logging\n'
                   'Task-4 | todo | Enable AWS X-Ray tracing across all services\n'
                   'Task-5 | todo | Enable AWS WAF for CloudFront distribution\n'
                   'Task-6 | todo | Build the collector pipeline (LETS pattern)\n'
                   'Task-7 | todo | Create traffic and error dashboards from collected data\n'
                   'Task-8 | todo | Document cost impact of enabling all logging\n'
                   'Task-9 | in-progress | DevOps brief on all AWS observability settings\n'
                   'Task-10 | blocked | DPO review of logging data protection implications')
        result = self.parser.parse(content, 'workstream-observability.issues')

        assert result.source_file  == 'workstream-observability.issues'
        assert len(result.issues)  == 10
        assert len(result.errors)  == 0
        assert result.issues[0].label      == 'Task-1'
        assert result.issues[0].issue_type == 'task'
        assert result.issues[8].status     == 'in-progress'
        assert result.issues[9].status     == 'blocked'
        assert result.issues[9].label      == 'Task-10'

    def test__parse__hierarchical_example(self):
        content = ('Workstream-1 | todo | Enable full AWS observability and build analytics\n'
                   '\tTask-1 | todo | Enable CloudFront access logs with IP masking\n'
                   '\tTask-2 | todo | Enable S3 object access logging\n'
                   '\tTask-3 | todo | Create dashboards from collected data\n'
                   '\t\tSub-Task-1 | todo | Real-time traffic dashboard\n'
                   '\t\tSub-Task-2 | todo | Error rate and type dashboard\n'
                   '\t\tSub-Task-3 | todo | AWS cost tracking dashboard')
        result = self.parser.parse(content, 'hierarchical.issues')

        assert len(result.issues)  == 7
        assert len(result.errors)  == 0

        # top level
        assert result.issues[0].label        == 'Workstream-1'
        assert result.issues[0].indent_level == 0
        assert result.issues[0].parent_label == ''
        assert result.issues[0].issue_type   == 'workstream'

        # first-level children
        assert result.issues[1].label        == 'Task-1'
        assert result.issues[1].indent_level == 1
        assert result.issues[1].parent_label == 'Workstream-1'

        assert result.issues[3].label        == 'Task-3'
        assert result.issues[3].parent_label == 'Workstream-1'

        # second-level children
        assert result.issues[4].label        == 'Sub-Task-1'
        assert result.issues[4].indent_level == 2
        assert result.issues[4].parent_label == 'Task-3'
        assert result.issues[4].issue_type   == 'sub-task'

        assert result.issues[6].label        == 'Sub-Task-3'
        assert result.issues[6].parent_label == 'Task-3'

    def test__parse__cross_reference_example(self):
        content = ('Task-1 | todo | Enable CloudFront logs -> Task-10\n'
                   'Task-10 | blocked | DPO review')
        result = self.parser.parse(content)

        assert len(result.issues)        == 2
        assert result.issues[0].cross_refs == ['Task-10']
        assert result.issues[1].cross_refs == []

    def test__parse__question_answer_example(self):
        content = ('Question-1 | open | Does the URL hash fragment ever leave the client in any HTTP request?\n'
                   '\tAnswer-1 | answered | Hash fragment is not included in HTTP requests per RFC 3986 -> Question-1')
        result = self.parser.parse(content)

        assert len(result.issues)            == 2
        assert result.issues[0].issue_type   == 'question'
        assert result.issues[1].issue_type   == 'answer'
        assert result.issues[1].parent_label == 'Question-1'
        assert result.issues[1].cross_refs   == ['Question-1']

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__empty_content(self):
        result = self.parser.parse('')
        assert len(result.issues) == 0
        assert len(result.errors) == 0

    def test__parse__only_comments(self):
        content = ('# file header\n'
                   '# workstream: observability\n'
                   '# date: 2026-02-13')
        result = self.parser.parse(content)
        assert len(result.issues) == 0
        assert len(result.errors) == 0

    def test__parse__sibling_after_children(self):
        content = ('Task-1 | todo | Parent\n'
                   '\tSub-Task-1 | todo | Child\n'
                   'Task-2 | todo | Sibling of Task-1')
        result = self.parser.parse(content)

        assert result.issues[2].indent_level == 0
        assert result.issues[2].parent_label == ''
