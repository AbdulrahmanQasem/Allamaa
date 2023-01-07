# -*- coding: utf-8 -*-

from odoo import api, models, fields ,_


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    ref = fields.Char(copy=False, string='Reference')
    location_id = fields.Char(copy=False, string='Location')
    last_check = fields.Date(copy=False)
    contact_mobile = fields.Char(copy=False, string='Contact Mobile')

    def qrcode_info(self):
        # 1 - name
        info =  (_('Asset Name :')) + ' '+ self.name
        # 2- location
        if self.location_id:
            info += "\n" + (_("Location : ")) + ' '+self.location_id
        # 3- ref
        if self.ref:
            info += "\n" + (_('Reference :')) + ' ' + self.ref
        # 4- company
        if self.company_id:
            info += "\n" + (_('Company :')) + ' ' +  self.company_id.name
        # 5- last inventory
        if self.last_check:
            info += "\n" + (_('Last Inventory Check :')) + ' ' + str(self.last_check)
         # 6- Contact Mobile
        if self.location_id:
            info += "\n" + (_("Cotact Mobile : ")) + ' ' +self.contact_mobile
        return info
