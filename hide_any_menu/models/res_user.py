from odoo import api, fields, models, SUPERUSER_ID, _


class Users(models.Model):
    _inherit = 'res.users'

    menu_ids = fields.Many2many('ir.ui.menu', 'user_menu_rel', 'user_id', 'menu_id', string='Menu To Hide',
                                help='Select Menus To Hide From This User')
    report_ids = fields.Many2many('ir.actions.report', 'user_report_rel', 'user_id', 'report_id', 'Report To Hide',
                                  help='Select Report To Hide From This User')

    # Earlier user needs to restart server to take invisible effect
    # After multiple request from users added clear cache code so no need to restart server
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(Users, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(Users, self).write(values)


class ResGroups(models.Model):
    _inherit = 'res.groups'

    menu_ids = fields.Many2many('ir.ui.menu', 'group_menu_rel', 'group_id', 'menu_id', string='Menu To Hide')
    report_ids = fields.Many2many('ir.actions.report', 'group_report_rel', 'group_id', 'report_id', 'Report To Hide',
                                  help='Select Report To Hide From This User')

    # Earlier user needs to restart server to take invisible effect
    # After multiple request from users added clear cache code so no need to restart server
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(ResGroups, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(ResGroups, self).write(values)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    hide_user_ids = fields.Many2many('res.users', 'user_report_rel', 'report_id', 'user_id', string='Hide From Users')
    hide_group_ids = fields.Many2many('res.groups', 'group_report_rel', 'report_id', 'group_id', string='Hide From Groups')

    def report_action(self, docids, data=None, config=True):
        res = super(IrActionsReport, self).report_action(docids, data=data, config=config)
        if self._uid == SUPERUSER_ID:
            return res
        for report in self:
            for user in report.hide_user_ids:
                if user.id == self._uid:
                    return None
            for group in report.hide_group_ids:
                for user in group.users:
                    if user.id == self._uid:
                        return None
        return res


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    hide_group_ids = fields.Many2many('res.groups', 'group_menu_rel', 'menu_id', 'group_id', string='Hide From Groups')
    hide_user_ids = fields.Many2many('res.users', 'user_menu_rel', 'menu_id', 'user_id', string='Hide From Users')

    # Earlier user needs to restart server to take invisible effect
    # After multiple request from users added clear cache code so no need to restart server
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(IrUiMenu, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(IrUiMenu, self).write(values)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user == self.env.ref('base.user_root'):
            return super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
        else:
            menus = super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
            if menus:
                menu_ids = [menu for menu in self.env.user.menu_ids]
                menu_ids2 = [menu for group in self.env.user.groups_id for menu in group.menu_ids]
                for menu in list(set(menu_ids).union(menu_ids2)):
                    if menu in menus:
                        menus -= menu
                if offset:
                    menus = menus[offset:]
                if limit:
                    menus = menus[:limit]
            return len(menus) if count else menus


class IrModel(models.Model):
    _inherit = 'ir.model'

    field_configuration_ids = fields.One2many('field.configuration', 'model_id', string='Field Configuration')
    hide_button_config_ids = fields.One2many('hide.button.config', 'model_id', string='Hide Button Configuration')


class FieldConfiguration(models.Model):
    _name = 'field.configuration'
    _description = 'Field Configuration'

    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True)
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete='cascade', required=True)
    field_name = fields.Char(related='field_id.name', string='Technical Name', readonly=True)
    group_ids = fields.Many2many('res.groups', 'field_config_group_rel', 'group_id', 'field_config_id', required=True, string='Groups')
    readonly = fields.Boolean('ReadOnly', default=False)
    invisible = fields.Boolean('Invisible', default=False)

    _sql_constraints = [
        ('field_model_readonly_unique', 'UNIQUE ( field_id, model_id, readonly)',
         _('Readonly Attribute Is Already Added To This Field, You Can Add Group To This Field!')),
        ('model_field_invisible_uniq', 'UNIQUE (model_id, field_id, invisible)',
         _('Invisible Attribute Is Already Added To This Field, You Can Add Group To This Field'))
    ]

    @api.model
    def default_get(self, fields):
        result = super(FieldConfiguration, self).default_get(fields)
        result.update({'model_id': self.env['ir.model'].search([('id', '=', self.env.context.get('default_model_id', None))])})
        return result

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for record in self:
            if record.model_id:
                if record.field_id and record.field_id.model_id == record.model_id:
                    pass
                else:
                    record.field_id = None
            else:
                record.field_id = None


class HideButtonConfig(models.Model):
    _name = 'hide.button.config'
    _description = 'Hide Button Configuration'

    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True)
    button_type = fields.Selection([('regular_button', 'Regular Button'), ('smart_button', 'Smart Button')], required=True, default='regular_button')
    button_hide_by = fields.Selection([('method', 'Method'), ('action_id', 'Action Id'),
                                       ('field', 'Field'), ('label', 'Label')], required=True, default='method')
    button_hide_by_statement = fields.Char(required=True)
    group_ids = fields.Many2many('res.groups', 'button_config_group_rel', 'config_id', 'group_id', required=False, string='Hide From Groups')
    hide_user_ids = fields.Many2many('res.users', 'button_config_user_rel', 'config_id', 'user_id', required=False, string='Hide From Users')
    description = fields.Char(help="Button Description so next time you will easily understand what button it is.")
