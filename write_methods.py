import utils
import simplejson

# Edit Methods:
#   The following methods primarily write to and delete from the database.

def save(filename, city_data, routes, sources):
  """Write the database to a json file."""
  metros = city_data.values()
  
  def format_routes(route):
    return {
      'distance': route[2],
      'ports': [ route[0], route[1] ]
    }
  
  formatted_routes = map(format_routes, routes)
  
  data = {
    'data sources': sources,
    'metros': metros,
    'routes': formatted_routes
  }
  
  try:
    json_file = open(filename, 'w')
    simplejson.dump(data, json_file, indent='\t')
  except IOError:
    raise IOError('Error: Couldn\'t write to "%s".' % filename)

def del_city(city_name, city_data, routes):
  """Delete all airports in a city and return their airport codes."""
  ports_with_name = lambda city: city['name'] == city_name
  cities_with_name = filter(ports_with_name, city_data.values())
  
  if not cities_with_name:
    raise KeyError('No city named %s.' % city_name)

  codes = [city['code'] for city in cities_with_name]

  for code in codes:
    del city_data[code]
    # Remove routes involving the city.
    routes.difference_update(utils.routes_with(routes, code)) 
  
  return codes

def del_route(port_a, port_b, city_data, routes):
  """Given two airport codes, remove the route connecting the airports.

  Keyword arguments:
  port_a and port_b -- The pair of cities in the route.

  Throw KeyError if the ports are the same or if the route isn't in the
  database.

  """
  if port_a == port_b:
    raise KeyError('Entered the same city twice.')

  for route in routes:
    if port_a in route and port_b in route:
      routes.remove(route)
      return route

  raise KeyError('Could not find route between %s and %s.' % (port_a, port_b))

def add_city(new_city, city_data, routes):
  """Add a new city to the database.

  Keyword arguments:
  new_city -- A dictionary containing the city's relevant information
  
  Throw a ValueError if a city already exists with the same code.

  """
  code = new_city['code']

  if code in city_data:
    raise ValueError('%s is already mapped to %s in database.' %
      (code, city_data[code]['name']))

  city_data[code] = new_city

def edit_city(code, data, city_data, routes, key=None):
  """Edit an airport's data element or data dictionary.

  For example, database.edit_city('CHI', 'Chicago Land', 'name') changes the
  name of CHI to 'Chicago Land'.
  
  database.edit_city('CHI', city_dict) replaces all of Chicago's information
  with updated information in city_dict.

  Keyword arguments:
  code -- The code of the airport to edit.
  key -- A string specifying which element to edit. If left blank, replace
         the entire city.
  data -- The updated data. If field is blank, this contains an updated data
          dictionary for the city.
  
  Throw a KeyError if the code isn't in database.

  """
  if code not in city_data.keys():
    raise KeyError('"%s" is not an airport code in our database.' % code)

  if key is None:
    utils.change_code(code, data['code'], city_data, routes)
    city_data[data['code']] = data
  
  else:
    city_data[code][key] = data
    if key == 'code':
      utils.change_code(code, data, city_data, routes)

def add_route(port_a, port_b, distance, city_data, routes):
  """Add a new route to the database.

  Keyword arguments:
  port_a, port_b, distance -- The cities and distance of the new route.

  Throw a KeyError if one of the given cities isn't in the database.
  
  """
  if port_a not in city_data.keys() or \
    port_b not in city_data.keys():
    raise KeyError('One of the entered cities isn\'t in the database.')

  routes.add((port_a, port_b, distance))
  
if __name__ == '__main__':
  print 'To run the Pandemic Mapper, run "python mapper.py" instead.'
