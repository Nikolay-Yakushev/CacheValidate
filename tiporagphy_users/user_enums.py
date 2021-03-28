from enum import Enum

#
class UserTypesEnums(Enum):
    author = "author"
    writer = "writer"
    publisher = "publisher"

    @classmethod
    def get_user_types(cls):
        return [(type.name, type.value) for type in cls]


# class UserGroupsEnums(Enum):
#     authors = "authors"
#     writers = "writers"
#     publishers = "publishers"
#
#     @classmethod
#     def get_group_types(cls):
#         return [(type.name, type.value) for type in cls]
