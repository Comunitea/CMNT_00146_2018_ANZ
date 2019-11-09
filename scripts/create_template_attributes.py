# -*- coding: utf-8 -*-
session.open(db='anzamar')

# import ipdb; ipdb.set_trace()

# Creo atributo género:
vals = {
    'name': 'GENERO',
    'product_brand_id': 194,
    'product_type_id': 61,
    'create_variant': True,
    'feature': True,
    'type': 'select'
}
att_genero = session.env['product.attribute'].create(vals)

genero_tags = session.env['product.attribute.tag'].search([('type', '=', 'gender')])
genero_tags_vals = genero_tags.mapped('value')
genero_tags_vals = list(set(genero_tags_vals))


for val in genero_tags_vals:
    vals = {
        'attribute_id': att_genero.id,
        'name': val
    }
    session.env['product.attribute.value'].create(vals)



# Creo atributo tipo producto:
vals = {
    'name': 'TIPO PRODUCTO',
    'product_brand_id': 194,
    'product_type_id': 61,
    'create_variant': True,
    'feature': True,
    'type': 'select'
}
att_tipo = session.env['product.attribute'].create(vals)

tipo_tags = session.env['product.attribute.tag'].search([('type', '=', 'type')])
tipo_tags_vals = tipo_tags.mapped('value')
tipo_tags_vals = list(set(tipo_tags_vals))
for tipo in tipo_tags_vals:
    vals = {
        'attribute_id': att_tipo.id,
        'name': tipo
    }
    session.env['product.attribute.value'].create(vals)



# Creo atributo tipo edad:
vals = {
    'name': 'EDAD',
    'product_brand_id': 194,
    'product_type_id': 61,
    'create_variant': True,
    'feature': True,
    'type': 'select'
}
att_edad = session.env['product.attribute'].create(vals)

edad_tags = session.env['product.attribute.tag'].search([('type', '=', 'age')])
edad_tags_vals = edad_tags.mapped('value')
edad_tags_vals = list(set(edad_tags_vals))
for edad in edad_tags_vals:
    vals = {
        'attribute_id': att_edad.id,
        'name': edad
    }
    session.env['product.attribute.value'].create(vals)


session.cr.commit()
exit()
