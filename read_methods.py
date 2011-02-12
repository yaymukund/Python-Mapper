import utils

# Read Methods:
# 	The following methods primarily read from the database.

def get_cities(city_data, routes):
  """Get a list of city names and airport codes."""
  return [ (city['name'], city['code']) for city in city_data.values() ]

def get_cities_by_name(name, city_data, routes):
  """Get detailed information about all airports in a city.
  
  Return the data dictionary for every airport in the city, along with a
  dictionary containing information about adjacent cities.

  Keyword arguments:
  name -- The name of the city.
  """
  cities = utils.cities_named(name, city_data)
  
  adjacent = {}
  for city in cities:
  	ports = utils.find_adjacent(city['code'], routes)
  	adjacent[city['code']] = []

  	for port in ports:
  		adj_name = city_data[port]['name']
  		adj_code = city_data[port]['code']
  		adjacent[city['code']].append((adj_name, adj_code))

  return cities, adjacent

def get_longest_route(city_data, routes):
  """Return the longest route's data tuple."""
  distance = lambda route: route[2]
  sorted_routes = sorted(routes, key=distance)
  return sorted_routes.pop()

def get_shortest_route(city_data, routes):
  """Return the shortest route's data tuple."""
  distance = lambda route: route[2]
  sorted_routes = sorted(routes, key=distance, reverse=True)
  return sorted_routes.pop()

def get_avg_distance(city_data, routes):
  """Return the mean distance of the routes."""
  total = sum([route[2] for route in routes])
  avg = total / len(routes)
  return avg

def get_largest_city(city_data, routes):
  """Return the city with greatest population."""
  pop_sort = lambda city: city['population']
  sorted_cities = sorted(city_data.values(), key=pop_sort)
  return sorted_cities.pop()

def get_smallest_city(city_data, routes):
  """Return the city with lowest population."""
  pop_sort = lambda city: city['population']
  sorted_cities = sorted(city_data.values(), key=pop_sort, reverse=True)
  return sorted_cities.pop()

def get_average_pop(city_data, routes):
  """Return the average population."""
  total = sum([city['population'] for city in city_data.values()])
  avg = total / len(city_data)
  return avg

def get_continents(city_data, routes):
  """Return a dictionary where each continent is mapped to a list of cities"""
  continents = set([city['continent'] for city in city_data.values()])
  city_and_cont = {}

  for cont in continents:
  	filter_cont = lambda city: city['continent'] == cont
  	cities = filter(filter_cont, city_data.values())
  	city_and_cont[cont] = [(city['name'], city['code']) for city in cities]

  return city_and_cont

def get_hubs(city_data, routes):
  """Return a tuple containing a list of hubs and number of connections."""
  connections = {}
  for city in city_data.keys():
  	connections[city] = len(utils.find_adjacent(city, routes))

  maximum = max(connections.values())
  filter_max = lambda (city, connections): connections == maximum
  hub_routes = filter(filter_max, connections.items())

  hubs = []
  for hub in hub_routes:
  	code = hub[0]
  	hubs.append((city_data[code]['name'], code)) # (name, code)
  
  return hubs, maximum

def get_url(city_data, routes):
  """Construct a URL using all the stored routes."""
  code_strings = [ route[0] + '-' + route[1] for route in routes ]
  return 'http://www.gcmap.com/mapui?P=' + ',+'.join(code_strings)

def get_distance(code_pairs, city_data, routes):
  distance = 0
  for source, dest in code_pairs:
    distance += utils.find_route(routes, source, dest)[2]
  return distance

def get_time(code_pairs, city_data, routes):
  """Calculate the total time for a set of routes."""
  first_flight = code_pairs[0]
  time = utils.route_time(routes, first_flight[0], first_flight[1], layover=False)
  for pair in code_pairs[1:]:
  	time += utils.route_time(routes, pair[0], pair[1])

  return time

def check_path(code_pairs, city_data, routes):
  """Check whether a list of source-destination pairs is possible."""
  for pair in code_pairs:
    if utils.find_route(routes, pair[0], pair[1]) is None:
      raise ValueError('There is no route from %s to %s.' % pair)

def get_cost(code_pairs, city_data, routes):
  """Calculate the cost of a set of routes."""
  distances = \
    [ utils.find_route(routes, pair[0], pair[1])[2] for pair in code_pairs ]

  cost = 0.0
  rate = 0.35
  for leg in distances:
    cost += leg * rate
    rate -= 0.05
    rate = max(rate, 0.0)

  return cost

def shortest(source, destination, city_data, routes):
  """Given a source and destination, find the shortest path."""
  if source not in city_data.keys() or destination not in city_data.keys():
    raise KeyError('Both source and destination must be in the database.')

  path, distance = utils.dijkstra(source, destination, city_data, routes)
  cost = get_cost(path, city_data, routes)
  time = get_time(path, city_data, routes)

  codes = [ path[0][0] ]
  codes.extend([ route[1] for route in path ])
  route = ' -> '.join(codes)
  
  return route, distance, time, cost

if __name__ == '__main__':
  print 'To run the Pandemic Mapper, run "python mapper.py" instead.'
