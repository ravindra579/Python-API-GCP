from marshmallow import Schema, fields

class bigQueryResponseSchema(Schema):
    data = fields.Dict(example={"val":"val"})

class bigQueryGetResponseSchema(Schema):
    data = fields.Str(dump_default="Welcome to the page")

class bigQueryRequestSchema(Schema):
    id = fields.Integer(required=True,example=1)