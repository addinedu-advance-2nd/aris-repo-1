#%%
import datetime
from sqlite3_db import init_database, add_new_member,update_order_history,update_member_prefer_rewards, greeting_member

init_database()

#%%

# 신규 회원 케이스
# 1. 신규 회원 김모모, 바닐라 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
members_number_MM = add_new_member(datetime_order, name='김모모', phone='01012341234', flavor="Vanilla")
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='100', membership_n=members_number_MM)
print(members_number_MM)

# 2. 신규 회원 이현수, 초코 아이스크림, 토핑 1번, 2번 구매
datetime_order = datetime.datetime.now()
members_number_HS = add_new_member(datetime_order, name='이현수', phone='01098765432', flavor="Chocolate")
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='110', membership_n=members_number_HS)
print(members_number_HS)

# 3. 신규 회원 박소현, 딸기 아이스크림, 토핑 3번 구매
datetime_order = datetime.datetime.now()
members_number_SH = add_new_member(datetime_order, name='박소현', phone='01045678912', flavor="Strawberry")
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='001', membership_n=members_number_SH)
print(members_number_SH)

# 4. 신규 회원 최민수, 초코 아이스크림, 토핑 1번과 3번 구매
datetime_order = datetime.datetime.now()
members_number_MS = add_new_member(datetime_order, name='최민수', phone='01078912345', flavor="Chocolate")
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='101', membership_n=members_number_MS)
print(members_number_MS)

# 5. 신규 회원 김지연, 바닐라 아이스크림, 토핑 1번과 2번 구매
datetime_order = datetime.datetime.now()
members_number_JY = add_new_member(datetime_order, name='김지연', phone='01032165498', flavor="Vanilla")
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='110', 
                     membership_n=members_number_JY)
print(members_number_JY)

# 6. 신규 회원 장우진, 딸기 아이스크림, 토핑 없음 구매
datetime_order = datetime.datetime.now()
members_number_UJ = add_new_member(datetime_order, name='장우진', phone='01065412398', flavor="Strawberry")
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='000', 
                     membership_n=members_number_UJ)
print(members_number_UJ)

# 기존 회원 주문 케이스
# 7. 기존 회원 김모모, 딸기 아이스크림, 토핑 1번, 3번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_MM
update_member_prefer_rewards(date=datetime_order, flavor="Strawberry", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='101', membership_n=members_number)
print(members_number)

# 8. 기존 회원 이현수, 바닐라 아이스크림, 토핑 2번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_HS
update_member_prefer_rewards(date=datetime_order, flavor="Vanilla", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='010', membership_n=members_number)
print(members_number)

# 9. 기존 회원 박소현, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_SH
update_member_prefer_rewards(date=datetime_order, flavor="Chocolate", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n=members_number)
print(members_number)


# . 기존 회원 김모모, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_MM
update_member_prefer_rewards(date=datetime_order, flavor="Chocolate", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n=members_number)
print(members_number)

# . 기존 회원 이현수, 딸기 아이스크림, 토핑 1번과 2번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_HS
update_member_prefer_rewards(date=datetime_order, flavor="Strawberry", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='110', membership_n=members_number)
print(members_number)

# ... 이어서 회원 번호와 다양한 주문 내용을 반영하여 17건의 기존 회원 주문 추가 ...

# 비회원 주문 케이스
# . 비회원, 초코 아이스크림, 토핑 없음 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='000', membership_n="None")

# . 비회원, 딸기 아이스크림, 토핑 2번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='010', membership_n="None")

# . 기존 회원 최민수, 딸기 아이스크림, 토핑 없음 구매
datetime_order = datetime.datetime.now()
members_number = members_number_MS
update_member_prefer_rewards(date=datetime_order, flavor="Strawberry", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='000', membership_n=members_number)
print(members_number)

# . 기존 회원 김지연, 바닐라 아이스크림, 토핑 1번과 3번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_JY
update_member_prefer_rewards(date=datetime_order, flavor="Vanilla", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='101', membership_n=members_number)
print(members_number)

# . 기존 회원 장우진, 초코 아이스크림, 토핑 2번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_UJ
update_member_prefer_rewards(date=datetime_order, flavor="Chocolate", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='010', membership_n=members_number)
print(members_number)

# . 비회원, 바닐라 아이스크림, 토핑 1번, 3번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='101', membership_n="None")


# . 비회원, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n="None")


# . 비회원, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n="None")


# . 비회원, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n="None")


# . 비회원, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n="None")

# . 비회원, 초코 아이스크림, 토핑 1번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='100', membership_n="None")

# . 비회원, 바닐라 아이스크림, 토핑 1번, 3번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='101', membership_n="None")

# . 비회원, 바닐라 아이스크림, 토핑 1번, 3번 구매
datetime_order = datetime.datetime.now()
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='101', membership_n="None")

# . 기존 회원 박소현, 바닐라 아이스크림, 토핑 없음 구매
datetime_order = datetime.datetime.now()
members_number = members_number_SH
update_member_prefer_rewards(date=datetime_order, flavor="Vanilla", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Vanilla', toppings='000', membership_n=members_number)
print(members_number)

# . 기존 회원 최민수, 딸기 아이스크림, 토핑 2번과 3번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_MS
update_member_prefer_rewards(date=datetime_order, flavor="Strawberry", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Strawberry', toppings='011', membership_n=members_number)
print(members_number)

# . 기존 회원 김지연, 초코 아이스크림, 토핑 1번과 2번과 3번 구매
datetime_order = datetime.datetime.now()
members_number = members_number_JY
update_member_prefer_rewards(date=datetime_order, flavor="Chocolate", membership_n=members_number)
update_order_history(datetime_now=datetime_order, flavor='Chocolate', toppings='111', membership_n=members_number)
print(members_number)

# %%
import sqlite3
#create table - Order
con_Order = sqlite3.connect('./DB_list/Orders.db')
cur_Order = con_Order.cursor()
for row in cur_Order.execute('''SELECT * FROM Orders'''):
        print(row)

con_Order.close()

# %%
con_Membership = sqlite3.connect('./DB_list/Membership.db')
cur_Membership = con_Membership.cursor()
for row in cur_Membership.execute('''SELECT * FROM Membership'''):
        print(row)

con_Membership.close()

# %%

con_Reward_preference = sqlite3.connect('./DB_list/Reward_preference.db')
cur_Reward_preference = con_Reward_preference.cursor()
for row in cur_Reward_preference.execute('''SELECT * FROM Reward_preference'''):
        print(row)

con_Reward_preference.close()

# %%
greeting_member(7259436319372312577)

# %%
