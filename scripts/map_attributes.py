# -*- coding: utf-8 -*-
session.open(db='anzamar')

# import ipdb; ipdb.set_trace()

pa = session.env['product.attribute']
pav = session.env['product.attribute.value']

APPAREL = pa.create({'name': 'APPAREL', 'type': 'select'})
# APPAREL = pa.create({'name': 'APPAREL ADULTO', 'type': 'select'})
# APPAREL = pa.create({'name': 'APPAREL JUNIOR', 'type': 'select'})
# APPAREL = pa.create({'name': 'APPAREL BEBE', 'type': 'select'})
SOCKS = pa.create({'name': 'SOCKS', 'type': 'select'})
HARDWARE = pa.create({'name': 'HARDWARE', 'type': 'select'})
FOOTWEAR = pa.create({'name': 'FOOTWEAR', 'type': 'select'})
# FOOTWEAR= pa.create({'name': 'FOOTWEAR', 'type': 'select'})
# FOOTWEAR= pa.create({'name': 'FOOTWEAR', 'type': 'select'})
# FOOTWEAR= pa.create({'name': 'FOOTWEAR', 'type': 'select'})
# FOOTWEAR= pa.create({'name': 'FOOTWEAR', 'type': 'select'})

UNKNOW = pa.create({'name': '**UNKNOW'})

MAPINGS = {
    'APPAREAL': APPAREL,
    'Apparel': APPAREL,
    'APPAREL': APPAREL,
    'BALONES DE BALONCESTO': HARDWARE,
    'BALONES DE FUTBOL': HARDWARE,
    'BAÑADOR NK ADULTO': HARDWARE,
    'CALCETINES ADIDAS/PUMA': SOCKS,
    'CALCETINES NK': SOCKS,
    'CALCETIN UMBRO': SOCKS,
    'CALZADO': FOOTWEAR,
    'CALZADO EUROPEO': FOOTWEAR,
    'CALZADO JOHN SMITH': FOOTWEAR,
    'CALZADO JOMA CABALLERO': FOOTWEAR,
    'CALZADO JUNIOR EUROPEO': FOOTWEAR,
    'CALZADO MIZUNO CABALLERO': FOOTWEAR,
    'CALZADO MIZUNO SEÑORA': FOOTWEAR,
    'CALZADO NEW BALANCE CRO.': FOOTWEAR,
    'CALZADO NEW BALANCE JR.': FOOTWEAR,
    'CALZADO NEW BALANCE KIDS': FOOTWEAR,
    'CALZADO NEW BALANCE SRA.': FOOTWEAR,
    'CALZADO NEW BALANCE SRA.2': FOOTWEAR,
    'CALZADO NK CABALLERO': FOOTWEAR,
    'CALZADO NK NIÑOS (GS)': FOOTWEAR,
    'CALZADO NK NIÑOS (PS)': FOOTWEAR,
    'CALZADO NK NIÑOS (TD)': FOOTWEAR,
    'CALZADO NK SEÑORA': FOOTWEAR,
    'CALZADO PUMA CABALLERO': FOOTWEAR,
    'CALZADO PUMA SEÑORA': FOOTWEAR,
    'CALZADO REEBOK CABALLERO': FOOTWEAR,
    'CALZADO REEBOK CHILDRENS': FOOTWEAR,
    'CALZADO REEBOK INFANTIL': FOOTWEAR,
    'CALZADO REEBOK JUNIOR': FOOTWEAR,
    'CALZADO REEBOK NIÑO/A': FOOTWEAR,
    'CALZADO REEBOK SEÑORA': FOOTWEAR,
    'CALZADO SEÑORA EUROPEO': FOOTWEAR,
    'calzado umbro caballero': FOOTWEAR,
    'CALZADO UMBRO JUNIOR': FOOTWEAR,
    'CALZADO VANS ADULTO': FOOTWEAR,
    'CALZADO VANS JUNIOR': FOOTWEAR,
    'CALZADO VANS NIÑA': FOOTWEAR,
    'CALZADO VANS SEÑORA': FOOTWEAR,
    'CHANCLAS ADIDAS': FOOTWEAR,
    'CHANCLAS ADIDAS JR': FOOTWEAR,
    # 'Color':
    # 'Color de fornituras':
    'cuc': UNKNOW,  # TODO, REVISAR, NO DEBERÍA HABER NINGUNA
    # 'EDAD':
    'Equipment': HARDWARE,
    'ESCUDO': HARDWARE,
    'ESPINILLERAS CABALLERO': HARDWARE, 
    'ESPINILLERAS INFANTIL': HARDWARE, 
    'ESPINILLERAS JUNIOR': HARDWARE,
    'footwear': FOOTWEAR,
    'Footwear': FOOTWEAR,
    'FOOTWEAR ': FOOTWEAR,
    'FOOTWEAR': FOOTWEAR,
    # 'GENERO':
    'GORRAS ADIDAS': HARDWARE,
    'GUANTES': HARDWARE,
    'GUANTES DE FUTBOL': HARDWARE,
    'HARDWARE': HARDWARE,
    'Hardware': HARDWARE,
    'HARDWEAR': HARDWARE,
    'Hardwear': HARDWARE,
    'Ha': HARDWARE,
    'Indeterminada': UNKNOW,
    'MEDIAS FUTBOL': HARDWARE,
    'PROTECCIONES': HARDWARE,
    'RAQUETAS': HARDWARE,
    'STREET TRAINERS': HARDWARE,
    'TALLAJE UNICO': HARDWARE,
    'Tamaño de fornituras': UNKNOW,  # TODO, ARTICULOS NO VENTA, NO VER EN WEB
    'TEXTIL ADIDAS BEBE': APPAREL,
    'TEXTIL ADIDAS CABALLERO': APPAREL,
    'TEXTIL ADIDAS CABALLERO 2': APPAREL,
    'TEXTIL ADIDAS INFANTIL': APPAREL,
    'TEXTIL ADIDAS JUN-CAB': APPAREL,
    'TEXTIL ADIDAS JUNIOR': APPAREL,
    'TEXTIL ADIDAS SEÑORA': APPAREL,
    'TEXTIL ADULTO': APPAREL,
    'TEXTIL BAÑADOR': APPAREL,
    'TEXTIL BEBE':  APPAREL,
    'TEXTIL BETIS JR': APPAREL,
    'TEXTIL CASTELLANO': APPAREL,
    'TEXTIL JOHN SMITH': APPAREL,
    'TEXTIL JOMA JR': APPAREL,
    'TEXTIL JR': APPAREL,
    'Textil Junior España': APPAREL,
    'Textil Junior Internacional': APPAREL,
    'TEXTIL JUNIOR NIKE': APPAREL,
    'TEXTIL NIÑO/A': APPAREL,
    'TEXTIL NK BEBE': APPAREL,
    'TEXTIL NK CABALLERO': APPAREL,
    'TEXTIL NK NIÑA (GS)': APPAREL,
    'TEXTIL NK NIÑA (LG)': APPAREL,
    'TEXTIL NK NIÑO (BS)': APPAREL,
    'TEXTIL NK NIÑO (LB)': APPAREL,
    'TEXTIL NK SEÑORA': APPAREL,
    'TEXTIL PUMA JR': APPAREL,
    'TEXTTIL JU': APPAREL,
    # 'Tipo de bota':
    # 'TIPO PRODUCTO':

    'FOOTWEAR ': FOOTWEAR
}


def select_unique_att(att):
    res = False
    # Apparel
    if att.name == 'Apparel':
        res = APPAREL
        # if 'ADULT' in att.product_age_id.value:
        #     res = APPAREL
        # elif 'JUNIOR' in att.product_age_id.value:
        #     res = APPAREL
    # APPAREL
    elif att.name == 'APPAREL':
        # if 'ADULT' in att.product_age_id.value:
        #     res = APPAREL
        # elif 'JUNIOR' in att.product_age_id.value:
        #     res = APPAREL
        # elif 'KIDS' in att.product_age_id.value:
        #     res = APPAREL
        # elif 'INFANT' in att.product_age_id.value:
        #     res = APPAREL
        # elif 'BEBE' in att.product_age_id.value:
        #     res = APPAREL
        # else:
        #     res = FOOTWEAR
        res = APPAREL

    # FOOTWEAR
    elif att.name == 'FOOTWEAR':
        # if 'INFANT' in att.product_age_id.value:
        #     res = FOOTWEAR
        # elif 'KIDS' in att.product_age_id.value:
        #     res = FOOTWEAR
        # elif 'JUNIOR' in att.product_age_id.value:
        #     res = FOOTWEAR
        # elif 'ADULT' in att.product_age_id.value:
        #     res = FOOTWEAR
        # else:
        #     res = FOOTWEAR
        res = FOOTWEAR
    return res


def get_map_att(att):
    map_att = False
    map_att = MAPINGS.get(att.name, False)
    if not map_att:
        return False

    # if map_att == 'select':
    #     map_att = select_unique_att(att)

    return map_att


def map_att_values(att, map_att):
    res = False
    for value in att.value_ids:

        # Busco si existe value en el nuevo atributo
        domain = [('name', '=', value.name),
                  ('attribute_id', '=', map_att.id)]
        new_value = pav.search(domain, limit=1)
        # Si no existe lo creo
        if not new_value:
            vals = {
                'name': value.name,
                'attribute_id': map_att.id
            }
            new_value = pav.create(vals)

        # Actualizo m2m productos y valores
        query_product_values = """
        UPDATE product_attribute_value_product_product_rel
        SET product_attribute_value_id = %s
        WHERE product_attribute_value_id = %s
        """ % (new_value.id, value.id)

        session.cr.execute(query_product_values)

        # Actualizo m2m líneas de atributo y valores
        query_att_line_values = """
        UPDATE product_attribute_line_product_attribute_value_rel
        SET product_attribute_value_id = %s
        WHERE product_attribute_value_id = %s
        """ % (new_value.id, value.id)
        session.cr.execute(query_att_line_values)
    return res


def change_att_lines(att, map_att):
    res = False
    # Actualizo m2m líneas de atributo y valores
    query_att_line = """
    UPDATE product_attribute_line
    SET attribute_id = pa.new_att_id
    FROM product_attribute pa
    WHERE pa.id = product_attribute_line.attribute_id and pa.new_att_id is not null;
    """
    session.cr.execute(query_att_line)
    return res

domain = []
attributes = pa.search(domain)

num_total = len(attributes)
idx = 0
to_review = pa
for att in attributes:
    idx += 1
    print("******************************************************")
    print("PROCESANDO %s - %s / %s" % (att.name, idx, num_total))
    print("******************************************************")
    if att.is_tboot or att.is_color:
        print("IGNORO %s POR SER TIPO BOTA O COLOR" % att.name)
        continue
    if att.name.startswith('**'):
        print("IGNORO %s POR SER **" % att.name)
        continue

    map_att = get_map_att(att)
    if not map_att:
        print("IGNORO %s" % att.name)
        to_review += att
        continue

    # ESCRIBO NUEVO ATRIBUTO
    att.new_att_id = map_att.id

    # MAPERO LOS VALORES VIEJOS A LOS NUEVOISS
    map_att_values(att, map_att)

# ACTUALIZO LAS PLANTILLAS A LOS NUEVOS ATRIBUTOS
change_att_lines(att, map_att)

# Imprimo 2 review
if to_review:
    print("REVIEW:--------------------------------------------")
    print(to_review.ids)

session.cr.commit()
print("******************* DONE ****************************")
session.cr.close()
exit()