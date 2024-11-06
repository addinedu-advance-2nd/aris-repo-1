#%%
import sqlite3
import datetime
from snowflake import SnowflakeGenerator
import os
import shutil

kiosk_photo_path='../kioskphoto/' # 회원 얼굴사진 찍은 직후 저장위치, 임시, 기능x
member_photo_path='./face_photo/' # 회원 등록 완료 후 사진 보관 위치, 임시, 기능x
reward_counts=7 # 임시, 기능x
Flavor_list=["Strawberry", "Chocolate", "Vanilla"] # 선택가능한 맛 list, 없는 맛 선택시 오류

# 테이블 생성 -이미 존재할 경우 종료
def init_database (): 
    db_list = ["Orders", "Membership", "Reward_preference"]

    #create table - Order
    con_Order = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Orders.db')
    cur_Order = con_Order.cursor()
    try:
        cur_Order.execute('''CREATE TABLE Orders(dateTime datetime, flavor text, 
                    toppings text, membership_num integer )''')
    except:
        print("Table [Orders] already exist")

    #create table - Membership
    con_Membership = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Membership.db')
    cur_Membership = con_Membership.cursor()
    try:
        cur_Membership.execute('''CREATE TABLE Membership(dateTime datetime, name text, 
                    phone_num text, membership_num integer, 
                    face_path text )''')
    except:
         print("Table [Membership] already exist")

    #create table - Reward_preference
    con_Reward_preference = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Reward_preference.db')
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
def update_order_history(datetime_now, flavor, toppings, membership_n):
    db_sign = ""
    try:
        con_Order = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Orders.db')
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
        
        # end
        con_Order.close()
        db_sign = True
    except:
        db_sign = False


    return db_sign

# 신규회원 - 회원정보&회원적립 및 선호 DB 내역 입력
def add_new_member(datetime_now,name, phone, flavor):
    #default
    global member_photo_path
    member_name = '고객'
    member_phone = '01012345678'
    members_number='0'

    # 회원 번호 생성
    gen = SnowflakeGenerator(24)
    members_number = next(gen)

    # 회원번호 중복확인
    #check_member_num_duplication(members_number)

    # 이름 처리
    if name:
        member_name = str(name)
    
    # 폰 번호 처리
    if phone:
        member_phone = str(phone)

    #이미지 저장 위치 기록
    # 가장 최근 촬영 이미지 선택, 이름바꾸기
    new_member_photo_path=Find_rename_face_image(members_number)

    """
    if os.path.isfile(new_member_photo_path):
        print('complite adding new member')
    else:
        print("something wrong during save face photo")
    """

    # Membership DB - 회원 정보 기록
    con_Membership = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Membership.db')
    cur_Membership = con_Membership.cursor()

    sql = (datetime_now,member_name,member_phone,members_number,new_member_photo_path)
    print(sql)
    # Insert a row of data
    cur_Membership.execute("""INSERT INTO Membership VALUES (?,?,?,?,?)""",sql)
    # save chainge
    con_Membership.commit()
    # end
    con_Membership.close()
    

    # Membership preference & reward DB - 멤버쉽 쿠폰 생성
    #Reward_preference
    con_Reward_preference = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Reward_preference.db')
    cur_Reward_preference = con_Reward_preference.cursor()

    # default value
    total_order=1
    current_count = 1
    menu_history = ""
    flavor_num=Flavor_list.index(flavor) 
    for i in range(len(Flavor_list)):  
        if i == flavor_num:
            menu_history += "1_"
        else:
            menu_history += "0_" 


    last_menu=flavor
    last_menu_cont=1

    cur_Reward_preference.execute( """INSERT INTO Reward_preference Values (?,?,?,?,?,?,?)""",
                                    (datetime_now,members_number,total_order,current_count,menu_history,last_menu,last_menu_cont))
    con_Reward_preference.commit()
    con_Reward_preference.close()

    return members_number

# 회원번호 중복확인 - 미구현
def check_member_num_duplication(members_number):
    # 필요시 구축, 회원번호 중복여부 확인용
    is_duplication = False

    return is_duplication

# 회원번호 조회 - 미구현(얼굴인식과 연계예정)
def is_member(members_number):
    # 필요시 구축, 해당 회원번호가 멤버 목록에 있는지
    
    return 

# 얼굴인식 이미지 회원번호와 매칭 - 미구현(얼굴인식 및 사진과 연계), 이미지 경오 리턴
def Find_rename_face_image(members_number):
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
def is_reward_available(membership_n):
    #리워드 사용할때인가?
    global reward_counts
    return

# 회원의 구매 및 선호기록 - 최애메뉴 선정부분만 미완성
def update_member_prefer_rewards(date, flavor, membership_n):
    global Flavor_list
    total_order=0
    current_count = 0
    menu_history=""
    new_menu_history=""
    last_menu=""
    last_menu_cont=0

    #Reward_preference
    con_Reward_preference = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Reward_preference.db')
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
def greeting_member(membership_n):
    last_order="Null"
    total_order=0
    current_count = 0
    menu_history="Null"
    most_menu="Null"
    most_menu_count=0
    last_menu="Null"
    last_menu_cont=0
    
    #Reward_preference
    con_Reward_preference = sqlite3.connect('/home/hjpark/dev_hjp/aris-repo-1/DB/DB_list/Reward_preference.db')
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


# %%
