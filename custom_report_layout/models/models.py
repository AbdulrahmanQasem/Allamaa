# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    """"""
    _inherit = "res.company"

    header = fields.Image("Header")
    footer = fields.Image("Footer")
    header_width = fields.Char("Header Width", default="1000")
    header_height = fields.Char("Header height", default="150")
    footer_width = fields.Char("Footer Width", default="1000")
    footer_height = fields.Char("Footer height", default="100")



class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    header = fields.Image(related='company_id.header', readonly=True)
    footer = fields.Image(related='company_id.footer', readonly=True)
    header_width = fields.Char(related='company_id.header_width', readonly=True)
    header_height = fields.Char(related='company_id.header_height', readonly=True)
    footer_width = fields.Char(related='company_id.footer_width', readonly=True)
    footer_height = fields.Char(related='company_id.footer_height', readonly=True)
