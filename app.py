import pandas as pd
import streamlit as st
from simulation_module import main

st.title("★30対応版- スタフォシミュレーター")

# ユーザー入力（UIで設定可能）
start_star_num = st.slider("開始スタフォ星数", 16, 30, 22)
target_star_num = st.slider("目標スタフォ星数", 16, 30, 22)
equipment_level = st.slider("装備レベル", 100, 250, 250)
penalty = st.number_input("装備破壊時のペナルティ(m)", value=5000)
simulation_num = st.number_input("シミュレーション回数", value=1000)

shining_cost = st.checkbox("スタフォ費用30%OFF", value=True)
shining_15to16 = st.checkbox("15→16星 強化100%成功", value=True)
shining_destroy = st.checkbox("破壊率30%軽減", value=True)

if st.button("シミュレーション実行"):
    with st.spinner('シミュレーション中...'):
        cost_quantiles, destruction_quantiles = main(
            start_star_num=start_star_num,
            target_star_num=target_star_num,
            equipment_level=equipment_level,
            penalty=penalty,
            simulation_num=simulation_num,
            shining_cost=shining_cost,
            shining_15to16=shining_15to16,
            shining_destroy=shining_cost
        )
        

        st.write("## シミュレーション結果")
        st.write(pd.DataFrame({
            "パーセンタイル":["最良", "Top25%", "中央値", "Top75%", "最悪"],
            "合計費用 (m)": [f"{int(cost):,} m" for cost in cost_quantiles],
            "装備破壊回数 (回)": [f"{int(count)} 回" for count in destruction_quantiles]
        }))
