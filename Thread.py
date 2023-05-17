import threading
import time
from GPIO_insert import DHT_insert, Light_insert, Flame_insert, Gas_insert
from Frontcam import front_cam


class SensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                # 분리한 py 파일에서 각 센서 값을 읽어 DB에 입력하는 함수 호출
                DHT_insert()
                Light_insert()
                Flame_insert()
                Gas_insert()
                time.sleep(10)
            # 에러 발생 시 코드
            except RuntimeError as error:
                print(error.args[0])
                time.sleep(5)
                continue
            except Exception as error:
                raise error


# Cam Thread 지정
cam_thread = threading.Thread(target=front_cam)
# Cam Thread 시작
cam_thread.start()
# 센서 Thread 지정 및 시작
sensor_thread = SensorThread()
sensor_thread.start()
