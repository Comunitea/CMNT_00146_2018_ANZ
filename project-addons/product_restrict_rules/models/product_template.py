# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

class ProductTemplate(models.Model):

    _inherit = 'product.template'


    @api.multi
    def _get_partner_by_context(self):
        if self._context.get('partner_id', False):
            partner_id = self.env['res.partner'].browse(
                self._context.get('partner_id'))
        else:
            partner_id = False
        self.update(partner_by_context=partner_id)


    @api.multi
    def get_allowed_by_context(self):
        #el context es el mismo por lo que debiera ser el mimso
        partner_id = self and self[0].partner_by_context

        if partner_id:
            brand_ids = partner_id.brand_ids
            area_id = partner_id.area_id

        else:
            self.write({'allowed_by_context': True})
            return

        for product in self:
            allowed_by_brand = not(product.brand and brand_ids) or product.brand and product.allowed_brand_ids and product.brand in brand_ids
            allowed_by_area = not(product.allowed_area_id and product.area_ids) or product.allowed_area_id and product.area_ids and product.allowed_area_id not in product.area_ids
            product.update(allowed_area_id= product.allowed_area_id)
            product.allowed_by_context = allowed_by_brand and allowed_by_area


    allowed_area_id = fields.Many2one('res.partner.area', compute="get_allowed_by_area")
    allowed_brand_ids = fields.One2many('product.brand', compute="get_allowed_by_brand")
    allowed_by_context = fields.Boolean('Allowed', compute="_get_allowed_by_context")
    partner_by_context= fields.Many2one('res.partner', compute="_get_partner_by_context")




    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # TDE FIXME: strange
        if self._context.get('search_default_categ_id'):
            args.append((('categ_id', 'child_of', self._context['search_default_categ_id'])))
        return super(ProductTemplate, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        if self._table=='product_template' and self._context.get('partner_id', False):
            self._apply_product_rules(query=query, mode=mode)
        return super(ProductTemplate, self)._apply_ir_rules(query=query, mode=mode)


    @api.model
    def _apply_product_rules(self, query, mode='read'):
        """Add what's missing in ``query`` to implement all appropriate ir.rules
          (using the ``model_name``'s rules or the current model's rules if ``model_name`` is None)

           :param query: the current query object
        """
        #if self._uid == SUPERUSER_ID:
        #    return

        def apply_rule(clauses, params, tables, parent_model=None):
            """ :param parent_model: name of the parent model, if the added
                    clause comes from a parent model
            """
            if clauses:
                if parent_model:
                    # as inherited rules are being applied, we need to add the
                    # missing JOIN to reach the parent table (if not JOINed yet)
                    parent_table = '"%s"' % self.env[parent_model]._table
                    parent_alias = '"%s"' % self._inherits_join_add(self, parent_model, query)
                    # inherited rules are applied on the external table, replace
                    # parent_table by parent_alias
                    clauses = [clause.replace(parent_table, parent_alias) for clause in clauses]
                    # replace parent_table by parent_alias, and introduce
                    # parent_alias if needed
                    tables = [
                        (parent_table + ' as ' + parent_alias) if table == parent_table \
                            else table.replace(parent_table, parent_alias)
                        for table in tables
                    ]
                query.where_clause += clauses
                query.where_clause_params += params
                for table in tables:
                    if table not in query.tables:
                        query.tables.append(table)


        # apply main rules on the object
        Rule = self.env['product.rule']
        print(self._name)

        where_clause, where_params, tables = Rule.domain_get(self._name, mode)
        apply_rule(where_clause, where_params, tables)

        # apply ir.rules from the parents (through _inherits)
        for parent_model in self._inherits:
            where_clause, where_params, tables = Rule.domain_get(parent_model, mode)
            apply_rule(where_clause, where_params, tables, parent_model)


    @api.model
    def search3232(self, args, offset=0, limit=None, order=None, count=False):
        """ Display only standalone contact matching ``args`` or having
        attached contact matching ``args`` """
        ctx = self.env.context
        if (ctx.get('res.partner', False)):
            args = expression.normalize_domain(args)
            attached_contact_args = expression.AND(
                (args, [('contact_type', '=', 'attached')])
            )
            attached_contacts = super(ResPartner, self).search(
                attached_contact_args)
            args = expression.OR((
                expression.AND(([('contact_type', '=', 'standalone')], args)),
                [('other_contact_ids', 'in', attached_contacts.ids)],
            ))
        return super(ResPartner, self).search(args, offset=offset,
                                              limit=limit, order=order,
                                              count=count)

from odoo import SUPERUSER_ID