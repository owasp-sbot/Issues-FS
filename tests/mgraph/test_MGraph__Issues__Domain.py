# ═══════════════════════════════════════════════════════════════════════════════
# test_MGraph__Issues__Domain - Tests for MGraph domain layer (B18)
# Validates indexes (label, path, parent) and query methods
# (add_node, get_node_by_label, get_node_by_path, add_edge,
#  get_children, get_ancestors, clear, all_nodes)
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                                   import Edge_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                    import Obj_Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                   import Safe_Str__File__Path
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                  import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status
from issues_fs.mgraph.Schema__MGraph__Issues                                                        import Schema__MGraph__Issue__Node, Schema__MGraph__Issue__Edge, Schema__MGraph__Issues__Data
from issues_fs.mgraph.MGraph__Issues__Domain                                                        import MGraph__Issues__Domain


class test_MGraph__Issues__Domain(TestCase):

    def setUp(self):                                                             # Fresh domain for each test
        self.domain = MGraph__Issues__Domain()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def make_node(self                        ,                                  # Create test node
                  label     = 'Bug-1'         ,
                  node_type = 'bug'           ,
                  title     = 'Test bug'      ,
                  status    = 'todo'          ,
                  file_path = 'data/bug/Bug-1',
                  node_id   = None            ):
        if node_id is None:
            node_id = Node_Id()
        return Schema__MGraph__Issue__Node(node_id   = node_id                                  ,
                                            label     = Safe_Str__Node_Label(label)              ,
                                            title     = Safe_Str__Text(title)                    ,
                                            node_type = Safe_Str__Node_Type(node_type)           ,
                                            status    = Safe_Str__Status(status)                 ,
                                            file_path = Safe_Str__File__Path(file_path)          )

    def make_edge(self                        ,                                  # Create test edge
                  source_id = None            ,
                  target_id = None            ,
                  edge_type = 'contains'      ):
        return Schema__MGraph__Issue__Edge(edge_id   = Edge_Id()                            ,
                                            source_id = source_id or Node_Id()               ,
                                            target_id = target_id or Node_Id()               ,
                                            edge_type = Safe_Str__Text(edge_type)            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with MGraph__Issues__Domain() as _:
            assert type(_)                is MGraph__Issues__Domain
            assert type(_.data)           is Schema__MGraph__Issues__Data
            assert type(_.index_by_label) is dict
            assert type(_.index_by_path)  is dict
            assert type(_.index_by_parent) is dict
            assert len(_.data.nodes)      == 0
            assert len(_.data.edges)      == 0

    def test__inherits_type_safe(self):                                          # Verify Type_Safe inheritance
        assert issubclass(MGraph__Issues__Domain, Type_Safe)

    # ═══════════════════════════════════════════════════════════════════════════════
    # add_node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__add_node__stores_node(self):                                       # Test node is stored
        node    = self.make_node()
        node_id = self.domain.add_node(node)

        assert node_id == str(node.node_id)
        assert len(self.domain.data.nodes) == 1

    def test__add_node__updates_label_index(self):                               # Test label index is updated
        node = self.make_node(label='Task-1')
        self.domain.add_node(node)

        assert 'Task-1' in self.domain.index_by_label
        assert self.domain.index_by_label['Task-1'] == str(node.node_id)

    def test__add_node__updates_path_index(self):                                # Test path index is updated
        node = self.make_node(file_path='data/bug/Bug-1')
        self.domain.add_node(node)

        assert 'data/bug/Bug-1' in self.domain.index_by_path
        assert self.domain.index_by_path['data/bug/Bug-1'] == str(node.node_id)

    def test__add_node__multiple_nodes(self):                                    # Test adding multiple nodes
        node1 = self.make_node(label='Bug-1' , file_path='data/bug/Bug-1' )
        node2 = self.make_node(label='Task-1', node_type='task', file_path='data/task/Task-1')

        self.domain.add_node(node1)
        self.domain.add_node(node2)

        assert len(self.domain.data.nodes)  == 2
        assert len(self.domain.index_by_label) == 2

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_node_by_label Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_node_by_label__found(self):                                    # Test successful lookup
        node = self.make_node(label='Bug-1')
        self.domain.add_node(node)

        result = self.domain.get_node_by_label(Safe_Str__Node_Label('Bug-1'))

        assert result is not None
        assert str(result.label) == 'Bug-1'

    def test__get_node_by_label__not_found(self):                                # Test missing label
        result = self.domain.get_node_by_label(Safe_Str__Node_Label('Bug-999'))

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_node_by_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_node_by_path__found(self):                                     # Test successful path lookup
        node = self.make_node(file_path='data/bug/Bug-1')
        self.domain.add_node(node)

        result = self.domain.get_node_by_path('data/bug/Bug-1')

        assert result is not None
        assert str(result.label) == 'Bug-1'

    def test__get_node_by_path__not_found(self):                                 # Test missing path
        result = self.domain.get_node_by_path('data/bug/Bug-999')

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_node_by_id Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_node_by_id__found(self):                                       # Test successful ID lookup
        node    = self.make_node()
        node_id = self.domain.add_node(node)

        result = self.domain.get_node_by_id(node_id)

        assert result is not None
        assert str(result.label) == 'Bug-1'

    def test__get_node_by_id__not_found(self):                                   # Test missing ID
        result = self.domain.get_node_by_id('nonexistent')

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # add_edge Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__add_edge__stores_edge(self):                                       # Test edge is stored
        edge    = self.make_edge()
        edge_id = self.domain.add_edge(edge)

        assert edge_id == str(edge.edge_id)
        assert len(self.domain.data.edges) == 1

    def test__add_edge__updates_parent_index_for_contains(self):                 # Test parent index for 'contains'
        parent = self.make_node(label='Project-1', node_type='project', file_path='data/project/Project-1')
        child  = self.make_node(label='Task-1'   , node_type='task'   , file_path='data/task/Task-1'      )

        self.domain.add_node(parent)
        self.domain.add_node(child)

        edge = self.make_edge(source_id = parent.node_id ,
                              target_id = child.node_id  ,
                              edge_type = 'contains'     )

        self.domain.add_edge(edge)

        parent_id_str = str(parent.node_id)
        child_id_str  = str(child.node_id)

        assert parent_id_str in self.domain.index_by_parent
        assert child_id_str  in self.domain.index_by_parent[parent_id_str]

    def test__add_edge__non_contains_skips_parent_index(self):                   # Test non-contains edges
        edge = self.make_edge(edge_type='relates-to')
        self.domain.add_edge(edge)

        assert len(self.domain.index_by_parent) == 0

    def test__add_edge__no_duplicate_children(self):                             # Test duplicate child prevention
        parent_id = Node_Id()
        child_id  = Node_Id()

        edge1 = self.make_edge(source_id=parent_id, target_id=child_id, edge_type='contains')
        edge2 = self.make_edge(source_id=parent_id, target_id=child_id, edge_type='contains')

        self.domain.add_edge(edge1)
        self.domain.add_edge(edge2)

        parent_id_str = str(parent_id)

        assert len(self.domain.index_by_parent[parent_id_str]) == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_children Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_children__returns_child_nodes(self):                           # Test children retrieval
        parent = self.make_node(label='Project-1', node_type='project', file_path='data/project/Project-1')
        child1 = self.make_node(label='Task-1'   , node_type='task'   , file_path='data/task/Task-1'      )
        child2 = self.make_node(label='Task-2'   , node_type='task'   , file_path='data/task/Task-2'      )

        self.domain.add_node(parent)
        self.domain.add_node(child1)
        self.domain.add_node(child2)

        self.domain.add_edge(self.make_edge(source_id=parent.node_id, target_id=child1.node_id))
        self.domain.add_edge(self.make_edge(source_id=parent.node_id, target_id=child2.node_id))

        children = self.domain.get_children(parent.node_id)

        labels = [str(c.label) for c in children]

        assert len(children) == 2
        assert 'Task-1' in labels
        assert 'Task-2' in labels

    def test__get_children__no_children(self):                                   # Test node with no children
        node = self.make_node()
        self.domain.add_node(node)

        children = self.domain.get_children(node.node_id)

        assert len(children) == 0

    def test__get_children_by_label(self):                                       # Test children lookup by label
        parent = self.make_node(label='Project-1', node_type='project', file_path='data/project/Project-1')
        child  = self.make_node(label='Task-1'   , node_type='task'   , file_path='data/task/Task-1'      )

        self.domain.add_node(parent)
        self.domain.add_node(child)
        self.domain.add_edge(self.make_edge(source_id=parent.node_id, target_id=child.node_id))

        children = self.domain.get_children_by_label(Safe_Str__Node_Label('Project-1'))

        assert len(children) == 1
        assert str(children[0].label) == 'Task-1'

    def test__get_children_by_label__not_found(self):                            # Test with nonexistent label
        result = self.domain.get_children_by_label(Safe_Str__Node_Label('Bug-999'))

        assert result == []

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_ancestors Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_ancestors__returns_path_to_root(self):                         # Test ancestor chain
        root    = self.make_node(label='Project-1', node_type='project', file_path='data/project/Project-1')
        middle  = self.make_node(label='Version-1', node_type='version', file_path='data/version/Version-1')
        leaf    = self.make_node(label='Task-1'   , node_type='task'   , file_path='data/task/Task-1'      )

        self.domain.add_node(root)
        self.domain.add_node(middle)
        self.domain.add_node(leaf)

        self.domain.add_edge(self.make_edge(source_id=root.node_id  , target_id=middle.node_id))
        self.domain.add_edge(self.make_edge(source_id=middle.node_id, target_id=leaf.node_id  ))

        ancestors = self.domain.get_ancestors(leaf.node_id)

        labels = [str(a.label) for a in ancestors]

        assert len(ancestors) == 2
        assert labels[0]      == 'Version-1'                                     # Immediate parent first
        assert labels[1]      == 'Project-1'                                     # Root last

    def test__get_ancestors__root_node_has_none(self):                           # Test root has no ancestors
        root = self.make_node()
        self.domain.add_node(root)

        ancestors = self.domain.get_ancestors(root.node_id)

        assert len(ancestors) == 0

    def test__get_ancestors_by_label(self):                                      # Test ancestors by label
        root = self.make_node(label='Project-1', node_type='project', file_path='data/project/Project-1')
        leaf = self.make_node(label='Task-1'   , node_type='task'   , file_path='data/task/Task-1'      )

        self.domain.add_node(root)
        self.domain.add_node(leaf)
        self.domain.add_edge(self.make_edge(source_id=root.node_id, target_id=leaf.node_id))

        ancestors = self.domain.get_ancestors_by_label(Safe_Str__Node_Label('Task-1'))

        assert len(ancestors)        == 1
        assert str(ancestors[0].label) == 'Project-1'

    def test__get_ancestors_by_label__not_found(self):                           # Test with nonexistent label
        result = self.domain.get_ancestors_by_label(Safe_Str__Node_Label('Bug-999'))

        assert result == []

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Operation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__clear__resets_all(self):                                            # Test clear resets everything
        node = self.make_node()
        edge = self.make_edge()

        self.domain.add_node(node)
        self.domain.add_edge(edge)

        assert self.domain.node_count() == 1
        assert self.domain.edge_count() == 1

        self.domain.clear()

        assert self.domain.node_count()          == 0
        assert self.domain.edge_count()          == 0
        assert len(self.domain.index_by_label)   == 0
        assert len(self.domain.index_by_path)    == 0
        assert len(self.domain.index_by_parent)  == 0

    def test__all_nodes__returns_all(self):                                      # Test all_nodes returns all nodes
        node1 = self.make_node(label='Bug-1' , file_path='data/bug/Bug-1' )
        node2 = self.make_node(label='Task-1', node_type='task', file_path='data/task/Task-1')

        self.domain.add_node(node1)
        self.domain.add_node(node2)

        nodes  = self.domain.all_nodes()
        labels = [str(n.label) for n in nodes]

        assert len(nodes)  == 2
        assert 'Bug-1'  in labels
        assert 'Task-1' in labels

    def test__all_edges__returns_all(self):                                      # Test all_edges returns all edges
        edge1 = self.make_edge()
        edge2 = self.make_edge(edge_type='relates-to')

        self.domain.add_edge(edge1)
        self.domain.add_edge(edge2)

        edges = self.domain.all_edges()

        assert len(edges) == 2

    def test__node_count(self):                                                  # Test node count
        assert self.domain.node_count() == 0

        self.domain.add_node(self.make_node())

        assert self.domain.node_count() == 1

    def test__edge_count(self):                                                  # Test edge count
        assert self.domain.edge_count() == 0

        self.domain.add_edge(self.make_edge())

        assert self.domain.edge_count() == 1
