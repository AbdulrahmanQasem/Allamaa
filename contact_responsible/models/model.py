# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"


    contact_phone = fields.Char(string="Contact Phone", )
    contract_number = fields.Char(string="Contract Number", )
    contact_partner_id = fields.Many2one('res.partner', string='Responsible Contact', domain="[('parent_id','=', partner_id)]")
    partner_phone = fields.Char(string='Contact Mobile', compute='_compute_partner_phone', readonly=False)

    def _compute_partner_phone(self):
        for rec in self:
            rec.partner_phone = rec.contact_partner_id.mobile or rec.contact_partner_id.phone  or rec.partner_id.mobile or rec.partner_id.phone or False




    @api.onchange('contact_partner_id')
    def get_phone(self):
        for rec in self:
            rec.contact_phone = rec.contact_partner_id.phone or rec.contact_partner_id.mobile if rec.contact_partner_id else False

    # @api.onchange('contact_partner_id')
    # def get_number(self):
    #     for rec in self:
    #         rec.contact_number = rec.contact_partner_id.mobile if rec.contact_partner_id else False
    