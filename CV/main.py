import socket
import time


# 필요한 기능 별로 클래스를 만들어서 각 기능을 수행하게 하면 좋을 듯
# ex. 충돌 감지 클래스 / 고객 인식 클래스 / 로봇 동작 지원 클래스

# Robot과의 통신을 위한 클래스
class Connection_Robot():
    def __init__(self):
        super().__init__()


    def connect_robot(self):
        # socket 연결 with robot arm (연결 될때까지 지속적 시도.)
        self.HOST = '192.168.0.17'  # 본인 컴퓨터의 IP 입력
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
                print(f'[LISTENING] Server is listening on robot')
                time.sleep(1)
                while True:
                    try:
                        self.clientSocket, addr_info = self.serverSocket.accept()
                        print("socket for robot accepted")
                        break
                    except socket.timeout:
                        print("socket for robot timeout")
                        print("연결을 재시도 합니다")
                break
            except:
                pass

        print("--client info--")
        print(self.clientSocket)

        self.connected = True
        
        # 지속적으로 메시지 수령.
        while self.connected:
            print("로봇으로부터 메시지 대기 중...")
            time.sleep(0.5)
            
            try:
                # 대기 시간 설정
                self.clientSocket.settimeout(10.0)
                # 메시지 수령
                self.recv_msg = self.clientSocket.recv(self.BUFSIZE).decode('utf-8')
                print('received msg from robot : ' + self.recv_msg)
                
                
                # 메시지가 비어 있는 경우. 연결이 끊겼으므로 재연결을 위해 예외 처리
                if self.recv_msg == '':
                        print('received empty msg from robot')
                        raise Exception('empty msg')

                self.recv_msg = self.recv_msg.split('/')

                # 받은 메시지 타입 확인
                print(f'message type : {self.recv_msg[0]}')
                # 어떤 메시지를 받을 수 있는지 생각해봐야할 듯

                ############################################################################
                # 받은 요청에 따라 응답해주는 부분.

                # request 타입이라면 (어떤 비전 작업을 요청)
                if self.recv_msg[0] == 'request':
                    # 어떤 요청인지 확인
                    if self.recv_msg[1] == 'jig':
                        # jig 확인 요청을 받고 의도된 jig에 아이스크림 캡슐을 제대로 배치되었는지 확인
                        # 확인 결과를 통신을 통해 알림
                        pass
                    if self.recv_msg[1] == 'seal':
                        # seal 제거 여부 확인 요청을 받고 seal의 존재 여부를 확인
                        # 확인 결과를 통신을 통해 알림
                        pass
                    if self.recv_msg[1] == 'customer_position':
                        # 고객의 위치 정보를 요청 받고 고객의 위치 정보를 확인
                        # 확인 결과를 통신을 통해 알림
                        pass
                
                ############################################################################
                else:
                    # 예상되지 않은 메시지를 받은 경우
                    self.clientSocket.send('ERROR : wrong msg received'.encode('utf-8'))
                    print('got unexpected msg!')
                
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


if __name__ == "__main__":
    pass




