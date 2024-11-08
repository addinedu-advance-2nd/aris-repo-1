import sqlite3
import datetime, time
from snowflake import SnowflakeGenerator
import os
import shutil

import threading
import socket
import json

"""
------------------------------------
    TCP통신을 위한 DB
------------------------------------
"""
class Database():
    def __init__(self, **kwargs):
        self.kiosk_photo_path='../kioskphoto/' # 회원 얼굴사진 찍은 직후 저장위치, 임시, 기능x
        self.member_photo_path='./face_photo/' # 회원 등록 완료 후 사진 보관 위치, 임시, 기능x
        self.reward_counts=7 # 임시, 기능x
        self.Flavor_list=["Strawberry", "Banana","Chocolate"] # 선택가능한 맛 list, 없는 맛 선택시 오류

        self.Order_db_abspath = "/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Orders.db"
        self.Membership_db_abspath = "/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Membership.db"
        self.Reward_preference_db_abs_path = "/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Reward_preference.db"

        # 사진관련? test
        self.new_photo = False

    def socket_test(self):
        self.clientSocket.send(('new_member_added').encode('utf-8'))
        self.clientSocket.send(('already_registered').encode('utf-8'))
        self.clientSocket.send(('order_updated').encode('utf-8'))
        self.clientSocket.send(('db_error').encode('utf-8'))


    def socket_connect(self):
        # socket 연결  (연결 될때까지 지속적 시도.)
        self.HOST = '192.168.0.28' #############################################################################
        self.PORT = 65432
        self.BUFSIZE = 1024
        self.ADDR = (self.HOST, self.PORT)

        # 서버 소켓 설정
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.settimeout(10)

        # 연결 시도
        while True:
            try:
                self.serverSocket.bind(self.ADDR)
                print("bind")

                # 연결 대기
                self.serverSocket.listen(1)
                print(f'[LISTENING] Server is listening on db_server')
                time.sleep(1)
                while True:
                    try:
                        self.clientSocket, addr_info = self.serverSocket.accept()
                        self.socket_test()
                        print("socket accepted")
                        break
                    except socket.timeout:
                        print("socket timeout")
                        print("연결을 재시도 합니다")
                break
            except:
                pass

        print("--client info--")
        print(self.clientSocket)

        self.connected = True
        
        # 지속적으로 메시지 수령.
        while self.connected:
            print("메시지 대기 중...")
            time.sleep(0.5)
            
            try:
                # 대기 시간 설정
                self.clientSocket.settimeout(10.0)
                # 메시지 수령
                try:
                    self.recv_msg = self.clientSocket.recv(self.BUFSIZE).decode('utf-8')
                    print('received msg : ' + self.recv_msg)
                    self.clientSocket.send('socket_connect success!'.encode('utf-8'))
                except:
                    self.clientSocket.send('socket_connect failed!'.encode('utf-8'))
                
                
                # 메시지가 비어 있는 경우. 연결이 끊겼으므로 재연결을 위해 예외 처리
                if self.recv_msg == '':
                        print('received empty msg')
                        raise Exception('empty msg')

                self.recv_msg = self.recv_msg.split('/')

            
                # 어떤 메시지를 받을 수 있는지 생각해봐야할 듯
                if self.recv_msg[0] in ['test', 'DB주문내역업데이트해','DB이사람이회원가입한대','오류났어','DB시작']:
                    # 받은 메시지 타입 확인
                    print(f'message type : {self.recv_msg[0]}')
                    
                    # DB주문내역업데이트해 => 받은 메시지 정보를 활용하여 업데이트
                    if self.recv_msg[0] == 'DB시작':
                        self.init_database() ###############################################################################
                        print('DB시작 요청 - DB init 했습니다. - test')

                    elif self.recv_msg[0] == 'DB주문내역업데이트해':
                        #test
                        current_orders = ['딸기맛']
                        membership_n = ['11111']
                        try:
                            self.db_update_order(self,current_orders, membership_n)
                        except:
                            print('오류')
                        print('DB주문내역업데이트해 요청 - DB주문내역업데이트 했습니다. - test')
                    
                    elif self.recv_msg[0] == 'DB이사람이회원가입한대':
                        # 메시지 추출
                        try:
                            print("114: ",self.recv_msg[1])
                            member_name = " "
                            member_phone = " "
                            self.db_new_member(member_name, member_phone) ######################################################
                        except:
                            print('오류')

                        print('DB회원가입기능 요청 - DB신규회원 추가 했습니다. - test')
                        # 문자열 -> json 
                        temp = json.loads(self.recv_msg[1])
                        # 주문 queue에 넣음
                    elif self.recv_msg[0] == '오류났어':
                        """
                        키오스크쪽에서 뭔가 문제가 발생했다
                        """
                        print('키오스크쪽에서 뭔가 문제가 발생했다')
                    else:
                        self.clientSocket.send('ERROR : wrong msg received'.encode('utf-8'))
                        print('got unexpected msg! - 메시지의 상태가..?')
                        
            except socket.timeout:
                self.pprint('MainException: {}'.format(socket.timeout))

            except Exception as e:
                self.pprint('MainException: {}'.format(e))
                self.connected = False
                print('connection lost')
                # 재연결 시도
                while True:
                    time.sleep(2)
                    try:
                        # server socket 정리
                        self.serverSocket.shutdown(socket.SHUT_RDWR)
                        self.serverSocket.close()
                        
                        # 소켓 설정
                        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.serverSocket.settimeout(10)

                        self.serverSocket.bind(self.ADDR)
                        print("bind")

                        while True:
                            self.serverSocket.listen(1)
                            print(f'reconnecting...')
                            try:
                                self.clientSocket, addr_info = self.serverSocket.accept()
                                self.connected = True
                                break

                            except socket.timeout:
                                print('socket.timeout')

                            except:
                                pass
                        break
                    except Exception as e:
                        self.pprint('MainException: {}'.format(e))
                        print('except')
                        # pass

    def db_new_member(self,member_name, member_phone):
        # default
        db_massage = "DB connection failed"
        members_number = ""
        db_sign = False

        datetime_now = datetime.datetime.now()
        
        membership_db_sign, members_number = self.is_member(member_name,member_phone)
        
        if membership_db_sign:
            db_massage = "member" #이미 회원 가입이 되어있는 경우 (가입한것 까먹고 또 가입)
            db_sign = True
            print("already signed member, your membership number is ",members_number)
            try:
                self.clientSocket.send(('already_registered').encode('utf-8'))
            except:
                print('socket error')
        else:
            db_sign, members_number = self.add_new_member(datetime_now, name=member_name, phone=member_phone)
            db_sign = True
            db_massage = "New member added"
            # 사진관련? test
            try:
                self.clientSocket.send(('new_member_added').encode('utf-8'))
            except:
                print('socket error')
            print("new membership number:",members_number)
        
        return db_sign, db_massage, members_number 
    
    def db_update_order(self,current_orders, membership_n):
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
        try:
            if membership_n != "":
                db_sign = self.update_order_history(datetime_now=datetime_now, flavor=flavor , toppings=topping_signal,membership_n=membership_n)
            else:
                # 비회원 주문 케이스
                db_sign = self.update_order_history(datetime_now=datetime_now, flavor=flavor , toppings=topping_signal,membership_n="Null")

            self.clientSocket.send(('order_updated').encode('utf-8'))
        except:
            print('socket error')
       
        if db_sign:
            db_massage = "success"

        return db_massage

    # 테이블 생성 -이미 존재할 경우 종료
    def init_database (self): 
        #db_list = ["Orders", "Membership", "Reward_preference"]

        #create table - Order
        con_Order = sqlite3.connect(self.Order_db_abspath)
        cur_Order = con_Order.cursor()
        try:
            cur_Order.execute('''CREATE TABLE Orders(dateTime datetime, flavor text, 
                        toppings text, membership_num integer )''')
        except:
            print("Table [Orders] already exist")

        #create table - Membership
        con_Membership = sqlite3.connect(self.Membership_db_abspath)
        cur_Membership = con_Membership.cursor()
        try:
            cur_Membership.execute('''CREATE TABLE Membership(dateTime datetime, name text, 
                        phone_num text, membership_num integer, 
                        face_path text )''')
        except:
            print("Table [Membership] already exist")

        #create table - Reward_preference
        con_Reward_preference = sqlite3.connect(self.Reward_preference_db_abs_path)
        cur_Reward_preference = con_Reward_preference.cursor()
        try:
            cur_Reward_preference.execute('''CREATE TABLE Reward_preference(
                        update_datetime datetime, membership_num integer, 
                        total_order_count integer, current_count integer, 
                        menu_history text, latest_menu text, latest_menu_cont integer)''')
        except:
            print("Table [Reward_preference] already exist")    

        con_Order.close()
        con_Membership.close()
        con_Reward_preference.close()
        
    # 주문 이력 추가
    def update_order_history(self,datetime_now, flavor, toppings, membership_n):
        db_sign = ""
        try:
            con_Order = sqlite3.connect(self.Order_db_abspath)
            cur_Order = con_Order.cursor()

            DT = datetime_now
            Flavor = flavor
            Topping = toppings
            Member_n= membership_n
            
            sql=(DT,Flavor,Topping,Member_n)
            print(sql)

            # Insert a row of data
            cur_Order.execute("""INSERT INTO Orders VALUES (?,?,?,?)""",sql)

            # save chainge
            con_Order.commit()

            # if membership number exist, update member_prefer_rewards DB
            if membership_n != "":
                self.update_member_prefer_rewards(datetime_now,flavor,membership_n)
            
            # end
            con_Order.close()
            db_sign = True
        except:
            db_sign = False


        return db_sign

    # 신규회원 - 회원정보&회원적립 및 선호 DB 내역 입력
    def add_new_member(self,datetime_now,name, phone):
        #default
        global member_photo_path, Flavor_list
        member_name = ""
        member_phone = ""
        members_number="0"
        db_sign=""

        try:
            # 회원 번호 생성
            gen = SnowflakeGenerator(24)
            members_number = next(gen)

            # 회원번호 중복확인
            #check_member_num_duplication(members_number)

            # 이름 처리
            if name:
                member_name = str(name)
            
            # 폰 번호 처리 "010-0000-0000"으로 들어온다고 가정
            if phone:
                member_phone = str(phone)

            #이미지 저장 위치 기록
            # 키오스크에서 가장 최근 전송받은 이미지 선택, 이름바꾸기
            new_member_photo_path = self.Find_rename_face_image(members_number)

            """
            if os.path.isfile(new_member_photo_path):
                print('complite adding new member')
            else:
                print("something wrong during save face photo")
            """

            # Membership DB - 회원 정보 기록
            con_Membership = sqlite3.connect(self.Membership_db_abspath)
            cur_Membership = con_Membership.cursor()

            sql = (datetime_now,member_name,member_phone,members_number,new_member_photo_path)
            #print(sql)
            # Insert a row of data
            cur_Membership.execute("""INSERT INTO Membership VALUES (?,?,?,?,?)""",sql)
            # save chainge
            con_Membership.commit()
            # end
            con_Membership.close()
            

            # Membership preference & reward DB - 멤버쉽 쿠폰 생성
            #Reward_preference
            con_Reward_preference = sqlite3.connect(self.Reward_preference_db_abs_path)
            cur_Reward_preference = con_Reward_preference.cursor()

            # default value
            total_order=0
            current_count = 0
            menu_history = ""
            for i in range(len(Flavor_list)):  
                menu_history += "0_" 


            last_menu="Null"
            last_menu_cont=0

            cur_Reward_preference.execute( """INSERT INTO Reward_preference Values (?,?,?,?,?,?,?)""",
                                            (datetime_now,members_number,total_order,current_count,menu_history,last_menu,last_menu_cont))
            con_Reward_preference.commit()
            con_Reward_preference.close()

            db_sign = True

        except:
            db_sign = False


        return db_sign, members_number

    # 회원번호 중복확인 - 미구현
    def check_member_num_duplication(self,members_number):
        # 필요시 구축, 회원번호 중복여부 확인용
        is_duplication = False

        return is_duplication

    # 회원번호 조회 - (얼굴인식과 연계예정)
    def is_member(self,member_name,member_phone):
        membership_db_sign = False
        members_number =""
        join_time =""

        # 해당 회원번호가 멤버 목록에 있는지
        # Membership DB - 회원 정보 기록
        con_Membership = sqlite3.connect(self.Membership_db_abspath)
        cur_Membership = con_Membership.cursor()

        sql = (member_name,member_phone)
        print("186 DB/sqlite3_db:",sql)
        # Insert a row of data
    
        cur_Membership.execute("""SELECT * FROM Membership WHERE name=(?) and phone_num = (?)""",sql)
    
        
        for row in cur_Membership:
            
            # 회원 정보 리턴
            join_time=row[0]
            print("이미 가입한 이력이 있어요.",join_time)
            members_number = row[3]
            membership_db_sign = True
            
        if join_time == "":
            membership_db_sign = False

        #print("199 DB/sqlite3_db:",row)
        # end
        con_Membership.close()
        
        return membership_db_sign, members_number

    # 얼굴인식 이미지 회원번호와 매칭 - 미구현(얼굴인식 및 사진과 연계), 이미지 경오 리턴
    def Find_rename_face_image(self,members_number):
        global kiosk_photo_path # 사진 찍은 최초 파일들이 들어있는 폴더, 처리후 삭제
        global member_photo_path # 처리 후 저장할 폴더 

        file_name_and_time_lst = []

        dest = "test_image.jpg"
        """# 해당 경로에 있는 파일들의 생성시간 리스트
        for f_name in os.listdir(f"{kiosk_photo_path}"):
            written_time = os.path.getctime(f"{kiosk_photo_path}{f_name}")
            file_name_and_time_lst.append((f_name, written_time))

        # 생성시간 역순으로 정렬
        sorted_file_lst = sorted(file_name_and_time_lst, key=lambda x: x[1], reverse=True)
        recent_file = sorted_file_lst[0]
        recent_file_name = recent_file[0]
        print("recent_file_name",recent_file_name)

        # 파일 명을 회원번호로 변경 및 회원사진보관위치로 이동
        src = kiosk_photo_path+recent_file_name
        dest = member_photo_path+str(members_number)+'.jpg'
        try:
            shutil.move(src, dest)
            print("face image saved at ",dest)
        except:
            print("error during file moving")"""
        
        return dest

    # 리워드 사용관련 - 미구현
    def is_reward_available(self,membership_n):
        #리워드 사용할때인가?
        global reward_counts
        return

    # 회원의 구매 및 선호기록 
    def update_member_prefer_rewards(self,date, flavor, membership_n):
        global Flavor_list
        total_order=0
        current_count = 0
        menu_history=""
        new_menu_history=""
        last_menu=""
        last_menu_cont=0

        #Reward_preference
        con_Reward_preference = sqlite3.connect(self.Reward_preference_db_abs_path)
        cur_Reward_preference = con_Reward_preference.cursor()
        # 주문기록 추가
        cur_Reward_preference.execute("""SELECT * FROM Reward_preference WHERE membership_num=(?)""",(membership_n,))
        last_order=date
        for row in cur_Reward_preference:
            total_order=row[2]+1
            current_count = row[3]+1

            menu_history=row[4]
            flavor_num=Flavor_list.index(flavor) 
            menu_list=menu_history.split('_')
            
            for i in range(len(Flavor_list)):  
                    print("i=",i)
                    if i == flavor_num:
                            new_menu_history += str(int(menu_list[i])+1)+"_" 
                    else:
                            new_menu_history += str(menu_list[i])+"_" 

            # 최근 주문 메뉴가 현재 주문 메뉴와 같으면 연속일수 +1
            last_menu=flavor
            if flavor == row[5]: 
                last_menu_cont = row[6] +1
            else:
                last_menu_cont=1 
        
        cur_Reward_preference.execute( """UPDATE Reward_preference SET update_datetime = (?), total_order_count = (?), 
                                        current_count=(?), menu_history=(?), 
                                        latest_menu=(?), 
                                        latest_menu_cont=(?) WHERE membership_num=(?)""",
                                        (last_order,total_order,current_count,new_menu_history,last_menu,last_menu_cont,membership_n))
        con_Reward_preference.commit()
        
        #print(last_order,total_order,current_count,most_menu, most_menu_count,last_menu,last_menu_cont,membership_n)
        
        con_Reward_preference.close()

        return

    # 회원 인식 성공 했을 때 인삿말 등 활용 목적 - 회원 적립상태 반환
    def greeting_member(self,membership_n):
        last_order="Null"
        total_order=0
        current_count = 0
        menu_history="Null"
        most_menu="Null"
        most_menu_count=0
        last_menu="Null"
        last_menu_cont=0
        
        #Reward_preference
        con_Reward_preference = sqlite3.connect(self.Reward_preference_db_abs_path)
        cur_Reward_preference = con_Reward_preference.cursor()
        
        cur_Reward_preference.execute("""SELECT * FROM Reward_preference WHERE membership_num=(?)""",(membership_n,))
        for row in cur_Reward_preference:
            last_order=row[0]
            total_order=row[2]
            current_count = row[3]

            menu_history=row[4]
            menu_list=menu_history.split('_')
            most_menu_count = max(menu_list)

            # 최다주문 맛이 1개로 결정할수없는경우 확인목적
            dup_cnt = menu_list.count(most_menu_count)  
            if dup_cnt >=2 :
                most_menu = "아직 고민중이에요"
            else:
                most_menu = Flavor_list[menu_list.index(max(menu_list))]

            last_menu=row[5]
            last_menu_cont=row[6]
            
        """
        ('2024-11-05 14:28:12.366829', 7259436319301009409, 3, 3, '1_1_1_0_', 'Chocolate', 1)
        """
        
        # 주문횟수 / 적립상태(N개의 스탬프) / 최다주문메뉴, 횟수 / 최근주문메뉴, 연속횟수
        member_info = [last_order,total_order,current_count,most_menu,most_menu_count, last_menu,last_menu_cont]
        # end
        con_Reward_preference.close()


        return member_info


if __name__ == '__main__':
    DB_main = Database()
    # 소켓 통신용 스레드 동작. (지속적으로 메시지를 수령해야하기에.)
    socket_thread = threading.Thread(target=DB_main.socket_connect)
    socket_thread.start()
    print('socket_thread start')    

    DB_main.socket_test()
    # 서비스 스레드 동작. (수령받은 메시지에 기반하여서 계속 동작해야함.)
    #run_thread = threading.Thread(target=Database.run)
    #run_thread.start()
    #print('run_thread_started')