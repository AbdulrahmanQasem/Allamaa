from odoo import models, fields, api, _
import html2text
import urllib.parse as parse

class MessageError(models.TransientModel):
    _name='display.error.message'
    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get('message')
        return False
    name = fields.Text(string="Message", readonly=True, default=get_message)

class SendMessage(models.TransientModel):
    _name = 'whatsapp.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).partner_id)
    allowed_partner_ids = fields.Many2many('res.partner', string="Recipient Allowed", compute="compute_allowed_partner_ids", )
    mobile_number = fields.Char(related='user_id.mobile', readonly=False ,required=True)
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
#     pdf_url = fields.Char('')
    link_url = fields.Char('')

    template_id = fields.Many2one('mail.template', 'Use template', index=True)

    def post_msg_log(self):
            active_model = self.env.context.get('active_model')
            if not active_model:
                return True
            res_id = self.env.context.get('active_id')
            rec = self.env[active_model].browse(res_id)
            print("self.message ==> ",self.message)
            msg = self.message.replace('\n','<br>')
            if active_model == 'sale.order':
                rec.message_post(body=_("%s %s sent via WhatsApp <br> %s") % (
                _('Quotation') if rec.state in ('draft', 'sent', 'cancel') else _('Sales Order'), rec.name,msg))
                if rec.state == 'draft':
                    rec.write({'state': 'sent'})
            elif active_model == 'account.move':
                rec.message_post(body=_("Invoice %s sent via WhatsApp <br> %s") % (rec.name,msg))
            elif active_model == 'purchase.order':
                rec.message_post(body=_("%s %s sent via WhatsApp <br> %s") % (
                _('Request for Quotation') if rec.state in ['draft', 'sent'] else _('Purchase Order'), rec.name,msg))
                if rec.state == 'draft':
                    rec.write({'state': 'sent'})
            elif active_model == 'stock.picking':
                rec.message_post(body=_("Delivery Order %s sent via WhatsApp <br> %s") % (rec.name,msg))


    @api.depends('mobile_number')
    def compute_allowed_partner_ids(self):
        print("**** Partner compute ***")
        partner_id = self.env[self._context.get('active_model')].browse(
            self.env.context.get('active_ids')).partner_id
        lst = [partner_id.id]
        print("**** Partner ***",lst)
        if partner_id.child_ids:
            lst += partner_id.child_ids.ids
        self.allowed_partner_ids = [(6, 0, lst)]
        
    @api.onchange('user_id')
    def get_phone(self):
        for rec in self:
            rec.mobile_number = rec.user_id.mobile if rec.user_id else False


    @api.onchange('link_url','message')
    def onchange_method(self):
        if self.message:
            if self.link_url:
                self.message += '\n'+ '*For Show Your Order :* ' + '\n '+ self.link_url + '\n '
            print("/// link_url ==> ",self.link_url)
#             if self.pdf_url:
#                 self.message += '\n' + '*For Download Your PDF :* ' + '\n ' + self.pdf_url
                # msg_with_url += '\n' + 'For Download Your PDF : '
                # msg_with_url += '\n' + self.pdf_url


    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']
        returned_fields = fields + ['partner_ids']
        values = dict.fromkeys(res_ids, False)
        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if
                                 template_values[res_id].get(field))
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values
        return multi_mode and values or values[res_ids[0]]

    # rec.message_post(body=logmessage, attachments=attachments_list)
    # for at in self.attachment_ids:
    #     attachments_list.append((at.name, base64.decodebytes(at.datas)))
    def send_custom_message(self):
        if self.message and self.mobile_number:
            message_string = parse.quote(self.message)
            message_string = message_string[:(len(message_string))]
            number = self.user_id.mobile
            msg_with_url = message_string
            # if self.pdf_url:
            #     msg_with_url += '\n' + 'For Download Your PDF : '
            #     msg_with_url += '\n' + self.pdf_url
            # if self.link_url:
            #     print("self.link_url *** > ",self.link_url)
            #     msg_with_url += ' \n ' + 'For *Show* Your *Order :* '
            #     msg_with_url += ' \n ' + self.link_url
            print("msg_with_url ==>",msg_with_url)


            link = "https://web.whatsapp.com/send?phone=" + number
            self.post_msg_log()
            send_msg = {
                'type': 'ir.actions.act_url',
                'url': link + "&text=" + msg_with_url ,
                'target': 'new',
                'res_id': self.id,
            }
            return send_msg
