import requests
import json
import re
from datetime import datetime

from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9 이상에서 사용 가능

kst = ZoneInfo("Asia/Seoul")

# API 호출 함수 (그대로 유지)
def fetch_meal_data(api_key, atpt_code, sch_code, mlmeal_code=None, mlsv_ymd=None, pindex=1, psize=100):
    base_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": api_key,
        "Type": "json",
        "pIndex": pindex,
        "pSize": psize,
        "ATPT_OFCDC_SC_CODE": atpt_code,
        "SD_SCHUL_CODE": sch_code
    }
    if mlmeal_code:
        params["MMEAL_SC_CODE"] = mlmeal_code
    if mlsv_ymd:
        params["MLSV_YMD"] = mlsv_ymd

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except:
            return None
    else:
        return None
    
def beautify_dish_name(dish_str):
    """
    DDISH_NM 문자열에서 HTML 태그 및 괄호 내부 제거,
    각 요리명 뒤의 숫자/기호 제거하여 예쁜 문자열로 반환
    """
    # <br/> 태그 기준으로 분할
    lines = re.split(r'<br\s*/?>', dish_str)
    pretty_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 괄호 및 괄호 안 내용 제거
        line = re.sub(r'\([^)]*\)', '', line).strip()

        # 숫자 등장 전까지만 남기기
        match = re.search(r'\d', line)
        if match:
            line = line[:match.start()].strip()
        
        pretty_lines.append(line)
    return "\n".join(pretty_lines)

"""
# ✅ 콘솔에 보기 좋게 급식을 출력하는 함수 추가
def print_meal_info(meal_data, date):
    meal_service = meal_data.get('mealServiceDietInfo')
    if meal_service:
        meal_info = meal_service[1].get('row')
        if meal_info:
            for meal in meal_info:
                print("----------------------------")
                print("날짜 :", date)
                print("- 오늘의 급식 -")
                dish_name = meal.get("DDISH_NM", "")
                pretty_dish = beautify_dish_name(dish_name)
                print(pretty_dish)
                print("----------------------------")
        else:
            print("급식 정보가 없습니다.")
    else:
        print("급식 서비스 데이터가 없습니다.")
"""

def print_meal_info(meal_data, date):
    """
    급식 정보를 보기 좋게 출력하는 함수
    """
    meal_service = meal_data.get('mealServiceDietInfo')
    if meal_service:
        meal_info = meal_service[1].get('row')
        if meal_info:
            for meal in meal_info:
                print("----------------------------")
                print("날짜 : ", date)
                #print("학교명:", meal.get("SCHUL_NM"))
                #print("식사명:", meal.get("MMEAL_SC_NM"))
                #print("급식일자:", meal.get("MLSV_YMD"))
                #print("급식인원수:", meal.get("MLSV_FGR"))
                # DDISH_NM 항목을 예쁘게 변환하여 출력
                dish_name = meal.get("DDISH_NM", "")
                pretty_dish = beautify_dish_name(dish_name)
                print("-오늘의 급식")
                print(pretty_dish)
                #print("원산지정보:", meal.get("ORPLC_INFO"))
                #print("칼로리정보:", meal.get("CAL_INFO"))
                #print("영양정보:", meal.get("NTR_INFO"))
                print("----------------------------")
        else:
            print("급식 정보가 없습니다.")
    else:
        print("급식 서비스 데이터가 없습니다.")


# API 호출 및 결과 JSON 저장하는 함수 (그대로 유지)
def save_today_meal(api_key, atpt_code, sch_code):
    today = datetime.now().strftime("%Y%m%d")  # 오늘 날짜 (자동계산)
    meal_data = fetch_meal_data(api_key, atpt_code, sch_code, mlsv_ymd=today)

    if meal_data and 'mealServiceDietInfo' in meal_data:
        try:
            meal_info = meal_data['mealServiceDietInfo'][1]['row'][0]
            dish_name = meal_info.get("DDISH_NM", "")
            pretty_dish = beautify_dish_name(dish_name)

            final_result = {
                "date": today,
                "menu": pretty_dish
            }

            with open("today_menu.json", "w", encoding="utf-8") as f:
                json.dump(final_result, f, ensure_ascii=False, indent=4)

            # ✅ 저장 후 콘솔에 예쁘게 출력
            print_meal_info(meal_data, today)

        except Exception as e:
            print("급식 데이터 처리 실패:", e)
    else:
        print("급식 정보가 없습니다.", today)

if __name__ == "__main__":
    API_KEY = "1fb60bd35f834cd5bb50b33be4fe03d4"
    ATPT_OFCDC_SC_CODE = "J10"
    SD_SCHUL_CODE = "7530847"

    save_today_meal(API_KEY, ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)


print("test")
