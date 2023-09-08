"""Resolver for resolving attributes on Django models."""
from typing import Dict, Optional

from odin import Field
from odin.mapping import FieldResolverBase
from odin.utils import getmeta


class ModelFieldResolver(FieldResolverBase):
    """Field resolver for Django models."""

    def get_field_dict(self) -> Dict[str, Optional[Field]]:
        """Get a dictionary of fields from the source object."""
        meta = getmeta(self.obj)
        return {f.attname: f for f in meta.fields}