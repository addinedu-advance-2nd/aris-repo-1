import socket
import threading
import time

msg = ''
new_msg = False

def socket_connect():
    global msg
    global new_msg

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓 설정. 변경할 필요 없음
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 소켓 종료 시 port 사용 반환
    server_socket.bind(('192.168.0.17', 65432))  # IP와 포트 설정 (server의 경우 본인의 IP와 이용할 포트 번호. client의 경우 server의 IP와 포트에 연결)
    server_socket.listen()  # 서버가 연결을 받을 준비

    print("서버가 시작되었습니다. 연결을 기다리는 중...")

    # 클라이언트와 연결
    connection, address = server_socket.accept() # 클라이언트의 연결 요청을 기다림. 특별한 설정 없으면 무한정 대기
    print(f"{address}와 연결되었습니다.")

    # 지속적으로 메시지 수신
    while True:
        time.sleep(0.5)
        print('메시지 수신 대기중...')
        msg = connection.recv(1024) # 클라이언트로부터 데이터 수신. 1024는 최대 메시지 크기임 변경할 필요 없음. 무한정 대기
        msg = msg.decode()          # 수신 받은 데이터는 바이트 형식이여서 사용 어려움. python 문자열로 형태로 변경. 
        if msg == '':
            print("연결이 종료되었습니다.") # msg가 비어있다면 연결이 끊겼음을 의미
            break                       # 연결이 끊겼음으로 메시지 수신을 멈춤
        
        connection.sendall(f"제가 받은 메시지는 {msg} 입니다. 다음 메시지를 보내주세요.".encode()) # 클라이언트에게 메시지 전달 가능

        new_msg = True      # 새로운 메시지가 있다고 알림. 플래그


    
    # 연결 종료
    connection.close()
    server_socket.close()


def msg_print():
    global msg
    global new_msg

    while True:                                 # 지속적으로 출력하기 위해 반복
        if new_msg:                             # 새 메시지가 있을 때 출력
            print("수신 받은 메시지 : " + msg)      # 받은 메시지 출력
            new_msg = False                     # 메시지 출력했다는 표시



# 메인 문
# 쓰레드를 이용해 두 함수가 함께 계속 돌아가게 구현
socket_thread = threading.Thread(target=socket_connect)                 # 연결을 수행하고 지속적으로 메시지를 수신하게끔하는 쓰레드
socket_thread.start()
print('socket_thread start')    

msg_print_thread = threading.Thread(target=msg_print, daemon=True)      # 수신받은 메시지를 출력하는 보조 쓰레드
msg_print_thread.start()
print('msg_print_thread_started')


