import requests
import json
import re
from datetime import datetime

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

# 급식 문자열 예쁘게 다듬는 함수 (그대로 유지)
def beautify_dish_name(dish_str):
    lines = re.split(r'<br\s*/?>', dish_str)
    pretty_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.search(r'\d', line)
        if match:
            line = line[:match.start()].strip()
        pretty_lines.append(line)
    return "\n".join(pretty_lines)

# API 호출 및 결과 JSON 저장하는 함수
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
            print("급식 저장 완료:", today)

        except Exception as e:
            print("급식 데이터 처리 실패:", e)
    else:
        print("급식 정보가 없습니다.", today)

if __name__ == "__main__":
    API_KEY = "1fb60bd35f834cd5bb50b33be4fe03d4"
    ATPT_OFCDC_SC_CODE = "J10"
    SD_SCHUL_CODE = "7530847"

    save_today_meal(API_KEY, ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE)
