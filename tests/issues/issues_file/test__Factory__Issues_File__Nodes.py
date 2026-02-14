# ═══════════════════════════════════════════════════════════════════════════════
# test__Factory__Issues_File__Nodes - Tests for node factory
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from issues_fs.issues.issues_file.Factory__Issues_File__Nodes                   import Factory__Issues_File__Nodes
from issues_fs.issues.issues_file.Schema__Issues_File__Line                     import Schema__Issues_File__Line
from issues_fs.schemas.graph.Schema__Node                                       import Schema__Node


class test__Factory__Issues_File__Nodes(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = Factory__Issues_File__Nodes()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.factory as _:
            assert type(_)         is Factory__Issues_File__Nodes
            assert base_classes(_) == [Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # Single Node Creation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create_node__basic(self):
        line = Schema__Issues_File__Line(label        = 'Task-1'            ,
                                         status       = 'todo'              ,
                                         description  = 'Enable logs'       ,
                                         indent_level = 0                   ,
                                         parent_label = ''                  ,
                                         cross_refs   = []                  ,
                                         line_number  = 1                   ,
                                         issue_type   = 'task'              )
        node, error = self.factory.create_node(line)
        assert error            is None
        assert node             is not None
        assert type(node)       is Schema__Node
        assert str(node.label)  == 'Task-1'
        assert str(node.status) == 'todo'
        assert str(node.title)  == 'Enable logs'
        assert str(node.node_type)  == 'task'
        assert int(node.node_index) == 1

    def test__create_node__bug(self):
        line = Schema__Issues_File__Line(label='Bug-42', status='confirmed',
                                         description='Login fails', indent_level=0,
                                         parent_label='', cross_refs=[], line_number=1,
                                         issue_type='bug')
        node, error = self.factory.create_node(line)
        assert error is None
        assert str(node.label)      == 'Bug-42'
        assert str(node.node_type)  == 'bug'
        assert int(node.node_index) == 42

    def test__create_node__hyphenated_type(self):
        line = Schema__Issues_File__Line(label='User-Journey-1', status='todo',
                                         description='Onboarding', indent_level=0,
                                         parent_label='', cross_refs=[], line_number=1,
                                         issue_type='user-journey')
        node, error = self.factory.create_node(line)
        assert error is None
        assert str(node.node_type) == 'user-journey'
        assert int(node.node_index) == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Index Extraction
    # ═══════════════════════════════════════════════════════════════════════════

    def test__extract_index(self):
        assert self.factory.extract_index('Task-1')       == 1
        assert self.factory.extract_index('Bug-42')       == 42
        assert self.factory.extract_index('Task-100')     == 100
        assert self.factory.extract_index('Sub-Task-3')   == 3
        assert self.factory.extract_index('nolabel')      == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Batch Node Creation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create_nodes__multiple(self):
        lines = [
            Schema__Issues_File__Line(label='Task-1', status='todo', description='First',
                                      indent_level=0, parent_label='', cross_refs=[],
                                      line_number=1, issue_type='task'),
            Schema__Issues_File__Line(label='Task-2', status='done', description='Second',
                                      indent_level=0, parent_label='', cross_refs=[],
                                      line_number=2, issue_type='task'),
            Schema__Issues_File__Line(label='Bug-1', status='confirmed', description='A bug',
                                      indent_level=0, parent_label='', cross_refs=[],
                                      line_number=3, issue_type='bug'),
        ]
        nodes, errors = self.factory.create_nodes(lines)
        assert len(errors) == 0
        assert len(nodes)  == 3
        assert str(nodes[0].label) == 'Task-1'
        assert str(nodes[1].label) == 'Task-2'
        assert str(nodes[2].label) == 'Bug-1'

    # ═══════════════════════════════════════════════════════════════════════════
    # Parent-Child Link Wiring
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create_nodes__parent_child_links(self):
        lines = [
            Schema__Issues_File__Line(label='Workstream-1', status='todo', description='Parent',
                                      indent_level=0, parent_label='', cross_refs=[],
                                      line_number=1, issue_type='workstream'),
            Schema__Issues_File__Line(label='Task-1', status='todo', description='Child 1',
                                      indent_level=1, parent_label='Workstream-1', cross_refs=[],
                                      line_number=2, issue_type='task'),
            Schema__Issues_File__Line(label='Task-2', status='todo', description='Child 2',
                                      indent_level=1, parent_label='Workstream-1', cross_refs=[],
                                      line_number=3, issue_type='task'),
        ]
        nodes, errors = self.factory.create_nodes(lines)
        assert len(errors) == 0
        assert len(nodes)  == 3

        parent = nodes[0]
        assert len(parent.links) == 2
        assert str(parent.links[0].verb)         == 'has-task'
        assert str(parent.links[0].target_label) == 'Task-1'
        assert str(parent.links[1].target_label) == 'Task-2'

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Reference Link Wiring
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create_nodes__cross_reference_links(self):
        lines = [
            Schema__Issues_File__Line(label='Task-1', status='todo',
                                      description='Fix login -> Bug-1',
                                      indent_level=0, parent_label='',
                                      cross_refs=['Bug-1'],
                                      line_number=1, issue_type='task'),
            Schema__Issues_File__Line(label='Bug-1', status='confirmed',
                                      description='Login broken',
                                      indent_level=0, parent_label='',
                                      cross_refs=[],
                                      line_number=2, issue_type='bug'),
        ]
        nodes, errors = self.factory.create_nodes(lines)
        assert len(errors) == 0

        task = nodes[0]
        assert len(task.links) == 1
        assert str(task.links[0].verb)         == 'relates-to'
        assert str(task.links[0].target_label) == 'Bug-1'

    def test__create_nodes__cross_ref_to_unknown_label(self):
        lines = [
            Schema__Issues_File__Line(label='Task-1', status='todo',
                                      description='Fix -> Unknown-99',
                                      indent_level=0, parent_label='',
                                      cross_refs=['Unknown-99'],
                                      line_number=1, issue_type='task'),
        ]
        nodes, errors = self.factory.create_nodes(lines)
        assert len(nodes) == 1
        assert len(nodes[0].links) == 0                                         # unknown ref silently skipped

    # ═══════════════════════════════════════════════════════════════════════════
    # Nested Hierarchy with Links
    # ═══════════════════════════════════════════════════════════════════════════

    def test__create_nodes__nested_hierarchy(self):
        lines = [
            Schema__Issues_File__Line(label='Workstream-1', status='todo', description='Top',
                                      indent_level=0, parent_label='', cross_refs=[],
                                      line_number=1, issue_type='workstream'),
            Schema__Issues_File__Line(label='Task-1', status='todo', description='Child',
                                      indent_level=1, parent_label='Workstream-1', cross_refs=[],
                                      line_number=2, issue_type='task'),
            Schema__Issues_File__Line(label='Sub-Task-1', status='todo', description='Grandchild',
                                      indent_level=2, parent_label='Task-1', cross_refs=[],
                                      line_number=3, issue_type='sub-task'),
        ]
        nodes, errors = self.factory.create_nodes(lines)
        assert len(errors) == 0
        assert len(nodes)  == 3

        workstream = nodes[0]
        task       = nodes[1]

        assert len(workstream.links) == 1                                       # has-task -> Task-1
        assert str(workstream.links[0].target_label) == 'Task-1'

        assert len(task.links) == 1                                             # has-task -> Sub-Task-1
        assert str(task.links[0].target_label) == 'Sub-Task-1'
