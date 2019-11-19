
from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import split_every
from psycopg2 import OperationalError

from odoo import api, fields, models, registry, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round

from odoo.exceptions import UserError

class ProcurementGroup(models.Model):

    _inherit = 'procurement.group'

    @api.model
    def run_procurement_for_stock_move(self, moves = [], use_new_cursor=False, company_id=3):
        # Minimum stock rules
        self.sudo()._procure_orderpoint_confirm_for_moves(moves, use_new_cursor=False, company_id=3)

        # Search all confirmed stock_moves and try to assign them
        moves_to_assign = self.env['stock.move'].search([
            ('state', 'in', ['confirmed', 'partially_available']), ('product_uom_qty', '!=', 0.0)
        ], limit=None, order='priority desc, date_expected asc')
        for moves_chunk in split_every(100, moves_to_assign.ids):
            self.env['stock.move'].browse(moves_chunk)._action_assign()
            if use_new_cursor:
                self._cr.commit()

        exception_moves = self.env['stock.move'].search(self._get_exceptions_domain())
        for move in exception_moves:
            values = move._prepare_procurement_values()
            try:
                with self._cr.savepoint():
                    origin = (move.group_id and (move.group_id.name + ":") or "") + (
                                move.rule_id and move.rule_id.name or move.origin or move.picking_id.name or "/")
                    self.run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id,
                             move.rule_id and move.rule_id.name or "/", origin, values)
            except UserError as error:
                self.env['procurement.rule']._log_next_activity(move.product_id, error.name)
        if use_new_cursor:
            self._cr.commit()

        # Merge duplicated quants
        self.env['stock.quant']._merge_quants()



    @api.model
    def _procure_orderpoint_confirm_for_moves(self, move_ids=False, use_new_cursor=False, company_id=False):
        """ Create procurements based on orderpoints.
        :param bool use_new_cursor: if set, use a dedicated cursor and auto-commit after processing
            1000 orderpoints.
            This is appropriate for batch jobs only.
        """
        if company_id and self.env.user.company_id.id != company_id:
            self = self.with_context(company_id=company_id, force_company=company_id)
        OrderPoint = self.env['stock.warehouse.orderpoint']
        domain = [('product_id.default_code', '=', 'IC'), ('company_id', '=', company_id)]
        orderpoint = OrderPoint.with_context(prefetch_fields=False).search(domain,
            order=self._procurement_from_orderpoint_get_order())

        location_data = OrderedDict()

        def makedefault():
            return {
                'products': self.env['product.product'],
                'orderpoints': self.env['stock.warehouse.orderpoint'],
                'groups': []
            }

        for product_id in move_ids.mapped('product_ids'):
            key = self._procurement_from_orderpoint_get_grouping_key([orderpoint.id])
            if not location_data.get(key):
                location_data[key] = makedefault()
            location_data[key]['products'] += product_id
            location_data[key]['orderpoints'] += orderpoint
            location_data[key]['groups'] = self._procurement_from_orderpoint_get_groups([orderpoint.id])

        for location_id, location_data in location_data.items():
            location_orderpoints = location_data['orderpoints']
            product_context = dict(self._context, location=location_orderpoints[0].location_id.id)

            for group in location_data['groups']:
                if group.get('from_date'):
                    product_context['from_date'] = group['from_date'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                if group['to_date']:
                    product_context['to_date'] = group['to_date'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                product_quantity = location_data['products'].with_context(product_context)._product_available()
                for orderpoint in location_orderpoints:
                    try:
                        for move in move_ids:
                            product_id = move.product_id

                            values = orderpoint._prepare_procurement_values(product_id.qty_available,
                                                                            **group['procurement_values'])

                            self.env['procurement.group'].run(product_id, move.qty_done, orderpoint.product_uom, orderpoint.location_id,
                                                                              orderpoint.name, orderpoint.name, values)
                            self._procurement_from_orderpoint_post_process([orderpoint.id])
                        continue
                        op_product_virtual = product_quantity[product_id.id]['virtual_available']
                        if op_product_virtual is None:
                            continue
                        if float_compare(op_product_virtual, orderpoint.product_min_qty, precision_rounding=orderpoint.product_uom.rounding) <= 0:
                            qty = max(orderpoint.product_min_qty, orderpoint.product_max_qty) - op_product_virtual
                            remainder = orderpoint.qty_multiple > 0 and qty % orderpoint.qty_multiple or 0.0

                            if float_compare(remainder, 0.0, precision_rounding=orderpoint.product_uom.rounding) > 0:
                                qty += orderpoint.qty_multiple - remainder

                            if float_compare(qty, 0.0, precision_rounding=orderpoint.product_uom.rounding) < 0:
                                continue

                            qty -= substract_quantity[orderpoint.id]
                            qty_rounded = float_round(qty, precision_rounding=orderpoint.product_uom.rounding)
                            if qty_rounded > 0:
                                values = orderpoint._prepare_procurement_values(product_id.qty_available, **group['procurement_values'])
                                try:
                                    with self._cr.savepoint():
                                        self.env['procurement.group'].run(product_id, 0, orderpoint.product_uom, orderpoint.location_id,
                                                                          orderpoint.name, orderpoint.name, values)
                                except UserError as error:
                                    self.env['procurement.rule']._log_next_activity(product_id, error.name)
                                self._procurement_from_orderpoint_post_process([orderpoint.id])

                    except OperationalError:
                        raise
        return {}


class ProcurementRule(models.Model):

    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if not self._context.get('no_seller', False):
            return super()._run_buy(product_id, product_qty, product_uom, location_id, name, origin, values)

        default_seller = ()
        cache = {}
        suppliers = product_id.seller_ids\
            .filtered(lambda r: (not r.company_id or r.company_id == values['company_id']) and (not r.product_id or r.product_id == product_id))
        if not suppliers:
            msg = _('There is no vendor associated to the product %s. Please define a vendor for this product.') % (product_id.display_name,)
            raise UserError(msg)

        supplier = self._make_po_select_supplier(values, suppliers)
        partner = supplier.name

        domain = self._make_po_get_domain(values, partner)

        if domain in cache:
            po = cache[domain]
        else:
            po = self.env['purchase.order'].sudo().search([dom for dom in domain])
            po = po[0] if po else False
            cache[domain] = po
        if not po:
            vals = self._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
            company_id = values.get('company_id') and values['company_id'].id or self.env.user.company_id.id
            po = self.env['purchase.order'].with_context(force_company=company_id).sudo().create(vals)
            cache[domain] = po
        elif not po.origin or origin not in po.origin.split(', '):
            if po.origin:
                if origin:
                    po.write({'origin': po.origin + ', ' + origin})
                else:
                    po.write({'origin': po.origin})
            else:
                po.write({'origin': origin})

        # Create Line
        po_line = False
        for line in po.order_line:
            if line.product_id == product_id and line.product_uom == product_id.uom_po_id:
                if line._merge_in_existing_line(product_id, product_qty, product_uom, location_id, name, origin, values):
                    vals = self._update_purchase_order_line(product_id, product_qty, product_uom, values, line, partner)
                    po_line = line.write(vals)
                    break
        if not po_line:
            vals = self._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, supplier)
            self.env['purchase.order.line'].sudo().create(vals)