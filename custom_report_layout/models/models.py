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
    footer_height = fields.Char("Footer height", default="200")