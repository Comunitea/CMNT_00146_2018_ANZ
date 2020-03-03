# -*- coding: utf-8 -*-
session.open(db='anzamar')

import time
inicio_de_tiempo = time.time()


# templates = session.env['product.template'].search(
#     [('id', 'in', [49303, 49265])])

templates = session.env['product.template'].search([])

product_age_id = session.env['product.attribute'].\
    search([('name', '=', 'EDAD')]).id
product_gender_id = session.env['product.attribute'].\
    search([('name', '=', 'GENERO')]).id
product_type_id = session.env['product.attribute'].\
    search([('name', '=', 'TIPO PRODUCTO')]).id
product_brand_id = session.env['product.attribute'].\
    search([('name', '=', 'MARCA')]).id

num_total = len(templates)
idx = 0
for tmp in templates:
    idx += 1
    att_lst_vals = []
    if not tmp.attribute_line_ids:
        continue
    att = tmp.attribute_line_ids[0].attribute_id

    evals = ['product_type_id', 'product_gender_id', 'product_age_id',
             'product_brand_id']

    for field in evals:
        field_name = 'att.' + field
        tag_instance = eval(field_name)
        attribute_id = eval(field)
        if tag_instance:

            if field != 'product_brand_id':
                domain = [
                    ('attribute_id', '=', attribute_id),
                    ('name', '=', tag_instance.value),
                ]
            else:
                domain = [
                    ('attribute_id', '=', attribute_id),
                    ('name', '=', tag_instance.name),
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

tiempo_final = time.time()
tiempo_transcurrido = tiempo_final - inicio_de_tiempo
tiempo_horas = tiempo_transcurrido / 3600
print("\nTomo %d horas." % (tiempo_horas))

session.cr.commit()
exit()
