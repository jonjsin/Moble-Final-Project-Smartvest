import requests
import json
from db_info import db_connect, db_info


def Send_to_AWS(table):
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
    cur.execute(f"select * from {table} order by id desc limit 1")
    db_data = cur.fetchone()

    if db_data:
        data = {"data": {}}
        for col_name, col_idx in table_data[table]["columns"].items():
            data["data"][col_name] = str(db_data[col_idx])
        url = table_data[table]["url"]

        response = requests.post(url, json=data)  # 데이터를 POST 방식으로 전송
        print(response.text)  # 서버에서 전송받은 응답 반환
        print(data)
        print("해당 데이터를 AWS에 전송합니다...")
        cur.execute(f"delete from {table} order by id desc limit 1")
        db.commit()
        print("마지막으로 보낸 데이터가 성공적으로 삭제되었습니다.")
    else:
        print("No Datas Found!")
    cur.close()
