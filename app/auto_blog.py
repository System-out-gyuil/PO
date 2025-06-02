import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import traceback
from tkinter import filedialog, messagebox
import time
import random
from selenium.webdriver.common.keys import Keys

def log_message(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    log_box.update_idletasks()  # 👈 바로 화면 반영

def slow_typing(element, text, delay=0.2):
    for char in text:
        element.send_keys(char)
        time.sleep(delay + random.uniform(0.05, 0.1))  # 약간 랜덤한 딜레이 추가

def slow_type_with_actionchains(driver, element, text, min_delay=0.05, max_delay=0.1):
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()
    for char in text:
        actions = ActionChains(driver)
        actions.send_keys(char).perform()
        time.sleep(random.uniform(min_delay, max_delay))

def get_typing_delays():
    try:
        min_delay = float(min_delay_entry.get())
        max_delay = float(max_delay_entry.get())
        if min_delay > max_delay:
            min_delay, max_delay = max_delay, min_delay  # 자동 정정
        return min_delay, max_delay
    except ValueError:
        return 0.03, 0.08  # 기본값
    
def slow_type_with_typos(driver, element, text, min_delay=0.05, max_delay=0.1, typo_chance=0.1):
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

    for char in text:
        # 오타 확률 발생
        if random.random() < typo_chance:
            typo_length = random.randint(2, 7)  # 2~3글자짜리 오타 생성
            fake_chars = ''.join(random.choices("ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ", k=typo_length))

            # 오타 입력
            actions = ActionChains(driver)
            actions.send_keys(fake_chars).perform()
            time.sleep(random.uniform(min_delay, max_delay))

            # 오타 지우기 (Backspace 여러 번)
            for _ in range(typo_length):
                actions = ActionChains(driver)
                actions.send_keys(Keys.BACKSPACE).perform()
                time.sleep(random.uniform(min_delay, max_delay))

        # 정상 글자 입력
        actions = ActionChains(driver)
        actions.send_keys(char).perform()
        time.sleep(random.uniform(min_delay, max_delay))


def get_typo_chance():
    try:
        typo_chance = float(typo_chance_entry.get())
        return max(0.0, min(typo_chance, 1.0))  # 0~1 사이 값으로 클램핑
    except ValueError:
        return 0.1  # 기본값


# ✅ Selenium 설정
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("user-data-dir=selenium")  # 쿠키 저장용
    driver = webdriver.Chrome(options=options)
    return driver

# ✅ 네이버 로그인 (직접 입력 유도)
def naver_login(driver):
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(1)

    try:
        switch = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "switch"))
        )
        if switch.is_selected():
            driver.execute_script("arguments[0].click();", switch)
            log_message("✅ IP 보안 스위치 OFF 설정 완료")
    except Exception:
        log_message("⚠️ 스위치 비활성화 실패 (없거나 비정상):")
        traceback.print_exc()

# ✅ 블로그 글 작성페이지로 들어가기
def naver_blog(driver):
    try:
        blog_tab = WebDriverWait(driver, 600).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//li[contains(@class, 'MyView-module__menu_item')][.//span[contains(text(), '블로그')]]"
            ))
        )
        blog_tab.click()
        log_message("✅ '블로그' 탭 클릭 완료")

        try:
            blog_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "a.MyView-module__link_service___Ok8hP[href='https://blog.naver.com/MyBlog.naver']"
                ))
            )
            blog_link.click()
            log_message("✅ 내 블로그 버튼 클릭 완료")

            original_window = driver.current_window_handle
            time.sleep(2)

            # ✅ 새 창으로 전환
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    log_message("✅ 새 창으로 전환 완료")
                    break

            # ✅ 사용자 블로그 ID 추출
            try:
                current_url = driver.current_url  # 예: https://blog.naver.com/rbdlfdlsp2
                user_id = current_url.rstrip("/").split("/")[-1]
                log_message(f"✅ 블로그 사용자 ID 추출 완료: {user_id}")

                return driver, user_id
            
            except Exception:
                log_message("❌ 블로그 사용자 ID 추출 실패:")
                traceback.print_exc()


        except Exception:
            log_message("❌ 내 블로그 버튼 클릭 실패:")
            traceback.print_exc()

    except Exception:
        log_message("❌ 블로그 탭 클릭 실패:")
        traceback.print_exc()


def write_naver_blog(driver, user_id, title, content):
    min_d, max_d = get_typing_delays()
    time.sleep(3)

    try:
        driver.get(f"https://blog.naver.com/{user_id}?Redirect=Write&")
        log_message("✅ 블로그 글 작성 페이지로 이동 완료")

    except Exception:
        log_message("❌ 블로그 글 작성 페이지로 이동 실패:")
        traceback.print_exc()
    
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        log_message("✅ iframe(mainFrame) 진입 완료")

        try:
            load_write = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.se-popup-button-cancel"))
            )
            load_write.click()
            log_message("✅ 글 이어쓰기 취소 완료")
            time.sleep(1)

        except Exception:
            log_message("⚠️ 글 이어쓰기 취소 실패 (없거나 클릭 안됨)")
            traceback.print_exc()

        try:
            help_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.se-help-panel-close-button"))
            )
            driver.execute_script("arguments[0].click();", help_btn)
            log_message("✅ 도움말 패널 닫기 성공 (JS click)")
            time.sleep(1)

        except Exception:
            log_message("⚠️ 도움말 패널 닫기 실패 (없거나 클릭 안됨)")
            traceback.print_exc()

        # ✅ 제목 입력
        try:
            title_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.se-title-text"))
            )
            slow_type_with_actionchains(driver, title_container, title, min_delay=min_d, max_delay=max_d)
            log_message("✅ 제목 입력 완료")
            time.sleep(1)

        except Exception:
            log_message("❌ 제목 입력 실패:")
            traceback.print_exc()

        # ✅ 본문 입력
        try:
            body_paragraph = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div[data-a11y-title='본문'] p.se-text-paragraph"
                ))
            )

            typo_chance = get_typo_chance()
            slow_type_with_typos(driver, body_paragraph, content, min_delay=min_d, max_delay=max_d, typo_chance=typo_chance)

            log_message("✅ 본문 입력 완료")
            time.sleep(1)

        except Exception:
            log_message("❌ 본문 입력 실패:")
            traceback.print_exc()

        

        publish_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='저장']]"))
        )
        publish_button.click()
        log_message("✅ 저장 버튼 클릭 완료")
        time.sleep(1)

        # ✅ 저장 후: 현재 창 닫고 원래 창으로 복귀
        driver.close()  # 현재 블로그 작성 창 닫기
        driver.switch_to.window(driver.window_handles[0])  # 원래 창으로 전환
        log_message("✅ 블로그 작성 창 닫고 원래 창으로 전환 완료")

        # ✅ 네이버 메인으로 이동
        driver.get("https://www.naver.com")
        log_message("✅ 네이버 메인으로 이동 완료")
        time.sleep(1)

        return driver


    except Exception:
        log_message("❌ iframe(mainFrame) 진입 또는 제목 입력 실패:")
        traceback.print_exc()

# ✅ 파일 처리 & 자동 등록 흐름
def process_files(file_paths):
    driver = create_driver()
    naver_login(driver)

    for filepath in file_paths:
        try:
            # 🔁 매 반복마다 작성 페이지 재진입
            driver, user_id = naver_blog(driver)

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.strip().split("\n")
            title = lines[0]
            body = "\n".join(lines[1:])

            log_message(f"📄 {os.path.basename(filepath)} 처리 중...")
            log_message(f"  └ 제목: {title}")
            driver = write_naver_blog(driver, user_id, title, body)

            log_message("✅ 게시 완료")

        except Exception:
            log_message(f"❌ 파일 처리 실패: {filepath}")
            traceback.print_exc()

# ✅ 파일 선택
def choose_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
    process_files(file_paths)


# ✅ 파일 드롭
def handle_drop(event):
    file_path = event.data.strip("{}")
    if file_path.endswith(".txt"):
        process_files(file_path)


# ✅ Tkinter UI 구성
def start_main_gui():
    global log_box, min_delay_entry, max_delay_entry, typo_chance_entry
    root = TkinterDnD.Tk()
    root.title("네이버 블로그 자동 등록기")
    root.geometry("650x350")

    # 파일 선택 or 드래그
    tk.Button(root, text="파일 선택하기", command=choose_file).pack(pady=5)

    # ✅ 타이핑 속도 입력창
    speed_frame = tk.Frame(root)
    speed_frame.pack()

    tk.Label(speed_frame, text="n초마다 타이핑: 최저").pack(side=tk.LEFT)
    min_delay_entry = tk.Entry(speed_frame, width=5)
    min_delay_entry.insert(0, "0.03")
    min_delay_entry.pack(side=tk.LEFT, padx=(0, 10))

    tk.Label(speed_frame, text="최고").pack(side=tk.LEFT)
    max_delay_entry = tk.Entry(speed_frame, width=5)
    max_delay_entry.insert(0, "0.08")
    max_delay_entry.pack(side=tk.LEFT)

    # ✅ 오타 확률 입력창
    typo_frame = tk.Frame(root)
    typo_frame.pack()

    tk.Label(typo_frame, text="오타 확률(자동으로 오타 냈다가 다시 지움), 0:오타 없음, 1:전부 오타 (0~1): ").pack(side=tk.LEFT)
    typo_chance_entry = tk.Entry(typo_frame, width=5)
    typo_chance_entry.insert(0, "0.1")  # 기본값 10%
    typo_chance_entry.pack(side=tk.LEFT)

    # ✅ 로그 출력창
    log_box = tk.Text(root, height=10, wrap='word')
    log_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    log_box.insert(tk.END, "🟢 프로그램 시작됨...\n")

    root.mainloop()

def launch_login_ui():
    login_root = tk.Tk()
    login_root.title("사용자 로그인")
    login_root.geometry("300x180")

    tk.Label(login_root, text="아이디").pack(pady=(10, 0))
    id_entry = tk.Entry(login_root)
    id_entry.pack()

    tk.Label(login_root, text="비밀번호").pack(pady=(10, 0))
    pw_entry = tk.Entry(login_root, show="*")
    pw_entry.pack()

    def try_login():
        user_id = id_entry.get()
        password = pw_entry.get()

        valid_users = {
            "test": "test",
            "wnk1cx": "80rnnu",
            "cg8cdx": "sxjws1",
            "cprnnn": "i0x752",
            "tvtkys": "dzg015",
            "i604pv": "2g4b2y",
            "lj0u6i": "mic8xq",
            "result": "ga05190519!",
            "8orwvw": "l3ff6g",
            "h25z66": "i61vs6",
        }
        if valid_users.get(user_id) == password:
            login_root.destroy()
            start_main_gui()
        else:
            messagebox.showerror("로그인 실패", "아이디 또는 비밀번호가 틀렸습니다.")

    tk.Button(login_root, text="로그인", command=try_login).pack(pady=15)

    tk.Label(login_root, text="문의: 010-8177-1424", fg="gray").pack(pady=(10, 0))
    login_root.mainloop()

# === 프로그램 시작 ===
if __name__ == "__main__":
    launch_login_ui()