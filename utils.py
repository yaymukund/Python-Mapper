from Queue import PriorityQueue

DISTANCE_TO_CRUISE = 200
CRUISE_SPEED = 750

def find_adjacent(code, routes):
  """Given an airport code, return a set of adjacent airports."""
  routes_with_city = routes_with(routes, code)

  ports = set()
  for route in routes_with_city:
    # Get the code of the other airport in the route.
    if route[0] == code:
      other_port = route[1]
    else:
      other_port = route[0]
    ports.add(other_port)

  return ports

def find_route(routes, code_a, code_b):
  """Find a specific route from a source to a destination."""
  if code_a == code_b:
    raise ValueError('Both endpoints cannot be the same.')

  for route in routes:
    if code_a in route and code_b in route:
      return route
  raise ValueError('A route from %s to %s was not found in the database' % \
    (code_a, code_b))

def routes_with(routes, code):
  """Using a lambda matcher, filter routes by one code."""
  matcher = lambda route: code in route
  return filter(matcher, routes)

def cities_named(name, city_data):
  """Using a lambda matcher, filter cities with a specific name."""
  matcher = lambda city: city['name'] == name
  return filter(matcher, city_data.values())

def change_code(old_code, new_code, city_data, routes):
  """Change an airport's code in city_data and routes."""
  # Update city_data
  data = city_data[old_code]
  data['code'] = new_code
  del city_data[old_code]
  city_data[new_code] = data

  # Update routes
  routes_with_code = routes_with(routes, old_code)
  
  routes.difference_update(routes_with_code) # Remove old routes.
  for route in routes_with_code:
    if route[0] == old_code:
      updated_route = (new_code, route[1], route[2])
    else:
      updated_route = (route[0], new_code, route[2])
    routes_with_code.remove(route)
    routes_with_code.append(updated_route)

  routes.update(routes_with_code)

def route_time(routes, source, destination, layover=True):
  """Calculate the time of a single route."""
  distance = find_route(routes, source, destination)[2]

  if distance < 2*DISTANCE_TO_CRUISE:
    time = (2.0*distance)/CRUISE_SPEED
  
  else:
    # The amount of time to accelerate and decelerate.
    time = (4.0*DISTANCE_TO_CRUISE)/CRUISE_SPEED
    # Time spent cruising.
    time += (distance-(2.0*DISTANCE_TO_CRUISE))/CRUISE_SPEED

  if layover:
    num_outbound = len(find_adjacent(source, routes))
    layover_time = max(2.0 - (num_outbound-1.0)/6.0, 0.0)
    time += layover_time
  
  return time

def dijkstra(source, destination, city_data, routes):
  """Run dijkstra's algorithm on a list of routes using a priority queue."""
  # Initialize structures.
  next = {}
  distances = {}

  for code in city_data.keys():
    distances[code] = float('inf')
  
  queue = PriorityQueue(len(city_data))
  queue.put((0, destination))
  
  while not queue.empty():
    source_dist, source_city = queue.get()
    adj_cities = find_adjacent(source_city, routes)
    adj_distances = \
      [ find_route(routes, source_city, dest)[2] for dest in adj_cities ]

    # Relaxing edges.
    for (adj_city, adj_distance) in zip(adj_cities, adj_distances):
      alt_distance = source_dist + adj_distance
      if alt_distance < distances[adj_city]:
        distances[adj_city] = alt_distance
        next[adj_city] = source_city
        queue.put((alt_distance, adj_city))

  # Construct the path.
  path = []
  curr = source
  while curr != destination:
    path.append((curr, next[curr]))
    curr = next[curr]

  return path, distances[source]

if __name__ == '__main__':
  print 'To run the Pandemic Mapper, run "python mapper.py" instead.'
