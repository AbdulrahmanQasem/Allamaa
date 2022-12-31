# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    crate_from_so = fields.Boolean(string="", compute="compute_crate_from_so")

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order",compute="compute_crate_from_so",store=True )
    sale_line_id = fields.Many2one(comodel_name="sale.order.line", string="Order Line",compute="compute_crate_from_so" ,store=True )
    so_partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", related='sale_order_id.partner_id' ,store=True )
    image_product = fields.Binary(string="Product Image", related='sale_line_id.image')
    tech_description = fields.Text(string="Technical Description", related='sale_line_id.tech_description', readonly=False)
    sale_description = fields.Text(string="Sales Description", related='sale_line_id.name', readonly=False)
    show_image = fields.Boolean(related='company_id.show_sales_product_image',store=True)



    @api.depends('origin')
    def compute_crate_from_so(self):
        for rec in self:
            if rec.origin:
                if 'Replenishment Report - ' in rec.origin:
                    so = rec.origin.replace('Replenishment Report - ','')
                    print("so ==> ",so)
                    so_opj = self.env['sale.order'].sudo().search([('name','ilike',so)],limit=1)
                    print("so_opj ==> ",so_opj)
                    if so_opj:
                        rec.crate_from_so = True
                        rec.sale_order_id = so_opj.id
                        line_id = False
                        for line in so_opj.order_line:
                            if line.product_id.id == rec.product_id.id:
                                line_id = line.id
                                break
                        rec.sale_line_id = line_id

                    else:
                        rec.crate_from_so = False
                        rec.sale_order_id = False
                        rec.sale_line_id = False
                else:
                    so_opj = self.env['sale.order'].sudo().search([('name', 'ilike', rec.origin)], limit=1)
                    print("so_opj ==> ", so_opj)
                    if so_opj:
                        rec.crate_from_so = True
                        rec.sale_order_id = so_opj.id
                        line_id = False
                        for line in so_opj.order_line:
                            if line.product_id.id == rec.product_id.id:
                                line_id = line.id
                                break
                        rec.sale_line_id = line_id
                    else:
                        rec.crate_from_so = False
                        rec.sale_order_id = False
                        rec.sale_line_id = False
            else:
                rec.crate_from_so = False
                rec.sale_order_id = False
                rec.sale_line_id = False



