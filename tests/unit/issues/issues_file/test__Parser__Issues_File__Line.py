# ═══════════════════════════════════════════════════════════════════════════════
# test__Parser__Issues_File__Line - Tests for single line parser
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Parser__Issues_File__Line                     import Parser__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Line                     import Schema__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Error                    import Schema__Issues_File__Error


class test__Parser__Issues_File__Line(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = Parser__Issues_File__Line()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.parser as _:
            assert type(_)         is Parser__Issues_File__Line
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Valid Line Parsing
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__valid_line(self):
        parsed, error = self.parser.parse('Task-1 | todo | Enable CloudFront logs', 1)
        assert error  is None
        assert parsed is not None
        assert parsed.label       == 'Task-1'
        assert parsed.status      == 'todo'
        assert parsed.description == 'Enable CloudFront logs'
        assert parsed.line_number == 1
        assert parsed.issue_type  == 'task'
        assert parsed.cross_refs  == []

    def test__parse__valid_line__with_cross_ref(self):
        parsed, error = self.parser.parse('Task-1 | todo | Fix login -> Bug-3', 5)
        assert error  is None
        assert parsed.label       == 'Task-1'
        assert parsed.description == 'Fix login -> Bug-3'
        assert parsed.cross_refs  == ['Bug-3']

    def test__parse__valid_line__multiple_cross_refs(self):
        parsed, error = self.parser.parse('Task-1 | todo | Depends on -> Bug-3 and -> Task-5', 1)
        assert error  is None
        assert parsed.cross_refs == ['Bug-3', 'Task-5']

    def test__parse__valid_line__description_with_pipes(self):
        parsed, error = self.parser.parse('Task-1 | todo | a | b | c', 1)
        assert error  is None
        assert parsed.description == 'a | b | c'

    def test__parse__valid_line__extra_whitespace(self):
        parsed, error = self.parser.parse('  Task-1  |  todo  |  Enable logs  ', 1)
        assert error  is None
        assert parsed.label       == 'Task-1'
        assert parsed.status      == 'todo'
        assert parsed.description == 'Enable logs'

    # ═══════════════════════════════════════════════════════════════════════════
    # Type Inference
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__type_inference__simple(self):
        parsed, _ = self.parser.parse('Task-1 | todo | Something', 1)
        assert parsed.issue_type == 'task'

    def test__parse__type_inference__bug(self):
        parsed, _ = self.parser.parse('Bug-42 | confirmed | Login fails', 1)
        assert parsed.issue_type == 'bug'

    def test__parse__type_inference__hyphenated(self):
        parsed, _ = self.parser.parse('User-Journey-1 | todo | Onboarding flow', 1)
        assert parsed.issue_type == 'user-journey'

    def test__parse__type_inference__multi_word(self):
        parsed, _ = self.parser.parse('Sub-Task-3 | done | Build dashboard', 1)
        assert parsed.issue_type == 'sub-task'

    def test__parse__type_inference__workstream(self):
        parsed, _ = self.parser.parse('Workstream-1 | in-progress | Observability', 1)
        assert parsed.issue_type == 'workstream'

    def test__parse__type_inference__question(self):
        parsed, _ = self.parser.parse('Question-7 | open | Does the hash fragment leave the client?', 1)
        assert parsed.issue_type == 'question'

    def test__parse__type_inference__decision(self):
        parsed, _ = self.parser.parse('Decision-4 | accepted | Use JWT for auth', 1)
        assert parsed.issue_type == 'decision'

    def test__parse__type_inference__finding(self):
        parsed, _ = self.parser.parse('Finding-2 | open | SQL injection in login endpoint', 1)
        assert parsed.issue_type == 'finding'

    # ═══════════════════════════════════════════════════════════════════════════
    # Status Values
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__status__todo(self):
        parsed, _ = self.parser.parse('Task-1 | todo | Something', 1)
        assert parsed.status == 'todo'

    def test__parse__status__in_progress(self):
        parsed, _ = self.parser.parse('Task-1 | in-progress | Something', 1)
        assert parsed.status == 'in-progress'

    def test__parse__status__done(self):
        parsed, _ = self.parser.parse('Task-1 | done | Something', 1)
        assert parsed.status == 'done'

    def test__parse__status__blocked(self):
        parsed, _ = self.parser.parse('Task-1 | blocked | Something', 1)
        assert parsed.status == 'blocked'

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Cases
    # ═══════════════════════════════════════════════════════════════════════════

    def test__parse__error__missing_pipes(self):
        parsed, error = self.parser.parse('just some text', 3)
        assert parsed is None
        assert error  is not None
        assert error.line_number == 3
        assert error.raw_line    == 'just some text'
        assert 'Expected format' in error.message

    def test__parse__error__one_pipe(self):
        parsed, error = self.parser.parse('Task-1 | todo', 2)
        assert parsed is None
        assert error  is not None
        assert 'Expected format' in error.message

    def test__parse__error__empty_label(self):
        parsed, error = self.parser.parse(' | todo | something', 1)
        assert parsed is None
        assert error  is not None
        assert 'Label is empty' in error.message

    def test__parse__error__empty_status(self):
        parsed, error = self.parser.parse('Task-1 |  | something', 1)
        assert parsed is None
        assert error  is not None
        assert 'Status is empty' in error.message
