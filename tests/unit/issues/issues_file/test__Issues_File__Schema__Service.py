# ═══════════════════════════════════════════════════════════════════════════════
# test__Issues_File__Schema__Service - Tests for schema validation
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Issues_File__Schema__Service                  import Issues_File__Schema__Service
from issues_fs.issues.issues_file.Issues_File__Schema__Service                  import Schema__Issues_Type__Definition
from issues_fs.issues.issues_file.Issues_File__Schema__Service                  import PREDEFINED_SCHEMAS


class test__Issues_File__Schema__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.checker = Issues_File__Schema__Service()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.checker as _:
            assert type(_)         is Issues_File__Schema__Service
            assert base_classes(_) == [Type_Safe, object]

    def test__predefined_schemas(self):
        assert 'task'         in PREDEFINED_SCHEMAS
        assert 'bug'          in PREDEFINED_SCHEMAS
        assert 'workstream'   in PREDEFINED_SCHEMAS
        assert 'feature'      in PREDEFINED_SCHEMAS
        assert 'question'     in PREDEFINED_SCHEMAS
        assert 'risk'         in PREDEFINED_SCHEMAS
        assert 'user-journey' in PREDEFINED_SCHEMAS

    def test__list_schemas(self):
        schemas = self.checker.list_schemas()
        assert len(schemas) == 7
        names = [s.name for s in schemas]
        assert 'task' in names
        assert 'bug'  in names

    # ═══════════════════════════════════════════════════════════════════════════
    # Valid Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__valid_statuses(self):
        content = ('Task-1 | todo | A task\n'
                   'Task-2 | done | Done task')
        summary = self.checker.check_content(content)

        assert summary.is_valid     is True
        assert summary.total_errors == 0
        assert summary.total_checked == 2

    def test__check__valid_bug_statuses(self):
        content = ('Bug-1 | confirmed | A bug\n'
                   'Bug-2 | resolved | Fixed')
        summary = self.checker.check_content(content)

        assert summary.is_valid is True

    def test__check__valid_workstream(self):
        content = 'Workstream-1 | in-progress | Active stream'
        summary = self.checker.check_content(content)

        assert summary.is_valid is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Invalid Statuses
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__invalid_task_status(self):
        content = 'Task-1 | confirmed | Wrong status for task'
        summary = self.checker.check_content(content, 'test.issues')

        assert summary.is_valid     is False
        assert summary.total_errors == 1
        assert summary.errors[0].label == 'Task-1'
        assert 'confirmed' in summary.errors[0].message
        assert 'task'      in summary.errors[0].message

    def test__check__invalid_bug_status(self):
        content = 'Bug-1 | todo | Wrong status for bug'
        summary = self.checker.check_content(content)

        assert summary.is_valid     is False
        assert summary.total_errors == 1
        assert summary.errors[0].label == 'Bug-1'

    def test__check__multiple_invalid(self):
        content = ('Task-1 | confirmed | Wrong\n'
                   'Bug-1 | todo | Also wrong')
        summary = self.checker.check_content(content)

        assert summary.is_valid     is False
        assert summary.total_errors == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Unknown Types
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__unknown_type(self):
        content = 'Widget-1 | active | Some custom type'
        summary = self.checker.check_content(content)

        assert summary.is_valid      is True                                    # unknown types are not errors
        assert summary.unknown_types == ['widget']

    def test__check__mixed_known_unknown(self):
        content = ('Task-1 | todo | Known\n'
                   'Widget-1 | foo | Unknown')
        summary = self.checker.check_content(content)

        assert summary.is_valid      is True
        assert summary.unknown_types == ['widget']
        assert summary.total_checked == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check_multiple(self):
        files = [
            ('Task-1 | todo | Good',         'a.issues'),
            ('Bug-1 | confirmed | Also good', 'b.issues'),
        ]
        summary = self.checker.check_multiple(files)

        assert summary.is_valid      is True
        assert summary.total_checked == 2

    def test__check_multiple__cross_file_errors(self):
        files = [
            ('Task-1 | confirmed | Bad status',  'a.issues'),
            ('Bug-1 | todo | Also bad status',   'b.issues'),
        ]
        summary = self.checker.check_multiple(files)

        assert summary.is_valid     is False
        assert summary.total_errors == 2

    # ═══════════════════════════════════════════════════════════════════════════
    # Custom Schema Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def test__register_custom_schema(self):
        checker = Issues_File__Schema__Service()
        checker.register_schema(Schema__Issues_Type__Definition(
            name           = 'widget'                       ,
            display_name   = 'Widget'                       ,
            valid_statuses = ['active', 'deprecated']       ,
            description    = 'A custom widget type'         ))

        content = 'Widget-1 | active | A widget'
        summary = checker.check_content(content)

        assert summary.is_valid      is True
        assert summary.unknown_types == []

    def test__register_custom_schema__rejects_invalid(self):
        checker = Issues_File__Schema__Service()
        checker.register_schema(Schema__Issues_Type__Definition(
            name           = 'widget'                       ,
            display_name   = 'Widget'                       ,
            valid_statuses = ['active', 'deprecated']       ,
            description    = 'A custom widget type'         ))

        content = 'Widget-1 | broken | Invalid status'
        summary = checker.check_content(content)

        assert summary.is_valid     is False
        assert summary.total_errors == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Hyphenated Types
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__user_journey(self):
        content = 'User-Journey-1 | draft | Onboarding flow'
        summary = self.checker.check_content(content)

        assert summary.is_valid is True

    def test__check__user_journey__invalid(self):
        content = 'User-Journey-1 | todo | Wrong status for user-journey'
        summary = self.checker.check_content(content)

        assert summary.is_valid     is False
        assert summary.total_errors == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Report Formatting
    # ═══════════════════════════════════════════════════════════════════════════

    def test__format_report__pass(self):
        content = 'Task-1 | todo | Good'
        summary = self.checker.check_content(content)
        report  = self.checker.format_report(summary)

        assert 'PASS' in report
        assert 'Issues checked: 1' in report

    def test__format_report__fail(self):
        content = 'Task-1 | confirmed | Wrong'
        summary = self.checker.check_content(content)
        report  = self.checker.format_report(summary)

        assert 'FAIL'      in report
        assert 'Task-1'    in report
        assert 'confirmed' in report

    def test__format_report__unknown_types(self):
        content = 'Widget-1 | active | Custom'
        summary = self.checker.check_content(content)
        report  = self.checker.format_report(summary)

        assert 'Unknown types' in report
        assert 'widget'        in report

    # ═══════════════════════════════════════════════════════════════════════════
    # Empty
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__empty(self):
        summary = self.checker.check_content('')
        assert summary.is_valid      is True
        assert summary.total_checked == 0
