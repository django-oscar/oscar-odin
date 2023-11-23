"""Extended model mapper for Django models."""
from typing import Sequence, cast

from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.options import Options

from odin.mapping import MappingBase, MappingMeta
from odin.utils import getmeta


class ModelMappingMeta(MappingMeta):
    """Extended type of mapping meta."""

    def __new__(cls, name, bases, attrs):
        mapping_type = super().__new__(cls, name, bases, attrs)

        if mapping_type.to_obj is None:
            return mapping_type

        meta = cast(Options, getmeta(mapping_type.to_obj))

        # Extract out foreign field types.
        mapping_type.one_to_many_fields = one_to_many_fields = []
        mapping_type.many_to_one_fields = many_to_one_fields = []
        mapping_type.many_to_many_fields = many_to_many_fields = []
        mapping_type.foreign_key_fields = [
            field for field in meta.fields if isinstance(field, ForeignKey)
        ]

        # Break out related objects by their type
        for relation in meta.related_objects:
            if relation.many_to_many:
                many_to_many_fields.append(relation.field)
            elif relation.many_to_one:
                many_to_one_fields.append(relation.field)
            elif relation.one_to_many:
                one_to_many_fields.append(relation.field)

        return mapping_type


class ModelMapping(MappingBase, metaclass=ModelMappingMeta):
    """Definition of a mapping between two Objects."""

    exclude_fields = []
    mappings = []

    # Specific fields
    one_to_many_fields: Sequence[ManyToManyField] = []
    many_to_one_fields: Sequence[ManyToManyField] = []
    many_to_many_fields: Sequence[ManyToManyField] = []
    foreign_key_fields: Sequence[ForeignKey] = []

    def create_object(self, **field_values):
        """Create a new product model."""

        parent = super().create_object(**field_values)

        self.context["one_to_many_items"] = [
            (parent, field, field_values.pop(field.name))
            for field in self.one_to_many_fields
            if field.name in field_values
        ]
        self.context["many_to_one_items"] = [
            (parent, field, field_values.pop(field.name))
            for field in self.many_to_one_fields
            if field.name in field_values
        ]
        self.context["many_to_many_items"] = [
            (parent, field, field_values.pop(field.name))
            for field in self.many_to_many_fields
            if field.name in field_values
        ]
        self.context["foreign_key_items"] = [
            (parent, field, field_values.pop(field.name))
            for field in self.foreign_key_fields
            if field.name in field_values
        ]

        return parent
