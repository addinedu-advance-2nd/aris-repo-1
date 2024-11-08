#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2022, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
# Notice
#   1. Changes to this file on Studio will not be preserved
#   2. The next conversion will overwrite the file with the same name
# 
# xArm-Python-SDK: https://github.com/xArm-Developer/xArm-Python-SDK
#   1. git clone git@github.com:xArm-Developer/xArm-Python-SDK.git
#   2. cd xArm-Python-SDK
#   3. python setup.py install
"""
import sys
import math
import time
import queue
import datetime
import random
import traceback
import threading
import socket
import json
from xarm import version
from xarm.wrapper import XArmAPI


class RobotMain(object):
    """Robot Main Class"""
    def __init__(self, robot, **kwargs):
        self.alive = True
        self._arm = robot
        self._tcp_speed = 100
        self._tcp_acc = 2000
        self._angle_speed = 20
        self._angle_acc = 500
        self._vars = {}
        self._funcs = {}
        self._robot_init()
        self.state = 'stopped'
        self.next_customer = False
        self.order_msg_queue = queue.Queue()

        self.position_home = [179.2, -42.1, 7.4, 186.7, 41.5, -1.6]  # angle
        self.position_jig_A_grab = [-260.9, -130.6, 210.1, -39.2, 87.2, -150.9]  # linear
        self.position_jig_B_grab = [-159.3, -127.8, 205, -22.8, 87, -114.1]  # linear
        self.position_jig_C_grab = [-66.6, -140.7, 208, -71.1, 87.7, -133.6]  # linear
        self.position_sealing_check = [-136.8, 71.5, 307.6, 39.7, -82.8, -28.5]  # Linear
        self.position_capsule_place = [235, 133, 461.4, -143.8, 89.4, -57.3]  # Linear
        self.position_before_capsule_place = self.position_capsule_place.copy()
        self.position_before_capsule_place[2] += 25
        self.position_cup_grab = [216.6, -99.2, 150.1, -75.8, -89.6, 146.3]  # linear
        
        #before icecream
        self.position_topping_A = [-200.3, 162.8, 359.9, -31.7, 87.8, 96.1]  # Linear
        self.position_topping_B = [106.5, -39.7, 15.0, 158.7, 40.4, 16.9]  # Linear
        self.position_topping_C = [43.6, 137.9, 350.1, -92.8, 87.5, 5.3]  # Linear
        self.position_icecream_with_topping = [168.7, 175.6, 359.5, 43.9, 88.3, 83.3]  # Linear
        self.position_icecream_no_topping = [48.4, -13.8, 36.3, 193.6, 42.0, -9.2]  # angle
        #after icecream
        self.position_topping_A_later = [-197.7, 159.7, 305.4, 102.6, 89.3, -129.7]  # Linear
        self.position_topping_B_later = [-47.7, 159.7, 305.4, 102.6, 89.3, -129.7]  # Linear
        self.position_topping_C_later = [56.2, 142.7, 316.8, 162.2, 88.4, -92.0]  # Linear
        self.position_jig_A_serve = [-258.7, -136.4, 211.2, 43.4, 88.7, -72.2]  # Linear
        self.position_jig_B_serve = [-166.8, -126.5, 208, -45.2, 89.2, -133.6]  # Linear
        self.position_jig_C_serve = [-63.1, -138.2, 208, -45.5, 88.1, -112.1]  # Linear
        self.position_capsule_grab = [241.5, 130.0, 463.5, -140.1, 88.0, -52.5]  # Linear

    # Robot init
    def _robot_init(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)
        self._arm.register_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.register_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'register_count_changed_callback'):
            self._arm.register_count_changed_callback(self._count_changed_callback)

    # Register error/warn changed callback
    def _error_warn_changed_callback(self, data):
        if data and data['error_code'] != 0:
            self.alive = False
            self.pprint('err={}, quit'.format(data['error_code']))
            self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)

    # Register state changed callback
    def _state_changed_callback(self, data):
        if data and data['state'] == 4:
            self.alive = False
            self.pprint('state=4, quit')
            self._arm.release_state_changed_callback(self._state_changed_callback)

    # Register count changed callback
    def _count_changed_callback(self, data):
        if self.is_alive:
            self.pprint('counter val: {}'.format(data['count']))

    def _check_code(self, code, label):
        if not self.is_alive or code != 0:
            self.alive = False
            ret1 = self._arm.get_state()
            ret2 = self._arm.get_err_warn_code()
            self.pprint('{}, code={}, connected={}, state={}, error={}, ret1={}. ret2={}'.format(label, code, self._arm.connected, self._arm.state, self._arm.error_code, ret1, ret2))
        return self.is_alive

    @staticmethod
    def pprint(*args, **kwargs):
        try:
            stack_tuple = traceback.extract_stack(limit=2)[0]
            print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
        except:
            print(*args, **kwargs)

    @property
    def arm(self):
        return self._arm

    @property
    def VARS(self):
        return self._vars

    @property
    def FUNCS(self):
        return self._funcs

    @property
    def is_alive(self):
        if self.alive and self._arm.connected and self._arm.error_code == 0:
            if self._arm.state == 5:
                cnt = 0
                while self._arm.state == 5 and cnt < 5:
                    cnt += 1
                    time.sleep(0.1)
            return self._arm.state < 4
        else:
            return False


    def socket_connect(self):
        # socket 연결 with CV server (연결 될때까지 지속적 시도.)
        self.HOST = '192.168.0.17'
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
                print(f'[LISTENING] Server is listening on robot_server')
                time.sleep(1)
                while True:
                    try:
                        self.clientSocket, addr_info = self.serverSocket.accept()
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
        self.state = 'ready'

        # 지속적으로 메시지 수령.
        while self.connected:
            print("메시지 대기 중...")
            time.sleep(0.5)
            
            try:
                # 대기 시간 설정
                self.clientSocket.settimeout(10.0)
                # 메시지 수령
                self.recv_msg = self.clientSocket.recv(self.BUFSIZE).decode('utf-8')
                print('received msg : ' + self.recv_msg)
                
                
                # 메시지가 비어 있는 경우. 연결이 끊겼으므로 재연결을 위해 예외 처리
                if self.recv_msg == '':
                        print('received empty msg')
                        raise Exception('empty msg')

                self.recv_msg = self.recv_msg.split('/')

                

                # 어떤 메시지를 받을 수 있는지 생각해봐야할 듯
                if self.recv_msg[0] in ['test', 'test_stop', 'icecream']:
                    # 받은 메시지 타입 확인
                    print(f'message type : {self.recv_msg[0]}')
                    
                    # 로봇이 ready 상태라면 받은 메시지에 맞춰 상태 변경
                    if self.state == 'ready':
                        self.state = self.recv_msg[0]
                    
                    # 아이스크림 추출 메시지를 받았다면 관련 정보들을 order_msg로 저장
                    if self.recv_msg[0] == 'icecream':
                        # 문자열 -> json 
                        temp = json.loads(self.recv_msg[1])
                        # 주문 queue에 넣음
                        self.order_msg_queue.put(temp)

                    

                # 추후 비상 정지 / 중단 / 작동 재개를 위한 코드.
                elif self.recv_msg[0] == 'robot_stop':
                        code = self._arm.set_state(4)
                        if not self._check_code(code, 'set_state'):
                            return
                        sys.exit()
                        self.is_alive = False
                        print('Robot stop & program exit')
                elif self.recv_msg[0] == 'robot_pause':
                        code = self._arm.set_state(3)
                        if not self._check_code(code, 'set_state'):
                            return
                        print('Robot pause')
                elif self.recv_msg[0] == 'robot_resume':
                        code = self._arm.set_state(0)
                        if not self._check_code(code, 'set_state'):
                            return
                        print('Robot resume')
                else:
                    self.clientSocket.send('ERROR : wrong msg received'.encode('utf-8'))
                    print('got unexpected msg!')
                
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

        

    def motion_home(self):
        # cup dispenser 잠금
        code = self._arm.set_cgpio_analog(0, 5)
        if not self._check_code(code, 'set_cgpio_analog'):
            return
        code = self._arm.set_cgpio_analog(1, 5)
        if not self._check_code(code, 'set_cgpio_analog'):
            return
        time.sleep(1)

        # gripper 닫음
        code = self._arm.close_lite6_gripper()
        if not self._check_code(code, 'close_lite6_gripper'):
            return
        time.sleep(1)
        code = self._arm.stop_lite6_gripper()
        if not self._check_code(code, 'stop_lite6_gripper'):
            return
        
        # press_up
        code = self._arm.set_cgpio_digital(3, 0, delay_sec=0)
        if not self._check_code(code, 'set_cgpio_digital'):
            return

        # Joint Motion
        self._angle_speed = 80
        self._angle_acc = 200
        try:
            self.clientSocket.send('motion_home_start'.encode('utf-8'))
        except:
            print('socket error')
        print('motion_home start')
        code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        print('motion_home finish')
        try:
            self.clientSocket.send('motion_home_finish'.encode('utf-8'))
        except:
            print('socket error')

    def motion_grab_capsule(self):
        # Motion speed
        self._angle_speed = 100
        self._angle_acc = 100

        self._tcp_speed = 100
        self._tcp_acc = 1000

        try:
            self.clientSocket.send('motion_grab_capsule_start'.encode('utf-8'))
        except:
            print('socket error')

        # # capsule jig으로 이동 (2번째 스테이션 뒤)
        # motion_point_jig 에서 진행
        # code = self._arm.set_servo_angle(angle=[166.1, 30.2, 25.3, 75.3, 93.9, -5.4], speed=self._angle_speed,
        #                                     mvacc=self._angle_acc, wait=True, radius=30.0)
        # if not self._check_code(code, 'set_servo_angle'):
        #     return

        # gripper 열기
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, 'open_lite6_gripper'):
            return
        time.sleep(1)
        

        # 어느 jig이냐에 따라 각 jig으로 이동
        if self.jig == 'A':
            # # A jig 방향 바라보기
            # motion_point_jig 에서 진행
            # code = self._arm.set_servo_angle(angle=[179.5, 33.5, 32.7, 113.0, 93.1, -2.3], speed=self._angle_speed,
            #                                  mvacc=self._angle_acc, wait=True, radius=20.0)
            # if not self._check_code(code, 'set_servo_angle'):
            #     return

            # A jig capsule grab 준비
            code = self._arm.set_servo_angle(angle=[179.5, 33.5, 32.7, 113.0, 93.1, -2.3], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=20.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            
            # A jig capsule grab
            code = self._arm.set_position(*self.position_jig_A_grab, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return

        elif self.jig == 'B':
            # B jig capsule grab 준비
            code = self._arm.set_servo_angle(angle=[166.1, 30.2, 25.3, 75.3, 93.9, -5.4], speed=self._angle_speed,
                                                mvacc=self._angle_acc, wait=True, radius=30.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            
            # B jig capsule grab
            code = self._arm.set_position(*self.position_jig_B_grab, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return

        elif self.jig == 'C':
            # # C jig 방향 바라보기
            # motion_point_jig 에서 진행
            # code = self._arm.set_servo_angle(angle=[182.6, 27.8, 27.7, 55.7, 90.4, -6.4], speed=self._angle_speed,
            #                                  mvacc=self._angle_acc, wait=True, radius=20.0)
            # if not self._check_code(code, 'set_servo_angle'):
            #     return

            # C jig capsule grab 준비
            code = self._arm.set_servo_angle(angle=[182.6, 27.8, 27.7, 55.7, 90.4, -6.4], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=20.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            
            # C jig capsule grab
            code = self._arm.set_position(*self.position_jig_C_grab, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return

        # gripper 닫기
        code = self._arm.close_lite6_gripper()
        if not self._check_code(code, 'close_lite6_gripper'):
            return
        time.sleep(1)
        # gripper 정지 (capsule이 놓아지는 문제가 발생한다면 삭제)
        # code = self._arm.stop_lite6_gripper()
        # if not self._check_code(code, 'stop_lite6_gripper'):
        #     return
        
        # capsule 잡은 후 들어올리기
        if self.jig == 'C':
            code = self._arm.set_position(z=150, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                          wait=False)
            if not self._check_code(code, 'set_position'):
                return
            self._tcp_speed = 200
            self._tcp_acc = 1000
            # gripper 방향 틀어주기
            code = self._arm.set_tool_position(*[0.0, 0.0, -90.0, 0.0, 0.0, 0.0], speed=self._tcp_speed,
                                               mvacc=self._tcp_acc, wait=False)
            if not self._check_code(code, 'set_position'):
                return
        else:
            code = self._arm.set_position(z=100, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                          wait=True)
            if not self._check_code(code, 'set_position'):
                return

        self._angle_speed = 180
        self._angle_acc = 500

        # sealing 확인 위치로 이동
        code = self._arm.set_servo_angle(angle=[146.1, -10.7, 10.9, 102.7, 92.4, 24.9], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        try:
            self.clientSocket.send('motion_grab_capsule_finish'.encode('utf-8'))
        except:
            print('socket error')

    def motion_check_sealing(self):
        print('sealing check')
        self._angle_speed = 200
        self._angle_acc = 200
        # self.clientSocket.send('motion_sheck_sealing'.encode('utf-8'))
        code = self._arm.set_position(*self.position_sealing_check, speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        time.sleep(1)

    def motion_place_capsule(self):
        try:
            self.clientSocket.send('motion_place_capsule_start'.encode('utf-8'))
        except:
            print('socket error')
        
        # 아이스크림 기계에 박지 않게 밑으로 돌아 이동
        code = self._arm.set_servo_angle(angle=[81.0, -10.8, 6.9, 103.6, 88.6, 9.6], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=40.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[10, -20.8, 7.1, 106.7, 79.9, 26.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=50.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[8.4, -42.7, 23.7, 177.4, 31.6, 3.6], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=40.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[8.4, -32.1, 55.1, 96.6, 29.5, 81.9], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        
        # 프레스 밑 공간에 capsule 배치
        code = self._arm.set_position(*self.position_before_capsule_place, speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        code = self._arm.set_position(*self.position_capsule_place, speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
    
        # gripper 열어서 capsule 놓기
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, 'open_lite6_gripper'):
            return
        time.sleep(2)
        code = self._arm.stop_lite6_gripper()
        if not self._check_code(code, 'stop_lite6_gripper'):
            return
        time.sleep(0.5)

        # 프레스 밑 공간에서 팔 빼기
        code = self._arm.set_position(*[233.4, 15.3, 471.1, -172.2, 87.3, -84.5], speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=20.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return

        try:
            self.clientSocket.send('motion_place_capsule_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)

    def motion_grab_cup(self):
        try:
            self.clientSocket.send('motion_grab_cup_start'.encode('utf-8'))
        except:
            print('socket error')

        # dispenser 열기
        code = self._arm.set_cgpio_analog(0, 0)
        if not self._check_code(code, 'set_cgpio_analog'):
            return
        code = self._arm.set_cgpio_analog(1, 5)
        if not self._check_code(code, 'set_cgpio_analog'):
            return
        time.sleep(0.5)
        # # dispenser 닫기
        # code = self._arm.set_cgpio_analog(0, 5)
        # if not self._check_code(code, 'set_cgpio_analog'):
        #     return
        # code = self._arm.set_cgpio_analog(1, 5)
        # if not self._check_code(code, 'set_cgpio_analog'):
        #     return

        # cup 향해 로봇팔 이동
        code = self._arm.set_servo_angle(angle=[-16.2, -33.2, 47.4, 64.7, 18.6, 44.8], speed=self._angle_speed, mvacc=self._angle_acc, wait=True, radius=20.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        
        # gripper 열기
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, 'open_lite6_gripper'):
            return
        time.sleep(1)

        # cup 집기
        code = self._arm.set_servo_angle(angle=[-2.8, -2.5, 45.3, 119.8, -79.2, -18.8], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=30.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_position(*[195.0, -96.5, 200.8, -168.0, -87.1, -110.5], speed=self._tcp_speed,
                                        mvacc=self._tcp_acc, radius=10.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        code = self._arm.set_position(*self.position_cup_grab, speed=self._tcp_speed,
                                        mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        code = self._arm.close_lite6_gripper()
        if not self._check_code(code, 'close_lite6_gripper'):
            return
        time.sleep(2)

        # cup 집은 후 위로 올리기
        code = self._arm.set_position(z=120, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                      wait=True)
        if not self._check_code(code, 'set_position'):
            return
        # 토핑 또는 아이스크림 받기 전 마지막 위치
        code = self._arm.set_servo_angle(angle=[2.9, -31.0, 33.2, 125.4, -30.4, -47.2], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return

        

        try:
            self.clientSocket.send('motion_grab_cup_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)

    def motion_make_icecream(self):
        try:
            self.clientSocket.send('motion_make_icecream_start'.encode('utf-8'))
        except:
            print('socket error')
        
        # 프레스 누르기
        code = self._arm.set_cgpio_digital(3, 1, delay_sec=0)
        if not self._check_code(code, 'set_cgpio_digital'):
            return

        # topping 위 아래 선택에 따라 시간 변화
        # if self.order_msg['makeReq']['topping'] == 'bottom':
        #     time.sleep(5)
        # else:
        #     time.sleep(8)

        time.sleep(8)
        # 컵 밑으로 조금씩 내려가며 아이스크림 cup에 받기 (topping on top 기준 8+4+4+1 걸리는 듯)
        try:
            self.clientSocket.send('motion_icecreaming_1'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(4) # 4초 누르기
        code = self._arm.set_position(z=-20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                      wait=True)
        if not self._check_code(code, 'set_position'):
            return
        try:
            self.clientSocket.send('motion_icecreaming_2'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(4)
        code = self._arm.set_position(z=-10, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                      wait=True)
        if not self._check_code(code, 'set_position'):
            return
        # 이 부분 왜 있지? 멈추지 않나? 확인 필요.
        if not self._check_code(code, 'set_pause_time'):
            return
        try:
            self.clientSocket.send('motion_icecreaming_3'.encode('utf-8'))
        except:
            print('socket error')
        code = self._arm.set_position(z=-50, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                      wait=True)
        if not self._check_code(code, 'set_position'):
            return
        time.sleep(1)

        # 프레스 멈추기
        code = self._arm.set_cgpio_digital(3, 0, delay_sec=0)
        if not self._check_code(code, 'set_cgpio_digital'):
            return
        try:
            self.clientSocket.send('motion_make_icecream_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)

        # topping을 받지 않는다면 서빙 위치로 이동
        if self.topping_no == True:
            code = self._arm.set_servo_angle(angle=[35.2, -24.5, 11.4, 115.7, 74.0, 32.1], speed=self._angle_speed, mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            code = self._arm.set_servo_angle(angle=[65.4, -13.3, 4.0, 114.0, 82.1, 15.8], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=False, radius=20.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            code = self._arm.set_servo_angle(angle=[108.4, -10.8, 9.0, 128.5, 76.2, 13.6], speed=self._angle_speed,
                                                mvacc=self._angle_acc, wait=False, radius=20.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            code = self._arm.set_servo_angle(angle=[145.9, 19.4, 32.4, 90.4, 88.8, 9.4], speed=self._angle_speed,
                                                mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            code = self._arm.set_position(*[-180.7, 9.8, 225.6, -60.0, 85.8, -149.4], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=False)
            if not self._check_code(code, 'set_position'):
                return

    def motion_topping(self):
        try:
            self.clientSocket.send('motion_topping_start'.encode('utf-8'))
        except:
            print('socket error')
        print('send')

        self.topping_time_A = 0.0
        self.topping_time_B = 0.0
        self.topping_time_C = 0.0
        # 각 토핑을 얼마나 받는지 결정
        if self.topping == '111':
            self.topping_time_A = self.topping_time / 3.0
            self.topping_time_B = self.topping_time / 3.0
            self.topping_time_C = self.topping_time / 3.0
        elif self.topping == '110':
            self.topping_time_A = self.topping_time / 2.0
            self.topping_time_B = self.topping_time / 2.0
        elif self.topping == '101':
            self.topping_time_A = self.topping_time / 2.0
            self.topping_time_C = self.topping_time / 2.0
        elif self.topping == '011':
            self.topping_time_B = self.topping_time / 2.0
            self.topping_time_C = self.topping_time / 2.0
        elif self.topping == '100':
            self.topping_time_A = self.topping_time
        elif self.topping == '010':
            self.topping_time_B = self.topping_time
        elif self.topping == '001':
            self.topping_time_C = self.topping_time


        # topping을 먼저 받는지 나중에 받는지
        if self.topping_first == True: # 먼저 받는 경우
            # topping 위치로 이동
            code = self._arm.set_servo_angle(angle=[36.6, -36.7, 21.1, 85.6, 59.4, 44.5], speed=self._angle_speed,
                                             mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            # topping custom
            if self.topping_time_C > 0.0:
                # C topping 위치로 이동
                code = self._arm.set_position(*self.position_topping_C, speed=self._tcp_speed,
                                                mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                # 아이스크림이 없으니 살짝 위로 올리기
                code = self._arm.set_position(z=20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                              wait=False)
                if not self._check_code(code, 'set_position'):
                    return
                # C topping 시작
                code = self._arm.set_cgpio_digital(2, 1, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                # C topping 양 설정
                code = self._arm.set_pause_time(self.topping_time_C)
                if not self._check_code(code, 'set_pause_time'):
                    return
                # C topping 끝
                code = self._arm.set_cgpio_digital(2, 0, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                time.sleep(1)
                # 올린 만큼 밑으로 내리기
                code = self._arm.set_position(z=-20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc,
                                              relative=True, wait=False)
                if not self._check_code(code, 'set_position'):
                    return
            # B topping 위치로 이동
            code = self._arm.set_servo_angle(angle=[55.8, -48.2, 14.8, 86.1, 60.2, 58.7], speed=self._angle_speed,
                                                mvacc=self._angle_acc, wait=False, radius=20.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            if self.topping_time_B > 0.0:
                code = self._arm.set_servo_angle(angle=self.position_topping_B, speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                # 아이스크림이 없으니 살짝 위로 올리기
                code = self._arm.set_position(z=20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                              wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                # B topping 시작
                code = self._arm.set_cgpio_digital(1, 1, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                code = self._arm.set_pause_time(self.topping_time_B)
                if not self._check_code(code, 'set_pause_time'):
                    return
                # B topping 끝
                code = self._arm.set_cgpio_digital(1, 0, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                time.sleep(1)
                code = self._arm.set_position(z=-20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc,
                                              relative=True, wait=False)
                if not self._check_code(code, 'set_position'):
                    return
            if self.topping_time_A > 0.0:
                code = self._arm.set_position(*self.position_topping_A, speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_cgpio_digital(0, 1, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                code = self._arm.set_pause_time(self.topping_time_A)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_cgpio_digital(0, 0, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                time.sleep(1)
                code = self._arm.set_servo_angle(angle=[130.0, -33.1, 12.5, 194.3, 51.0, 0.0], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_position(*[-38.2, 132.2, 333.9, -112.9, 86.3, -6.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=10.0, wait=False)
                if not self._check_code(code, 'set_position'):
                    return
            # 아이스크림 받기 전 위치로 이동 (topping first)
            code = self._arm.set_position(*[43.6, 137.9, 350.1, -92.8, 87.5, 5.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=10.0, wait=False)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_position(*self.position_icecream_with_topping, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            
        elif self.topping_first == False:
            code = self._arm.set_servo_angle(angle=[35.2, -24.5, 11.4, 115.7, 74.0, 32.1], speed=self._angle_speed, mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return

            if self.topping_time_C > 0.0:
                code = self._arm.set_position(*self.position_topping_C_later, speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_cgpio_digital(2, 1, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                code = self._arm.set_pause_time(self.topping_time_C)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_cgpio_digital(2, 0, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                time.sleep(1)
            code = self._arm.set_servo_angle(angle=[65.4, -13.3, 4.0, 114.0, 82.1, 15.8], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=False, radius=20.0)
            if not self._check_code(code, 'set_servo_angle'):
                return

            if self.topping_time_B > 0.0:
                code = self._arm.set_position(*self.position_topping_B_later, speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_cgpio_digital(1, 1, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                code = self._arm.set_pause_time(self.topping_time_B)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_cgpio_digital(1, 0, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                time.sleep(1)
            code = self._arm.set_servo_angle(angle=[108.4, -10.8, 9.0, 128.5, 76.2, 13.6], speed=self._angle_speed, mvacc=self._angle_acc, wait=False, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            
            if self.topping_time_A > 0.0:
                code = self._arm.set_position(*self.position_topping_A_later, speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                # topping A 받기
                code = self._arm.set_cgpio_digital(0, 1, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                code = self._arm.set_pause_time(self.topping_time_A)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_cgpio_digital(0, 0, delay_sec=0)
                if not self._check_code(code, 'set_cgpio_digital'):
                    return
                time.sleep(1)
            # 서빙 위치 방향으로 이동
            code = self._arm.set_servo_angle(angle=[145.9, 19.4, 32.4, 90.4, 88.8, 9.4], speed=self._angle_speed, mvacc=self._angle_acc, wait=False, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return

            # # topping no custom. only one topping.
            # # C topping 인 경우
            # if self.topping == 'C':
            #     # C topping 위치로 이동
            #     code = self._arm.set_position(*self.position_topping_C, speed=self._tcp_speed,
            #                                   mvacc=self._tcp_acc, radius=0.0, wait=True)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     # 아이스크림이 없으니 살짝 위로 올리기
            #     code = self._arm.set_position(z=20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
            #                                   wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     # C topping 시작
            #     code = self._arm.set_cgpio_digital(2, 1, delay_sec=0)
            #     if not self._check_code(code, 'set_cgpio_digital'):
            #         return
            #     # topping 양 설정 (topping 시간은 나중에 조정)
            #     code = self._arm.set_pause_time(self.topping_time)
            #     if not self._check_code(code, 'set_pause_time'):
            #         return
            #     # C topping 끝
            #     code = self._arm.set_cgpio_digital(2, 0, delay_sec=0)
            #     if not self._check_code(code, 'set_cgpio_digital'):
            #         return
            #     time.sleep(1)

            #     # 올린 만큼 밑으로 내리기
            #     code = self._arm.set_position(z=-20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc,
            #                                   relative=True, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return

            # elif self.topping == 'B':
            #     # B topping 위치로 이동
            #     code = self._arm.set_servo_angle(angle=[55.8, -48.2, 14.8, 86.1, 60.2, 58.7], speed=self._angle_speed,
            #                                      mvacc=self._angle_acc, wait=False, radius=20.0)
            #     if not self._check_code(code, 'set_servo_angle'):
            #         return
            #     code = self._arm.set_servo_angle(angle=self.position_topping_B, speed=self._angle_speed,
            #                                      mvacc=self._angle_acc, wait=True, radius=0.0)
            #     if not self._check_code(code, 'set_servo_angle'):
            #         return
            #     # 아이스크림이 없으니 살짝 위로 올리기
            #     code = self._arm.set_position(z=20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
            #                                   wait=True)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     # B topping 시작
            #     code = self._arm.set_cgpio_digital(1, 1, delay_sec=0)
            #     if not self._check_code(code, 'set_cgpio_digital'):
            #         return
            #     code = self._arm.set_pause_time(self.topping_time)
            #     if not self._check_code(code, 'set_pause_time'):
            #         return
            #     # B topping 끝
            #     code = self._arm.set_cgpio_digital(1, 0, delay_sec=0)
            #     if not self._check_code(code, 'set_cgpio_digital'):
            #         return
            #     time.sleep(1)

            #     code = self._arm.set_position(z=-20, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc,
            #                                   relative=True, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     # 아이스크림 기계 방향으로 이동
            #     code = self._arm.set_servo_angle(angle=[87.5, -48.2, 13.5, 125.1, 44.5, 46.2], speed=self._angle_speed,
            #                                      mvacc=self._angle_acc, wait=False, radius=10.0)
            #     if not self._check_code(code, 'set_servo_angle'):
            #         return
            #     code = self._arm.set_position(*[43.6, 137.9, 350.1, -92.8, 87.5, 5.3], speed=self._tcp_speed,
            #                                   mvacc=self._tcp_acc, radius=10.0, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return

            # elif self.topping == 'A':
            #     code = self._arm.set_position(*self.position_topping_A, speed=self._tcp_speed,
            #                                   mvacc=self._tcp_acc, radius=0.0, wait=True)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     code = self._arm.set_cgpio_digital(0, 1, delay_sec=0)
            #     if not self._check_code(code, 'set_cgpio_digital'):
            #         return
            #     code = self._arm.set_pause_time(self.topping_time)
            #     if not self._check_code(code, 'set_pause_time'):
            #         return
            #     code = self._arm.set_cgpio_digital(0, 0, delay_sec=0)
            #     if not self._check_code(code, 'set_cgpio_digital'):
            #         return
            #     time.sleep(1)
            #     code = self._arm.set_servo_angle(angle=[130.0, -33.1, 12.5, 194.3, 51.0, 0.0], speed=self._angle_speed,
            #                                      mvacc=self._angle_acc, wait=True, radius=0.0)
            #     if not self._check_code(code, 'set_servo_angle'):
            #         return
            #     code = self._arm.set_position(*[-38.2, 132.2, 333.9, -112.9, 86.3, -6.6], speed=self._tcp_speed,
            #                                   mvacc=self._tcp_acc, radius=10.0, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     code = self._arm.set_position(*[43.6, 137.9, 350.1, -92.8, 87.5, 5.3], speed=self._tcp_speed,
            #                                   mvacc=self._tcp_acc, radius=10.0, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return

            # # 아이스크림 받기 전 위치로 이동 (topping first)
            # code = self._arm.set_position(*self.position_icecream_with_topping, speed=self._tcp_speed,
            #                               mvacc=self._tcp_acc, radius=0.0, wait=True)
            # if not self._check_code(code, 'set_position'):
            #     return

        # elif self.topping_first == False:
        #     code = self._arm.set_servo_angle(angle=[35.2, -24.5, 11.4, 115.7, 74.0, 32.1], speed=self._angle_speed, mvacc=self._angle_acc, wait=True, radius=0.0)
        #     if not self._check_code(code, 'set_servo_angle'):
        #         return

        #     if self.topping == 'A':
        #         # topping 받으러 이동
        #         code = self._arm.set_position(*self.position_topping_C_later, speed=self._tcp_speed,
        #                                       mvacc=self._tcp_acc, radius=0.0, wait=True)
        #         if not self._check_code(code, 'set_position'):
        #             return
        #         code = self._arm.set_position(*self.position_topping_B_later, speed=self._tcp_speed,
        #                                       mvacc=self._tcp_acc, radius=0.0, wait=True)
        #         if not self._check_code(code, 'set_position'):
        #             return
        #         code = self._arm.set_position(*self.position_topping_A_later, speed=self._tcp_speed,
        #                                       mvacc=self._tcp_acc, radius=0.0, wait=True)
        #         if not self._check_code(code, 'set_position'):
        #             return
        #         # topping A 받기
        #         code = self._arm.set_cgpio_digital(0, 1, delay_sec=0)
        #         if not self._check_code(code, 'set_cgpio_digital'):
        #             return
        #         code = self._arm.set_pause_time(self.topping_time)
        #         if not self._check_code(code, 'set_pause_time'):
        #             return
        #         code = self._arm.set_cgpio_digital(0, 0, delay_sec=0)
        #         if not self._check_code(code, 'set_cgpio_digital'):
        #             return
        #         time.sleep(1)
        #         # 서빙 위치 방향으로 이동
        #         code = self._arm.set_servo_angle(angle=[145.9, 19.4, 32.4, 90.4, 88.8, 9.4], speed=self._angle_speed, mvacc=self._angle_acc, wait=False, radius=0.0)
        #         if not self._check_code(code, 'set_servo_angle'):
        #             return

        #     elif self.topping == 'B':
        #         code = self._arm.set_position(*self.position_topping_C_later, speed=self._tcp_speed,
        #                                       mvacc=self._tcp_acc, radius=0.0, wait=True)
        #         if not self._check_code(code, 'set_position'):
        #             return
        #         code = self._arm.set_position(*self.position_topping_B_later, speed=self._tcp_speed,
        #                                       mvacc=self._tcp_acc, radius=0.0, wait=True)
        #         if not self._check_code(code, 'set_position'):
        #             return
        #         code = self._arm.set_cgpio_digital(1, 1, delay_sec=0)
        #         if not self._check_code(code, 'set_cgpio_digital'):
        #             return
        #         code = self._arm.set_pause_time(self.topping_time)
        #         if not self._check_code(code, 'set_pause_time'):
        #             return
        #         code = self._arm.set_cgpio_digital(1, 0, delay_sec=0)
        #         if not self._check_code(code, 'set_cgpio_digital'):
        #             return
        #         time.sleep(1)
        #         code = self._arm.set_servo_angle(angle=[108.4, -10.8, 9.0, 128.5, 76.2, 13.6], speed=self._angle_speed, mvacc=self._angle_acc, wait=False, radius=0.0)
        #         if not self._check_code(code, 'set_servo_angle'):
        #             return
        #         code = self._arm.set_servo_angle(angle=[145.9, 19.4, 32.4, 90.4, 88.8, 9.4], speed=self._angle_speed, mvacc=self._angle_acc, wait=False, radius=0.0)
        #         if not self._check_code(code, 'set_servo_angle'):
        #             return

        #     elif self.topping == 'C':
        #         code = self._arm.set_position(*self.position_topping_C_later, speed=self._tcp_speed,
        #                                       mvacc=self._tcp_acc, radius=0.0, wait=True)
        #         if not self._check_code(code, 'set_position'):
        #             return

        #         code = self._arm.set_cgpio_digital(2, 1, delay_sec=0)
        #         if not self._check_code(code, 'set_cgpio_digital'):
        #             return
        #         code = self._arm.set_pause_time(self.topping_time)
        #         if not self._check_code(code, 'set_pause_time'):
        #             return
        #         code = self._arm.set_cgpio_digital(2, 0, delay_sec=0)
        #         if not self._check_code(code, 'set_cgpio_digital'):
        #             return
        #         time.sleep(1)

        #         code = self._arm.set_servo_angle(angle=[65.4, -13.3, 4.0, 114.0, 82.1, 15.8], speed=self._angle_speed,
        #                                          mvacc=self._angle_acc, wait=False, radius=20.0)
        #         if not self._check_code(code, 'set_servo_angle'):
        #             return
        #         code = self._arm.set_servo_angle(angle=[108.4, -10.8, 9.0, 128.5, 76.2, 13.6], speed=self._angle_speed,
        #                                          mvacc=self._angle_acc, wait=False, radius=20.0)
        #         if not self._check_code(code, 'set_servo_angle'):
        #             return
        #         code = self._arm.set_servo_angle(angle=[145.9, 19.4, 32.4, 90.4, 88.8, 9.4], speed=self._angle_speed,
        #                                          mvacc=self._angle_acc, wait=True, radius=0.0)
        #         if not self._check_code(code, 'set_servo_angle'):
        #             return
        #     # 서빙 전 위치로 이동
        #     code = self._arm.set_position(*[-180.7, 9.8, 225.6, -60.0, 85.8, -149.4], speed=self._tcp_speed,
        #                                   mvacc=self._tcp_acc, radius=0.0, wait=False)
        #     if not self._check_code(code, 'set_position'):
        #         return

        try:
            self.clientSocket.send('motion_topping_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)

    def motion_topping_pass(self):
        try:
            self.clientSocket.send('motion_topping_pass_start'.encode('utf-8'))
        except:
            print('socket error')
        
        # cup을 프레스 밑에 가져가기
        code = self._arm.set_servo_angle(angle=self.position_icecream_no_topping, speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return

        try:
            self.clientSocket.send('motion_topping_pass_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)

    def motion_serve(self):
        try:
            self.clientSocket.send('motion_serve_start'.encode('utf-8'))
        except:
            print('socket error')

        self._tcp_speed = 100
        self._tcp_acc = 1000

        # jig에 따라
        if self.jig == 'A':
            code = self._arm.set_position(*self.position_jig_A_serve, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return

            code = self._arm.set_position(z=-18, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                          wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.open_lite6_gripper()
            if not self._check_code(code, 'open_lite6_gripper'):
                return
            time.sleep(1)
            code = self._arm.set_position(*[-256.2, -126.6, 210.1, -179.2, 77.2, 66.9], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.stop_lite6_gripper()
            if not self._check_code(code, 'stop_lite6_gripper'):
                return
            time.sleep(0.5)
            code = self._arm.set_position(*[-242.8, -96.3, 210.5, -179.2, 77.2, 66.9], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_position(*[-189.7, -26.0, 193.3, -28.1, 88.8, -146.0], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return

        elif self.jig == 'B':
            code = self._arm.set_position(*self.position_jig_B_serve, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=False)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_position(z=-15, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                          wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.open_lite6_gripper()
            if not self._check_code(code, 'open_lite6_gripper'):
                return
            time.sleep(1)
            code = self._arm.set_position(*[-165.0, -122.7, 200, -178.7, 80.7, 92.5], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.stop_lite6_gripper()
            if not self._check_code(code, 'stop_lite6_gripper'):
                return
            time.sleep(0.5)
            code = self._arm.set_position(*[-165.9, -81.9, 200, -178.7, 80.7, 92.5], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_position(*[-168.5, -33.2, 192.8, -92.9, 86.8, -179.3], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
        elif self.jig == 'C':
            code = self._arm.set_servo_angle(angle=[177.6, 0.2, 13.5, 70.0, 94.9, 13.8], speed=self._angle_speed,
                                             mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            code = self._arm.set_position(*self.position_jig_C_serve, speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_position(z=-12, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                          wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.open_lite6_gripper()
            if not self._check_code(code, 'open_lite6_gripper'):
                return
            time.sleep(1)
            code = self._arm.set_position(*[-78.5, -132.8, 208, -176.8, 76.1, 123.0], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.stop_lite6_gripper()
            if not self._check_code(code, 'stop_lite6_gripper'):
                return
            time.sleep(0.5)
            code = self._arm.set_position(*[-93.0, -107.5, 208, -176.8, 76.1, 123.0], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_position(*[-98.1, -52.1, 191.4, -68.4, 86.4, -135.0], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
            if not self._check_code(code, 'set_position'):
                return
        
        # 이동하기에 안전한 위치로 이동
        code = self._arm.set_position(*[-168.5, -33.2, 232.8, -92.9, 86.8, -179.3], speed=self._tcp_speed,
                                          mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        
        try:
            self.clientSocket.send('motion_serve_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)

        # 정위치
        code = self._arm.set_servo_angle(angle=[169.6, -8.7, 13.8, 85.8, 93.7, 19.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=10.0)
        if not self._check_code(code, 'set_servo_angle'):
            return


    def motion_trash_capsule(self):
        try:
            self.clientSocket.send('motion_trash_start'.encode('utf-8'))
        except:
            print('socket error')
        self._tcp_speed = 100
        self._tcp_acc = 1000
        self._angle_speed = 150
        self._angle_acc = 100
        # 빈 capsule 향해 이동
        code = self._arm.set_servo_angle(angle=[51.2, -8.7, 13.8, 95.0, 86.0, 17.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=50.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[-16.2, -19.3, 42.7, 82.0, 89.1, 55.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, 'open_lite6_gripper'):
            return
        code = self._arm.set_servo_angle(angle=[-19.9, -19.1, 48.7, 87.2, 98.7, 60.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        # capsule 앞
        code = self._arm.set_position(*[222.8, 0.9, 470.0, -153.7, 87.3, -68.7], speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        # capsule 집기
        code = self._arm.set_position(*self.position_capsule_grab, speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        code = self._arm.close_lite6_gripper()
        if not self._check_code(code, 'close_lite6_gripper'):
            return
        time.sleep(1)
        # capsule 들기
        code = self._arm.set_position(z=30, radius=-1, speed=self._tcp_speed, mvacc=self._tcp_acc, relative=True,
                                      wait=True)
        if not self._check_code(code, 'set_position'):
            return
        self._tcp_speed = 100
        self._tcp_acc = 1000
        # 빼기
        code = self._arm.set_position(*[221.9, -5.5, 500.4, -153.7, 87.3, -68.7], speed=self._tcp_speed,
                                      mvacc=self._tcp_acc, radius=0.0, wait=True)
        if not self._check_code(code, 'set_position'):
            return
        # 쓰레기 통으로 가져가기
        self._angle_speed = 60
        self._angle_acc = 100
        code = self._arm.set_servo_angle(angle=[-10.7, -2.4, 53.5, 50.4, 78.1, 63.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=10.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        self._angle_speed = 150
        self._angle_acc = 100
        code = self._arm.set_servo_angle(angle=[18.0, 11.2, 40.4, 90.4, 58.7, -148.8], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, 'open_lite6_gripper'):
            return
        time.sleep(1)
        # 버리기
        code = self._arm.set_servo_angle(angle=[25.2, 15.2, 42.7, 83.2, 35.0, -139.8], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[18.0, 11.2, 40.4, 90.4, 58.7, -148.8], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[25.2, 15.2, 42.7, 83.2, 35.0, -139.8], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.stop_lite6_gripper()
        if not self._check_code(code, 'stop_lite6_gripper'):
            return
        # motion home으로 복귀
        self._angle_speed = 150
        self._angle_acc = 100
        code = self._arm.set_servo_angle(angle=[28.3, -9.0, 12.6, 85.9, 78.5, 20.0], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=30.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=[149.3, -9.4, 10.9, 114.7, 69.1, 26.1], speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=False, radius=50.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        try:
            self.clientSocket.send('motion_trash_finish'.encode('utf-8'))
        except:
            print('socket error')
        time.sleep(0.5)


    # custom code.
    # 어느 jig에 놓을 것인지 안내하는 모션
    def motion_point_jig(self):
        # Motion speed
        self._angle_speed = 100
        self._angle_acc = 100

        self._tcp_speed = 100
        self._tcp_acc = 1000

        point_num = 5

        try:
            self.clientSocket.send('motion_point_jig_start'.encode('utf-8'))
        except:
            print('socket error')

        # capsule jig으로 이동 (2번째 스테이션 뒤)
        code = self._arm.set_servo_angle(angle=[166.1, 30.2, 25.3, 75.3, 93.9, 90.0], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=30.0)
        if not self._check_code(code, 'set_servo_angle'):
            return

        # 어느 jig이냐에 따라 각 jig으로 이동
        if self.jig == 'A':
            # A jig 방향 포인트
            for i in range(point_num):
                code = self._arm.set_servo_angle(angle=[179.5, 33.5, 32.7, 113.0, 98.1, 90.0], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=False, radius=20.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_servo_angle(angle=[179.5, 33.5, 32.7, 113.0, 88.1, 90.0], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=False, radius=20.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return

        elif self.jig == 'B':
            # B jig 방향 포인트
            for i in range(point_num):
                code = self._arm.set_servo_angle(angle=[166.1, 30.2, 25.3, 75.3, 98.9, 90.0], speed=self._angle_speed,
                                                mvacc=self._angle_acc, wait=False, radius=30.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_servo_angle(angle=[166.1, 30.2, 25.3, 75.3, 83.9, 90.0], speed=self._angle_speed,
                                                    mvacc=self._angle_acc, wait=False, radius=30.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return

        elif self.jig == 'C':
            # C jig 방향 포인트
            for i in range(point_num):
                code = self._arm.set_servo_angle(angle=[182.6, 27.8, 27.7, 55.7, 95.4, 90.0], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=False, radius=20.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_servo_angle(angle=[182.6, 27.8, 27.7, 55.7, 85.4, 90.0], speed=self._angle_speed,
                                                mvacc=\
                                                    self._angle_acc, wait=False, radius=20.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return    

        try:
            self.clientSocket.send('motion_point_jig_finish'.encode('utf-8'))
        except:
            print('socket error')
        
    # custom code.
    def motion_point_spoon(self):
        # 좌우앞 3 방향 중 스푼이 있다고 가정하고 각 상황에 맞춰 스푼 위치 안내 모션 (with UI & TTS)
        try:
            self.clientSocket.send('motion_point_spoon_start'.encode('utf-8'))
        except:
            print('socket error')
        
        point_num = 2
        self.spoon_angle = 180.0
        if self.spoon_angle < 180.0 or self.spoon_angle > 355.0:
            print("unexpected angle! set angle to 180.0")
            self.spoon_angle = 180.0
        
        self._angle_speed = 150
        self._angle_acc = 150
        self._tcp_speed = 150
        self._tcp_acc = 300

        code = self._arm.set_servo_angle(angle=[self.spoon_angle, 0.0, 50.0, 186.7, 40.2, 90.0], speed=self._angle_speed,
                                        mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return
        for i in range(point_num):
            code = self._arm.set_tool_position(z=50.0, speed=self._tcp_speed,
                                            mvacc=self._tcp_acc, wait=False)
            if not self._check_code(code, 'set_position'):
                return
            code = self._arm.set_tool_position(z=-50.0, speed=self._tcp_speed,
                                            mvacc=self._tcp_acc, wait=False)
            if not self._check_code(code, 'set_position'):
                return
        time.sleep(1.0)
        code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
                                        mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return

        # if self.spoon_direction == 'R':
            # code = self._arm.set_servo_angle(angle=[179.4, -32.4, 19.4, 187.3, 39.2, 90], speed=self._angle_speed,
            #                              mvacc=self._angle_acc, wait=False, radius=0.0)
            # if not self._check_code(code, 'set_servo_angle'):
            #     return
            # code = self._arm.set_position(x=-200, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, 
            #                               relative=True, wait=False)
            # if not self._check_code(code, 'set_position'):
            #     return
            # for i in range(point_num):
            #     code = self._arm.set_position(x=50, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, 
            #                                 relative=True, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     code = self._arm.set_position(x=-50, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, 
            #                                 relative=True, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            # time.sleep(1.0)
            # code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
            #                              mvacc=self._angle_acc, wait=True, radius=0.0)
            # if not self._check_code(code, 'set_servo_angle'):
            #     return
            
        # elif self.spoon_direction == 'L':
            # code = self._arm.set_servo_angle(angle=[179.4, 30.4, 260.0, 0.0, -39.2, 90], speed=self._angle_speed,
            #                              mvacc=self._angle_acc, wait=False, radius=0.0)
            # if not self._check_code(code, 'set_servo_angle'):
            #     return
            # code = self._arm.set_position(x=200, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, 
            #                               relative=True, wait=False)
            # if not self._check_code(code, 'set_position'):
            #     return
            # for i in range(point_num):
            #     code = self._arm.set_position(x=-50, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, 
            #                                 relative=True, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            #     code = self._arm.set_position(x=50, radius=0, speed=self._tcp_speed, mvacc=self._tcp_acc, 
            #                                 relative=True, wait=False)
            #     if not self._check_code(code, 'set_position'):
            #         return
            # time.sleep(1.0)
            # code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
            #                              mvacc=self._angle_acc, wait=True, radius=0.0)
            # if not self._check_code(code, 'set_servo_angle'):
            #     return
        # elif self.spoon_direction == 'F':
        #     print()


        try:
            self.clientSocket.send('motion_point_spoon_finish'.encode('utf-8'))
        except:
            print('socket error')


    def motion_bye(self):
        print()



    def input_listener(self):
        input()
        self.input_queue.put(True)


    def order_msg_process(self):
        # order_msg를 각 변수에 저장
        self.order_msg = self.order_msg_queue.get()
        self.jig = self.order_msg['jig']
        self.topping_first = self.order_msg['topping_first']
        self.topping_no = self.order_msg['topping_no']
        self.topping = self.order_msg['topping']
        self.topping_time = self.order_msg['topping_time']
        self.spoon_angle = self.order_msg['spoon_angle']

    # Robot Main Run
    def run(self):
        try:
            while self.is_alive:
                time.sleep(1)
                if self.state == 'icecream':
                    ################ icecream의 경우 order_msg 변수의 정보를 이용하여 실행 환경을 설정 #######
                    self.order_msg_process()
                    # self.jig = 'A' # 사용할 jig
                    # self.topping_first = False # 아이스크림보다 토핑을 먼저 받을지 말지. True : 먼저 받음
                    # self.topping_no = False # 토핑 받지 않기
                    # self.topping = 'ABC' # A / B / C / AB / AC / BC / ABC
                    # self.topping_time = 2.0 # 총 토핑 받는 시간 == 토핑 량
                    # self.spoon_direction = 'R' # L(eft) R(ight) F(ront)
                    # self.spoon_angle = 180.0 # Angle 기준

                    # # 신호를 받는 부분이 미구현이므로 인풋 신호 대기로 구현 (추후 변경 필요)
                    # self.input_queue = queue.Queue()
                    # listener_thread = threading.Thread(target=robot_main.input_listener, daemon=False)
                    # listener_thread.start()

                    # self.motion_home() # home 자세 대기
                    # self.motion_point_jig() # capsule 위치시킬 jig 가르키기
                    # while True:
                    #     if not self.input_queue.empty():
                    #         break
                    #     print("캡슐을 "+ self.jig + " jig에 배치하고 엔터 키 입력...")
                    #     time.sleep(3)
                    # self.motion_grab_capsule() # 아이스크림 capsule 잡기
                    # self.motion_check_sealing() # seal 제거 여부 확인하는 장소로 이동
                    # # seal 제거 여부 확인 코드 위치 (예정)
                    # # seal 제거 안함 코드 위치 (예정)
                    # # seal 제거 확인 후 코드 진행
                    # self.motion_place_capsule() # capsule 프레스 밑에 위치시키기
                    # self.motion_grab_cup() # cup 잡기
                    # if self.topping_no == True:
                    #     self.motion_topping_pass()
                    #     self.motion_make_icecream()
                    # else:
                    #     if self.topping_first == True:
                    #         self.motion_topping()
                    #         self.motion_make_icecream()
                    #     else:
                    #         self.motion_topping_pass()
                    #         self.motion_make_icecream()
                    #         self.motion_topping()
                    # self.motion_serve()
                    
                    # # 다음 손님이 있는지 확인
                    # if self.order_msg_queue.empty():
                    #     self.next_customer = False
                    # else:
                    #     self.next_customer = True
                    # # 만약 다음 손님이 없다면.
                    #     # 수저 위치 안내 및 인사
                    # if self.next_customer == False:
                    #     self.motion_point_spoon()
                    #     self.motion_bye()
                    # self.motion_trash_capsule() # 캡슐 껍데기 버리기
                    # self.motion_home() # home 자세 대기

                    time.sleep(5)
                    # 손님이 아이스크림을 수령해갔다고 가정하고 서버에 메시지 보내기
                    try:
                        self.clientSocket.send(('icecream_service_finish/'+self.jig).encode('utf-8'))
                    except:
                        print('socket error')

                    if self.next_customer == True:
                        self.state = 'icecream'
                    else:
                        self.state = 'ready'
                elif self.state == 'test':
                    print('test motion 진입')
                    while True:
                        code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=0.0)
                        if not self._check_code(code, 'set_servo_angle'):
                            return
                        code = self._arm.set_servo_angle(angle=[190.2, -42.1, 7.4, 186.7, 41.5, -1.6], speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=0.0)
                        if not self._check_code(code, 'set_servo_angle'):
                            return
                        if self.state == 'test_stop':
                            code = self._arm.set_servo_angle(angle=self.position_home, speed=self._angle_speed,
                                            mvacc=self._angle_acc, wait=True, radius=0.0)
                            if not self._check_code(code, 'set_servo_angle'):
                                return
                            break

        except Exception as e:
            self.pprint('MainException: {}'.format(e))
        self.alive = False
        self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.release_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'release_count_changed_callback'):
            self._arm.release_count_changed_callback(self._count_changed_callback)


if __name__ == '__main__':
    RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
    arm = XArmAPI('192.168.1.162', baud_checkset=False)
    robot_main = RobotMain(arm)
    # 소켓 통신용 스레드 동작. (지속적으로 메시지를 수령해야하기에.)
    socket_thread = threading.Thread(target=robot_main.socket_connect)
    socket_thread.start()
    print('socket_thread start')    
    # 로봇 서비스 스레드 동작. (수령받은 메시지에 기반하여서 계속 동작해야함.)
    run_thread = threading.Thread(target=robot_main.run)
    run_thread.start()
    print('run_thread_started')