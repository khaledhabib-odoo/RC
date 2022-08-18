from odoo import fields, models, api, _


class ModelName (models.Model):
    _inherit = 'res.partner'

    palette_tracking_count = fields.Integer(compute="compute_palette_tracking_count")
    
    def compute_palette_tracking_count(self):
        for rec in self:
            rec.palette_tracking_count = self.env['palette.tracking'].search_count([('partner_id', '=', rec.id)])

    def show_palette_tracking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("palette_tracking.palette_tracking_action")
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action

