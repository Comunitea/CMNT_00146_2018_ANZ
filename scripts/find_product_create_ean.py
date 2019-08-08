# -*- coding: utf-8 -*-
import os
import csv

session.open(db='anzamar')
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

path = script_path + '/eans2import.csv'



processed = 0
duplicated_by_ean = {}
products_ok = session.env['product.product']
products_fixed = session.env['product.product']
not_found = []
with open(path, 'r') as file:
    reader = csv.reader(file)
    # import ipdb; ipdb.set_trace()
    for row in reader:
        processed += 1
        ean13 = row[0]
        false_code = ean13[2:-2]
        print(ean13)
        print(false_code)

        # BUSCO DESACTIVADOS CON EAN Y SE LO QUITO
        domain = [('active', '=', False), ('barcode', '=', ean13)]
        products_desactivated = session.env['product.product'].search(domain)
        products_desactivated.write({'barcode': False})

        # BUSCO SOLO POR EAN
        domain = [('barcode', '=', ean13)]
        products = session.env['product.product'].search(domain, limit=1)
        if products:
            products_ok += products
            continue  # DESCARTO LOS QUE TIENEN EAN

        # BUSCO POR REFERENCIA FALSE
        else:
            domain = [('default_code', '=', false_code)]
            products_no_ean = session.env['product.product'].search(domain)
            if products_no_ean:
                if len(products_no_ean) == 1:
                    product = products_no_ean[0]
                    product.write({'barcode': ean13})
                    products_fixed += products_no_ean
                    continue  # CORRIGO LOS QUE ENCUENTO
                else:
                    duplicated_by_ean[ean13] = products_no_ean
                    continue  # ME SALTO LOS DUPLICADOS PARA LUEGO
            else:
                not_found.append(ean13)
                continue  # NO ENCONTRADOS

    print("DE UN TOTAL DE %s" % processed)
    print("Ya correctos %s" % len(products_ok))
    print("Encontrados y corregidos %s" % len(products_fixed))
    print("Duplicados %s" % len(duplicated_by_ean.keys()))
    print("No encontrados %s" % len(not_found))

    sum_processed = len(products_ok) + len(products_fixed) + \
        len(duplicated_by_ean.keys()) + len(not_found)
    print("PROCESADOS %s" % sum_processed)

    # ESCRIBO FICHERO DE NO ENCONTRADOS
    output_file = open(script_path + '/eans2fix.csv', 'w')
    for ean13 in not_found:
        output_file.write(ean13 + '\n')
session.cr.commit()
exit()
