## product_request_management/models/product_request.py

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductRequest(models.Model):
    # Existing fields and methods remain unchanged.

    def action_submit(self):
        self.write({'state': 'open'})

    def action_confirm(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def fulfill_request(self):
        if not self.env.user.has_group('product_request_management.ProductRequest/PR Approver'):
            raise ValidationError("You do not have the required access to confirm the Product Request.")

        for request in self:
            if request.state == 'open':
                # Check if all requested products are available in the main warehouse
                products_available = True
                unavailable_products = []
                for detail in request.detail_ids:
                    if detail.quantity > detail.product_id.qty_available:
                        products_available = False
                        unavailable_products.append(detail.product_id.name)

                if products_available:
                    # Create an internal transfer for each request detail
                    internal_transfer = self.env['stock.picking'].create({
                        'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                        'location_id': self.env.ref('stock.stock_location_stock').id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'product_request_id': request.id,
                        # Add other fields as needed for the internal transfer
                    })

                    for detail in request.detail_ids:
                        transfer_line = self.env['stock.move'].create({
                            'name': detail.product_id.name,
                            'product_id': detail.product_id.id,
                            'product_uom_qty': detail.quantity,
                            'product_uom': detail.product_id.uom_id.id,
                            'picking_id': internal_transfer.id,
                            'location_id': self.env.ref('stock.stock_location_stock').id,
                            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                            # Add other fields as needed for the transfer line
                        })

                    # Confirm the internal transfer
                    internal_transfer.action_confirm()
                    internal_transfer.action_assign()

                    # Mark the request as done
                    request.action_confirm()
                else:
                    raise ValidationError(
                        f"The following requested products are not available in the main warehouse: {', '.join(unavailable_products)}"
                    )
            else:
                raise ValidationError("The request must be in 'Open' state to fulfill it.")

    def create_purchase_order(self):
        if not self.env.user.has_group('product_request_management.ProductRequest/PR Fulfillment'):
            raise ValidationError(
                "You do not have the required access to create Moves and RFQs for the Product Request."
            )

        for request in self:
            if request.state == 'open':
                for detail in request.detail_ids:
                    if detail.quantity > detail.product_id.qty_available:
                        purchase_order = self.env['purchase.order'].create({
                            'partner_id': self.env.user.partner_id.id,
                            'product_request_id': request.id,
                            'order_line': [(0, 0, {
                                'name': detail.product_id.name,
                                'product_id': detail.product_id.id,
                                'product_qty': detail.quantity,
                                'product_uom': detail.product_id.uom_id.id,
                                # Add other fields as needed for the purchase order line
                            })]
                        })
                        purchase_order.button_confirm()
            else:
                raise ValidationError("The request must be in 'Open' state to create a Purchase Order.")

class RequestDetail(models.Model):
    _name = 'request.detail'
    _description = 'Request Detail'

    name = fields.Char(string='Name', required=True)
    spesification = fields.Text(string='Specification')
    brochure = fields.Binary(string='Brochure')
    quantity = fields.Integer(string='Requested Quantity')
    quantity_moved = fields.Integer(string='Fulfilled Quantity by Movement', compute='_compute_quantity_moved', store=True)
    quantity_po = fields.Integer(string='Fulfilled Quantity by PO', compute='_compute_quantity_po', store=True)
    quantity_remaining = fields.Integer(string='Remaining Quantity', compute='_compute_quantity_remaining', store=True)
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

    # Existing fields and methods in the Product Request model

    # Smart button actions
    def action_view_internal_transfers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Internal Transfers',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.mapped('transfer_ids').ids)],
            'context': {'default_product_request_id': self.id},
        }

    def action_view_purchase_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.mapped('po_ids').ids)],
            'context': {'default_product_request_id': self.id},
        }
    
    from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductRequest(models.Model):
    _name = 'product.request'
    _description = 'Product Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    date_required = fields.Date(string='Required Date')
    reason = fields.Html(string='Reason')
    state = fields.Selection(
        [('draft', 'Draft'), ('open', 'Open'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        string='State', default='draft', track_visibility='onchange'
    )

    stage_id = fields.Many2one('product.request.stage', string='Stage', default=lambda self: self.env.ref('product_request_management.stage_draft').id, tracking=True)

    transfer_count = fields.Integer(compute='_compute_transfer_count', string='Transfer Count')
    po_count = fields.Integer(compute='_compute_po_count', string='Purchase Order Count')
    fulfilled_quantity = fields.Integer(string='Total Fulfilled Quantity', compute='_compute_fulfilled_quantity')

    # Rest of the fields and methods remain unchanged.

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id:
            self.state = self.stage_id.state

    @api.depends('transfer_ids')
    def _compute_transfer_count(self):
        for request in self:
            request.transfer_count = len(request.transfer_ids)

    @api.depends('po_ids')
    def _compute_po_count(self):
        for request in self:
            request.po_count = len(request.po_ids)

    @api.depends('transfer_ids.move_lines')
    def _compute_fulfilled_quantity(self):
        for request in self:
            request.fulfilled_quantity = sum(request.transfer_ids.mapped('move_lines').filtered(lambda x: x.state == 'done').mapped('quantity_done'))

