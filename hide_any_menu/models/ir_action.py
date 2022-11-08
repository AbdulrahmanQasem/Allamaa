from odoo import api, models, tools


class IrActions(models.Model):
    _inherit = 'ir.actions.actions'

    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'model_name', 'debug')
    def _get_bindings(self, model_name, debug=False):
        result = super(IrActions, self)._get_bindings(model_name, debug=debug)
        lst = result.get('report')
        if lst:
            for item in lst:
                reports = self.env['ir.actions.report'].sudo().search([('name', '=', item.get('name'))])
                if reports:
                    for report in reports:
                        skip_report = False
                        for user in report.hide_user_ids:
                            if user.id == self._uid:
                                skip_report = True
                                break
                        for group in report.hide_group_ids:
                            for user in group.users:
                                if user.id == self._uid:
                                    skip_report = True
                                    break
                        if skip_report:
                            lst.remove(item)
            result.update({'report': lst})
        return result
