from Common.models import *
from rest_framework.settings import api_settings
from rest_framework.utils import html, model_meta, representation
from collections import Mapping, OrderedDict

from rest_framework import serializers

from rest_framework.utils.field_mapping import (
    ClassLookupDict, get_field_kwargs, get_nested_relation_kwargs,
    get_relation_kwargs, get_url_kwargs
)

from rest_framework.relations import (  # NOQA # isort:skip
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField, StringRelatedField,
)


def serializerHash(data):
    return make_hash(data)

class WithHashSerializerMixin(object):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['hash'] = serializerHash(ret)
        return ret

class CreatorIsAuthenticatedUserMixin(object):

    def get_creator_alias(self):
        return "creator"

    def to_internal_value(self, data):
        if(isinstance(data, dict)):
            data.update({"creator": self.context.get("request").user.id})
        else:
            for d in data:
                d.update({"creator": self.context.get("request").user.id})
        return super().to_internal_value(data)

class RemoveFieldsOnCreationMixin(object):
    def to_internal_value(self, data):
        toRemove = self.get_remove_fields_on_creation()
        for remove in toRemove:
            data.pop(remove, None)
        return super().to_internal_value(data)

    def get_remove_fields_on_creation(self):
        if(hasattr(self, "Meta") and hasattr(self.Meta, 'remove_fields_on_creation')):
            return self.Meta.remove_fields_on_creation
        else:
            return []

class ReadNestedWriteFlatMixin(object):

    def __init__(self, *args, **kwargs):
        self.reading = False
        return super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        self.reading = True
        ret = super().to_representation(instance)
        self.reading = False
        return ret

    def to_internal_value(self, data):
        self.reading = False
        ret = super().to_internal_value(data)
        return ret

    def build_relational_field(self, field_name, relation_info):
        """
        Create fields for forward and reverse relationships.
        """
        field_kwargs = get_relation_kwargs(field_name, relation_info)
        field_class = self.serializer_related_field


        to_field = field_kwargs.pop('to_field', None)
        if to_field and not relation_info.reverse and not relation_info.related_model._meta.get_field(to_field).primary_key:
            field_kwargs['slug_field'] = to_field
            field_class = self.serializer_related_to_field

        # `view_name` is only valid for hyperlinked relationships.
        if not issubclass(field_class, HyperlinkedRelatedField):
            field_kwargs.pop('view_name', None)
        
        #here is the hack, if we are serializing an object and this field
        #is meant to be replaced, change the field_class to what's
        #specified in Meta
        if(self.reading and hasattr(self, "Meta") and 
                hasattr(self.Meta, "read_nested_fields") and 
                field_name in self.Meta.read_nested_fields):
            field_class = self.Meta.read_nested_fields.get(field_name)
            field_kwargs = {}

        return field_class, field_kwargs
