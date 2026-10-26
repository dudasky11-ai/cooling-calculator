# 냉각 소재 비교 계산기
# 음료를 원하는 온도로 식히려면 소재별로 얼마나 필요한지 계산하고,
# 녹는 소재(잠열)와 녹지 않는 소재(현열)의 차이를 비교함
#
# 실행 방법 두 가지 (같은 파일!)
#   IDLE에서 F5            → 콘솔 프로그램. 끝에 w를 누르면 웹앱이 브라우저에 열림
#   streamlit run 이파일.py → 바로 웹앱

WATER_C = 4.18  # 물(음료)의 비열 (J/g·°C)

# 1. 냉각 소재 정보
#    c: 고체일 때 비열(J/g·°C), melt: 녹는점(°C, 녹지 않으면 None)
#    latent: 융해열(J/g), c_liquid: 녹은 뒤 비열, piece: 한 개 무게(g), mix: 음료에 섞이는지
MATERIALS = {
    "얼음": {"c": 2.1, "melt": 0, "latent": 334, "c_liquid": 4.18, "piece": 10, "mix": True},
    "젤 아이스팩": {"c": 2.1, "melt": 0, "latent": 334, "c_liquid": 4.18, "piece": 100, "mix": False},
    "스테인리스 큐브": {"c": 0.50, "melt": None, "latent": 0, "c_liquid": 0, "piece": 25, "mix": False},
    "위스키 스톤(화강암)": {"c": 0.79, "melt": None, "latent": 0, "c_liquid": 0, "piece": 20, "mix": False},
}


# 2. 소재 1g이 처음 온도(start)에서 목표 온도(target)까지 데워지며 흡수하는 열
def heat_per_gram(m, start, target):
    if m["melt"] is None or target < m["melt"]:
        return m["c"] * (target - start)  # 현열만 (녹지 않음)

    solid = m["c"] * (m["melt"] - start)          # 녹는점까지 데워짐 (현열)
    melting = m["latent"]                          # 녹음 (잠열)
    liquid = m["c_liquid"] * (target - m["melt"])  # 녹은 뒤 목표 온도까지 (현열)
    return solid + melting + liquid


# 3. 음료가 목표 온도까지 식으며 내놓는 열
def drink_heat(mass, drink_temp, target):
    return mass * WATER_C * (drink_temp - target)


# 4. 숫자를 입력받음. Enter만 누르면 기본값(default), 잘못 입력하면 다시 물어봄
def ask_number(message, default):
    while True:
        text = input(message).strip()
        if text == "":
            return default
        try:
            return float(text)
        except ValueError:
            print("  숫자로 입력하세요.")


# 5. 소재마다 필요한 양을 계산해 출력
def compare(mass, drink_temp, target, start):
    q = drink_heat(mass, drink_temp, target)
    print(f"\n음료가 내놓는 열: {q:,.0f} J")
    print("-" * 60)

    ice_grams = None
    for name in MATERIALS:
        m = MATERIALS[name]
        per_gram = heat_per_gram(m, start, target)
        grams = q / per_gram
        pieces = grams / m["piece"]
        if name == "얼음":
            ice_grams = grams

        line = f"{name:<14} 1g당 {per_gram:6.1f} J  →  {grams:8,.0f} g  ({pieces:5.0f}개)"
        if ice_grams is not None and name != "얼음":
            line += f"  얼음의 {grams / ice_grams:.1f}배"
        print(line)

        if m["mix"]:
            water_ratio = grams / (mass + grams) * 100
            print(f"{'':<14} └ 녹은 물이 섞여 음료의 {water_ratio:.0f}%가 물이 됨")
    print("-" * 60)


# 6. 메인 (콘솔)  — 원래 코드를 함수 안에 넣은 것. 마지막 물음에 w를 추가함
def run_console():
    print("=== 냉각 소재 비교 계산기 ===")
    print("뜨거운 음료를 식힐 때 얼음, 재사용 얼음, 돌이 얼마나 필요한지 비교해요.\n")

    while True:
        mass = ask_number("음료 양(g) [Enter=300]: ", 300)
        drink_temp = ask_number("음료 온도(°C) [Enter=80]: ", 80)
        target = ask_number("목표 온도(°C) [Enter=10]: ", 10)
        start = ask_number("냉각 소재 처음 온도(°C, 냉동실) [Enter=-18]: ", -18)

        # 계산이 불가능한 경우 걸러내기
        if mass <= 0:
            print("  음료 양은 0보다 커야 해요.\n")
        elif target >= drink_temp:
            print("  목표 온도는 음료 온도보다 낮아야 해요.\n")
        elif target <= start:
            print("  목표 온도는 냉각 소재 온도보다 높아야 해요. (더 차가운 것으로는 식힐 수 없어요)\n")
        elif target < 0:
            print("  목표 온도가 0°C보다 낮으면 음료가 얼어요.\n")
        else:
            compare(mass, drink_temp, target, start)

        again = input("\n다시 계산할까요? (y=다시 / w=웹앱으로 열기 / n=끝): ").strip().lower()
        if again == "w":
            open_web()
            return
        if again != "y":
            break
        print()

    print("\n※ 컵이나 공기로 빠져나가는 열은 계산하지 않아서, 실제로는 조금 더 필요해요.")
    input("Enter를 누르면 닫힙니다.")


# 7. 브라우저에 웹앱을 띄움
#    이 컴퓨터에 Streamlit이 있으면 → 이 파일을 streamlit run으로 다시 실행 (내 컴퓨터에서)
#    없으면(선생님 컴퓨터 등)     → 같은 코드가 올라가 있는 인터넷 주소를 엶 (설치 필요 없음)
WEB_URL = "https://cooling-calculator.streamlit.app"

def open_web():
    import subprocess, sys, os, time, webbrowser
    try:
        import streamlit  # 설치돼 있는지만 확인
    except ImportError:
        print(f"\n이 컴퓨터엔 Streamlit이 없어서, 배포해 둔 웹앱을 엽니다: {WEB_URL}")
        webbrowser.open(WEB_URL)
        input("Enter를 누르면 닫힙니다.")
        return
    print("\n웹앱을 켜는 중... 잠시 후 브라우저가 열립니다. (끄려면 새로 뜬 까만 창을 닫으세요)")
    exe = sys.executable.replace("pythonw.exe", "python.exe")  # IDLE은 창 없는 pythonw로 실행되므로
    subprocess.Popen([exe, "-m", "streamlit", "run", os.path.abspath(__file__), "--server.headless", "true"])
    time.sleep(6); webbrowser.open("http://localhost:8501")  # 웹 서버가 켜지길 6초 기다린 뒤 열기
# 8. 웹앱 화면 — 계산 함수(2, 3)는 위의 것을 그대로 쓰고, 입력과 출력만 웹으로
def run_web():
    import streamlit as st

    st.title("🧊 냉각 소재 비교 계산기")
    st.write("재사용 얼음(스테인리스 큐브)은 왜 진짜 얼음만큼 시원하지 않을까? 직접 계산해 보세요.")

    col1, col2 = st.columns(2)
    with col1:
        mass = st.slider("음료 양 (g)", 50, 1000, 300, step=10)
        drink_temp = st.slider("음료 온도 (°C)", 1, 100, 80)
    with col2:
        target = st.slider("목표 온도 (°C)", 0, 50, 10)
        start = st.slider("냉각 소재 처음 온도 (°C, 냉동실)", -30, 0, -18)

    if target >= drink_temp:
        st.error("목표 온도는 음료 온도보다 낮아야 해요.")
        return
    if target <= start:
        st.error("목표 온도는 냉각 소재 온도보다 높아야 해요. (더 차가운 것으로는 식힐 수 없어요)")
        return

    # 콘솔의 compare()와 같은 계산을 하되, print 대신 표에 넣을 줄(rows)로 모음
    q = drink_heat(mass, drink_temp, target)
    ice_grams = q / heat_per_gram(MATERIALS["얼음"], start, target)
    rows = []
    for name in MATERIALS:
        m = MATERIALS[name]
        per_gram = heat_per_gram(m, start, target)
        grams = q / per_gram
        water = f"{grams / (mass + grams) * 100:.0f}% 묽어짐" if m["mix"] else "안 묽어짐"
        rows.append({
            "냉각 소재": name,
            "1g당 흡수열(J)": round(per_gram, 1),
            "필요한 양(g)": round(grams),
            "개수": round(grams / m["piece"]),
            "얼음 대비(배)": round(grams / ice_grams, 1),
            "음료": water,
        })

    st.metric("음료가 내놓는 열", f"{q:,.0f} J")
    st.dataframe(rows, hide_index=True)

    st.subheader("필요한 양 비교 (g)")
    st.bar_chart(rows, x="냉각 소재", y="필요한 양(g)", horizontal=True)

    steel = rows[2]["얼음 대비(배)"]
    st.info(f"스테인리스 큐브는 얼음보다 약 {steel}배 더 필요해요. 얼음은 녹을 때 열을 많이 흡수(잠열)하지만, 스테인리스는 녹지 않아 온도가 오르는 만큼(현열)만 흡수하기 때문이에요.")

    with st.expander("왜 이런 차이가 날까? (현열과 잠열)"):
        st.write("- **현열**: 온도가 바뀌면서 주고받는 열. Q = m × c × ΔT")
        st.write("- **잠열(융해열)**: 녹을 때 온도는 그대로인 채 흡수하는 열. 얼음 1g = 334 J")
        st.write("- **열평형**: 음료가 잃은 열 = 냉각 소재가 얻은 열 → 필요한 양 = 음료 열 ÷ 1g당 흡수열")
        st.write("녹을 때의 큰 잠열을 일부러 이용하는 소재가 **상변화 물질(PCM)**이에요. 반도체 칩 방열, 배터리 온도 관리에 연구되고 있어요.")

    st.caption("컵과 공기로 빠져나가는 열은 계산하지 않아서 실제로는 조금 더 필요해요. 음료는 물로 보고 계산했어요.")


# 9. 어떻게 실행됐는지 보고 고름: streamlit run이면 웹앱, 아니면(F5, python) 콘솔
def running_in_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:
        return False


if running_in_streamlit():
    run_web()
else:
    run_console()
