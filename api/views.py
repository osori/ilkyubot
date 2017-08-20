from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .places import Places
import logging

logger = logging.getLogger(__name__)

STATUS_IDLE = "STATUS_IDLE"
STATUS_RESTAURANT_SEARCH = "STATUS_RESTAURANT_SEARCH"
STATUS_CAFE_SEARCH = "STATUS_CAFE_SEARCH"

CURRENT_STATUS = dict()
INTENT = dict()
LAST_INPUT = dict()

INTENT_RESTAURANT_SEARCH = "INTENT_RESTAURANT_SEARCH"
INTENT_CAFE_SEARCH = "INTENT_CAFE_SEARCH"
INTENT_UNKNOWN = "INTENT_UNKNOWN"

SIGNAL_RESTAURANT_naive = ["맛집 찾기", "다른 지역 맛집 알아보기"]
SIGNAL_RESTAURANT_regex = []
SIGNAL_CAFE_naive = ["카페 찾기", "다른 지역 카페 알아보기"]

plc = Places()

# MAIN_BUTTONS = ["맛집 찾기", "초기화(개발자용)", "테스트(개발자용)"]
MAIN_BUTTONS = ["맛집 찾기", "카페 찾기", "English"]

DEFAULT_RESPONSE = {'message' : {
						'text': "장시간 사용하지 않아 처음화면으로 돌아갑니다. (굿)"
						},
						'keyboard' : {
							'type': "buttons",
							'buttons': MAIN_BUTTONS
						}
					}		

def index(request):
	return render(request, 'api/index.html')

# Create your views here.
def keyboard(request):
	response = {
		'type' : "buttons",
		'buttons' : MAIN_BUTTONS
	}
	return JsonResponse(response)


@csrf_exempt
def message(request):
	msg = ""
	btns = ""
	kbtype = "text"

	post_data = request.body

	if post_data:
		post_data = json.loads(post_data)

	choice = post_data.get('content')
	user_key = post_data.get('user_key')

	print("User", user_key, "sent input", choice, ".", "STATUS: ", CURRENT_STATUS.get(user_key) )

	if choice in SIGNAL_RESTAURANT_naive:
		INTENT[user_key] = INTENT_RESTAURANT_SEARCH

	elif choice in SIGNAL_CAFE_naive:
		INTENT[user_key] = INTENT_CAFE_SEARCH

	else:
		INTENT[user_key] = INTENT_UNKNOWN

	print("User", user_key, "INTENT: ", INTENT[user_key])

	if (CURRENT_STATUS.get(user_key) in [STATUS_IDLE, None]):
		if (INTENT.get(user_key) == INTENT_RESTAURANT_SEARCH):
			msg = "현재 위치를 알려주세요. (흡족) \n(입력 예: 공덕역, 경리단길, 광화문 교보)"
			kbtype = "text"
			CURRENT_STATUS[user_key] = STATUS_RESTAURANT_SEARCH
			response = {
				'message' : {
					'text':msg
				},
				'keyboard': {
					'type': kbtype
				}
			}

		elif (INTENT.get(user_key) == INTENT_CAFE_SEARCH):
			msg = "현재 위치를 알려주세요. (윙크) \n(입력 예: 이태원, 가로수길, 샌프란시스코)"
			kbtype = "text"
			CURRENT_STATUS[user_key] = STATUS_CAFE_SEARCH
			response = {
				'message' : {
					'text':msg
				},
				'keyboard': {
					'type': kbtype
				}
			}


		elif (choice == "초기화" or choice == "처음으로"):
			CURRENT_STATUS[user_key] = STATUS_IDLE
			msg = "초기화(꽃) 되었습니다. \n오류가 생길 시 이 채팅방을 나간 후 다시 들어와주세요. (꺄아)"
			kbtype="buttons"
			response = {
				'message' : {
					'text':msg
				},
				'keyboard': {
					'type': kbtype,
					'buttons': MAIN_BUTTONS
				}
			}

		else:
			response = DEFAULT_RESPONSE

	elif (CURRENT_STATUS.get(user_key) == STATUS_RESTAURANT_SEARCH):
		city = choice
		LAST_INPUT[user_key] = city
		lat_lng = plc.get_lat_lng(city)
		if(lat_lng == "NotFoundError"):
			msg = city + "?? 어딘지 잘 모르겠어요. (부르르) 죄송하지만... (제발) 다른 위치로 시도해보세요."
		else:
			restaurant_search_result = plc.restaurant_search(lat_lng, "prominence", "1000", "")
			msg = city + "(축하) 주변 맛집 TOP 7! (축하)\n"
			for index, (k, v) in enumerate(restaurant_search_result.items()):
				rating = repr(v.get('rating', "정보없음"))
				address = v.get('address', "정보없음")
				place_id = v.get('place_id')
				place_info = plc.get_place_info(place_id)
				msg += str(index+1) + ". " + (k+ " (평점: " + rating + ")")
				msg += "\n주소: " + address + "\n"
				msg += "\"" + place_info.get('review') +"\"\n" 
				msg += place_info.get('link')
				msg += "\n================\n"
				if(index==6):
					break
			msg += "다른 지역도 입력해보세요! (뿌듯)"
		kbtype= "buttons"
		btns = ["다른 지역 맛집 알아보기", "처음으로"]
		response = {
			'message' : {
				'text':msg
			},
			'keyboard': {
				'type': kbtype,
				'buttons': btns
			}
		}
		CURRENT_STATUS[user_key] = STATUS_IDLE

	elif (CURRENT_STATUS.get(user_key) == STATUS_CAFE_SEARCH):
		city = choice
		lat_lng = plc.get_lat_lng(city)
		if(lat_lng == "NotFoundError"):
			msg = city + "?? 어딘지 잘 모르겠어요. (부르르) 죄송하지만... (제발) 다른 위치로 시도해보세요."
		else:
			cafe_search_result = plc.cafe_search(lat_lng, "prominence", "1000", "")
			msg = city + "(커피) 주변 카페 TOP 7! (커피)\n"
			for index, (k, v) in enumerate(cafe_search_result.items()):
				rating = repr(v.get('rating', "정보없음"))
				address = v.get('address', "정보없음")
				place_id = v.get('place_id')
				place_info = plc.get_place_info(place_id)
				msg += str(index+1) + ". " + (k+ " (평점: " + rating + ")")
				msg += "\n주소: " + address + "\n" 
				msg += "\"" + place_info.get('review')+"\"\n" 
				msg += place_info.get('link')
				msg += "\n================\n"
				if(index==6):
					break
			msg += "다른 지역도 입력해보세요! (발그레)"
		kbtype= "buttons"
		btns = ["다른 지역 카페 알아보기", "처음으로"]
		response = {
			'message' : {
				'text':msg
			},
			'keyboard': {
				'type': kbtype,
				'buttons': btns
			}
		}
		CURRENT_STATUS[user_key] = STATUS_IDLE
		"""
	elif (CURRENT_STATUS.get(user_key) == None):


		"""

	return JsonResponse(response)

"""
def friend(request):
	if (request.method)
	post_data = request.body
	if post_data:
		post_data = json.loads(post_data)
	
	user_key = post_data['user_key']
"""

