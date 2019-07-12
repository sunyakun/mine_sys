from super_dash import jsonschema

from django.dispatch import Signal

user_register = Signal(providing_args=['request', 'user'])
register_jsonschema = Signal(providing_args=['schema', 'import_path'])


def handle_register_jsonschema(sender, **kwargs):
    schema = kwargs.get('schema')
    name = kwargs.get('import_path')
    name = name.replace('.', '_')
    setattr(jsonschema, name, schema)


register_jsonschema.connect(handle_register_jsonschema)
