from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id import Obj_Id

# we need to refactor the code to use this
class Issue_Id(Obj_Id):                                 # Obj_Id that allows empty values (needed for serialisation)
    def __new__(cls, value=None):
        if value is None or value == '':
            return str.__new__(cls, '')
        else:
            return super().__new__(cls, value)

    @classmethod
    def new(cls):                                       # helper method for the easy creation of non-empty Issue_ids
        return cls(Obj_Id())