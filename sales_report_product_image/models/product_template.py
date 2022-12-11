# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tech_description = fields.Text(
        'Technical Description', translate=True,
        help="A description of the Product that you want to communicate to your customers.")




