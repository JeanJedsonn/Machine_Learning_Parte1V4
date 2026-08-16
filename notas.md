# Tablas removidas
* sources
* * solo son links
* last_update
* * links sin importancia
* ds_options
* * informacion de graficos, no relevante
* ds_leader
* * se ve que es el leader de cada competencia, pero existe la referencia
* ds_unit compo
* * informacion de cuantas unidades tienen

### Tablas removidas por otros factores
* abilities 
* ds_abilities 
* detachment_abilities
* ds_detachment_abilities
* enhancements
* ds_enhancements
* stratagems
* ds_stratagems

fueron removidas por estar formadas casi en su totalidad por texto o por carecer de caracteristicas que puedan ser utilizadas para identificar la faccion de una unidad. Sin embargo, podrian tener informacion util para otros propositos.

# Tablas principales
### Datasheets
es la tabla principal, contiene la funcion objetivo faction_id, el nombre de la unidad name, 
#### Se le remueven las columas: 
* source_id, la tabla sources se elimina por completo
* legend, mucho texto que procesar de forma ineficiente
* role, indiferente para determinar si una unidad es d euna faccion u otra
* transport, gran cantidad de datos faltantes
* virtual, no aporta informacion
* leader_footer, gran cantidad de datos faltantes y no aportan
* damage_w, datos insuficientes (comprobar)
* link, url que no aporta

#### Columnas presentes
* id, identificador unico de la unidad
* name, nombre de la unidad
* faction_id, identificador unico de la faccion y variable objetivo
* loadout, informacion textual de las armas disponibles (las armas dan informacion de faccion)


### Factions
tabla que contiene el nombre de las facciones y su identificador unico, se utiliza para obtener el nombre de la faccion
#### Se le remueven las columas:
* link, url que no aporta
#### Columnas presentes
* id, identificador unico de la faccion
* name, nombre de la faccion

# Tablas con datos
### DS_Wargear
Tabla que contiene el armamento disponible para cada unidad
#### Se le remueven las columnas:
* line, line_in_wargear, dice.

#### Columnas presentes
* datasheet_id
* name
* description
* range
* type
* A
* BS_WS
* S
* AP
* D

### DS_Models
Tabla que contiene informacion del modelo
#### Se le remueven las columnas:
* Line
* INV_SV_DESCR, esta muy vacia 
* Base_Size
* Base_size_descr

#### Columnas presentes
* datasheet_id
* name
* M
* T
* SV
* INV_SV
* W
* LD
* OC

### DS_Model Cost
Costo del modelo y cantidad de unidades

#### Columnas presentes
* datasheet_id
* line (sigo sin saber que es)
* description
* cost
