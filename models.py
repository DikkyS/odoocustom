## product_request_management/models.py
from odoo import models, fields, api

class ProductRequest(models.Model):
    _name = 'product.request'
    _description = 'Product Request'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: 'New')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    date_required = fields.Date(string='Required Date')
    reason = fields.Html(string='Reason')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')],
                             string='Status', default='draft', readonly=True)
    transfer_count = fields.Integer(compute='_compute_transfer_count', string='Stock Transfers', readonly=True)
    po_count = fields.Integer(compute='_compute_po_count', string='Purchase Orders', readonly=True)
    transfer_ids = fields.One2many('stock.picking', 'product_request_id', string='Stock Transfers')
    po_ids = fields.One2many('purchase.order', 'product_request_id', string='Purchase Orders')

    @api.depends('transfer_ids')
    def _compute_transfer_count(self):
        for request in self:
            request.transfer_count = len(request.transfer_ids)

    @api.depends('po_ids')
    def _compute_po_count(self):
        for request in self:
            request.po_count = len(request.po_ids)


class RequestDetail(models.Model):
    _name = 'request.detail'
    _description = 'Request Detail'

    name = fields.Char(string='Name', required=True)
    specification = fields.Text(string='Specification')
    brochure = fields.Binary(string='Brochure')
    quantity = fields.Integer(string='Quantity')
    quantity_moved = fields.Integer(compute='_compute_quantity_moved', string='Quantity Moved', readonly=True)
    quantity_remaining = fields.Integer(compute='_compute_quantity_remaining', string='Quantity Remaining', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)

    @api.depends('quantity', 'transfer_ids')
    def _compute_quantity_moved(self):
        for detail in self:
            detail.quantity_moved = sum(detail.transfer_ids.filtered(lambda t: t.state == 'done').mapped('product_qty'))

    @api.depends('quantity', 'po_ids')
    def _compute_quantity_remaining(self):
        for detail in self:
            detail.quantity_remaining = detail.quantity - sum(detail.po_ids.filtered(lambda po: po.state not in ('cancel', 'draft')).mapped('product_qty'))
