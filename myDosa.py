import keyboard
import win32api
import win32con
import time
import threading
import ctypes, os

REALTIME_PRIORITY_CLASS = 0x00000100
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), REALTIME_PRIORITY_CLASS)


#########################################################################################
############ CONFIG #####################################################################
#########################################################################################

BH_HEAL_INTERVAL = 25.5   # 백호의희원 간격(초) 비활성화를 원하는 경우, '0' 입력,
BH2_HEAL_INTERVAL = 30.5   # 백호의희원'첨 간격(초) 비활성화를 원하는 경우, '0' 입력,
#BH_GAP = BH2_HEAL_INTERVAL/2 # 희원과 희원'첨 사이의 최소 간격
BH_GAP = 1 # 희원과 희원'첨 사이의 최소 간격

MP_REFILL_FREQ = 100     # 공증간격, 액션 N회 후 공증 2회씩. 마력이 부족하면 숫자를 줄일것. 비활성화를 원하는 경우 '0' (추천값 : 마력/10000)

GUMGANG_INTERVAL = 13   # 금강불체 시간간격(추천값:13초). 비활성화를 원하는 경우 '0'
SHIELD_PROTECT_INTERVAL = 186   # 보호 무장 시간간격(추천값:186초). 비활성화를 원하는 경우 '0'

## 아래 키들은 반드시 '숫자' 키에 매핑되어 있어야 합니다.
KEY_HEAL = 3        # 기본 힐 키
KEY_MP_REFILL = 2   # 공력증강 키
KEY_BH_HEAL = 1     # 백호의희원 키
KEY_GUMGANG = 4     # 금강불체 키
KEY_HON = 5         # 혼마술키

## 아래키는 반드시 숫자에 매핑되어 있을필요는 없습니다. 단, 소문자에 할당되어야 합니다.
KEY_BH2_HEAL = "j"     # 백호의희원'첨 키
KEY_REVIVE="g"        # 부활키
#KEY_MP_INJECTION="i"      # 공력주입 키(비활성화)
KEY_SHOUT="s"               # 사자후키
KEY_SHIELD="q"              # 무장 키
KEY_PROTECT="w"             # 보호 키
KEY_POWER_ZONE="h"          # 파력 키

## 사자후 텍스트
CALL_STRING="중입니다"


#########################################################################################

up_pressed = False
down_pressed = False
right_pressed = False
left_pressed = False

f1_pressed = False
f2_pressed = False
f3_pressed = False
f4_pressed = False
f5_pressed = False
f6_pressed = False
f7_pressed = False
f8_pressed = False
f9_pressed = False
f11_pressed = False

grave_pressed = False  # '~' (Grave) 키
pause_pressed = False
eat_pressed = False

running = True  # 프로그램 실행 상태
is_heal_mode=False
is_tabtab_restore=False

def press_key(hexKeyCode, interval=0.02, subkey=0):
    if subkey!=0:
        win32api.keybd_event(subkey, 0, 0, 0)  # Subkey 누름 (ex : win32con.VK_SHIFT)
        time.sleep(0.02)
    win32api.keybd_event(hexKeyCode, 0, 0, 0)  # Key Down
    time.sleep(interval)  # 20ms 대기
    win32api.keybd_event(hexKeyCode, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key Up
    if subkey!=0:
        time.sleep(0.02)
        win32api.keybd_event(subkey, 0, win32con.KEYEVENTF_KEYUP, 0)  # Subkey 뗌
        time.sleep(0.02)

def sp_press_key(hexKeyCode):    
    win32api.keybd_event(hexKeyCode, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key Up
    time.sleep(0.01)
    win32api.keybd_event(hexKeyCode, 0, 0, 0)  # Key Down

def right_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)  # 우클릭 누름
    time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)  # 우클릭 뗌

def left_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)  # 우클릭 누름
    time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)  # 우클릭 뗌

def press_valid_key(KeyCode, interval=0.02):
    if 'a' <= KeyCode and KeyCode < 'j':
        recode=0x31+(ord(KeyCode)-ord('a'))
        press_key(recode, interval)
    elif KeyCode == 'j':
        press_key(0x30, interval)
    else:
        press_key(0x5A, 0.02, win32con.VK_SHIFT)  # Shift + Z 입력
        time.sleep(0.02)
        press_key(ord(KeyCode.upper()))


def pres_tabtab():
    # ESC-TAB-TAB
    press_key(0x1B)
    keyboard.block_key("up")
    keyboard.block_key("down")
    keyboard.block_key("right")
    keyboard.block_key("left")
    time.sleep(0.02)
    press_key(0x9, 0.04)
    time.sleep(0.1)
    press_key(0x9, 0.04)
    keyboard.unblock_key("up")
    keyboard.unblock_key("down")
    keyboard.unblock_key("right")
    keyboard.unblock_key("left")
    time.sleep(0.01)


DEFAULT_DELAY=0.05
class ActionQueue:
    def __init__(self):
        self.q = []
        
    def getCount(self):
        return len(self.q)

    def add(self, func):
        self.q.append(func)
        
    def do(self):
        if self.q:
            item=self.q.pop(0)
            item()
        else:
            #sp_press_key(0x30+KEY_HEAL)
            press_key(0x30+KEY_HEAL)
            
def _action_diamond():
    press_key(0x30+KEY_GUMGANG)
def _action_heal():
    press_key(0x30+KEY_HEAL)
def _action_diamond():
    press_key(0x30+KEY_GUMGANG)
def _action_mp_refill():
    press_key(0x30+KEY_MP_REFILL)
def _action_shield():
    press_valid_key(KEY_SHIELD)
    time.sleep(0.05)
def _action_protect():
    press_valid_key(KEY_PROTECT)
    time.sleep(0.05)
def _action_bh_heal():
    press_key(0x30+KEY_BH_HEAL)
def _action_bh2_heal():
    press_valid_key(KEY_BH2_HEAL)
def _action_self_heal():
    global is_heal_mode, is_tabtab_restore
    if is_heal_mode and not is_tabtab_restore:
        is_tabtab_restore=True
    press_key(0x1B)  # ESC
    time.sleep(0.02)
    press_key(0x30+KEY_HEAL)
    time.sleep(0.02)
    press_key(0x24)  # HOME
    time.sleep(0.02)
    press_key(0xD)
    time.sleep(0.02)
    press_key(0x1B)   # ESC 키 입력 (종료 X)


def key_loop():
    global running
    global f1_pressed, f2_pressed, f3_pressed, f4_pressed
    global f5_pressed, f6_pressed, f7_pressed, f8_pressed, f9_pressed, f11_pressed
    global up_pressed, down_pressed, right_pressed, left_pressed
    global grave_pressed , pause_pressed, eat_pressed
    
    global is_heal_mode, is_tabtab_restore
    
    last_tick=0
    diamond_tick=0
    protected_tick=0
    action_tick=0
    bh_heal_tick=0
    bh2_heal_tick=0
    
    powerup_tick = 0
    is_power_up=False
    
    on_pause = False
    
    
    bh_ready_flag=False
    bh2_ready_flag=False
    
    action_count=0
    total_action_count=0

    myAction = ActionQueue()

    pres_tabtab()
    
    press_key(0x1B) #ESC
    time.sleep(0.1)
    
    press_key(0x1B) #ESC
    time.sleep(0.1)
        
    while running:
        if pause_pressed:
            pause_pressed=False
            if on_pause:
                print('일시중단해제')
                on_pause=False
            else:
                print('일시중단')
                on_pause=True
               
        if on_pause:
            time.sleep(0.5)
            continue

    
        if f7_pressed and not is_heal_mode:        
            pres_tabtab()
            is_heal_mode=True
            f7_pressed=False
        
        if f7_pressed and is_heal_mode:        
            is_heal_mode=False
            press_key(0x1B)  # ESC
            time.sleep(0.03)
            f7_pressed=False
        
        if is_power_up and (time.perf_counter()-powerup_tick) > 30.5:
            is_power_up=False
        
        if is_heal_mode and not f4_pressed:
            if is_tabtab_restore:
                is_tabtab_restore=False
                pres_tabtab()
            crnt_tick=time.perf_counter()
            if (crnt_tick-action_tick) > 1:
                action_tick=crnt_tick
                action_count=0
                
            #금강
            if GUMGANG_INTERVAL and (crnt_tick-diamond_tick) >= GUMGANG_INTERVAL:
                diamond_tick = crnt_tick
                myAction.add(_action_diamond)
                myAction.add(_action_diamond)
                
            #보무걸기
            if SHIELD_PROTECT_INTERVAL and (crnt_tick-protected_tick) >= SHIELD_PROTECT_INTERVAL:
                protected_tick = crnt_tick
                myAction.add(_action_shield)
                myAction.add(_action_protect)
                
            #희원
            if BH_HEAL_INTERVAL and (crnt_tick-bh_heal_tick) >= BH_HEAL_INTERVAL:
                bh_heal_tick = crnt_tick
                myAction.add(_action_bh_heal)
                if not is_power_up:
                    myAction.add(_action_mp_refill)
                    myAction.add(_action_mp_refill)
                myAction.add(_action_bh_heal)
                #myAction.add(_action_self_heal)
                bh_ready_flag=False
                
            
            #희원준비
            if BH_HEAL_INTERVAL and (crnt_tick-bh_heal_tick) >= (BH_HEAL_INTERVAL-2) and not bh_ready_flag and not is_power_up:
                myAction.add(_action_mp_refill)
                myAction.add(_action_mp_refill)
                myAction.add(_action_mp_refill)
                #myAction.add(_action_self_heal)
                bh_ready_flag = True
            
            #희원 첨
            if BH2_HEAL_INTERVAL and (crnt_tick-bh2_heal_tick) >= BH2_HEAL_INTERVAL and ((crnt_tick-bh_heal_tick) > BH_GAP):
                bh2_heal_tick = crnt_tick
                myAction.add(_action_bh2_heal)
                if not is_power_up:
                    myAction.add(_action_mp_refill)
                    myAction.add(_action_mp_refill)
                    if BH2_HEAL_INTERVAL < 30.5:
                        myAction.add(_action_mp_refill)
                        myAction.add(_action_mp_refill)
                        if BH2_HEAL_INTERVAL < 16.5:
                            myAction.add(_action_mp_refill)
                            myAction.add(_action_mp_refill)
               # myAction.add(_action_self_heal)
                bh2_ready_flag=False
            
            #희원 첨 준비
            if BH2_HEAL_INTERVAL and (crnt_tick-bh2_heal_tick) >= (BH2_HEAL_INTERVAL-2) and not bh2_ready_flag and not is_power_up:
                myAction.add(_action_mp_refill)
                myAction.add(_action_mp_refill)
                myAction.add(_action_mp_refill)
                #myAction.add(_action_self_heal)
                bh2_ready_flag = True
            
            #공증
            if MP_REFILL_FREQ and (MP_REFILL_FREQ <= total_action_count) and not is_power_up:
                myAction.add(_action_mp_refill)
                myAction.add(_action_mp_refill)
                #myAction.add(_action_self_heal)
                total_action_count=0
            
            if action_count < 5:               
                myAction.do()
                time.sleep(DEFAULT_DELAY)                
                action_count=action_count+1
                total_action_count=total_action_count+1
                
            if up_pressed:
                press_key(0x26)
                up_pressed=False
                
            if down_pressed:
                press_key(0x28)
                down_pressed=False
                
            if right_pressed:
                press_key(0x27)
                right_pressed=False
                
            if left_pressed:
                press_key(0x25)
                left_pressed=False
            
        if f9_pressed:
            press_key(0x58, 0.2, win32con.VK_MENU)  #ALT+X
            time.sleep(0.1)
            press_key(0x59) #Y
            time.sleep(0.1)
            f9_pressed=False
          
        
        # 사자후출
        if f6_pressed:
            press_valid_key(KEY_SHOUT)
            time.sleep(0.05)
            keyboard.write(CALL_STRING,0.05)
            time.sleep(0.05)
            press_key(0xD)
            f6_pressed=False
        
            
        #전체 혼
        if f4_pressed:
            if is_heal_mode and not is_tabtab_restore:
                is_tabtab_restore=True
            press_key(0x1B)  # ESC
            time.sleep(0.01)
            press_key(0x30+KEY_HON)  # 5
            time.sleep(0.01)
            press_key(0x26)  # UP
            time.sleep(0.01)
            press_key(0xD)

        #보무걸기
        if f5_pressed:
            pres_tabtab()
            press_valid_key(KEY_PROTECT)
            time.sleep(0.06)
            press_valid_key(KEY_SHIELD)
            time.sleep(0.03)
            press_key(0x1B, 0.02)  # ESC 키 입력 (종료 X)
            time.sleep(0.03)
            press_valid_key(KEY_PROTECT)
            time.sleep(0.05)
            press_key(0x24)  # HOME
            time.sleep(0.03)
            press_key(0xD)
            time.sleep(0.03)
            press_valid_key(KEY_SHIELD)
            time.sleep(0.03)
            press_key(0x24)  # HOME
            time.sleep(0.03)
            press_key(0xD)
            time.sleep(0.03)
            #threading.Thread(target=create_floating_box).start()
            f5_pressed = False
        
        #파력
        if f1_pressed:
            press_valid_key(KEY_POWER_ZONE)
            powerup_tick = time.perf_counter()
            is_power_up=True
            f1_pressed = False
        #공주
        """
            if is_heal_mode and not is_tabtab_restore:
                is_tabtab_restore=True
            pres_tabtab()
            press_valid_key(KEY_MP_INJECTION)
            time.sleep(0.03)
            press_key(0x1B, 0.02)   # ESC 키 입력 (종료 X)
            time.sleep(0.03)
            press_key(0x41, 0.03, win32con.VK_CONTROL)
            time.sleep(0.03)
            press_key(0x30+KEY_MP_REFILL)
            time.sleep(0.03)
            while f1_pressed:
                press_key(0x41, 0.03, win32con.VK_CONTROL)
                time.sleep(0.03)
                press_key(0x30+KEY_MP_REFILL)
                time.sleep(0.03)
            f1_pressed = False
        """
        
        #격수부활
        if f11_pressed:
            pres_tabtab()      
            press_valid_key(KEY_REVIVE)  # 7
            time.sleep(0.05)
            press_key(0x30+KEY_HEAL)  # 3
            time.sleep(0.02)
            press_key(0x30+KEY_HEAL)  # 3
            time.sleep(0.02)
            press_key(0x30+KEY_HEAL)  # 3
            time.sleep(0.02)
            press_key(0x30+KEY_HEAL)  # 3
            time.sleep(0.02)
            press_key(0x1B, 0.02)   # ESC 키 입력 (종료 X)
            f11_pressed = False
        
        #셀프부활
        if f2_pressed:
            if is_heal_mode and not is_tabtab_restore:
                is_tabtab_restore=True
            press_key(0x1B)  # ESC
            time.sleep(0.02)
            press_valid_key(KEY_REVIVE)  # 7
            time.sleep(0.04)
            press_key(0x24)  # HOME
            time.sleep(0.04)
            press_key(0xD)
            time.sleep(0.08)
            press_key(0x30+KEY_HEAL)
            time.sleep(0.03)
            press_key(0x24)  # HOME
            time.sleep(0.03)
            press_key(0xD)
            time.sleep(0.03)
            press_key(0x30+KEY_HEAL)
            time.sleep(0.03)
            press_key(0xD)
            time.sleep(0.03)
            press_key(0x1B, 0.02)   # ESC 키 입력 (종료 X)
            f2_pressed = False
            
        #셀프힐
        if f3_pressed:
            if is_heal_mode and not is_tabtab_restore:
                is_tabtab_restore=True

            press_key(0x1B)  # ESC
            time.sleep(0.02)
            press_key(0x30+KEY_HEAL)
            time.sleep(0.03)
            press_key(0x24)  # HOME
            time.sleep(0.03)
            press_key(0xD)
            time.sleep(0.03)
            press_key(0x30+KEY_HEAL)
            time.sleep(0.03)
            press_key(0xD)
            time.sleep(0.03)
            press_key(0x1B, 0.02)   # ESC 키 입력 (종료 X)
            f3_pressed = False
            
        #템먹기
        if eat_pressed:
            press_key(0xBC, 0.02, win32con.VK_SHIFT)  # Shift + ',' 입력
            eat_pressed=False
        time.sleep(0.02)  # 20ms 주기로 상태 확인

#################
def on_esc_press(event):
    global is_heal_mode
    is_heal_mode=False
    
def on_tab_press(event):
    global is_heal_mode
    is_heal_mode=False

def on_f1_press(event):
    global f1_pressed
    f1_pressed = True

def on_f1_release(event):
    global f1_pressed
    f1_pressed = False

def on_f2_press(event):
    global f2_pressed
    f2_pressed = True
    
def on_f3_press(event):
    global f3_pressed
    f3_pressed = True

def on_f4_press(event):
    global f4_pressed
    f4_pressed = True

def on_f4_release(event):
    global f4_pressed
    f4_pressed = False

def on_f5_press(event):
    global f5_pressed
    f5_pressed = True

def on_f5_release(event):
    global f5_pressed
    f5_pressed = False
    
def on_f6_press(event):
    global f6_pressed
    f6_pressed = True

def on_f6_release(event):
    global f6_pressed
    f6_pressed = False

def on_f7_press(event):
    global f7_pressed
    f7_pressed = True
    
def on_f7_release(event):
    global f7_pressed
    f7_pressed = False

def on_f8_press(event):
    global f8_pressed
    f8_pressed = True

def on_f9_press(event):
    global f9_pressed
    f9_pressed = True
    
def on_f11_press(event):
    global f11_pressed
    f11_pressed = True

def on_f12_press(event):
    global running
    running = False  # 프로그램 종료
    time.sleep(0.5)

   
def on_down_press(event):
    global down_pressed
    down_pressed = True

def on_down_release(event):
    global down_pressed
    down_pressed = False

def on_up_press(event):
    global up_pressed
    up_pressed = True

def on_up_release(event):
    global up_pressed
    up_pressed = False    

def on_right_press(event):
    global right_pressed
    right_pressed = True

def on_right_release(event):
    global right_pressed
    right_pressed = False 

def on_left_press(event):
    global left_pressed
    left_pressed = True

def on_left_release(event):
    global left_pressed
    left_pressed = False 
        
def on_grave_press(event):
    global grave_pressed
    grave_pressed = True

def on_grave_release(event):
    global grave_pressed
    grave_pressed = False

def on_pause_press(event):
    global pause_pressed
    pause_pressed = True
    
def on_eat_press(event):
    global eat_pressed
    eat_pressed=True

keyboard.on_press_key("esc", on_esc_press)
keyboard.on_press_key("tab", on_tab_press)
keyboard.on_press_key("`", on_grave_press,  suppress=True)
keyboard.on_release_key("`", on_grave_release,  suppress=True)
keyboard.on_press_key("pause", on_pause_press,  suppress=True)
keyboard.on_press_key(",",on_eat_press, suppress=True)

keyboard.on_press_key("up", on_up_press)
#keyboard.on_release_key("up", on_up_release)
keyboard.on_press_key("down", on_down_press)
#keyboard.on_release_key("down", on_down_release)
keyboard.on_press_key("right", on_right_press)
#keyboard.on_release_key("right", on_right_release)
keyboard.on_press_key("left", on_left_press)
#keyboard.on_release_key("left", on_left_release)

keyboard.on_press_key("f1", on_f1_press,  suppress=True)
#keyboard.on_release_key("f1", on_f1_release,  suppress=True)
keyboard.on_press_key("f2", on_f2_press,  suppress=True)
keyboard.on_press_key("f3", on_f3_press,  suppress=True)
keyboard.on_press_key("f4", on_f4_press,  suppress=True)
keyboard.on_release_key("f4", on_f4_release,  suppress=True)

keyboard.on_press_key("f5", on_f5_press,  suppress=True)
keyboard.on_release_key("f5", on_f5_release,  suppress=True)
keyboard.on_press_key("f6", on_f6_press,  suppress=True)
keyboard.on_release_key("f6", on_f6_release,  suppress=True)

keyboard.on_press_key("f7", on_f7_press,  suppress=True)
#keyboard.on_release_key("f7", on_f7_release,  suppress=True)

keyboard.on_press_key("f8", on_f8_press,  suppress=True)
keyboard.on_press_key("f9", on_f9_press,  suppress=True)

keyboard.on_press_key("f11", on_f11_press,  suppress=True)


#keyboard.block_key("f12")
#keyboard.add_hotkey("f12", on_f12_press,  suppress=False)  # F12를 누르면 종료
keyboard.on_press_key("f12", on_f12_press)  # F12를 누르면 종료


thread = threading.Thread(target=key_loop, daemon=True)
thread.start()

while running:
    time.sleep(1)
