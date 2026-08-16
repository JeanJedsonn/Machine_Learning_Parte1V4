import os
import re
import csv
import sqlite3
from pathlib import Path

def get_base_dir() -> Path:
    """Obtiene el directorio base del proyecto."""
    return Path(__file__).resolve().parent

def extraer_ddl_tablas(sql_path: Path, tablas_permitidas: list[str]) -> list[tuple[str, str]]:
    """
    Extrae únicamente las sentencias CREATE TABLE para las tablas especificadas
    en 'tablas_permitidas' a partir de diagrama.sql, removiendo foreign keys
    a tablas no incluidas.
    """
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);', re.DOTALL | re.IGNORECASE)
    ddl_tablas = {}

    for match in pattern.finditer(content):
        table_name = match.group(1)
        if table_name in tablas_permitidas:
            body = match.group(2)
            # Filtrar foreign keys que apunten a tablas no existentes en el conjunto
            lines = body.split("\n")
            cleaned_lines = []
            for line in lines:
                fk_match = re.search(r'FOREIGN\s+KEY\s*\([^)]+\)\s*REFERENCES\s+(\w+)', line, re.IGNORECASE)
                if fk_match and fk_match.group(1) not in tablas_permitidas:
                    continue
                cleaned_lines.append(line)
            
            # Limpiar comas sobrantes al final del cuerpo
            new_body = "\n".join(cleaned_lines)
            new_body = re.sub(r',\s*$', '', new_body.rstrip())
            stmt = f"CREATE TABLE IF NOT EXISTS {table_name} (\n{new_body}\n);"
            ddl_tablas[table_name] = stmt

    # Retornar en el orden de tablas_permitidas
    return [(tbl, ddl_tablas[tbl]) for tbl in tablas_permitidas if tbl in ddl_tablas]

def crear_base_de_datos(db_filename: str = "warhammer40k.db"):
    base_dir = get_base_dir()
    db_path = base_dir / db_filename
    sql_path = base_dir / "diagrama.sql"
    importantes_dir = base_dir / "importantes"

    # Mapeo ordenado de archivos CSV en 'importantes' y sus tablas asociadas
    # Orden respetando dependencias: Factions -> Datasheets -> Tablas hijas
    csv_to_table_map = [
        ("Wahapedia Data Export - Factions.csv", "Factions"),
        ("Wahapedia Data Export - Datasheets.csv", "Datasheets"),
        ("Wahapedia Data Export - DS_Models.csv", "DS_Models"),
        ("Wahapedia Data Export - DS_Model Costs.csv", "DS_Model_Costs"),
        ("Wahapedia Data Export - DS_Wargear.csv", "DS_Wargear"),
    ]

    tablas_permitidas = [table for _, table in csv_to_table_map]

    print("=" * 60)
    print("CREACIÓN DE BASE DE DATOS SQLITE (SOLO TABLAS IMPORTANTES)")
    print("=" * 60)
    print(f"Directorio base:   {base_dir}")
    print(f"Archivo de BD:     {db_path}")
    print(f"Archivo SQL:       {sql_path}")
    print(f"Tablas a incluir:  {', '.join(tablas_permitidas)}")
    print("-" * 60)

    # Eliminar la base de datos previa para recrearla limpiamente
    if db_path.exists():
        print(f"Eliminando base de datos previa: {db_filename}...")
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Extraer y crear únicamente las tablas seleccionadas
    print("\n1. Extrayendo y creando esquema de las 5 tablas desde diagrama.sql...")
    ddl_list = extraer_ddl_tablas(sql_path, tablas_permitidas)

    for tbl_name, ddl in ddl_list:
        cursor.execute(ddl)
        print(f"   -> Creada tabla: {tbl_name}")

    conn.commit()

    # 2. Insertar los datos desde los archivos CSV de 'importantes'
    print("\n2. Insertando datos desde archivos CSV en 'importantes'...")
    resumen = []

    for csv_file, table_name in csv_to_table_map:
        csv_path = importantes_dir / csv_file
        if not csv_path.exists():
            print(f"   [AVISO] No se encontró el archivo: {csv_file}")
            continue

        with open(csv_path, "r", encoding="utf-8", newline="", errors="replace") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                print(f"   [AVISO] Archivo vacío: {csv_file}")
                continue

            # Limpiar encabezados
            headers = [h.strip().replace("\ufeff", "") for h in headers]
            placeholders = ", ".join(["?"] * len(headers))
            cols_str = ", ".join([f'"{h}"' for h in headers])
            query = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'

            rows = []
            for row in reader:
                # Convertir cadenas vacías a None (NULL en SQLite)
                cleaned_row = [val if val != "" else None for val in row]
                rows.append(cleaned_row)

            cursor.executemany(query, rows)
            conn.commit()
            print(f"   -> Tabla '{table_name}': {len(rows)} filas insertadas desde '{csv_file}'")
            resumen.append((table_name, csv_file, len(rows)))

    # 3. Verificación de tablas en la base de datos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tablas_existentes = [row[0] for row in cursor.fetchall()]

    print("\n" + "=" * 60)
    print("RESUMEN DE CARGA Y TABLAS EN LA BASE DE DATOS")
    print("=" * 60)
    print(f"Total tablas creadas: {len(tablas_existentes)} -> {tablas_existentes}")
    print("-" * 60)
    print(f"{'Tabla':<20} | {'Filas en BD':<14} | {'Archivo Origen'}")
    print("-" * 60)
    for table_name, csv_file, count in resumen:
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        db_count = cursor.fetchone()[0]
        print(f"{table_name:<20} | {db_count:<14} | {csv_file}")

    conn.close()
    print("-" * 60)
    print(f"¡Base de datos generada exitosamente en: {db_path.name}!")
    print("=" * 60)

if __name__ == "__main__":
    crear_base_de_datos()
