# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_report_product_image = fields.Boolean(related='company_id.sale_report_product_image', readonly=False)

class ResCompany(models.Model):
    _inherit = "res.company"

    sale_report_product_image = fields.Boolean('Show Product Image')
