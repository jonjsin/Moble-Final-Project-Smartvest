import adafruit_dht
from datetime import datetime
import board
import RPi.GPIO as GPIO
import time
from Api_SendtoAWS import Send_to_AWS
from db_info import db_connect, db_info

# 센서들의 GPIO 핀 번호 지정
db = db_connect(db_info)
cur = db.cursor()
dhtDevice = adafruit_dht.DHT22(board.D4)
LIGHT = 13
Danger_LED = 3
Light_LED = 21
GAS = 17
FIRE = 26
BUZ = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT, GPIO.IN)
GPIO.setup(Danger_LED, GPIO.OUT)
GPIO.setup(Light_LED, GPIO.OUT)
GPIO.setup(GAS, GPIO.IN)
GPIO.setwarnings(False)
GPIO.setup(FIRE, GPIO.IN)
GPIO.setup(BUZ, GPIO.OUT)
p = GPIO.PWM(BUZ, 1)
scale = [261]


# DHT - 온습도 체크
def DHT_insert():
    now = datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
    # DHT 센서에서 온습도 측정
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    print("Temp: {:.1f} C    Humidity: {:.1f}% ".format(temperature_c, humidity))
    # TempHm 테이블에 온습도, 시간, 조끼번호 입력
    sql = f"insert into TempHm(Temp, Hm, TempHmTime, vest) values(%s,%s,%s,%s)"
    values = [(temperature_c, humidity, now, "1")]
    cur.executemany(sql, values)
    db.commit()
    # 입력 확인 후 AWS 서버에 데이터 전송하는 함수 실행
    print("온습도 정보가 DB에 입력되었습니다.")
    Send_to_AWS("TempHm")


# Light - 빛 감지
def Light_insert():
    now = datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
    if GPIO.input(LIGHT) == 1:  # 빛이 없을 때
        # 조명 LED 켜짐
        GPIO.output(Light_LED, True)
        print("Dark", now)
        # 테이블에 조도센서 값, 시간, 조끼번호 및 LED 점등유무, 시간, 조끼번호 입력
        cur.execute(
            f"insert into LightSensor(Light, LightTime,vest) values('Dark', now(),('1'))"
        )
        cur.execute(
            f"insert into Led(OnOff, LedTime,vest) values('LED ON', now(),('1'))"
        )
        db.commit()
        # AWS에 데이터 전송하는 함수 실행
        Send_to_AWS("LightSensor")
        Send_to_AWS("Led")
    else:  # 빛이 감지될 때
        # 조명 LED 꺼짐
        GPIO.output(Light_LED, False)
        print("Light", now)
        # 테이블에 조도센서 값, 시간, 조끼번호 및 LED 점등유무, 시간, 조끼번호 입력
        cur.execute(
            f"insert into LightSensor(Light, LightTime,vest) values('Light', now(),('1'))"
        )
        cur.execute(
            f"insert into Led(OnOff, LedTime,vest) values('LED OFF', now(),('1'))"
        )
        db.commit()
        # AWS에 데이터 전송하는 함수 실행
        Send_to_AWS("LightSensor")
        Send_to_AWS("Led")


# Flame - 화염 감지
def Flame_insert():
    now = datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
    # Flame, Buz, Danger_LED - 화염 감지, 버저 및 위험감지 LED
    p.start(50)
    if GPIO.input(FIRE) == 1:  # 평소 1을 전송함
        p.stop()
        print("안전", now)
        GPIO.output(Danger_LED, False)
    else:  # 불꽃 감지시 0을 전송함
        print("화재 발생", now)
        for i in range(0, 1):
            # 버저 작동
            p.ChangeFrequency(scale[i])
            time.sleep(0.5)
            # 위험감지 LED 켜짐
            GPIO.output(Danger_LED, True)
            # Flame 테이블에 불꽃 감지, 시간, 조끼번호 입력
            cur.execute(
                f"insert into Flame(Fire, FlameTime, vest) values('FIRE!', now(), ('1'))"
            )
            # Buzzer 테이블에 버저 켜짐 유무, 시간, 켜진 이유, 조끼번호 입력
            cur.execute(
                f"insert into Buzzer(Buz, BuzTime, BuzReason, vest) values('BUZ ON', now(), 'FIRE!', ('1'))"
            )
            # Led 테이블에 켜짐 유무, 시간, 조끼번호 입력
            cur.execute(
                f"insert into Led(OnOff, LedTime,vest) values('DANGER LED ON', now(),('1'))"
            )
            db.commit()
            # AWS 서버에 데이터 전송
            Send_to_AWS("Flame")
            Send_to_AWS("Buzzer")
            Send_to_AWS("Led")


# Gas - 가스 감지
def Gas_insert():
    now = datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
    p.start(50)
    if GPIO.input(GAS) == 1:  # 가스가 감지되지 않을 때
        p.stop()
        GPIO.output(Danger_LED, GPIO.LOW)  # LED OFF
        print("안전", now)
    else:  # 가스가 감지되었을 때
        GPIO.output(Danger_LED, GPIO.HIGH)  # 위험감지 LED 켜짐
        print("GAS!", now)
        for i in range(0, 1):
            # 버저 작동
            p.ChangeFrequency(scale[i])
            time.sleep(0.5)
            # Gassensor 테이블에 가스 감지 유무, 시간, 조끼번호 입력
            cur.execute(
                f"insert into Gassensor(Gas, GasTime, vest) values('GAS!', now(), ('1'))"
            )
            # Led 테이블에 켜짐 유무, 시간, 조끼번호 입력
            cur.execute(
                f"insert into Led(OnOff,LedTime, vest) values('DANGER LED ON', now(), ('1'))"
            )
            # Buzzer 테이블에 버저 켜짐 유무, 시간, 켜진 이유, 조끼번호 입력
            cur.execute(
                f"insert into Buzzer(Buz, BuzTime, BuzReason, vest) values('BUZ ON', now(), 'GAS!',('1'))"
            )
            db.commit()
            # AWS 서버에 데이터 전송
            Send_to_AWS("Gassensor")
            Send_to_AWS("Led")
            Send_to_AWS("Buzzer")
