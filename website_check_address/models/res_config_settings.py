# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    smarty_auth_id = fields.Char(string="Smarty Auth-ID")
    smarty_auth_token = fields.Char(string="Smarty Auth-Token")


    def set_values(self):
        obj = self.env['ir.config_parameter'].sudo()
        obj.set_param('website_check_address.smarty_auth_id', self.smarty_auth_id)
        obj.set_param('website_check_address.smarty_auth_token', self.smarty_auth_token)
        super(ResConfigSettings, self).set_values()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        conf = self.env['ir.config_parameter'].sudo()
        res.update(smarty_auth_id=conf.get_param('website_check_address.smarty_auth_id'),
                   smarty_auth_token=conf.get_param('website_check_address.smarty_auth_token'))
        return res