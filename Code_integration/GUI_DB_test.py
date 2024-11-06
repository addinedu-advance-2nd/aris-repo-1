# 터미널 설치 파일들
#pip3 install pyqt5  
#sudo apt install python3-pyqt5  
#sudo apt install pyqt5-dev-tools
#sudo apt install qttools5-dev-tools


import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt, QStringListModel
#----------- DB--------------------
import datetime
sys.path.append(os.path.dirname(os.path.relpath(os.path.dirname("/home/hjpark/dev_hjp/aris-repo-1/DB/"))))
from DB import sqlite3_db
#from sqlite3_db import init_database, add_new_member,update_order_history,update_member_prefer_rewards, greeting_member
#----------------------------------

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

# UI 경로
main_file_path = os.path.join(base_dir, "../GUI/untitled.ui")
topping_file_path = os.path.join(base_dir, "../GUI/sub.ui")
main_page_class = uic.loadUiType(main_file_path)[0]
topping_page_class = uic.loadUiType(topping_file_path)[0]

# sub.ui(토핑 선택창) 설정 
class NewWindow(QDialog, topping_page_class):
    def __init__(self, menu_name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
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
        # 토핑 초기에 noOption이미지에 선택표시
        self.noOption.setStyleSheet("border: 5px solid red;")
        self.selected_option = self.noOption

        self.selected_toppings = []  # 선택된 토핑 저장

        # 여기서 topping_name을 추가적으로 전달
        self.Topping_1.mousePressEvent = lambda event: self.select_option(self.Topping_1, "로투스")
        self.Topping_2.mousePressEvent = lambda event: self.select_option(self.Topping_2, "레인보우")
        self.Topping_3.mousePressEvent = lambda event: self.select_option(self.Topping_3, "오레오")
        self.noOption.mousePressEvent = lambda event: self.select_option(self.noOption, "없음")

        # 토핑창에서의 취소,담기 버튼
        self.cancel_btn.clicked.connect(self.close)
        self.order_btn.clicked.connect(self.add_to_order)

    def select_option(self, selected_label, topping_name):
        if self.selected_option:
            self.selected_option.setStyleSheet("border: none;") 
        selected_label.setStyleSheet("border: 5px solid red;")
        self.selected_option = selected_label

        # 선택된 토핑을 리스트에 추가, 없을 경우 없음만 추가하고 이전 기록 삭제(selected toppings 리스트초기화)
        if topping_name == "없음":
            self.selected_toppings = []
        if topping_name not in self.selected_toppings:
            self.selected_toppings.append(topping_name)

    def add_to_order(self):
        order_string = self.text_label.text()
        
        # 선택된 토핑을 문자열로 변환하여 추가
        if self.selected_toppings:
            order_string += " + " + " + ".join(self.selected_toppings)

        if self.parent():
            self.parent().update_order_list(order_string)

        self.close()

    def set_image(self, pixmap):
        self.image_label.setPixmap(pixmap)  
        self.image_label.setScaledContents(True)

class OrderListDialog(QDialog): # 임시 리스트 출력
    def __init__(self, order_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("주문 내역")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()
        self.order_list_widget = QListWidget()
        
        # 주문 목록 추가
        self.order_list_widget.addItems(order_list)
        
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

        self.order_model = QStringListModel()
        self.order_list_widget.setModel(self.order_model) # 리스트 받아옴
        self.receipt.clicked.connect(self.show_receipt) # 임시 영수증 출력

        sqlite3_db.init_database() # DB 시작 및 연결확인

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
        receipt_dialog = OrderListDialog(current_orders, self)
        print(update_DB(current_orders)) 
        receipt_dialog.exec_()

def update_DB(current_orders):
        # default
        db_massage = "DB connection failed"

        # DB로 전송
        orders = current_orders[0].split(' + ')
        flavor= orders[0]

        kor_flavor_list = ["딸기맛", "바나나맛", "초코맛"] ######################## global, later
        eng_flavor_list = ["Strawberry", "Banana", "Chocolate"] ######################## global, later
        for i in range(len(kor_flavor_list)):
            if flavor == kor_flavor_list[i]:
                flavor = eng_flavor_list[i]
            
        # topping 정보
        kor_topping_list = ["로투스", "레인보우", "오레오"] ######################## global, later
        topping_signal = ""
        if len(orders)>1:
            for i in range(len(kor_topping_list)):
                if kor_topping_list[i] in orders[1:]:
                    topping_signal += "1"
                else:
                    topping_signal += "0"
 
        datetime_now = datetime.datetime.now()
        db_sign = sqlite3_db.update_order_history(datetime_now=datetime_now, flavor=flavor , toppings=topping_signal, membership_n= "Null")

        if db_sign:
            db_massage = "success"

        return db_massage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = WindowClass()
    my_window.show()
    sys.exit(app.exec_())
