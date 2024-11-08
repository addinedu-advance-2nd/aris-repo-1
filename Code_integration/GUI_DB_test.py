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

# UI 경로 ---path수정할것----------------------------------------------------
main_file_path = os.path.join(base_dir, "../GUI/untitled.ui") 
topping_file_path = os.path.join(base_dir, "../GUI/sub.ui")
memberinfo_file_path = os.path.join(base_dir, "../GUI/memberinfo.ui")
# ------------------------------------------------------------------------

main_page_class = uic.loadUiType(main_file_path)[0]
topping_page_class = uic.loadUiType(topping_file_path)[0]
memberinfo_page_class = uic.loadUiType(memberinfo_file_path)[0]

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

# 회원정보 
class MemberInfoDialog(QDialog,memberinfo_page_class):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
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
        self.receipt.clicked.connect(self.show_receipt) # 임시 영수증 출력 
        self.member_btn.clicked.connect(self.open_member_window)

        self.user_name = ""
        self.user_phone = ""
        self.user_membership_num = ""

        sqlite3_db.init_database() # DB 시작 및 연결확인

    def update_member_info(self, name, phone):
        # 받은 이름과 전화번호로 레이블을 업데이트
        self.user_name = name
        self.user_phone = phone
        self.user_membership_num = "" # 초기화
        db_sign = False
        db_message = ""

        try:
            db_sign, db_message, self.user_membership_num =db_new_member(self.user_name, self.user_phone)
            print("225:",db_sign, db_message, self.user_membership_num)
        except:
            print("회원가입기능오류 - update member info() & DB ")
        
        if db_message == "member":
            print("이미 가입된 회원입니다.")
        elif (db_sign == False) | (self.user_membership_num == "") :
            print("회원가입기능오류 - db_new_member DB ")



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

    def show_receipt(self): #임시 영수증 출력 | 아무것도 장바구니 넣지 않은 상태에서의 결제 처리 미완
        current_orders = self.order_model.stringList()
        receipt_dialog = OrderListDialog(current_orders, self.user_name, self.user_phone, self)
        
        # DB 전송 - 결제시 한번에
        print("current_orders: ",current_orders)
        if current_orders != []: # 비어있으면, 주문전송x
            print("show_receipt:",db_update_order(current_orders,self.user_membership_num)) 

        receipt_dialog.exec_()

# Local
def db_new_member(member_name, member_phone):
    # default
    db_massage = "DB connection failed"
    members_number = ""
    db_sign = False

    datetime_now = datetime.datetime.now()
    print("268")
    membership_db_sign, members_number = sqlite3_db.is_member(member_name,member_phone)
    print("270: membership_db_sign, members_number: ", membership_db_sign, members_number)
    if membership_db_sign:
        db_massage = "member" #이미 회원 가입이 되어있는 경우 (가입한것 까먹고 또 가입)
        db_sign = True
        print("274 already signed member, your membership number is ",members_number)
    else:
        db_sign, members_number = sqlite3_db.add_new_member(datetime_now, name=member_name, phone=member_phone)
        db_sign = True
        db_massage = "New member added"
        print("279 newbi membership number:",members_number)
      
    return db_sign, db_massage, members_number 

def db_update_order(current_orders, membership_n):
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
        else:
            topping_signal += "0"*len(kor_topping_list)
 
        datetime_now = datetime.datetime.now()

        # 회원 비회원 여부
        if membership_n != "":
            db_sign = sqlite3_db.update_order_history(datetime_now=datetime_now, flavor=flavor , toppings=topping_signal,membership_n=membership_n)
        else:
            # 비회원 주문 케이스
            db_sign = sqlite3_db.update_order_history(datetime_now=datetime_now, flavor=flavor , toppings=topping_signal,membership_n="Null")

        if db_sign:
            db_massage = "success"

        return db_massage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = WindowClass()
    my_window.show()
    sys.exit(app.exec_())

