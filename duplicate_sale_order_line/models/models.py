from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    def copy_sale_order_line(self):
        self.copy(default={'order_id': self.order_id.id})