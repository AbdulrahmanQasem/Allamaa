# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

from num2words import num2words

class Company(models.Model):
    _inherit = 'res.company'
    footer_data = fields.Html()
    html_text_header = fields.Html()

class SaleOrder(models.Model):
    _inherit = "sale.order"

    print_image = fields.Boolean(
        "Print Image",
        help="""If ticked, you can see the product image in
        report of sale order/quotation""",
        default=True
    )
    image_sizes = fields.Selection(
        [
            ("image", "Big sized Image"),
            ("image_medium", "Medium Sized Image"),
            ("image_small", "Small Sized Image"),
        ],
        "Image Sizes",
        default="image",
        help="Image size to be displayed in report",
    )
    contact_id = fields.Many2one('res.partner')
    contact_phone = fields.Char()
    html_text_header = fields.Html()
    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
    show_product_image = fields.Boolean(default=lambda self: self.env.company.show_product_image, )


    @api.onchange('company_id')
    def change_company(self):
        self.html_text_header= self.env.company.html_text_header

    @api.depends('amount_total')
    def amount_to_words(self):
        self.text_amount = "tesst"
        # if self.company_id.text_amount_language_currency:
        #     self.text_amount = num2words(self.amount_total, to='currency',
        #                                  lang=self.company_id.text_amount_language_currency)

    contract_number = fields.Char()
    html_contract_bref = fields.Html()
    html_contract_details = fields.Html()


    @api.onchange('partner_id')
    def onchange_partner_id_get_first_contact(self):
        """
        Update the following fields when the partner is changed:
        - Contact
        """
        if not self.partner_id:
            self.update({
                'contact_id': False,
                'contact_phone':False,
            })
            return

        values = {
            'contact_id': self.partner_id.child_ids[0].id if self.partner_id.child_ids else False,
            'contact_phone': self.partner_id.child_ids[0].phone if self.partner_id.child_ids else False
        }
        self.update(values)
    

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_small = fields.Binary("Product Image")
    technical_description = fields.Html()
    show_product_image = fields.Boolean(default=lambda self: self.env.company.show_product_image, )


    @api.onchange('product_id')
    def _change_image(self):
        if not self.image_small and self.product_id.image_1920:
            self.image_small = self.product_id.image_1920

class StockMove(models.Model):
    _inherit = 'mrp.production'

    # @api.model
    # def _default_image(self):
    #     image_path = get_module_resource('sales_report_product_image', 'static/src/img', 'default_image.png')
    #     return base64.b64encode(open(image_path, 'rb').read())

    product_image = fields.Binary("Product Image", related='sale_order_line_id.image_small')
    technical_description = fields.Html(related='sale_order_line_id.technical_description', store=True)
    # sales_description = fields.Text(related='sale_order_line_id.name')
    sales_description = fields.Text('Sales Description')
    sale_order_line_id = fields.Many2one('sale.order.line')
    show_product_image = fields.Boolean(default=lambda self: self.env.company.show_product_image, )



class ProductTemplate(models.Model):
    _inherit = 'product.template'
    technical_description = fields.Html()
    show_product_image = fields.Boolean(default=lambda self: self.env.company.show_product_image, )



class ProductProduct(models.Model):
    _inherit = 'product.product'
    technical_description = fields.Html()
    show_product_image = fields.Boolean(default=lambda self: self.env.company.show_product_image, )

