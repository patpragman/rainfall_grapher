import airportsdata
airports = airportsdata.load()  # key is ICAO code, the default
print(airports['PAMR'])