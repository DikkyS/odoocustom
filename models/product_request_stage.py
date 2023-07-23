## product_request_management/models/product_request_stage.py
from odoo import models, fields

class ProductRequestStage(models.Model):
    _name = 'product.request.stage'
    _description = 'Product Request Stage'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, copy=False)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'The stage name must be unique.'),
    ]
