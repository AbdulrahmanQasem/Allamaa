from odoo import models, SUPERUSER_ID
import logging

logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def _apply_groups(self, node, name_manager, node_info):
        # May Be it is unused for new version needs to double check and if not needed remove code
        res = super(IrUiView, self)._apply_groups(node, name_manager, node_info)
        if self._uid == SUPERUSER_ID:
            return res
        try:
            self._cr.execute("SELECT id FROM ir_model WHERE model=%s", (name_manager.model._name,))
            model_rec = self.env['ir.model'].sudo().browse(self._cr.fetchone()[0])
            for config_rec in model_rec.field_configuration_ids:
                if (node.tag == 'field' and node.get('name') == config_rec.field_id.name):
                    if self.env.user.groups_id & config_rec.group_ids:
                        if config_rec.invisible:
                            node.set('invisible', '1')
                            node_info['modifiers']['invisible'] = True
                        if config_rec.readonly:
                            node.set('readonly', '1')
                            node_info['modifiers']['readonly'] = True
        except Exception as e:
            logger.info('\n\nException:\n %s' % str(e))
            return res
        return res

    def _postprocess_tag_button(self, node, name_manager, node_info):
        # Hide Any Button
        postprocessor = getattr(super(IrUiView, self), '_postprocess_tag_button', False)
        if postprocessor:
            super(IrUiView, self)._postprocess_tag_button(node, name_manager, node_info)
        hide = None
        for hide_button_config in self.env['ir.model']._get(name_manager.model._name).mapped('hide_button_config_ids'):
            if hide_button_config.button_hide_by in ['method', 'action_id', 'field']:
                for elem in node.iter(tag='field'):
                    if elem.get('name') == hide_button_config.button_hide_by_statement or \
                            (elem.get('string') and elem.get('string').lower() == hide_button_config.button_hide_by_statement.lower()):
                        hide = [hide_button_config]
                        break
                if node.get('name') == hide_button_config.button_hide_by_statement or \
                        (node.get('string') and node.get('string').lower() == hide_button_config.button_hide_by_statement.lower()):
                    hide = [hide_button_config]
                    break
                hide = [hide_button_config for elem in node.iter(tag='field') if elem.get('name') == hide_button_config.button_hide_by_statement]
                if hide:
                    break
            elif hide_button_config.button_hide_by == 'label':
                for elem in node.iter(tag='span'):
                    if elem.text and hide_button_config.button_hide_by_statement in elem.text.lower():
                        hide = [hide_button_config]
                        break
                if node.get('string') and node.get('string').lower() == hide_button_config.button_hide_by_statement.lower():
                    hide = [hide_button_config]
                    break
                hide = [hide_button_config for elem in node.iter(tag='span') if elem.text == hide_button_config.button_hide_by_statement]
                if hide:
                    break
        if hide:
            if (not self.env.user.groups_id & hide[0].group_ids) and (not self.env.user & hide[0].hide_user_ids):
                return None
            node.set('invisible', '1')
            node_info['modifiers']['invisible'] = True
        return None
