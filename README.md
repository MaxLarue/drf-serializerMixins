# drf-serializerMixins
A few mixins to use with django-rest-framework's ModelSerializer


## WithHashSerializerMixin
Will add a hash field to object upon serialization. If the representation is nested, this will affect the hash.
In order to account for all changes, this mixin should be used last (rightMost before base class).

Watch out this could be a performance issue on really large data (like a deeply nested representation).

Example:
```python
  class TodoSerializer(WithHashSerializerMixin, serializers.ModelSerializer):
    class Meta:
      model = ToDo
      fields = ("__all__",)
```

If the model ToDo has the following fields : 
*. what : CharField
*. when : DatetimeField

then the output of ModelSerializer might be:
```python
  {"id": 1, "what": "write docs", "when": "2018-04-30T19:25:20.119974Z"}
```
When using WithHashSerializerMixin:
```python
  {"id": 1, "what": "write docs", "when": "2018-04-30T19:25:20.119974Z", "hash": -6564626725321286430}
```

## CreatorIsAuthenticatedUserMixin
Will infer the value for creator from the currrently authenticated user.
You can define another field than creator to hold this value

Example:
```python
  class TodoSerializer(CreatorIsAuthenticatedUserMixin, serializers.ModelSerializer):
    class Meta:
      model = ToDo
      fields = ("__all__",)
```

If the model ToDo has the following fields : 
*. what : CharField
*. when : DatetimeField
*. creator : ForeignKey("user", ...)

Posting the following json:
```python
  {"what": "write docs", "when": "2018-04-30T19:25:20.119974Z"}
```

Will create a new ToDo object where creator is the user authenticated when posting

Changing the field:
Maybe you don't want a creator field in your model or you called it owner, etc...
In that case you can change the field creator with another.
You'll need to override the get_creator_alias(self) method to provide the name of the field

Example:
```python
  class TodoSerializer(CreatorIsAuthenticatedUserMixin, serializers.ModelSerializer):
    class Meta:
      model = ToDo
      fields = ("__all__",)
    def get_creator_alias(self):
      return "owner"
```

## RemoveFieldsOnCreationMixin
This will remove some fields on creation.
Let's say you defined a few fields that are not to be written in your serializer,
mixin with this and specifying a toRemove iterable in the Meta class of the serializer you won't have trouble posting.

(bad) Example:
```python
  class UserSerializer(RemoveFieldsOnCreationMixin, serializers.ModelSerializer):
    class Meta:
      model = User
      fields = ("__all__",)
      toRemove = ("username",)
```


## ReadNestedWriteFlatMixin
A problem with drf is when you want to output nested representation while still using ModelSerializer. One solution is the depth option, but then you'll have to deal with writing nested. This mixins allows to serialize object to nested representation but when deserializing data to create an object, will use primary keys.

Example:
```python
  class UserSerializer(serializers.ModelSerializer):
    class Meta:
      model = User
      fields = ("__all__",)
      
  class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
      model = ToDo
      fields = ("__all__",)
      
```

serializing a todo object to JSON will look like this
```python
  {
    "id": 1, 
    "what": "write docs", 
    "when": "2018-04-30T19:25:20.119974Z",
    "creator" : {
      "id": 1,
      "username": "foobar",
      ...
    }
  }
```

but in order to post a ToDo you can simply
```python
  {"what": "write docs", "when": "2018-04-30T19:25:20.119974Z", creator: 1}
```
