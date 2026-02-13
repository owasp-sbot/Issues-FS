# ═══════════════════════════════════════════════════════════════════════════════
# test__Issues_File__Check__Service - Tests for validation and reporting
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Issues_File__Check__Service                   import Issues_File__Check__Service
from issues_fs.issues.issues_file.Issues_File__Check__Service                   import Schema__Issues_File__Check__Summary


class test__Issues_File__Check__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.checker = Issues_File__Check__Service()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.checker as _:
            assert type(_)         is Issues_File__Check__Service
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Valid Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__valid_file(self):
        content = ('Task-1 | todo | First\n'
                   'Task-2 | done | Second')
        summary = self.checker.check_content(content, 'test.issues')

        assert type(summary)         is Schema__Issues_File__Check__Summary
        assert summary.is_valid      is True
        assert summary.total_issues  == 2
        assert summary.total_errors  == 0
        assert summary.duplicate_labels == []
        assert summary.broken_refs      == []

    def test__check__issues_by_type(self):
        content = ('Task-1 | todo | A task\n'
                   'Bug-1 | confirmed | A bug\n'
                   'Bug-2 | resolved | Another bug\n'
                   'Question-1 | open | A question')
        summary = self.checker.check_content(content)

        assert summary.issues_by_type == {'task': 1, 'bug': 2, 'question': 1}

    def test__check__issues_by_status(self):
        content = ('Task-1 | todo | First\n'
                   'Task-2 | todo | Second\n'
                   'Task-3 | done | Third\n'
                   'Task-4 | in-progress | Fourth')
        summary = self.checker.check_content(content)

        assert summary.issues_by_status == {'todo': 2, 'done': 1, 'in-progress': 1}

    # ═══════════════════════════════════════════════════════════════════════════
    # Duplicate Labels
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__duplicate_labels__within_file(self):
        content = ('Task-1 | todo | First occurrence\n'
                   'Task-1 | done | Duplicate!')
        summary = self.checker.check_content(content)

        assert summary.is_valid      is False
        assert summary.duplicate_labels == ['Task-1']

    def test__check__duplicate_labels__across_files(self):
        files = [
            ('Task-1 | todo | In file A',  'a.issues'),
            ('Task-1 | done | In file B',  'b.issues'),
        ]
        summary = self.checker.check_multiple(files)

        assert summary.is_valid      is False
        assert summary.duplicate_labels == ['Task-1']

    # ═══════════════════════════════════════════════════════════════════════════
    # Broken Cross-References
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__broken_cross_ref(self):
        content = 'Task-1 | todo | Depends on -> Bug-99'
        summary = self.checker.check_content(content)

        assert summary.is_valid   is False
        assert summary.broken_refs == ['Bug-99']

    def test__check__valid_cross_ref(self):
        content = ('Task-1 | todo | Depends on -> Bug-1\n'
                   'Bug-1 | confirmed | The bug')
        summary = self.checker.check_content(content)

        assert summary.is_valid    is True
        assert summary.broken_refs == []

    def test__check__cross_ref_across_files(self):
        files = [
            ('Task-1 | todo | Needs -> Bug-1',  'tasks.issues'),
            ('Bug-1 | confirmed | The bug',      'bugs.issues'),
        ]
        summary = self.checker.check_multiple(files)

        assert summary.is_valid    is True
        assert summary.broken_refs == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Mixed Indentation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__mixed_indent(self):
        content = ('Task-1 | todo | Parent\n'
                   '\tTask-2 | todo | Tab child\n'
                   '    Task-3 | todo | Space child')
        summary = self.checker.check_content(content, 'mixed.issues')

        assert summary.mixed_indent == ['mixed.issues']

    def test__check__no_mixed_indent(self):
        content = ('Task-1 | todo | Parent\n'
                   '\tTask-2 | todo | Tab child\n'
                   '\tTask-3 | todo | Tab child')
        summary = self.checker.check_content(content, 'clean.issues')

        assert summary.mixed_indent == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Parse Errors
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__with_parse_errors(self):
        content = ('Task-1 | todo | Good\n'
                   'bad line\n'
                   'also bad')
        summary = self.checker.check_content(content)

        assert summary.is_valid     is False
        assert summary.total_errors == 2
        assert summary.total_issues == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Report Formatting
    # ═══════════════════════════════════════════════════════════════════════════

    def test__format_report__pass(self):
        content = ('Task-1 | todo | First\n'
                   'Task-2 | done | Second')
        summary = self.checker.check_content(content, 'test.issues')
        report  = self.checker.format_report(summary)

        assert 'PASS'   in report
        assert 'Issues: 2' in report
        assert 'Errors: 0' in report

    def test__format_report__fail_with_duplicates(self):
        content = ('Task-1 | todo | First\n'
                   'Task-1 | done | Dup')
        summary = self.checker.check_content(content)
        report  = self.checker.format_report(summary)

        assert 'FAIL'           in report
        assert 'Duplicate'      in report
        assert 'Task-1'         in report

    def test__format_report__fail_with_broken_refs(self):
        content = 'Task-1 | todo | Needs -> Ghost-1'
        summary = self.checker.check_content(content)
        report  = self.checker.format_report(summary)

        assert 'FAIL'     in report
        assert 'Broken'   in report
        assert 'Ghost-1'  in report

    # ═══════════════════════════════════════════════════════════════════════════
    # Empty and Comments-Only
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__empty(self):
        summary = self.checker.check_content('')
        assert summary.is_valid     is True
        assert summary.total_issues == 0

    def test__check__comments_only(self):
        content = '# just a comment\n# another comment'
        summary = self.checker.check_content(content)
        assert summary.is_valid     is True
        assert summary.total_issues == 0
