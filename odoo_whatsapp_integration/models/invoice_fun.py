from odoo import models, fields, api, _
import urllib.parse as parse
from odoo.exceptions import UserError
from itertools import groupby

class InvoiceTransferDone(models.Model):
    _inherit = 'account.move'

    def get_order_link_url(self):
        access_action = self.with_context(force_website=True).get_access_action()
        print("access_action ==> ", access_action)
        is_online = access_action and access_action['type'] == 'ir.actions.act_url'
        print("is_online ==> ", is_online)
        base_url = self.get_base_url()
        print("base_url ==> ", base_url)
        share_url = is_online and self._get_share_url(redirect=True)
        print("share_url ==> ", share_url)
        link_url = is_online and share_url and base_url + share_url or ''
        print("link_url ==> ", link_url)
        return link_url

    def get_pdf_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        pdf_url = base_url + '/report/pdf/account.report_invoice/' + str(self.id)
        print("** pdf_url => ", pdf_url)
        return pdf_url

    def invoice_whatsapp(self):
        record_phone = self.partner_id.mobile
        if not record_phone:
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "Please add a mobile number!"
            return {
                'name': 'Mobile Number Field Empty',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        if not record_phone[0] == "+":
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "No Country Code! Please add a valid mobile number along with country code!"
            return {
                'name': 'Invalid Mobile Number',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp Message'),
                    'res_model': 'whatsapp.wizard',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_template_id': self.env.ref('odoo_whatsapp_integration.whatsapp_invoice_template').id,
                    'default_link_url': self.get_order_link_url(),
                    'default_pdf_url': self.get_pdf_url()
                    },
                   }

    def send_direct_message(self):
        record_phone = self.partner_id.mobile
        if not record_phone:
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "Please add a mobile number!"
            return {
                'name': 'Mobile Number Field Empty',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        if not record_phone[0] == "+":
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "No Country Code! Please add a valid mobile number along with country code!"
            return {
                'name': 'Invalid Mobile Number',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        else:
            prods = ""
            for rec in self:
                for id in rec.invoice_line_ids:
                            prods = prods + "*" +str(id.product_id.name) + " : " + str(id.quantity) + "* \n"

            custom_msg = "Hello *{}*, your Invoice *{}* with amount *{} {}* is ready. \nYour invoice contains following items:\n {}".format(str(self.partner_id.name),str(self.name),str(self.currency_id.symbol),str(self.amount_total),prods)
            ph_no = [number for number in record_phone if number.isnumeric()]
            ph_no = "".join(ph_no)
            ph_no = "+" + ph_no

            link = "https://web.whatsapp.com/send?phone=" + ph_no
            message_string = parse.quote(custom_msg)
            link_url = self.get_order_link_url()
            pdf_url = self.get_pdf_url()
            if link_url:
                message_string += '\n' + '*For Show Your Order :* ' + '\n ' + link_url + '\n '
            if pdf_url:
                message_string += '\n' + '*For Download Your PDF :* ' + '\n ' + pdf_url

            url_id = link + "&text=" + message_string
            return {
                'type': 'ir.actions.act_url',
                'url': url_id,
                'target': 'new',
                'res_id': self.id,
            }

    def check_value(self, partner_ids):
        partners = groupby(partner_ids)
        return next(partners, True) and not next(partners, False)

    def multi_sms(self):
        invoice_order_ids = self.env['account.move'].browse(self.env.context.get('active_ids'))

        cust_ids = []
        invoice_nums = []
        for sale in invoice_order_ids:
            cust_ids.append(sale.partner_id.id)
            invoice_nums.append(sale.name)

        # To check unique customers
        cust_check = self.check_value(cust_ids)

        if cust_check:
            invoice_numbers = invoice_order_ids.mapped('name')
            invoice_numbers = "\n".join(invoice_numbers)

            form_id = self.env.ref('odoo_whatsapp_integration.whatsapp_multiple_message_wizard_form').id
            product_all = []
            for each in invoice_order_ids:
                prods = ""
                for id in each.invoice_line_ids:
                    prods = prods + "*" + "Product: " + str(id.product_id.name) + ", Qty: " + str(id.quantity) + "* \n"
                product_all.append(prods)

            custom_msg = "Hi" + " " + self.partner_id.name + ',' + '\n' + "Your Invoice" + '\n' + invoice_numbers + \
                         ' ' + '\n' + "are ready for review.\n"
            counter = 0
            for every in product_all:
                custom_msg = custom_msg + "Your order " + "*" + invoice_nums[
                    counter] + "*" + " contains following items: \n{}".format(every) + '\n'
                counter += 1

            final_msg = custom_msg + "\nDo not hesitate to contact us if you have any questions."

            ctx = dict(self.env.context)
            ctx.update({
                'default_message': final_msg,
                'default_partner_id': self.partner_id.id,
                'default_mobile': self.partner_id.mobile,
            })
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'whatsapp.wizard.multiple.contact',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
                'context': ctx,
            }
        else:
            raise UserError(_('Please Select Orders of Unique Customers'))
