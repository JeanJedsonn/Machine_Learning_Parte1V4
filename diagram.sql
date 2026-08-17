-- Diagrama ERD para ERD Editor (Sintaxis SQL DDL)

CREATE TABLE Factions (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  link VARCHAR(255)
);

CREATE TABLE Sources (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  type VARCHAR(255),
  edition VARCHAR(255),
  version VARCHAR(255),
  errata_date VARCHAR(255),
  errata_link VARCHAR(255)
);

CREATE TABLE Datasheets (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  faction_id VARCHAR(255),
  source_id VARCHAR(255),
  legend VARCHAR(255),
  role VARCHAR(255),
  loadout TEXT,
  transport TEXT,
  virtual VARCHAR(255),
  leader_head TEXT,
  leader_footer TEXT,
  damaged_w VARCHAR(255),
  damaged_description TEXT,
  link VARCHAR(255),
  FOREIGN KEY (faction_id) REFERENCES Factions(id),
  FOREIGN KEY (source_id) REFERENCES Sources(id)
);

CREATE TABLE Abilities (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  legend VARCHAR(255),
  faction_id VARCHAR(255),
  description TEXT,
  FOREIGN KEY (faction_id) REFERENCES Factions(id)
);

CREATE TABLE Detachment_Abilities (
  id VARCHAR(255) PRIMARY KEY,
  faction_id VARCHAR(255),
  name VARCHAR(255),
  legend VARCHAR(255),
  description TEXT,
  detachment VARCHAR(255),
  FOREIGN KEY (faction_id) REFERENCES Factions(id)
);

CREATE TABLE Enhancements (
  id VARCHAR(255) PRIMARY KEY,
  faction_id VARCHAR(255),
  name VARCHAR(255),
  cost INT,
  detachment VARCHAR(255),
  legend VARCHAR(255),
  description TEXT,
  FOREIGN KEY (faction_id) REFERENCES Factions(id)
);

CREATE TABLE Stratagems (
  id VARCHAR(255) PRIMARY KEY,
  faction_id VARCHAR(255),
  name VARCHAR(255),
  type VARCHAR(255),
  cp_cost VARCHAR(255),
  legend VARCHAR(255),
  turn VARCHAR(255),
  phase VARCHAR(255),
  detachment VARCHAR(255),
  description TEXT,
  FOREIGN KEY (faction_id) REFERENCES Factions(id)
);

CREATE TABLE DS_Abilities (
  datasheet_id VARCHAR(255),
  line INT,
  ability_id VARCHAR(255),
  model VARCHAR(255),
  name VARCHAR(255),
  description TEXT,
  type VARCHAR(255),
  parameter VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id),
  FOREIGN KEY (ability_id) REFERENCES Abilities(id)
);

CREATE TABLE DS_Detachment_Abilities (
  datasheet_id VARCHAR(255),
  detachment_ability_id VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id),
  FOREIGN KEY (detachment_ability_id) REFERENCES Detachment_Abilities(id)
);

CREATE TABLE DS_Enhancements (
  datasheet_id VARCHAR(255),
  enhancement_id VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id),
  FOREIGN KEY (enhancement_id) REFERENCES Enhancements(id)
);

CREATE TABLE DS_Keywords (
  datasheet_id VARCHAR(255),
  keyword VARCHAR(255),
  model VARCHAR(255),
  is_faction_keyword BOOLEAN,
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id)
);

CREATE TABLE DS_Leader (
  leader_id VARCHAR(255),
  attached_id VARCHAR(255),
  FOREIGN KEY (leader_id) REFERENCES Datasheets(id),
  FOREIGN KEY (attached_id) REFERENCES Datasheets(id)
);

CREATE TABLE DS_Model_Costs (
  datasheet_id VARCHAR(255),
  line INT,
  description TEXT,
  cost VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id)
);

CREATE TABLE DS_Models (
  datasheet_id VARCHAR(255),
  line INT,
  name VARCHAR(255),
  M VARCHAR(255),
  T VARCHAR(255),
  Sv VARCHAR(255),
  inv_sv VARCHAR(255),
  inv_sv_descr VARCHAR(255),
  W VARCHAR(255),
  Ld VARCHAR(255),
  OC VARCHAR(255),
  base_size VARCHAR(255),
  base_size_descr VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id)
);

CREATE TABLE DS_Options (
  datasheet_id VARCHAR(255),
  line INT,
  button VARCHAR(255),
  description TEXT,
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id)
);

CREATE TABLE DS_Stratagems (
  datasheet_id VARCHAR(255),
  stratagem_id VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id),
  FOREIGN KEY (stratagem_id) REFERENCES Stratagems(id)
);

CREATE TABLE DS_Unit_Comp (
  datasheet_id VARCHAR(255),
  line INT,
  description TEXT,
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id)
);

CREATE TABLE DS_Wargear (
  datasheet_id VARCHAR(255),
  line INT,
  line_in_wargear INT,
  dice VARCHAR(255),
  name VARCHAR(255),
  description TEXT,
  range VARCHAR(255),
  type VARCHAR(255),
  A VARCHAR(255),
  BS_WS VARCHAR(255),
  S VARCHAR(255),
  AP VARCHAR(255),
  D VARCHAR(255),
  FOREIGN KEY (datasheet_id) REFERENCES Datasheets(id)
);

CREATE TABLE Last_Update (
  last_update VARCHAR(255)
);
