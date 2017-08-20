import json, requests
import random
from collections import OrderedDict

class Places(object):
	global GOOGLE_API_KEY, NEARBY_PLACES_URL, GEOCODE_URL, PLACE_DETAILS_URL, SEARCH_RADIUS, LANGUAGE
	
	GOOGLE_API_KEY = 'AIzaSyCJQ2LfhnG44np1BSxJnWZoOaLLWaOyrIA'
	NEARBY_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
	GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
	PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
	SEARCH_RADIUS = 1000
	LANGUAGE = "ko"

	def get_lat_lng(self, city):
		params = {
			'key' : GOOGLE_API_KEY,
			'address': city,
			'language': LANGUAGE,
			'region': "kr"
		}
		response = requests.get(GEOCODE_URL, params=params)
		json = response.json()
		#city_name = json['predictions'][0]['structured_formatting']['main_text']
		if (len(json['results']) == 0):
			return "NotFoundError"
		else:
			lat_lng = json['results'][0]['geometry']['location']
			ret= repr(lat_lng['lat']) + "," + repr(lat_lng['lng'])

		return (ret)

	def restaurant_search(self, location=None, 
			rankby=None, radius=None, keyword=None,):
		if (location is None or rankby is None or radius is None or keyword is None):
			raise ArgumentError("필수 파라미터가 입력되지 않았습니다.")

		params = {
			'key': GOOGLE_API_KEY,
			'location': location,
			'radius': radius,
			'keyword': keyword,
			'language': LANGUAGE,
			'type': ['restaurant', 'food']
		}

		response = requests.get(NEARBY_PLACES_URL, params=params)
		json = response.json()

		#print(json['results'][0])
		candidates = dict()

		for restaurant in json['results']:
			curr_restaurant = restaurant
			candidates[restaurant["name"]] = {
				"place_id": curr_restaurant.get('place_id'),
				"rating": curr_restaurant.get('rating', 0),
				"address": curr_restaurant.get('vicinity')
			}

		candidates_by_ratings = OrderedDict(sorted(candidates.items(), key=lambda x: x[1]['rating'], reverse=True))

		return candidates_by_ratings

	def cafe_search(self, location=None, 
			rankby=None, radius=None, keyword=None,):
		if (location is None or rankby is None or radius is None or keyword is None):
			raise ArgumentError("필수 파라미터가 입력되지 않았습니다.")

		params = {
			'key': GOOGLE_API_KEY,
			'location': location,
			'radius': radius,
			'keyword': keyword,
			'language': LANGUAGE,
			'type': 'cafe'
		}

		try:
			response = requests.get(NEARBY_PLACES_URL, params=params)
			json = response.json()
		except Exception as e: print(e)

		#print(json['results'][0])
		candidates = dict()

		for cafe in json['results']:
			curr_cafe = cafe
			candidates[cafe["name"]] = {
				"place_id": curr_cafe.get('place_id'),
				"rating": curr_cafe.get('rating', 0),
				"address": curr_cafe.get('vicinity')
			}

		candidates_by_ratings = OrderedDict(sorted(candidates.items(), key=lambda x: x[1]['rating'], reverse=True))

		return candidates_by_ratings

	def get_place_info(self, placeid=None):
		if (placeid is None and reference is None):
			raise ArgumentError("필수 파라미터가 입력되지 않았습니다.")

		params = {
			'key': GOOGLE_API_KEY,
			'placeid': placeid,
		}

		response = requests.get(PLACE_DETAILS_URL, params=params)
		json = response.json()

		place_info = dict()
		place_result = json['result']

		place_info['link'] = place_result['url']

		review_list = place_result['reviews']

		try:
			#review_list = [review for review in review_list if review['text'] != '']
			review_list = [review for review in review_list if (review.get('text') != '')]

			if (review_list):
				random_review = random.choice(review_list)
				place_info['review'] = random_review['text']
			else:
				place_info['review'] = "아직 후기 없음 (눈물)"

		except Exception as e: print(e)

		return place_info


		#sorted(candidates.items(), key=lambda item: item[])

"""
place_dict = dict()
p = Places()
loc = p.get_lat_lng("공덕")
result = p.restaurant_search(loc, "prominence", "1000", "")

for index, (k,v) in enumerate(result.items()):
	print(k,v)
	place_dict[k] = v
	if (index == 5):
		break

for place in place_dict.items():
	print(place)
	pid = p.get_place_info(place[1].get('place_id'))
"""
