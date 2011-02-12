import cmd
import sys
import database
import read_methods as read
import write_methods as write
import webbrowser

NEWLINE = ''

class Mapper(cmd.Cmd):
  """Handle all the input and output, interfacing with the database."""
  database = None
  prompt = '> '

  def preloop(self):
    """Print introductory text upon entering the program."""
    print NEWLINE
    print 'Pandemic Mapper'
    print '==============='
    print 'Welcome to the Pandemic Mapper. Type "help" to get a list of the'
    print 'available commands, or type "exit" to leave.'

  def emptyline(self):
    """Return immediately when the user inputs a newline.
    
    This exists to override the default behavior, which repeats the previously
    entered command.
    
    """
    # We don't want to do anything.
    return

  def default(self, line):
    """Print the default error message."""
    print 'Error: "%s" is not a valid command.' % line

  def do_exit(self, arg):
    """ Exits the program immediately. """
    sys.exit(0)

  # Database methods.
  def do_load(self, filename):
    """Load a .json database file.
    
    Keyword arguments:
    filename -- The relative or absolute path to the .json file.
    
    """
    try:
      self.database = database.MapDatabase(filename)
      print '%s loaded successfully.' % filename
    except IOError as error:
      print 'Error: %s' % error

  def do_list(self, args):
    """List every city and airport code in the database."""
    if self.database is None:
      _print_no_file()
    else:
      city_data = self.database.do(read.get_cities)
      for city, code in city_data:
        print '%s (%s)' % (city, code)
 
  def do_info(self, city):
    """Print information about a specific city.
   
    Specifically, print the airport code, name, country, continent, timezone,
    latitude and longitude, population, region, and a list of cities that are
    accessible.
 
    Keyword arguments:
    city -- The name of the city to find. This is case-sensitive, so use the
    "list" command to find exact names if necessary.
    
    """
    if self.database is None:
      _print_no_file()
    
    else:
      cities, adjacent = self.database.do(read.get_cities_by_name, city)
      if not cities:
        print 'Error: We don\'t serve any cities named "%s."' % city
        return

      for city in cities:
        for key, value in city.items():
          print '%s: %s' % (key, value)

        print NEWLINE
        print 'Accessible Cities:'
        if not adjacent[city['code']]:
          print ' None'
        else:
          for adj_city_info in adjacent[city['code']]:
            print ' %s (%s)' % adj_city_info
        print NEWLINE
  
  def do_continents(self, arg):
    """Print each continent and cities within that continent."""
    if self.database is None:
      _print_no_file()

    else:
      continent_and_cities = self.database.do(read.get_continents)
      for continent, cities in continent_and_cities.items():
        print 'Cities in %s:' % continent
        for name, code in cities:
          print '  %s (%s)' % (name, code)      
        print NEWLINE

  def do_map(self, arg):
    """Open the gcmap in a browser."""
    if self.database is None:
      _print_no_file()

    else:
      url = self.database.do(read.get_url)
      webbrowser.open(url)

  def do_stat(self, subcommand):
    """Query the database for statistics about the entire database.

    Keyword arguments:
    subcommand -- Contains a subcommand which, if left blank, prints a help
    message and exits.
    
    """
    if self.database is None:
      _print_no_file()
      return

    # If they just type 'stat', we print a help message.
    if not subcommand:
      print NEWLINE
      print '"stat longflight"  prints the longest flight.'
      print '"stat shortflight" prints the shortest flight.'
      print '"stat avgdistance" prints the average distance of our flights.'
      print '"stat bigcity"     prints the biggest city by population.'
      print '"stat smallcity"   prints the smallest city by population.'
      print '"stat avgpop"      prints the average population our cities.'
      print '"stat hubs"        prints the city or cities with the most direct'
      print '                   connections.'
      print NEWLINE

    # Process commands.
    else:
      self.process_subcommand(subcommand)

  def process_subcommand(self, subcommand):
    """Process a subcommand of type "stat subcommand.\""""
    # A dictionary mapping command strings to methods.
    subcommand_map = {
      'longflight': self.print_longflight,
      'shortflight': self.print_shortflight,
      'avgdistance': self.print_avgdistance,
      'bigcity': self.print_bigcity,
      'smallcity': self.print_smallcity,
      'avgpop': self.print_avgpop,
      'hubs': self.print_hubs
    }

    if subcommand not in subcommand_map:
      # Print error message that it's not a valid subcommand.
      self.default('stat ' + subcommand)
    else:
      # Execute the command from the map.
      subcommand_map[subcommand]()

  # Subcommand print methods.
  def print_longflight(self):
    """Print the longest route's cities and distance."""
    route = self.database.do(read.get_longest_route)
    print 'Between %s and %s, %d kilometers.' % route  

  def print_shortflight(self):
    """Print the shortest route's cities and distance."""
    route = self.database.do(read.get_shortest_route)
    print 'Between %s and %s, %d kilometers.' % route  

  def print_avgdistance(self):
    """Print the mean distance of all the routes in the database."""
    avg = self.database.do(read.get_avg_distance)
    print 'Average route distance: %d kilometers.' % avg

  def print_bigcity(self):
    """Print the city with the biggest population."""
    city = self.database.do(read.get_largest_city)
    print '%s (Population: %d)' % (city['name'], city['population'])

  def print_smallcity(self):
    """Print the city with lowest population."""
    city = self.database.do(read.get_smallest_city)
    print '%s (Population: %d)' % (city['name'], city['population'])
  
  def print_avgpop(self):
    """Print the average population."""
    avg = self.database.do(read.get_average_pop)
    print 'Average population: %d folks.' % avg

  def print_hubs(self):
    """Print the city or cities with the largest population."""
    hubs, maximum = self.database.do(read.get_hubs)

    for name, code in hubs:
      print '%s (%s)' % (name, code)
    print 'with %d connections.' % maximum

  # Edit methods.

  def do_save(self, filename):
    """Save the current database to a file."""
    if self.database is None:
      _print_no_file()
      return

    try:
      self.database.do(write.save, filename)
      print 'Saved current database as "%s"' % filename
    except IOError as error:
      print 'Error: %s' % error

  def do_uncity(self, name):
    """Delete all cities with a certain name.
    
    Keyword arguments:
    name -- The name of the city to delete.

    """
    if self.database is None:
      _print_no_file()
      return

    try:
      codes = self.database.do(write.del_city, name)
      print 'Deleted %s.' % ', '.join(codes)
    except KeyError as error:
      print 'Error: %s' % error

  def do_unroute(self, route):
    """Delete a route from the database.
    
    Keyword arguments:
    route -- The route entered as "<code1> <code2>". To delete a route between
             CHI and NYC, for example, you would type "unroute CHI NYC".
    
    """
    if self.database is None:
      _print_no_file()
      return
    
    cities = route.split()
    if len(cities) != 2:
      print 'Error: Could not read cities. Type "help unroute" for'
      print 'instructions.'
      return

    try:
      route = self.database.do(write.del_route, cities[0], cities[1])
      print 'Removed route %s <-> %s with distance %d.' % route

    except KeyError as error:
      print 'Error: %s' % error

  def do_newcity(self, arg):
    """Gather information for a city and add it to the database."""
    if self.database is None:
      _print_no_file()
      return

    try:
      print 'Adding new city:'
      city = _prompt('all')
      self.database.do(write.add_city, city)
      print 'Added city %s with code %s.' % (city['name'], city['code'])  

    except (TypeError, ValueError) as error:
      print 'Error: %s' % error

  def do_edit(self, raw_args):
    """Edit a city's details, including its airport code and city name.

    Keyword arguments:
    raw_args -- There are two methods of editing a city. First, "edit <code>"
                edits all of a city's information. Second, "edit <code> <key>"
                edits a specific element. For example, "edit NYC" prompts for
                all information about New York and "edit NYC coordinates"
                prompts for New York's coordinates.

    """
    if self.database is None:
      _print_no_file()
      return
    
    args = raw_args.split()
    if not args or len(args) > 2:
      print 'Error: Incorrect arguments. Type "help edit" for instructions.'
      return

    if len(args) == 1:
      code = args[0]
      print 'Enter new information for %s:' % code
      
      try:
        city = _prompt('all')
        self.database.do(write.edit_city, code, city)
      except (KeyError, TypeError, ValueError) as error:
        print 'Error: %s' % error

    elif len(args) == 2:
      code, key = args[0], args[1]
      print 'Change %s\'s %s value:' % (code, key)

      try:
        val = _prompt(key)
        self.database.do(write.edit_city, code, val, key=key)
      except (KeyError, TypeError, ValueError) as error:
        print 'Error: %s' % error


  def do_newroute(self, raw_route):
    """Gather information for a route and add it to the database.
    
    Keyword arguments:
    raw_ports -- Two airport codes followed by a distance, separated by a single
                 space. For example, "newroute CHI NYC 1145". If left blank, we
                 prompt for these values manually.
    
    """
    if self.database is None:
      _print_no_file()
      return

    route = raw_route.split()

    # If blank, we'll prompt for arguments.
    if not route:
      route = _prompt_ports()

    try:
      city_a, city_b, distance = _format_route(route)
      self.database.do(write.add_route, city_a, city_b, distance)
      print 'Successfully added route from %s <-> %s, %d kilometers.' % \
        (city_a, city_b, distance)
      
    except (TypeError, KeyError, ValueError) as error:
      print 'Error: %s' % error

  def do_route(self, cities):
    """Given a list of cities on a route, calculate the time and cost.
    
    Keyword arguments -- A set of airport codes corresponding to airports in the
                         route. For example, "route SCL LIM BOG" calculates the
                         time and cost to fly from Santiago -> Lima -> Bogota.
    
    """
    if self.database is None:
      _print_no_file()
      return

    codes = cities.split()
    if not codes:
      print 'Error: Please enter a list of city codes. Type "help route" for'
      print 'instructions.'
      return

    pairs = []
    for i in range(1, len(codes)):
      pairs.append((codes[i-1], codes[i]))

    try:
      self.database.do(read.check_path, pairs)
      time = self.database.do(read.get_time, pairs)
      cost = self.database.do(read.get_cost, pairs)
      distance = self.database.do(read.get_distance, pairs)

      print 'This route is %d kilometres, takes %.3f hours and costs $%.2f.' % \
       (distance, time, cost)
    except ValueError as error:
      print 'Error: %s' % error
 
  # Shortcuts:
  do_quit = do_exit
  do_ls = do_list
  do_cont = do_continents

  def do_shortest(self, cities):
    """Apply Dijkstra's algorithm to print a shortest path.

    Keyword arguments:
    cities -- A pair of city codes. The first code is the source and the second
              is the destination. For example, "shortest JKT MEX" prints the
              shortest path from Jakarta to Mexico, along with its distance,
              time, and cost.
    
    """
    if self.database is None:
      _print_no_file()
      return

    pair = cities.split()
    if len(pair) != 2:
      print 'Error: Please enter exactly two valid city codes.'
      return

    try:
      route, distance, time, cost = \
        self.database.do(read.shortest, pair[0], pair[1])
      print route
      print 'This route is %d kilometres, takes %.3f hours, costs $%.2f' % \
        (distance, time, cost)

    except KeyError as error:
      print 'Error: %s' % error

def _prompt(key):
  """Prompt for city data, validate their format, and return the value.

  For example, _prompt('code') prompts for a city code value and returns a
  string. If you call _prompt('all'), prompt for all the values and return a
  dictionary with the city's data. If any input is invalid, print an error and
  return.

  This method validates the data's format, but does not check if the city code
  is already in the database. That is done in read_methods.add_city.

  """
  prompt_commands = {
    'code': _prompt_code,
    'name': _prompt_name,
    'region': _prompt_region,
    'coordinates': _prompt_coordinates,
    'timezone': _prompt_timezone,
    'country': _prompt_country,
    'population': _prompt_population
  }

  if key == 'all':
    city = {}
    for key, method in prompt_commands.items():
      city[key] = method()
    return city
  
  elif key in prompt_commands.keys():
    return prompt_commands[key]()

  else:
    raise KeyError('"%s" is not a valid key.' % key)

def _prompt_code(): 
  """Prompt for the airport code, check it is three letters, and return it."""
  code = raw_input('  Enter code: ')
  if len(code) != 3:
    raise ValueError('Airport codes must be three characters.')
  return code

def _prompt_name():
  """Prompt for the city name and return a string."""
  return raw_input('  Name: ')

def _prompt_region():
  """Prompt for the region, check it is valid, and return an integer.

  Throw a TypeError if the input is not an integer.
  Throw a ValueError if the input is negative.

  """
  region = raw_input('  Enter region: ')
  
  try:
    region = int(region)
  except TypeError:
    raise TypeError('Region must be a non-negative integer.')

  if region < 0:
    raise ValueError('Region must be non-negative.')

  return region

def _prompt_coordinates():
  """Prompt for the coordinates, check they are valid, and return a dict.

  Throw a ValueError if they don't enter exactly two coordinates.
  Throw a TypeError if any coordinate is not an integer.
  
  """
  coordinates = {}
  print '  Enter coordinates (leave blank to ignore):'
  coordinates['N'] = raw_input('    N: ')
  coordinates['S'] = raw_input('    S: ')
  coordinates['E'] = raw_input('    E: ')
  coordinates['W'] = raw_input('    W: ')

  for key, value in coordinates.items():
    if not value.strip():
      del coordinates[key] # Remove blank coordinates.
  if len(coordinates.values()) != 2:
    raise ValueError('Enter exactly two coordinates and leave the rest blank.')
  
  try:
    for direction, val in coordinates.items():
      coordinates[direction] = int(val)
  except TypeError:
    raise TypeError('Both coordinates must be integers.')

  return coordinates

def _prompt_timezone():
  """Prompt for the timezone, check it is valid, and return an integer.
  
  Throw a TypeError if the input is not an integer.
  Throw a ValueError if the input is not between -12 and 14 inclusive.
  
  """
  timezone = raw_input('  Time zone (-12 to 14): ')
  
  try:
    timezone = int(timezone)
  except TypeError:
    raise TypeError('Time zone must be an integer from -12 to 14.')
  
  if timezone not in range(-12, 15):
    raise ValueError('Time zone must be between -12 and 14.')

  return timezone

def _prompt_continent():
  """Prompt for the continent name."""
  return raw_input('  Continent: ')

def _prompt_country():
  """Prompt for the country name."""
  return raw_input('  Country: ')

def _prompt_population():
  """Prompt for the population, check it is valid, and return an integer.

  Throw a TypeError if the input is not an integer.
  Throw a ValueError if the input is negative.
  
  """
  population = raw_input('  Population: ')
  
  try:
    population = int(population)
  except TypeError:
    raise TypeError('Population must be a non-negative integer.')

  if population < 0:
    raise ValueError('Population cannot be negative.')
  
  return population

def _prompt_ports():
  """Prompt for two airport codes and a distance and return the values."""
  city_a = raw_input('  Enter airport code: ')
  city_b = raw_input('  Enter another airport code: ')
  distance = raw_input('  Enter distance (non-negative integer): ')

  return city_a, city_b, distance

def _format_route(raw_route):
  """Given a tuple of three strings, type-check and format it as a route."""
  city_a, city_b, distance = raw_route
  
  if len(city_a) != 3 or len(city_b) != 3:
    raise ValueError('Airport codes must be three characters.')
    
  try:
    distance = int(distance)
  except TypeError:
    raise TypeError('Distance must be a valid integer.')
  if distance < 0:
    raise ValueError('Distance must be non-negative.')
  
  return city_a, city_b, distance

# Helpers
def _print_no_file():
  """Print an error message saying the file hasn't been loaded."""
  print 'Error: You need to initialize the database with "load" before you can'
  print 'use this command. Type "help load" for more information.'

# Main
if __name__ == '__main__':
  Mapper().cmdloop() # Start processing commands.
