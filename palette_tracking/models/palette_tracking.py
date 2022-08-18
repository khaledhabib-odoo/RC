# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaletteTracking(models.Model):
    _name = "palette.tracking"
    _description = 'Palette Tracking'
    _rec_name = 'partner_id'

    picking_id = fields.Many2one('stock.picking', string="Picking", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    license_plate = fields.Char(string="License Plate")
    picking_partner_id = fields.Many2one('res.partner', string="Picking Partner", related="picking_id.partner_id")
    picking_date_done = fields.Datetime(string="Picking Date Done", related="picking_id.date_done")
    palette_count_plus = fields.Integer(string="Count Palette Plus")
    palette_count_minus = fields.Integer(string="Count Palette Minus")
    balance = fields.Integer(string="Balance", compute="compute_balance")

    @api.depends('palette_count_plus', 'palette_count_minus')
    def compute_balance(self):
        for rec in self:
            rec.balance = rec.palette_count_plus - rec.palette_count_minus

