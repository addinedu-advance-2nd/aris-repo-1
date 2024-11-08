# 터미널 설치 파일들
#pip3 install pyqt5  
#sudo apt install python3-pyqt5  
#sudo apt install pyqt5-dev-tools
#sudo apt install qttools5-dev-tools


import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt, QStringListModel, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
import socket
import time
import json
import threading
import queue


# 파일경로
base_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(base_dir, "image")

# 이미지 파일 경로
pixmap_path = os.path.join(image_dir, "str.png")
pixmap1_path = os.path.join(image_dir, "ban.png")
pixmap2_path = os.path.join(image_dir, "choco.png") 
pixmap3_path = os.path.join(image_dir, "topping1.png")
pixmap4_path = os.path.join(image_dir, "topping2.png")
pixmap5_path = os.path.join(image_dir, "topping3.png")
pixmap6_path = os.path.join(image_dir, "no.png")
position_path = os.path.join(image_dir,"position.png")
minus_path = os.path.join(image_dir,"minus_icon.png")
plus_path = os.path.join(image_dir,"plus-icon.png")
cancel_path = os.path.join(image_dir,"cancel_icon.png")
# UI 경로
main_file_path = os.path.join(base_dir, "untitled.ui")
topping_file_path = os.path.join(base_dir, "sub.ui")
memberinfo_file_path = os.path.join(base_dir, "memberinfo.ui")
position_file_path = os.path.join(base_dir,'position.ui')
main_page_class = uic.loadUiType(main_file_path)[0]
topping_page_class = uic.loadUiType(topping_file_path)[0]
memberinfo_page_class = uic.loadUiType(memberinfo_file_path)[0]
position_page_class = uic.loadUiType(position_file_path)[0]


# sub.ui(토핑 선택창) 설정 
class NewWindow(QDialog, topping_page_class):
    def __init__(self, menu_name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("토핑 선택")
        # 메인 창으로부터 받아오는 값들
        self.image_label = self.findChild(QLabel, 'pixMap_clicked')
        self.text_label = self.findChild(QLabel, 'menu_name_label_clicked')
        self.menu_price_label = self.findChild(QLabel, 'menu_price_label')

        self.menu_price_label.setText("2000 원")
        self.text_label.setText(menu_name)
        self.frame.lower()  # 프레임뒤로보내는 UI 코드
        # 토핑 이미지 출력
        self.Topping_1.setPixmap(QPixmap(pixmap3_path))
        self.Topping_2.setPixmap(QPixmap(pixmap4_path))
        self.Topping_3.setPixmap(QPixmap(pixmap5_path))
        self.noOption.setPixmap(QPixmap(pixmap6_path))
        # 토핑 설명 text
        self.topping_name_label_0.setText("없음")
        self.topping_name_label_1.setText("로투스")
        self.topping_name_label_2.setText("레인보우")
        self.topping_name_label_3.setText("오레오")
        # 토핑 이미지 label 크게에 맞게 조정
        self.Topping_1.setScaledContents(True)
        self.Topping_2.setScaledContents(True)
        self.Topping_3.setScaledContents(True)
        self.noOption.setScaledContents(True)
        # 이미지에 대면 HandCursor로 변형
        self.Topping_1.setCursor(Qt.PointingHandCursor)
        self.Topping_2.setCursor(Qt.PointingHandCursor)
        self.Topping_3.setCursor(Qt.PointingHandCursor)
        self.noOption.setCursor(Qt.PointingHandCursor)

        self.selected_toppings = []  # 선택된 토핑 저장
        self.Topping_1.mousePressEvent = lambda event: self.toggle_option(self.Topping_1, "로투스")
        self.Topping_2.mousePressEvent = lambda event: self.toggle_option(self.Topping_2, "레인보우")
        self.Topping_3.mousePressEvent = lambda event: self.toggle_option(self.Topping_3, "오레오")
        self.noOption.mousePressEvent = lambda event: self.select_no_option()

        # 토핑창에서의 취소, 담기 버튼
        self.cancel_btn.clicked.connect(self.close)
        self.order_btn.clicked.connect(self.add_to_order)

        # "없음"이 클릭되면 모든 토핑의 선택을 해제하고 "없음"만 빨간 테두리
    def select_no_option(self):
        self.clear_all_borders()
        self.noOption.setStyleSheet("border: 5px solid red;")
        self.selected_option = self.noOption
        self.selected_toppings = ["없음"]
        # "없음" 선택이 있을 경우 제거
    def toggle_option(self, selected_label, topping_name):
        if "없음" in self.selected_toppings:
            self.selected_toppings.remove("없음")
            self.noOption.setStyleSheet("border: none;")

        # 선택된 토핑이 이미 선택된 상태라면 테두리를 해제하고 리스트에서 제거
        if topping_name in self.selected_toppings:
            selected_label.setStyleSheet("border: none;")
            self.selected_toppings.remove(topping_name)
        else:
            # 선택된 토핑에 빨간 테두리 표시하고 리스트에 추가
            selected_label.setStyleSheet("border: 5px solid red;")
            self.selected_toppings.append(topping_name)

    # 모든 토핑의 스타일 초기화
    def clear_all_borders(self):
        for topping in [self.Topping_1, self.Topping_2, self.Topping_3]:
            topping.setStyleSheet("border: none;")

    def add_to_order(self):
        order_string = self.text_label.text()
        # 없음을 빼는 코드
        selected_toppings = [topping for topping in self.selected_toppings if topping != "없음"]
        
        # 선택된 토핑을 문자열로 변환하여 추가
        if selected_toppings:
            order_string += " + " + " + ".join(selected_toppings)

        if self.parent():
            self.parent().update_order_list(order_string)

        self.close()

    def set_image(self, pixmap):
        self.image_label.setPixmap(pixmap)  
        self.image_label.setScaledContents(True)

class PositionLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.circle_x = 50  # 원의 x 좌표
        self.circle_x_1 = 310  # 원의 x 좌표
        self.circle_x_2 = 570  # 원의 x 좌표

        self.circle_y = 50  # 원의 y 좌표
        self.circle_radius = 50  # 원의 반지름

    def paintEvent(self, event):
        super().paintEvent(event)  # QLabel 기본 이미지 그리기

        # QPainter를 사용해 원 그리기
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor(255, 0, 0))  # 빨간색 테두리
        pen.setWidth(5)  # 테두리 두께 설정
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  # 내부를 채우지 않음
        
        # 원 그리기
        painter.drawEllipse(self.circle_x, self.circle_y, self.circle_radius * 2, self.circle_radius * 2)
        painter.drawEllipse(self.circle_x_1, self.circle_y, self.circle_radius * 2, self.circle_radius * 2)
        painter.drawEllipse(self.circle_x_2, self.circle_y, self.circle_radius * 2, self.circle_radius * 2)

class PositionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("아이스크림 놓는 위치")
        
        # PositionLabel을 사용해 position을 설정
        self.position = PositionLabel(self)
        self.position.setGeometry(0, 0, 800, 700)  # 이미지의 위치와 크기 설정
        self.position.setPixmap(QPixmap(position_path))
        self.position.setScaledContents(True)

        # 원 좌표 설정
        self.position.circle_x = 60  # 예제 좌표
        self.position.circle_y = 450
        self.position.circle_radius =80

        # 원이 라벨 위에 보이도록 position 라벨 다시 그리기
        self.position.update()

# 회원정보 
class MemberInfoDialog(QDialog,memberinfo_page_class):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("회원 정보")
        self.mb_cancel_btn.clicked.connect(self.close)
        self.mb_regist_btn.clicked.connect(self.register_member)
    # 회원등록 textedit에 작성한 이름 , 번호를 각각의 name , phone 에 저장
    def register_member(self):
        name = self.name_textEdit.toPlainText()
        phone = self.phone_textEdit.toPlainText()
        # 메인 윈도우에 전송
        if name and phone:
            if self.parent():
               self.parent().update_member_info(name,phone)
            self.close()
        else:
            # 입력이 비어있는 경우 처리
            QMessageBox.warning(self, "입력 오류", "이름과 전화번호를 모두 입력해주세요.")

class OrderListDialog(QDialog): # 임시 리스트 출력
    def __init__(self, order_list, name, phone, parent=None):
        super().__init__(parent)
        self.setWindowTitle("주문 내역")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()
       # 이름 , 번호 써질 라벨 임시 생성
        self.name_label = QLabel(f"{name}")
        self.phone_label = QLabel(f"{phone}")

        
        # 주문 목록 추가
        self.order_list_widget = QListWidget()
        self.order_list_widget.addItems(order_list)
        layout.addWidget(self.name_label)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.order_list_widget)

        self.setLayout(layout)

# 메인 윈도우 클래스
class WindowClass(QMainWindow, main_page_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Aris 아이스크림 판매 키오스크")

        self.pixMap.setPixmap(QPixmap(pixmap_path))
        self.pixMap_2.setPixmap(QPixmap(pixmap1_path))
        self.pixMap_3.setPixmap(QPixmap(pixmap2_path))

        self.pixMap.setScaledContents(True)
        self.pixMap_2.setScaledContents(True)
        self.pixMap_3.setScaledContents(True)

        self.pixMap.setCursor(Qt.PointingHandCursor)
        self.pixMap_2.setCursor(Qt.PointingHandCursor)
        self.pixMap_3.setCursor(Qt.PointingHandCursor)

        self.pixMap.mousePressEvent = lambda event: self.open_new_window(pixmap_path, "딸기맛")
        self.pixMap_2.mousePressEvent = lambda event: self.open_new_window(pixmap1_path, "바나나맛")
        self.pixMap_3.mousePressEvent = lambda event: self.open_new_window(pixmap2_path, "초코맛")

        self.menu_name_label_1.setText("딸기맛")
        self.menu_name_label_2.setText("바나나맛")
        self.menu_name_label_3.setText("초코맛")
        self.menu_price_label_1.setText("2000 원")
        self.menu_price_label_2.setText("2000 원")
        self.menu_price_label_3.setText("2000 원")
        # 리스트 받아옴
        
        self.order_model = QStringListModel()
        self.order_list_widget.setModel(self.order_model)
        self.order_model.setStringList([])  # 초기 빈 리스트 설정
        # 삭제 버튼
        self.delete_btn_1.clicked.connect(lambda: self.delete_item_at_index(0))
        self.delete_btn_2.clicked.connect(lambda: self.delete_item_at_index(1))
        self.delete_btn_3.clicked.connect(lambda: self.delete_item_at_index(2))
        self.delete_btn_4.clicked.connect(lambda: self.delete_item_at_index(3))



        self.receipt.clicked.connect(self.show_receipt) # 임시 영수증 출력
        self.member_btn.clicked.connect(self.open_member_window)
        # 임시 버튼
        self.Warning_btn.clicked.connect(self.Warning_event)
        self.Position_btn.clicked.connect(self.open_position_window)

        self.user_name = ""
        self.user_phone = ""
    # 제조 과정 중 사람 접근 확인 시 안내 문구 - 임시로 버튼 활용
    def open_position_window(self):
        position_dialog = PositionDialog(self)
        position_dialog.exec_()

    def Warning_event(self):
        QMessageBox.warning(self,'경고','               뒤로 물러나 주세요                  ')

    def delete_item_at_index(self, index):
        # 현재 주문 리스트 가져오기
        current_orders = self.order_model.stringList()

        # index가 리스트 범위 내인지 확인 후 삭제
        if 0 <= index < len(current_orders):
            del current_orders[index]  # 해당 인덱스의 항목 삭제
            self.order_model.setStringList(current_orders)  
    def update_member_info(self, name, phone):
        # 받은 이름과 전화번호로 레이블을 업데이트
        self.user_name = name
        self.user_phone = phone

    def open_member_window(self):
        member_dialog = MemberInfoDialog(self)
        member_dialog.exec_()    

    def open_new_window(self, image_path, menu_name):
        self.new_window = NewWindow(menu_name, self)
        self.new_window.set_image(QPixmap(image_path))
        self.new_window.exec_()
    

    def update_order_list(self, order_string):
        current_orders = self.order_model.stringList()
        current_orders.append(order_string)
        self.order_model.setStringList(current_orders)

    def show_receipt(self): #임시 영수증 출력
        current_orders = self.order_model.stringList()
        order.order_receipt = self.order_model.stringList()
        order.icecream_order()
        receipt_dialog = OrderListDialog(current_orders, self.user_name, self.user_phone, self)
        receipt_dialog.exec_()
        self.order_model.setStringList([])


class OrderClass():
    def __init__(self):
        super().__init__()
        self.order_press = False
        self.avaliable_jig_A = True
        self.avaliable_jig_B = True
        self.avaliable_jig_C = True
        self.order_receipt = ""
        self.order_queue = queue.Queue()
        

    def order_receipt_process(self):
        # 우선 주문이 하나만 들어온다고 가정하고 코드 작성
        topping_orders = self.order_receipt[0].split(' + ')
        
        # topping 정보
        kor_topping_list = ["로투스", "레인보우", "오레오"]
        topping_signal = ""
        if len(topping_orders)>1:
            for i in range(len(kor_topping_list)):
                if kor_topping_list[i] in topping_orders[1:]:
                    topping_signal += "1"
                else:
                    topping_signal += "0"
        if topping_signal == "000":
            topping_no = True
        else:
            topping_no = False
        topping = topping_signal

        # jig 선택부
        # jig의 가용 상태를 저장해두고 비어있는 jig를 A B C 순으로 사용
        if self.avaliable_jig_A:
            jig = "A"
            self.avaliable_jig_A = False
        elif self.avaliable_jig_B:
            jig = "B"
            self.avaliable_jig_B = False
        elif self.avaliable_jig_C:
            jig = "C"
            self.avaliable_jig_C = False
        else:
            # 사용 가능한 jig가 없는 경우
            print("there is no avaliable jig!")

        

        # 관리자쪽의 설정 부분
        topping_first = False # 아이스크림보다 토핑을 먼저 받을지 말지. True : 먼저 받음
        topping_time = 3.0 # 총 토핑 받는 시간 == 토핑 량
        spoon_angle = 180.0 # 스푼의 위치 (Angle 기준) 기계 기준 오른쪽 180.0 / 중앙 270.0 / 왼쪽 355.0 
        
        # 메시지 생성부
        data_icecream = {
            "jig" : jig,
            "topping_first" : topping_first,
            "topping_no" : topping_no,
            "topping" : topping,
            "topping_time" : topping_time,
            "spoon_angle" : spoon_angle,
        }

        return data_icecream
        

    # robot arm에 아이스크림 추출 명령 전달 함수
    def icecream_order(self):

        data_icecream = self.order_receipt_process()
        msg_type = "icecream"

        json_data = json.dumps(data_icecream)
        data = msg_type + '/' + json_data

        self.robot_client_socket.sendall(data.encode())


    # robot arm과의 socket 연결부
    def connect_robot(self):
        self.robot_ADDR = '192.168.0.17'
        self.robot_PORT = 65432
        
        self.robot_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 추후 시간이 된다면 관리자 페이지를 만들어서 로봇과 통신 연결 / 로봇 테스트 / 설정 변경 등 구현
        self.robot_client_socket.connect((self.robot_ADDR, self.robot_PORT))
        self.connected = True
        # 연결을 계속 유지함
        # 데이터를 수신받아서 정보를 저장함. ex) 지그 사용 완료 및 서비스 완료.

        while self.connected:
            time.sleep(1)
            print("로봇으로부터 메시지 수신 대기중")
            try:
                # 대기 시간 설정
                self.robot_client_socket.settimeout(10.0)
                # 메시지 수령
                self.recv_msg = self.robot_client_socket.recv(1024).decode('utf-8')

                # 메시지가 비어 있는 경우. 연결이 끊겼으므로 재연결을 위해 예외 처리
                if self.recv_msg == '':
                    print("received empty msg")
                    raise Exception("empty msg")
                
                self.recv_msg = self.recv_msg.split('/')
                print(self.recv_msg)
                if self.recv_msg[0] == 'icecream_service_finish':
                    print("Jig " + self.recv_msg[1] + " icecream service end")
                    print("Set jig " + self.recv_msg[1] + " avaliable")
                    if self.recv_msg[1] == 'A':
                        self.avaliable_jig_A = True
                    elif self.recv_msg[1] == 'B':
                        self.avaliable_jig_B = True
                    elif self.recv_msg[1] == 'C':
                        self.avaliable_jig_C = True
                
            
            except socket.timeout:
                print('MainException: {}'.format(socket.timeout))
            except Exception as e:
                print('MainException: {}'.format(e))
                self.connected = False
                print('connection lost')
                # 재연결 시도
                while True:
                    time.sleep(2)
                    try:
                        # 소켓 정리
                        self.robot_client_socket.shutdown(socket.SHUT_RDWR)
                        self.robot_client_socket.close()
                        
                        # 소켓 설정
                        self.robot_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                        try:
                            self.robot_client_socket.connect((self.robot_ADDR, self.robot_PORT))
                            self.connected = True
                        except socket.error as e:
                            print("서버에 연결할 수 없습니다. 2초 후 재시도합니다.")
                        
                    except Exception as e:
                        print('MainException: {}'.format(e))
                        print('except')
                        # pass
                

class DB_Access():
    def __init__(self):
        super().__init__()


        def socket_DB(self):
            self.ADDR = '192.168.0.28'          # DB 주소로 변경
            self.PORT = 65432                   # DB의 Port로 변경
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 추후 시간이 된다면 관리자 페이지를 만들어서 로봇과 통신 연결 / 로봇 테스트 / 설정 변경 등 구현
            while True:
                try:
                    self.client_socket.connect((self.ADDR, self.PORT))
                    self.connected = True
                    break
                except socket.error as e:
                    print(f"서버에 연결할 수 없습니다: {e}")
                    print("2초 후 연결을 재시도 합니다")
                    time.sleep(2.0)

            while self.connected:
                time.sleep(1)
                print("DB로부터 메시지 수신 대기중")
                try:
                    # 대기 시간 설정
                    self.client_socket.settimeout(10.0)
                    # 메시지 수령
                    self.recv_msg = self.client_socket.recv(1024).decode('utf-8')

                    # 메시지가 비어 있는 경우. 연결이 끊겼으므로 재연결을 위해 예외 처리
                    if self.recv_msg == '':
                        print("received empty msg")
                        raise Exception("empty msg")
                    
                    self.recv_msg = self.recv_msg.split('/')
                    print("receieved msg : "+ self.recv_msg)

                    #########################################
                    # 전달받는 메시지 처리부
                    if self.recv_msg[0] == 'db_error':
                        print("DB 데이터 처리 중 에러 발생")
                    if self.recv_msg[0] == 'order_updated':
                        print("요청한 주문내역 업데이트 완료")
                    if self.recv_msg[0] == 'new_member_added':
                        print("회원 가입 및 사진 저장 완료")
                    if self.recv_msg[0] == 'already_registered':
                        print("기존에 등록된 회원임")
                        # 회원의 선호 정보를 수신
                    #########################################
                
                except socket.timeout:
                    print('MainException: {}'.format(socket.timeout))
                except Exception as e:
                    print('MainException: {}'.format(e))
                    self.connected = False
                    print('connection lost')
                    # 재연결 시도
                    while True:
                        time.sleep(2)
                        try:
                            # 소켓 정리
                            self.client_socket.shutdown(socket.SHUT_RDWR)
                            self.client_socket.close()
                            
                            # 소켓 설정
                            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                            try:
                                self.client_socket.connect((self.ADDR, self.PORT))
                                self.connected = True
                            except socket.error as e:
                                print("서버에 연결할 수 없습니다. 2초 후 재시도합니다.")
                            
                        except Exception as e:
                            print('MainException: {}'.format(e))
                            print('except')
                            # pass


    # DB에게 데이터를 전송하는 함수를 짤 때 self.connected를 확인하면 좋을 듯
    



            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = WindowClass()
    order = OrderClass()
    # order.connect_robot()
    order_thread = threading.Thread(target=order.connect_robot, daemon=True)
    order_thread.start()
    print("order_thread start")
    my_window.show()
    sys.exit(app.exec_())
