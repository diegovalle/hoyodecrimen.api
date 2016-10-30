import neighbors
for key, value in neighbors.neighbors.iteritems():
  sql = ("CREATE INDEX cuadrantes_neighbors_partial" + neighbors.neighbors[key][0].replace('-','_').replace('.',"_") 
        + " ON cuadrantes (date) WHERE ")
  sql += "(upper(cuadrantes.cuadrante) = '" + neighbors.neighbors[key][0] +"' OR upper(cuadrantes.cuadrante) = '" 
  sql += neighbors.neighbors[key][1] +"' OR upper(cuadrantes.cuadrante) = '" 
  sql += neighbors.neighbors[key][2] +"' OR upper(cuadrantes.cuadrante) = '" 
  sql += neighbors.neighbors[key][3] +"' OR upper(cuadrantes.cuadrante) ='" 
  sql += neighbors.neighbors[key][4] 
  sql += "' OR upper(cuadrantes.cuadrante) = '" + neighbors.neighbors[key][5]
  sql += "' OR upper(cuadrantes.cuadrante) = '" + neighbors.neighbors[key][6] 
  sql +=  "' OR upper(cuadrantes.cuadrante) = '" + neighbors.neighbors[key][7] 
  sql +=  "' OR upper(cuadrantes.cuadrante) = '" + neighbors.neighbors[key][8] +"');"
  print(sql)
