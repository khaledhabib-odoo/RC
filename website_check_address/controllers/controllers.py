# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website_sale.controllers.main import WebsiteSale
import requests


class WebsiteSaleAddress(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        values, errors = {}, {}
        # print("NEWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
        # print("KW = ", kw)
        conf = request.env['ir.config_parameter'].sudo()
        auth_id = str(conf.get_param('website_check_address.smarty_auth_id'))
        auth_token = str(conf.get_param('website_check_address.smarty_auth_token'))
        # print("auth_id = ", auth_id)
        # print("auth_token = ", auth_token)
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()
        # print("partner_2", Partner)
        # print("order2 = ", order)
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False


        partner_id = int(kw.get('partner_id', -1))
        # print("partner_id = ", partner_id)

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ('new', 'shipping')
                        partner_id = -1
                    elif partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            #######################
            check_addrs = self.check_partner_address(kw)
            if check_addrs != 200:
                errors['error_message'] = ['your address is wrong plz Enter another valid address']
                # print("Errors =", errors)
            #######################
            if errors:

                # errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                # print("final_partnerr = ", partner_id)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                     mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                # errors['error_message'] = ['your address is wrong plz try again']
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)

    # conf = self.env['ir.config_parameter'].sudo()
    # request_picking_operation_id = int(conf.get_param('request.picking.operation'))

    def check_partner_address(self, kw):
        street = kw['street']
        street2 = kw['street2']
        city = kw['city']
        zip = kw['zip']
        country = request.env['res.country'].search([('id', '=', kw.get('country_id'))])
        state = request.env['res.country.state'].search([('id', '=', kw.get('state_id'))])

        conf = request.env['ir.config_parameter'].sudo()
        auth_id = str(conf.get_param('website_check_address.smarty_auth_id'))
        auth_token = str(conf.get_param('website_check_address.smarty_auth_token'))

        url = 'https://international-street.api.smartystreets.com/verify?'

        params = {'auth-id': auth_id,
                  'auth-token': auth_token,
                  'address1': street,
                  'address2': street2,
                  'locality': state.name,
                  'administrative_area': city,
                  'postal_code': zip,
                  'country': country.name
                  }

        x = requests.get(url, params)
        # print(x)
        return int(x.status_code)