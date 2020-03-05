-- ELIMINO valores de estos atributos que no se usan
delete from product_attribute_value where id in 
	(select id from product_attribute_value where attribute_id in 
		(select id from product_attribute
         where id not in (select distinct(attribute_id) from product_attribute_line) and is_tboot is not true and is_color is not true));
 
-- ELIMINO Atributos que no se usan en las plantillas ni son color ni tipo bota
delete from product_attribute
where id not in (select distinct(attribute_id) from product_attribute_line) and is_tboot is not true and is_color is not true;


-- ELIMINO valores de atributos que no están relaccionados con ningún producto ni  pertenecen a atributos que están en las plantillas
delete from product_attribute_value
where
	id not in (
	select
		distinct(product_attribute_value_id)
	from
		product_attribute_value_product_product_rel)
	and attribute_id not in (select distinct(attribute_id) from product_attribute_line);
	