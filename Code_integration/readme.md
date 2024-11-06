# 실제 실행시 코드 내 절대경로 정보 수정 필요
> * 원활한 DB-GUI 연동을 위해..
> 1. [GUI_DB_test.py] 15행, 본인의 컴퓨터에서 현재 레포지토리의 DB파일이 있는 위치의 경로로 수정해주세요.
>    ```python
>    sys.path.append(os.path.dirname(os.path.relpath(os.path.dirname("/home/[수정할곳]/aris-repo-1/DB/"))))
>    ```
>
> 2. [DB/sqlite3_db.py] 13,14,15행, 본인의 컴퓨터에서 DB파일 저장할 위치의 경로로 수정해주세요.(db파일이 생성되길 바라는 곳으로)
>    ```python
>    Order_db_abspath = "/home/[수정할곳]/Orders.db"
>    Membership_db_abspath = "/home/[수정할곳]/Membership.db"
>    Reward_preference_db_abs_path = "/home/[수정할곳]/Reward_preference.db"
>    ```
>    
