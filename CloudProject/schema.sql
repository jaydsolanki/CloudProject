DROP TABLE IF EXISTS parking_data;
CREATE TABLE parking_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude DOUBLE,
    longitude DOUBLE,
    parking_spots INTEGER,
    street_ave_name VARCHAR(100),
    between_street_ave VARCHAR(100),
    parking_allowed BOOL
)
