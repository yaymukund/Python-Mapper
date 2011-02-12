import simplejson

NEWLINE = ''

class MapDatabase:

  def __init__(self, filename):
    """Given a filename, build and store city data and route information.

    Keyword arguments:
    filename -- A string with the filename.
    
    """
    try:
      json = open(filename)
      parsed_data = simplejson.load(json)

    except (IOError, simplejson.decoder.JSONDecodeError):
      raise IOError('Couldn\'t open file "%s".' % filename)

    #: Cities are in a dictionary with key == airport code.
    self._city_data = self._parse_city_data(parsed_data)
    #: Routes are kept in an unordered set.
    self._routes = self._parse_routes(parsed_data)
    #: Sources are stored as a list.
    self._sources = parsed_data['data sources']

  def _parse_city_data(self, data):
    """Given the parsed json, build a dict of cities where the keys are airport
    codes and values are a dict containing the continent, coordinates, country,
    name, population, region, and timezone.

    Keyword arguments:
    data -- A json dict containing all the data.
    
    """
    raw_data_list = data['metros']
    data_dict = {}

    for raw_data in raw_data_list:
      city_code = raw_data['code']
      data_dict[city_code] = raw_data
    
    return data_dict

  def _parse_routes(self, data):
    """Given the parsed json, build a set of routes. 
    
    Keyword arguments:
    data -- A json dict containing all the data.
    
    """
    raw_route_list = data['routes']
    route_set = set()

    for raw_route in raw_route_list:
      raw_ports = raw_route.pop('ports')
      
      # Each route is a tuple with the cities and a distance.
      route = str(raw_ports[0]), str(raw_ports[1]), raw_route['distance']
      route_set.add(route) # Add to final set.

    return route_set

  def do(self, function, *arguments, **keyword_arguments):
    data_args = [ self._city_data, self._routes ]
    if function.__name__ == 'save':
      data_args.append(self._sources)

    if not arguments:
      full_args = data_args
    else:
      full_args = list(arguments)
      full_args.extend(data_args)

    return function(*full_args, **keyword_arguments)
    
if __name__ == '__main__':
  print 'To run the Pandemic Mapper, run "python mapper.py" instead.'
