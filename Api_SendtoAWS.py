import requests
import json
from db_info import db_connect, db_info


def Send_to_AWS(table):
    # 테이블 데이터를 딕셔너리 형태로 정의
    # url : AWS 서버의 엔드포인트 url
    table_data = {
        "TempHm": {
            "url": "http://13.209.88.1:8080/insert/TempHm",
            "columns": {"vest": 1, "Temp": 2, "Hm": 3, "TempHmTime": 4},
        },
        "Flame": {
            "url": "http://13.209.88.1:8080/insert/Flame",
            "columns": {"vest": 1, "Fire": 2, "FireTime": 3},
        },
        "Gassensor": {
            "url": "http://13.209.88.1:8080/insert/Gas",
            "columns": {"vest": 1, "Gas": 2, "GasTime": 3},
        },
        "Led": {
            "url": "http://13.209.88.1:8080/insert/Led",
            "columns": {"vest": 1, "OnOff": 2, "LedTime": 3},
        },
        "LightSensor": {
            "url": "http://13.209.88.1:8080/insert/Light",
            "columns": {"vest": 1, "Light": 2, "LightTime": 3},
        },
        "Buzzer": {
            "url": "http://13.209.88.1:8080/insert/Buzzer",
            "columns": {"vest": 1, "Buz": 2, "BuzTime": 3, "BuzReason": 4},
        },
    }
    db = db_connect(db_info)
    cur = db.cursor()
    # 가장 최근에 입력된 데이터를 하나씩 전송
    cur.execute(f"select * from {table} order by id desc limit 1")
    db_data = cur.fetchone()
    
    if db_data:
        data = {"data": {}}
        # 테이블 값을 키로 지정한 후 각 테이블 이름에 맞는 컬럼 이름을 묶어서 데이터로 지정
        for col_name, col_idx in table_data[table]["columns"].items():
            data["data"][col_name] = str(db_data[col_idx])
        url = table_data[table]["url"]

        response = requests.post(url, json=data)  # 데이터를 JSON 형식으로 전환한 후 POST 방식으로 AWS에 전송
        print(response.text)  # 서버에서 전송받은 응답 반환
        print(data) # 전송한 데이터 출력
        print("해당 데이터를 AWS에 전송합니다...")
        cur.execute(f"delete from {table} order by id desc limit 1") # 마지막으로 전송한 데이터 DB에서 삭제
        db.commit()
        print("마지막으로 보낸 데이터가 성공적으로 삭제되었습니다.")
    else:
        print("No Datas Found!")
    cur.close()
