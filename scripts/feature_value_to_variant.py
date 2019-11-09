# -*- coding: utf-8 -*-
session.open(db='anzamar')

templates = session.env['product.template'].search([])

num_total = len(templates)
idx = 0
for tmpl_id in templates:

    idx += 1
    att_lst_vals = []
    # adding an attribute with only one value should not recreate product
    # write this attribute on every product to make sure we don't lose them
    variant_alone = tmpl_id.attribute_line_ids.filtered(
        lambda line: line.attribute_id.create_variant and len(line.value_ids) == 1).mapped('value_ids')
    for value_id in variant_alone:
        updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
        updated_products.write({'attribute_value_ids': [(4, value_id.id)]})

    print('PROCESADO %s/%s' % (idx, num_total))

session.cr.commit()
exit()
