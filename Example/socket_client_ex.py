import socket

# 클라이언트 설정
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.0.17', 65432))  # 서버에 연결 요청

try:
    # 서버에 데이터 전송
    while True:
        message = input('전송할 메시지를 입력하세요 : ')
        if message == '그만':
            break
        client_socket.sendall(message.encode())               # 메시지 전송 시 byte 형식으로 encode 해야만 함.

        # 서버로부터 데이터 수신
        data = client_socket.recv(1024)                         # 서버로부터 데이터를 전송 받을 수도 있음
        print(f"서버로부터 받은 응답: {data.decode()}")             # 전송 받은 데이터는 바이트 형식이므로 str로 decode하여 사용
finally:
    # 연결 종료
    client_socket.close()
