# 냉각 소재 비교 계산기 (웹앱, Streamlit)
# 2901_냉각소재비교계산기.py와 같은 계산 함수를 쓰고, 입력과 결과만 웹 화면으로 바꿈
import streamlit as st

WATER_C = 4.18  # 물(음료)의 비열 (J/g·°C)

# 1. 냉각 소재 정보 (콘솔 버전과 같음)
MATERIALS = {
    "얼음": {"c": 2.1, "melt": 0, "latent": 334, "c_liquid": 4.18, "piece": 10, "mix": True},
    "젤 아이스팩": {"c": 2.1, "melt": 0, "latent": 334, "c_liquid": 4.18, "piece": 100, "mix": False},
    "스테인리스 큐브": {"c": 0.50, "melt": None, "latent": 0, "c_liquid": 0, "piece": 25, "mix": False},
    "위스키 스톤(화강암)": {"c": 0.79, "melt": None, "latent": 0, "c_liquid": 0, "piece": 20, "mix": False},
}


# 2. 소재 1g이 처음 온도에서 목표 온도까지 흡수하는 열 (콘솔 버전과 같음)
def heat_per_gram(m, start, target):
    if m["melt"] is None or target <= m["melt"]:
        return m["c"] * (target - start)  # 현열만

    solid = m["c"] * (m["melt"] - start)
    melting = m["latent"]
    liquid = m["c_liquid"] * (target - m["melt"])
    return solid + melting + liquid


# 3. 음료가 목표 온도까지 식으며 내놓는 열
def drink_heat(mass, drink_temp, target):
    return mass * WATER_C * (drink_temp - target)


# 4. 모든 소재의 계산 결과를 리스트로 돌려줌 (화면에 표로 보여 주기 위해)
def compare(mass, drink_temp, target, start):
    q = drink_heat(mass, drink_temp, target)
    ice_grams = q / heat_per_gram(MATERIALS["얼음"], start, target)
    rows = []
    for name in MATERIALS:
        m = MATERIALS[name]
        per_gram = heat_per_gram(m, start, target)
        grams = q / per_gram
        if m["mix"]:
            water = f"{grams / (mass + grams) * 100:.0f}% 묽어짐"
        else:
            water = "안 묽어짐"
        rows.append({
            "냉각 소재": name,
            "1g당 흡수열(J)": round(per_gram, 1),
            "필요한 양(g)": round(grams),
            "개수": round(grams / m["piece"]),
            "얼음 대비(배)": round(grams / ice_grams, 1),
            "음료": water,
        })
    return q, rows


# 5. 화면: 제목과 입력
st.title("🧊 냉각 소재 비교 계산기")
st.write("재사용 얼음(스테인리스 큐브)은 왜 진짜 얼음만큼 시원하지 않을까? 직접 계산해 보세요.")

col1, col2 = st.columns(2)
with col1:
    mass = st.slider("음료 양 (g)", 50, 1000, 300, step=10)
    drink_temp = st.slider("음료 온도 (°C)", 1, 100, 80)
with col2:
    target = st.slider("목표 온도 (°C)", 0, 50, 10)
    start = st.slider("냉각 소재 처음 온도 (°C, 냉동실)", -30, 0, -18)

# 6. 계산할 수 없는 경우 걸러내기, 아니면 결과 출력
if target >= drink_temp:
    st.error("목표 온도는 음료 온도보다 낮아야 해요.")
elif target <= start:
    st.error("목표 온도는 냉각 소재 온도보다 높아야 해요. (더 차가운 것으로는 식힐 수 없어요)")
else:
    q, rows = compare(mass, drink_temp, target, start)
    st.metric("음료가 내놓는 열", f"{q:,.0f} J")
    st.dataframe(rows, hide_index=True)

    st.subheader("필요한 양 비교 (g)")
    st.bar_chart(rows, x="냉각 소재", y="필요한 양(g)", horizontal=True)

    steel = rows[2]["얼음 대비(배)"]
    st.info(f"스테인리스 큐브는 얼음보다 약 {steel}배 더 필요해요. 얼음은 녹을 때 열을 많이 흡수(잠열)하지만, 스테인리스는 녹지 않아 온도가 오르는 만큼(현열)만 흡수하기 때문이에요.")

# 7. 원리 설명
with st.expander("왜 이런 차이가 날까? (현열과 잠열)"):
    st.write("- **현열**: 온도가 바뀌면서 주고받는 열. Q = m × c × ΔT")
    st.write("- **잠열(융해열)**: 녹을 때 온도는 그대로인 채 흡수하는 열. 얼음 1g = 334 J")
    st.write("- **열평형**: 음료가 잃은 열 = 냉각 소재가 얻은 열 → 필요한 양 = 음료 열 ÷ 1g당 흡수열")
    st.write("녹을 때의 큰 잠열을 일부러 이용하는 소재가 **상변화 물질(PCM)**이에요. 반도체 칩 방열, 배터리 온도 관리에 연구되고 있어요.")

st.caption("컵과 공기로 빠져나가는 열은 계산하지 않아서 실제로는 조금 더 필요해요. 음료는 물로 보고 계산했어요.")
