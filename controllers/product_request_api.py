# product_request_management/controllers/product_request_api.py

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.product_request_management.models.product_request import ProductRequest

class ProductRequestAPI(http.Controller):

    @http.route('/api/product_request/<int:request_id>', auth='public', methods=['GET'], csrf=False, type='json')
    def get_product_request(self, request_id, **kwargs):
        request_record = request.env['product.request'].sudo().browse(request_id)
        if not request_record:
            return {'error': 'Product request not found'}
        return request_record.read(['name', 'date', 'date_required', 'reason', 'state'])

    @http.route('/api/product_request', auth='public', methods=['POST'], csrf=False, type='json')
    def create_product_request(self, name, date, date_required, reason, **kwargs):
        vals = {
            'name': name,
            'date': date,
            'date_required': date_required,
            'reason': reason,
            'state': 'draft',
        }
        new_request = ProductRequest.sudo().create(vals)
        return {'id': new_request.id, 'message': 'Product request created successfully'}

    @http.route('/api/product_request/<int:request_id>/confirm', auth='public', methods=['POST'], csrf=False, type='json')
    def confirm_product_request(self, request_id, **kwargs):
        request_record = request.env['product.request'].sudo().browse(request_id)
        if not request_record:
            return {'error': 'Product request not found'}
        try:
            request_record.action_confirm()
        except ValidationError as e:
            return {'error': str(e)}
        return {'message': 'Product request confirmed successfully'}
