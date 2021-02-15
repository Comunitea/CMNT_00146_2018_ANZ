# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _


class AcquirerRedsys(models.Model):
    _inherit = 'payment.acquirer'

    def _prepare_merchant_parameters(self, tx_values):
        """
        Workaround para cambiar la Ds_Merchant_UrlOk como Url de retorno.
        Esto se hace porque no confirmaba el pedido, el problema viene de que debería de darnos dos respuestas,
        una con el OK, que ya la daba y otra con la devolucion para el proceso de confirmacion
        y a esta ultima no la llamaba nunca, asi que la Ds_Merchant_UrlOk se cambia a la url de retorno
        para que haga las dos llamadas.
        """
        # Check multi-website
        base_url = self._get_website_url()
        callback_url = self._get_website_callback_url()
        if self.redsys_percent_partial > 0:
            amount = tx_values['amount']
            tx_values['amount'] = amount - (
                amount * self.redsys_percent_partial / 100)
        values = {
            'Ds_Sermepa_Url': (
                self._get_redsys_urls(self.environment)[
                    'redsys_form_url']),
            'Ds_Merchant_Amount': str(int(round(tx_values['amount'] * 100))),
            'Ds_Merchant_Currency': self.redsys_currency or '978',
            'Ds_Merchant_Order': (
                tx_values['reference'] and tx_values['reference'][-12:] or
                False),
            'Ds_Merchant_MerchantCode': (
                self.redsys_merchant_code and
                self.redsys_merchant_code[:9]),
            'Ds_Merchant_Terminal': self.redsys_terminal or '1',
            'Ds_Merchant_TransactionType': (
                self.redsys_transaction_type or '0'),
            'Ds_Merchant_Titular': tx_values.get(
                'billing_partner', self.env.user.partner_id).display_name[:60],
            'Ds_Merchant_MerchantName': (
                self.redsys_merchant_name and
                self.redsys_merchant_name[:25]),
            'Ds_Merchant_MerchantUrl': (
                '%s/payment/redsys/return' % (callback_url or base_url))[:250],
            'Ds_Merchant_MerchantData': self.redsys_merchant_data or '',
            'Ds_Merchant_ProductDescription': (
                self._product_description(tx_values['reference']) or
                self.redsys_merchant_description and
                self.redsys_merchant_description[:125]),
            'Ds_Merchant_ConsumerLanguage': (
                self.redsys_merchant_lang or '001'),
            'Ds_Merchant_UrlOk':
            '%s/payment/redsys/return' % base_url,
            'Ds_Merchant_UrlKo':
            '%s/payment/redsys/result/redsys_result_ko' % base_url,
            'Ds_Merchant_Paymethods': self.redsys_pay_method or 'T',
        }
        return self._url_encode64(json.dumps(values))
