# ═══════════════════════════════════════════════════════════════════════════════
# Comments__Service - Business logic for comment CRUD operations
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                         import List
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                    import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                    import Timestamp_Now
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                 import Safe_Str__Node_Type, Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.schemas.issues.Schema__Comment                      import Schema__Comment__List__Response, Schema__Comment__Create__Request, Schema__Comment__Response, Schema__Comment, Schema__Comment__Update__Request, Schema__Comment__Delete__Response
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository     import Graph__Repository


class Comments__Service(Type_Safe):                                              # Comment business logic service
    repository : Graph__Repository = None                                                   # Graph__Repository instance

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Comments
    # ═══════════════════════════════════════════════════════════════════════════════

    def list_comments(self                              ,                        # List all comments on a node
                      node_type : Safe_Str__Node_Type   ,
                      label     : Safe_Str__Node_Label
                 ) -> Schema__Comment__List__Response:
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Comment__List__Response(success  = False                     ,
                                                   comments = []                        ,
                                                   total    = 0                         ,
                                                   message  = f'Node not found: {label}')

        raw_comments = node.properties.get('comments', []) if node.properties else []
        comments     = self._parse_comments(raw_comments)

        return Schema__Comment__List__Response(success  = True          ,
                                               comments = comments      ,
                                               total    = len(comments) )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Comment
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_comment(self                                    ,                 # Add comment to node
                       node_type : Safe_Str__Node_Type         ,
                       label     : Safe_Str__Node_Label        ,
                       request   : Schema__Comment__Create__Request
                  ) -> Schema__Comment__Response:
        # Validate request
        if not request.text or str(request.text).strip() == '':
            return Schema__Comment__Response(success = False                    ,
                                             message = 'Comment text is required')

        if not request.author or str(request.author).strip() == '':
            return Schema__Comment__Response(success = False                   ,
                                             message = 'Author is required'    )

        # Load node
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Comment__Response(success = False                     ,
                                             message = f'Node not found: {label}')

        # Create comment with server-generated ID and timestamp
        now     = Timestamp_Now()
        comment = Schema__Comment(id         = Obj_Id()       ,
                                  author     = request.author ,
                                  text       = request.text   ,
                                  created_at = now            ,
                                  updated_at = now            )

        # Add to node properties
        if node.properties is None:
            node.properties = {}
        if 'comments' not in node.properties:
            node.properties['comments'] = []

        node.properties['comments'].append(comment.json())
        node.updated_at = now

        # Save node
        if self.repository.node_save(node) is False:
            return Schema__Comment__Response(success = False                  ,
                                             message = 'Failed to save node'  )

        return Schema__Comment__Response(success = True    ,
                                         comment = comment )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Single Comment
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_comment(self                              ,                          # Get single comment by ID
                    node_type  : Safe_Str__Node_Type  ,
                    label      : Safe_Str__Node_Label ,
                    comment_id : str
               ) -> Schema__Comment__Response:
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Comment__Response(success = False                     ,
                                             message = f'Node not found: {label}')

        raw_comments = node.properties.get('comments', []) if node.properties else []

        for raw in raw_comments:
            if raw.get('id') == comment_id:
                comment = self._parse_comment(raw)
                return Schema__Comment__Response(success = True    ,
                                                 comment = comment )

        return Schema__Comment__Response(success = False                              ,
                                         message = f'Comment not found: {comment_id}')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Comment
    # ═══════════════════════════════════════════════════════════════════════════════

    def update_comment(self                                    ,                 # Edit comment text
                       node_type  : Safe_Str__Node_Type        ,
                       label      : Safe_Str__Node_Label       ,
                       comment_id : str                        ,
                       request    : Schema__Comment__Update__Request
                  ) -> Schema__Comment__Response:
        # Validate request
        if not request.text or str(request.text).strip() == '':
            return Schema__Comment__Response(success = False                     ,
                                             message = 'Comment text is required')

        # Load node
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Comment__Response(success = False                     ,
                                             message = f'Node not found: {label}')

        raw_comments = node.properties.get('comments', []) if node.properties else []

        # Find and update comment
        found   = False
        updated = None
        now     = Timestamp_Now()

        for raw in raw_comments:
            if raw.get('id') == comment_id:
                raw['text']       = str(request.text)
                raw['updated_at'] = int(now)
                updated           = self._parse_comment(raw)
                found             = True
                break

        if not found:
            return Schema__Comment__Response(success = False                              ,
                                             message = f'Comment not found: {comment_id}')

        # Save node
        node.properties['comments'] = raw_comments
        node.updated_at             = now

        if self.repository.node_save(node) is False:
            return Schema__Comment__Response(success = False                 ,
                                             message = 'Failed to save node' )

        return Schema__Comment__Response(success = True    ,
                                         comment = updated )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Comment
    # ═══════════════════════════════════════════════════════════════════════════════

    def delete_comment(self                              ,                       # Remove comment from node
                       node_type  : Safe_Str__Node_Type  ,
                       label      : Safe_Str__Node_Label ,
                       comment_id : str
                  ) -> Schema__Comment__Delete__Response:
        # Load node
        node = self.repository.node_load(node_type = node_type ,
                                         label     = label     )
        if node is None:
            return Schema__Comment__Delete__Response(success    = False                     ,
                                                     deleted    = False                     ,
                                                     comment_id = comment_id                ,
                                                     message    = f'Node not found: {label}')

        raw_comments = node.properties.get('comments', []) if node.properties else []
        original_len = len(raw_comments)

        # Filter out the comment to delete
        raw_comments = [c for c in raw_comments if c.get('id') != comment_id]

        if len(raw_comments) == original_len:
            return Schema__Comment__Delete__Response(success    = False                              ,
                                                     deleted    = False                              ,
                                                     comment_id = comment_id                         ,
                                                     message    = f'Comment not found: {comment_id}')

        # Save node
        node.properties['comments'] = raw_comments
        node.updated_at             = Timestamp_Now()

        if self.repository.node_save(node) is False:
            return Schema__Comment__Delete__Response(success    = False                 ,
                                                     deleted    = False                 ,
                                                     comment_id = comment_id            ,
                                                     message    = 'Failed to save node' )

        return Schema__Comment__Delete__Response(success    = True       ,
                                                 deleted    = True       ,
                                                 comment_id = comment_id )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _parse_comments(self, raw_comments: list) -> List[Schema__Comment]:      # Parse raw dicts to Schema__Comment
        comments = []
        for raw in raw_comments:
            comment = self._parse_comment(raw)
            if comment:
                comments.append(comment)
        return comments

    def _parse_comment(self, raw: dict) -> Schema__Comment:                      # Parse single raw dict
        if not raw:
            return None

        try:
            return Schema__Comment(id         = Obj_Id(raw.get('id', str(Obj_Id())))                           ,
                                   author     = raw.get('author', 'unknown')                                   ,
                                   text       = raw.get('text', '')                                            ,
                                   created_at = Timestamp_Now(raw.get('created_at', raw.get('timestamp', 0)))  ,
                                   updated_at = Timestamp_Now(raw.get('updated_at', raw.get('created_at', 0))) )
        except Exception:
            return None