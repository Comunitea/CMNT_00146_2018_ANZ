# -*- coding: utf-8 -*-
session.open(db='anzamar')

# import ipdb; ipdb.set_trace()

# Creo atributo marca:
vals = {
    'name': 'MARCA',
    'product_brand_id': 194,
    'product_type_id': 61,
    'create_variant': True,
    'feature': True,
    'type': 'select'
}
att_brand = session.env['product.attribute'].create(vals)

brands = session.env['product.brand'].search([])
for brand in brands:
    vals = {
        'attribute_id': att_brand.id,
        'name': brand.name
    }
    session.env['product.attribute.value'].create(vals)


templates = session.env['product.template'].search([])

product_brand_id = session.env['product.attribute'].\
    search([('name', '=', 'MARCA')]).id


num_total = len(templates)
idx = 0
for tmp in templates:
    idx += 1
    att_lst_vals = []
    if not tmp.attribute_line_ids:
        continue
    att = tmp.attribute_line_ids.filtered(
        lambda r: r.attribute_id.create_variant and
        r.attribute_id.feature is False)[0].attribute_id

    evals = ['product_brand_id']

    for field in evals:
        field_name = 'att.' + field
        brand_instance = eval(field_name)
        attribute_id = eval(field)

        if not brand_instance and tmp.product_brand_id:
            brand_instance = tmp.product_brand_id
        if brand_instance:

            domain = [
                ('attribute_id', '=', attribute_id),
                ('name', '=', brand_instance.name),
            ]
            value = session.env['product.attribute.value'].search(domain,
                                                                  limit=1)

            if not value:
                continue

            vals = {
                # 'product_tmpl_id': tmp.id,
                'attribute_id': attribute_id,
                'value_ids': [(6, 0, [value.id])],
            }
            att_lst_vals.append((0, 0, vals))

    tmp.write({'attribute_line_ids': att_lst_vals})
    print('PROCESADO %s/%s' % (idx, num_total))



session.cr.commit()
exit()
