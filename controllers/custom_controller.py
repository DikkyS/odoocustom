## product_request_management/controllers/custom_controller.py

from odoo import http
from odoo.http import request, JsonRequest

class CustomController(http.Controller):

    @http.route('/api/product_details/<int:product_id>', type='json', auth='public', methods=['GET'])
    def get_product_details(self, product_id):
        # Perform any necessary logic here to fetch product details based on the product_id
        product = request.env['product.product'].sudo().browse(product_id)
        if not product.exists():
            return JsonRequest(status=404).response
        return JsonRequest(status=200).response({'name': product.name, 'price': product.list_price})

