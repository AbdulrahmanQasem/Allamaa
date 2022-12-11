# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    print_image = fields.Boolean("Print Image",
                                 help="""If ticked, you can see the product image in 
                    report of sale order/quotation""")
    image_sizes = fields.Selection(
        [("image", "Big sized Image"),
         ("image_medium", "Medium Sized Image"),
         ("image_small", "Small Sized Image"),
         ], "Image Sizes", default="image_small",
        help="Image size to be displayed in report")

    show_image = fields.Boolean(related='company_id.show_sales_product_image',store=True)



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image = fields.Binary('Product Image')

    tech_description = fields.Text(string="Technical Description", readonly=False)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        print("self.price_unit ==> ",self.price_unit)
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
        if self.price_unit == 0.0:
            self.price_unit = product._get_tax_included_unit_price(
                self.company_id or self.order_id.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                'sale',
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(product),
                product_currency=self.order_id.currency_id
            )





    @api.onchange('product_id')
    @api.depends('product_id')
    def onchange_product_image(self):
        for record in self:
            if record.product_id:
                record.image = record.product_id.image_1920
                record.tech_description = record.product_id.tech_description


