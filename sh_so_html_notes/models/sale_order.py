# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models, api
from odoo.tools.translate import html_translate


class ResCompany(models.Model):
    _inherit = "res.company"

    html_notes = fields.Html(
        "Notes", translate=html_translate, sanitize=False, prefetch=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    html_notes = fields.Html(
        related='company_id.html_notes', string="Notes", readonly=False)


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    sh_html_notes = fields.Html(
        "Notes", default=lambda self: self.env.company.html_notes)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    sh_html_notes = fields.Html(
        "Notes", default=lambda self: self.env.company.html_notes)

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        if self.sale_order_template_id:
            self.sh_html_notes = self.sale_order_template_id.sh_html_notes
