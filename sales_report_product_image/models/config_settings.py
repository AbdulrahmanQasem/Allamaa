# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Company(models.Model):
    _inherit = "res.company"

    show_sales_product_image = fields.Boolean('Show Sales Product Image')


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_sales_product_image = fields.Boolean(related='company_id.show_sales_product_image', readonly=False)




