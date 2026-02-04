# ═══════════════════════════════════════════════════════════════════════════════
# Test cases for v0.2.18 backend changes
# Run with: pytest tests/unit/test_v0_2_18_changes.py -v
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                 import Safe_Str__Node_Type, Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Request         import Schema__Node__Create__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Update__Request         import Schema__Node__Update__Request
from tests.unit.Html_Transformation_Workbench__Test_Objs                                            import setup__html_transformation_workbench__test_objs


class test_Node__Service__deep_merge(TestCase):
    """Test deep merge functionality for properties."""

    @classmethod
    def setUpClass(cls):

        cls.test_objs    = setup__html_transformation_workbench__test_objs()
        cls.node_service = cls.test_objs.fast_api.node_service

    def test_deep_merge_properties__preserves_existing_keys(self):
        # Create node with existing properties
        create_request = Schema__Node__Create__Request(title      = 'Test Node'         ,
                                                       node_type  = 'task'              ,
                                                       properties = {'severity': 'high' ,
                                                                     'component': 'auth'})
        create_response = self.node_service.create_node(create_request)
        assert create_response.success is True

        label     = create_response.node.label
        node_type = create_response.node.node_type

        # Update with partial properties (add comments)
        update_request = Schema__Node__Update__Request(
            properties = {'comments': [{'id': '123', 'text': 'test comment'}]}
        )
        update_response = self.node_service.update_node(node_type = node_type      ,
                                                        label     = label          ,
                                                        request   = update_request )

        # Verify deep merge - original properties preserved
        assert update_response.success is True
        assert update_response.node.properties['severity']  == 'high'
        assert update_response.node.properties['component'] == 'auth'
        assert update_response.node.properties['comments']  == [{'id': '123', 'text': 'test comment'}]

    def test_deep_merge_properties__merges_nested_dicts(self):
        # Create node with nested properties
        create_request = Schema__Node__Create__Request(title      = 'Test Node'               ,
                                                       node_type  = 'task'                    ,
                                                       properties = {'meta': {'created_by': 'human',
                                                                              'version': 1}})
        create_response = self.node_service.create_node(create_request)
        label     = create_response.node.label
        node_type = create_response.node.node_type

        # Update nested property
        update_request = Schema__Node__Update__Request(
            properties = {'meta': {'version': 2, 'updated_by': 'claude'}}
        )
        update_response = self.node_service.update_node(node_type = node_type      ,
                                                        label     = label          ,
                                                        request   = update_request )

        # Verify nested merge
        assert update_response.node.properties['meta']['created_by'] == 'human'      # Preserved
        assert update_response.node.properties['meta']['version']    == 2            # Updated
        assert update_response.node.properties['meta']['updated_by'] == 'claude'     # Added

    def test_deep_merge_properties__replaces_non_dict_values(self):
        create_request = Schema__Node__Create__Request(title      = 'Test Node'       ,
                                                       node_type  = 'task'            ,
                                                       properties = {'tags': ['old']})
        create_response = self.node_service.create_node(create_request)
        label     = create_response.node.label
        node_type = create_response.node.node_type

        # Update list property (should replace, not merge)
        update_request = Schema__Node__Update__Request(
            properties = {'tags': ['new1', 'new2']}
        )
        update_response = self.node_service.update_node(node_type = node_type      ,
                                                        label     = label          ,
                                                        request   = update_request )

        # List is replaced, not merged
        assert update_response.node.properties['tags'] == ['new1', 'new2']


    """Test graph traversal functionality."""


    def test_get_node_graph__returns_root_node(self):
        # Create a single node
        create_request = Schema__Node__Create__Request(title     = 'Root Node' ,
                                                       node_type = 'feature'   )
        create_response = self.node_service.create_node(create_request)
        label     = create_response.node.label
        node_type = create_response.node.node_type

        # Get graph with depth=0 (just root)
        graph_response = self.node_service.get_node_graph(node_type = node_type ,
                                                          label     = label     ,
                                                          depth     = 0         )

        assert graph_response.success is True
        assert str(graph_response.root) == str(label)
        assert len(graph_response.nodes) == 1
        assert graph_response.nodes[0].label == label

    def test_get_node_graph__not_found(self):


        graph_response = self.node_service.get_node_graph(node_type = Safe_Str__Node_Type('task')           ,
                                                          label     = Safe_Str__Node_Label('NonExistent-99'),
                                                          depth     = 1                                     )

        assert graph_response.success is False
        assert 'not found' in graph_response.message.lower()

    def test_get_node_graph__caps_depth_at_3(self):
        create_request = Schema__Node__Create__Request(title     = 'Test Node' ,
                                                       node_type = 'task'      )
        create_response = self.node_service.create_node(create_request)
        label     = create_response.node.label
        node_type = create_response.node.node_type

        # Request depth=10, should be capped to 3
        graph_response = self.node_service.get_node_graph(node_type = node_type ,
                                                          label     = label     ,
                                                          depth     = 10        )

        assert graph_response.success is True
        assert graph_response.depth == 3                                         # Capped



    """Test that multiline descriptions preserve newlines."""

    def test_description__preserves_newlines_on_create(self):
        description = "Line 1\n\nLine 2\n- Bullet 1\n- Bullet 2"

        create_request = Schema__Node__Create__Request(title       = 'Multiline Test' ,
                                                       node_type   = 'task'           ,
                                                       description = description      )
        create_response = self.node_service.create_node(create_request)

        assert create_response.success is True
        assert '\n' in str(create_response.node.description)                     # Newlines preserved

    def test_description__preserves_newlines_through_save_load_cycle(self):
        description = "First paragraph.\n\nSecond paragraph.\n\n## Header\n- Item"

        create_request = Schema__Node__Create__Request(title       = 'Save Load Test' ,
                                                       node_type   = 'task'           ,
                                                       description = description      )
        create_response = self.node_service.create_node(create_request)
        label     = create_response.node.label
        node_type = create_response.node.node_type

        # Load the node back
        loaded_node = self.node_service.get_node(node_type = node_type ,
                                                 label     = label     )

        # Verify newlines survived
        loaded_description = str(loaded_node.description)
        assert '\n\n' in loaded_description                                      # Double newlines preserved
        assert '## Header' in loaded_description
        assert '_' not in loaded_description or 'Header' in loaded_description   # No underscore corruption