from odoo import fields, models, api

class Company(models.Model):
    _inherit = 'res.company'
    html_text_header = fields.Html()

class SaleOrder(models.Model):
    _inherit = "sale.order"

    contact_id = fields.Many2one('res.partner')
    contact_phone = fields.Char()
    html_text_header = fields.Html()
    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
    


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