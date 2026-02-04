# ═══════════════════════════════════════════════════════════════════════════════
# test_Path__Handler__Graph_Node - Unit tests for graph path generation
# Tests path generation for nodes, attachments, indices, and config files
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Objects                                                                          import base_classes
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                     import Safe_Str__Node_Type, Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.service.issues.storage.Path__Handler__Graph_Node        import Path__Handler__Graph_Node


class test_Path__Handler__Graph_Node(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - path handler is stateless
        cls.path_handler = Path__Handler__Graph_Node()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test initialization and defaults
        with Path__Handler__Graph_Node() as _:
            assert type(_)            is Path__Handler__Graph_Node
            assert base_classes(_)    == [Type_Safe, object]
            assert str(_.base_path)   == '.issues'                               # Default base path

    def test__init____custom_base_path(self):                                    # Test custom base path
        with Path__Handler__Graph_Node(base_path='/custom/path') as _:
            assert str(_.base_path)   == '/custom/path'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_node(self):                                               # Test node file path generation
        path = self.path_handler.path_for_node(node_type = Safe_Str__Node_Type('bug')    ,
                                               label     = Safe_Str__Node_Label('Bug-27'))

        assert path == '.issues/data/bug/Bug-27/node.json'

    def test__path_for_node__task(self):                                         # Test task node path
        path = self.path_handler.path_for_node(node_type = Safe_Str__Node_Type('task')   ,
                                               label     = Safe_Str__Node_Label('Task-1'))

        assert path == '.issues/data/task/Task-1/node.json'

    def test__path_for_node__feature(self):                                      # Test feature node path
        path = self.path_handler.path_for_node(node_type = Safe_Str__Node_Type('feature'),
                                               label     = Safe_Str__Node_Label('Feature-99'))

        assert path == '.issues/data/feature/Feature-99/node.json'

    def test__path_for_node_folder(self):                                        # Test node folder path
        path = self.path_handler.path_for_node_folder(node_type = Safe_Str__Node_Type('bug')    ,
                                                      label     = Safe_Str__Node_Label('Bug-27'))

        assert path == '.issues/data/bug/Bug-27'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Attachment Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_attachment(self):                                         # Test attachment file path
        path = self.path_handler.path_for_attachment(node_type = Safe_Str__Node_Type('bug')    ,
                                                     label     = Safe_Str__Node_Label('Bug-27'),
                                                     filename  = 'screenshot.png'              )

        assert path == '.issues/data/bug/Bug-27/attachments/screenshot.png'

    def test__path_for_attachment__multiple_extensions(self):                    # Test attachment with complex filename
        path = self.path_handler.path_for_attachment(node_type = Safe_Str__Node_Type('task')   ,
                                                     label     = Safe_Str__Node_Label('Task-5'),
                                                     filename  = 'error.log.txt'               )

        assert path == '.issues/data/task/Task-5/attachments/error.log.txt'

    def test__path_for_attachments_folder(self):                                 # Test attachments folder path
        path = self.path_handler.path_for_attachments_folder(node_type = Safe_Str__Node_Type('bug')    ,
                                                             label     = Safe_Str__Node_Label('Bug-27'))

        assert path == '.issues/data/bug/Bug-27/attachments'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Index Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_type_index(self):                                         # Test per-type index path
        path = self.path_handler.path_for_type_index(node_type = Safe_Str__Node_Type('bug'))

        assert path == '.issues/data/bug/_index.json'

    def test__path_for_type_index__task(self):                                   # Test task type index path
        path = self.path_handler.path_for_type_index(node_type = Safe_Str__Node_Type('task'))

        assert path == '.issues/data/task/_index.json'

    def test__path_for_global_index(self):                                       # Test global index path
        path = self.path_handler.path_for_global_index()

        assert path == '.issues/_index.json'

    def test__path_for_type_folder(self):                                        # Test type folder path
        path = self.path_handler.path_for_type_folder(node_type = Safe_Str__Node_Type('feature'))

        assert path == '.issues/data/feature'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Config Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__path_for_node_types(self):                                         # Test node-types.json path
        path = self.path_handler.path_for_node_types()

        assert path == '.issues/config/node-types.json'

    def test__path_for_link_types(self):                                         # Test link-types.json path
        path = self.path_handler.path_for_link_types()

        assert path == '.issues/config/link-types.json'

    def test__path_for_settings(self):                                           # Test settings.json path
        path = self.path_handler.path_for_settings()

        assert path == '.issues/config/settings.json'

    def test__path_for_config_folder(self):                                      # Test config folder path
        path = self.path_handler.path_for_config_folder()

        assert path == '.issues/config'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__label_from_type_and_index(self):                                   # Test label generation
        label = self.path_handler.label_from_type_and_index(node_type  = Safe_Str__Node_Type('bug'),
                                                            node_index = 27                        )

        assert str(label) == 'Bug-27'

    def test__label_from_type_and_index__task(self):                             # Test task label generation
        label = self.path_handler.label_from_type_and_index(node_type  = Safe_Str__Node_Type('task'),
                                                            node_index = 1                          )

        assert str(label) == 'Task-1'

    def test__label_from_type_and_index__feature(self):                          # Test feature label generation
        label = self.path_handler.label_from_type_and_index(node_type  = Safe_Str__Node_Type('feature'),
                                                            node_index = 100                           )

        assert str(label) == 'Feature-100'

    def test__label_from_type_and_index__person(self):                           # Test person label generation
        label = self.path_handler.label_from_type_and_index(node_type  = Safe_Str__Node_Type('person'),
                                                            node_index = 5                             )

        assert str(label) == 'Person-5'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Custom Base Path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__custom_base_path__node(self):                                      # Test paths with custom base
        with Path__Handler__Graph_Node(base_path='/repo/.tracking') as handler:
            path = handler.path_for_node(node_type = Safe_Str__Node_Type('bug')    ,
                                         label     = Safe_Str__Node_Label('Bug-1') )

            assert path == '/repo/.tracking/data/bug/Bug-1/node.json'

    def test__custom_base_path__global_index(self):                              # Test global index with custom base
        with Path__Handler__Graph_Node(base_path='/data/issues') as handler:
            path = handler.path_for_global_index()

            assert path == '/data/issues/_index.json'

    def test__custom_base_path__config(self):                                    # Test config with custom base
        with Path__Handler__Graph_Node(base_path='project/.issues') as handler:
            path = handler.path_for_node_types()

            assert path == 'project/.issues/config/node-types.json'
