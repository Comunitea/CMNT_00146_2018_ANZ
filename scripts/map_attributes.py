# -*- coding: utf-8 -*-
session.open(db='anzamar')

# import ipdb; ipdb.set_trace()

pa = session.env['product.attribute']
pav = session.env['product.attribute.value']

APPAREL_ADULTO = pa.create({'name': 'APPAREL ADULTO', 'type': 'select'})
APPAREL_JUNIOR = pa.create({'name': 'APPAREL JUNIOR', 'type': 'select'})
APPAREL_BEBE = pa.create({'name': 'APPAREL BEBE', 'type': 'select'})
SOCKS = pa.create({'name': 'SOCKS', 'type': 'select'})
HARDWARE = pa.create({'name': 'HARDWARE', 'type': 'select'})
FOOTWEAR_INFANT = pa.create({'name': 'FOOTWEAR_INFANT', 'type': 'select'})
FOOTWEAR_KIDS = pa.create({'name': 'FOOTWEAR_KIDS', 'type': 'select'})
FOOTWEAR_JUNIOR = pa.create({'name': 'FOOTWEAR_JUNIOR', 'type': 'select'})
FOOTWEAR_ADULT = pa.create({'name': 'FOOTWEAR_ADULT', 'type': 'select'})

UNKNOW = pa.create({'name': '**UNKNOW'})

MAPINGS = {
    'APPAREAL': APPAREL_ADULTO,
    'Apparel': 'select',
    'APPAREL': 'select',
    'BALONES DE BALONCESTO': HARDWARE,
    'BALONES DE FUTBOL': HARDWARE,
    'BAÑADOR NK ADULTO': HARDWARE,
    'CALCETINES ADIDAS/PUMA': SOCKS,
    'CALCETINES NK': SOCKS,
    'CALCETIN UMBRO': SOCKS,
    'CALZADO': FOOTWEAR_ADULT,
    'CALZADO EUROPEO': FOOTWEAR_ADULT,
    'CALZADO JOHN SMITH': FOOTWEAR_ADULT,
    'CALZADO JOMA CABALLERO': FOOTWEAR_ADULT,
    'CALZADO JUNIOR EUROPEO': FOOTWEAR_JUNIOR,
    'CALZADO MIZUNO CABALLERO': FOOTWEAR_ADULT,
    'CALZADO MIZUNO SEÑORA': FOOTWEAR_ADULT,
    'CALZADO NEW BALANCE CRO.': FOOTWEAR_ADULT,
    'CALZADO NEW BALANCE JR.': FOOTWEAR_JUNIOR,
    'CALZADO NEW BALANCE KIDS': FOOTWEAR_KIDS,
    'CALZADO NEW BALANCE SRA.': FOOTWEAR_ADULT,
    'CALZADO NEW BALANCE SRA.2': FOOTWEAR_ADULT,
    'CALZADO NK CABALLERO': FOOTWEAR_ADULT,
    'CALZADO NK NIÑOS (GS)': FOOTWEAR_JUNIOR,
    'CALZADO NK NIÑOS (PS)': FOOTWEAR_KIDS,
    'CALZADO NK NIÑOS (TD)': FOOTWEAR_INFANT,
    'CALZADO NK SEÑORA': FOOTWEAR_ADULT,
    'CALZADO PUMA CABALLERO': FOOTWEAR_ADULT,
    'CALZADO PUMA SEÑORA': FOOTWEAR_ADULT,
    'CALZADO REEBOK CABALLERO': FOOTWEAR_ADULT,
    'CALZADO REEBOK CHILDRENS': FOOTWEAR_KIDS,
    'CALZADO REEBOK INFANTIL': FOOTWEAR_INFANT,
    'CALZADO REEBOK JUNIOR': FOOTWEAR_JUNIOR,
    'CALZADO REEBOK NIÑO/A': FOOTWEAR_KIDS, 
    'CALZADO REEBOK SEÑORA': FOOTWEAR_ADULT,
    'CALZADO SEÑORA EUROPEO': FOOTWEAR_ADULT,
    'calzado umbro caballero': FOOTWEAR_ADULT,
    'CALZADO UMBRO JUNIOR': FOOTWEAR_JUNIOR,
    'CALZADO VANS ADULTO': FOOTWEAR_ADULT, 
    'CALZADO VANS JUNIOR': FOOTWEAR_JUNIOR,
    'CALZADO VANS NIÑA': FOOTWEAR_KIDS,
    'CALZADO VANS SEÑORA': FOOTWEAR_ADULT,
    'CHANCLAS ADIDAS': FOOTWEAR_ADULT,
    'CHANCLAS ADIDAS JR': FOOTWEAR_JUNIOR,
    # 'Color':
    # 'Color de fornituras':
    'cuc': UNKNOW,  # TODO, REVISAR, NO DEBERÍA HABER NINGUNA
    # 'EDAD':
    'Equipment': HARDWARE,
    'ESCUDO': HARDWARE,
    'ESPINILLERAS CABALLERO': HARDWARE,  
    'ESPINILLERAS INFANTIL': HARDWARE,  
    'ESPINILLERAS JUNIOR': HARDWARE,  
    'Footwear': FOOTWEAR_JUNIOR,
    'FOOTWEAR': 'select',
    'FOOTWEAR ': FOOTWEAR_ADULT,
    # 'GENERO':
    'GORRAS ADIDAS': HARDWARE,
    'GUANTES': HARDWARE,
    'GUANTES DE FUTBOL': HARDWARE,
    'HARDWARE': HARDWARE,
    'Indeterminada': UNKNOW,
    'MEDIAS FUTBOL': HARDWARE,
    'PROTECCIONES': HARDWARE,
    'RAQUETAS': HARDWARE,
    'STREET TRAINERS': HARDWARE,
    'TALLAJE UNICO': HARDWARE,
    'Tamaño de fornituras': UNKNOW,  # TODO, ARTICULOS NO VENTA, NO VER EN WEB
    'TEXTIL ADIDAS BEBE': APPAREL_BEBE,
    'TEXTIL ADIDAS CABALLERO': APPAREL_ADULTO,
    'TEXTIL ADIDAS CABALLERO 2': APPAREL_ADULTO,
    'TEXTIL ADIDAS INFANTIL': APPAREL_JUNIOR,
    'TEXTIL ADIDAS JUN-CAB': APPAREL_JUNIOR,
    'TEXTIL ADIDAS JUNIOR': APPAREL_JUNIOR,
    'TEXTIL ADIDAS SEÑORA': APPAREL_ADULTO,
    'TEXTIL ADULTO': APPAREL_ADULTO,
    'TEXTIL BAÑADOR': APPAREL_ADULTO,
    'TEXTIL BEBE':  APPAREL_BEBE,
    'TEXTIL BETIS JR': APPAREL_JUNIOR,
    'TEXTIL CASTELLANO': APPAREL_ADULTO,
    'TEXTIL JOHN SMITH': APPAREL_ADULTO,
    'TEXTIL JOMA JR': APPAREL_JUNIOR,
    'TEXTIL JR': APPAREL_JUNIOR,
    'Textil Junior España': APPAREL_JUNIOR,
    'Textil Junior Internacional': APPAREL_JUNIOR,
    'TEXTIL JUNIOR NIKE': APPAREL_JUNIOR,
    'TEXTIL NIÑO/A': APPAREL_JUNIOR,
    'TEXTIL NK BEBE': APPAREL_BEBE,
    'TEXTIL NK CABALLERO': APPAREL_ADULTO,
    'TEXTIL NK NIÑA (GS)': APPAREL_JUNIOR,
    'TEXTIL NK NIÑA (LG)': APPAREL_JUNIOR,
    'TEXTIL NK NIÑO (BS)': APPAREL_JUNIOR,
    'TEXTIL NK NIÑO (LB)': APPAREL_JUNIOR,
    'TEXTIL NK SEÑORA': APPAREL_ADULTO,
    'TEXTIL PUMA JR': APPAREL_JUNIOR,
    # 'Tipo de bota':
    # 'TIPO PRODUCTO':
}


def select_unique_att(att):
    res = False
    # Apparel
    if att.name == 'Apparel':
        if 'ADULT' in att.product_age_id.value:
            res = APPAREL_ADULTO
        elif 'JUNIOR' in att.product_age_id.value:
            res = APPAREL_JUNIOR
    # APPAREL
    elif att.name == 'APPAREL':
        if 'ADULT' in att.product_age_id.value:
            res = APPAREL_ADULTO
        elif 'JUNIOR' in att.product_age_id.value:
            res = APPAREL_JUNIOR
        elif 'KIDS' in att.product_age_id.value:
            res = APPAREL_JUNIOR
        elif 'INFANT' in att.product_age_id.value:
            res = APPAREL_BEBE
        elif 'BEBE' in att.product_age_id.value:
            res = APPAREL_BEBE
        else:
            res = UNKNOW

    # FOOTWEAR
    elif att.name == 'FOOTWEAR':
        if 'INFANT' in att.product_age_id.value:
            res = FOOTWEAR_INFANT
        elif 'KIDS' in att.product_age_id.value:
            res = FOOTWEAR_KIDS
        elif 'JUNIOR' in att.product_age_id.value:
            res = FOOTWEAR_JUNIOR
        elif 'ADULT' in att.product_age_id.value:
            res = FOOTWEAR_KIDS
        else:
            res = UNKNOW
    return res


def get_map_att(att):
    map_att = False
    map_att = MAPINGS.get(att.name, False)
    if not map_att:
        return False

    if map_att == 'select':
        map_att = select_unique_att(att)

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