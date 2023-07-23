## product_request_management/models/request_detail.py

from odoo import models, fields, api

class RequestDetail(models.Model):
    _name = 'request.detail'
    _description = 'Request Detail'

    name = fields.Char(string='Name', required=True)
    spesification = fields.Text(string='Specification')
    brochure = fields.Binary(string='Brochure')
    quantity = fields.Integer(string='Quantity')
    quantity_moved = fields.Integer(string='Quantity Moved', compute='_compute_quantity_moved', store=True)
    quantity_po = fields.Integer(string='Quantity PO', compute='_compute_quantity_po', store=True)
    quantity_remaining = fields.Integer(string='Quantity Remaining', compute='_compute_quantity_remaining', store=True)

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_request_id = fields.Many2one('product.request', string='Product Request', ondelete='cascade')

    @api.depends('quantity', 'product_request_id.transfer_ids.move_lines')
    def _compute_quantity_moved(self):
        for detail in self:
            moves = detail.product_request_id.transfer_ids.filtered(lambda x: x.state == 'done')
            detail.quantity_moved = sum(moves.mapped('move_lines').filtered(lambda x: x.product_id == detail.product_id).mapped('quantity_done'))

    @api.depends('quantity', 'product_request_id.po_ids.order_line')
    def _compute_quantity_po(self):
        for detail in self:
            po_lines = detail.product_request_id.po_ids.mapped('order_line').filtered(lambda x: x.product_id == detail.product_id)
            detail.quantity_po = sum(po_lines.mapped('product_qty'))

    @api.depends('quantity', 'quantity_moved', 'quantity_po')
    def _compute_quantity_remaining(self):
        for detail in self:
            detail.quantity_remaining = detail.quantity - detail.quantity_moved - detail.quantity_po
