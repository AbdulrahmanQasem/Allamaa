# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_product_image = fields.Boolean(related='company_id.show_product_image', readonly=False)

class ResCompany(models.Model):
    _inherit = "res.company"

    show_product_image = fields.Boolean('Show Product Image')
