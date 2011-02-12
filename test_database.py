import unittest2
import database
import read_methods as read
import write_methods as write

# test_list data
correct_list = [
	('New York', 'JFK'),
	('Lima', 'LIM'),
	('New York', 'LGA'),
	('London', 'LON'),
	('Chennai', 'MAA'),
	('Madrid', 'MAD'),
	('Bagdad', 'BGW'),
	('Kinshasa', 'FIH'),
	('Mexico City', 'MEX'),
	('Bogota', 'BOG')
]

# test_info data
jfk = {
	'code': 'JFK',
	'name': 'New York',
	'country': 'US',
	'continent': 'North America',
	'timezone': -5,
	'coordinates': {'N': 41, 'W': 74},
	'population': 22200000,
	'region': 3
}

lga = {
	'code': 'LGA',
	'name': 'New York',
	'country': 'US',
	'continent': 'North America',
	'timezone': -5,
	'coordinates': {'N': 41, 'W': 74},
	'population': 22200000,
	'region': 3
}

adj_jfk = [('London', 'LON'), ('Madrid', 'MAD')]
adj_lga = []

# test_longflight data
longflight_list = ['JFK', 'MAD']
longflight_distance = 5786

# test_shortflight data
shortflight_list = ['MAD', 'LON']
shortflight_distance = 1786

# test_avgdistance data
correct_avgdistance = 3736

# test_bigcity data
correct_bigcity = 'MEX'

# test_smallcity data
correct_smallcity = 'MAD'

# test_avgpop data
correct_avgpop = 12775000

# test_hubs data
correct_hubcount = 2
correct_hubs = [
	('Mexico City', 'MEX'),
	('New York', 'JFK'),
	('London', 'LON'),
	('Bogota', 'BOG'),
	('Madrid', 'MAD'),
	('Lima', 'LIM')
]

# test_continents data
correct_continents = {
	'South America': [('Lima', 'LIM'), ('Bogota', 'BOG')],
	'Asia': [('Bagdad', 'BGW'), ('Chennai', 'MAA')],
	'North America': [('Mexico City', 'MEX'), ('New York', 'JFK'),
										('New York', 'LGA')],
	'Europe': [('London', 'LON'), ('Madrid', 'MAD')],
	'Africa': [('Kinshasa', 'FIH')]
}

class TestMapDatabase(unittest2.TestCase):
	# read_methods tests.
	def setUp(self):
		self.database = database.MapDatabase('test_data.json')

	def test_list(self):
		self.assertItemsEqual(correct_list, self.database.do(read.get_cities))

	def test_info(self):
		cities, adjacent = self.database.do(read.get_cities_by_name, jfk['name'])
		
		self.assertItemsEqual([jfk, lga], cities)
		self.assertEqual(adj_jfk, adjacent[jfk['code']])
		self.assertEqual(adj_lga, adjacent[lga['code']])

	def test_longflight(self):
		city1, city2, distance = self.database.do(read.get_longest_route)
		self.assertItemsEqual(longflight_list, [city1, city2])
		self.assertEqual(longflight_distance, distance)

	def test_shortflight(self):
		city1, city2, distance = self.database.do(read.get_shortest_route)
		self.assertItemsEqual(shortflight_list, [city1, city2])
		self.assertEqual(shortflight_distance, distance)

	def test_avgdistance(self):
		avg = self.database.do(read.get_avg_distance)
		self.assertEqual(correct_avgdistance, avg)
	
	def test_bigcity(self):
		city = self.database.do(read.get_largest_city)['code']
		self.assertEqual(correct_bigcity, city)

	def test_smallcity(self):
		city = self.database.do(read.get_smallest_city)['code']
		self.assertEqual(correct_smallcity, city)

	def test_avgpop(self):
		avg = self.database.do(read.get_average_pop)
		self.assertEqual(correct_avgpop, avg)

	def test_hubs(self):
		hubs, maximum = self.database.do(read.get_hubs)
		self.assertItemsEqual(correct_hubs, hubs)
		self.assertEqual(correct_hubcount, maximum)

	def test_continents(self):
		self.assertItemsEqual(correct_continents,
			self.database.do(read.get_continents))
	
if __name__ == '__main__':
	# Run the test cases with a bit of fancy formatting.
	suite = unittest2.TestLoader().loadTestsFromTestCase(TestMapDatabase)
	unittest2.TextTestRunner(verbosity=2).run(suite)
