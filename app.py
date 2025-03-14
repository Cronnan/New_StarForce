import pandas as pd
import streamlit as st
from simulation_module import main

# ページ設定（タイトル、アイコン、レイアウトなど）
st.set_page_config(
    page_title="★30対応版- スタフォシミュレーター",
    page_icon="✨",
    layout="centered"
)

# タイトル表示
st.markdown("""
<style>
.title-container {text-align: center;}
.modern-title {color: #FF6EC7; font-weight: 500; display: inline-block; margin-bottom: 5px;}
.modern-subtitle {color: #FF69B4; font-size: 1.2rem; text-align: center; display: block;}
</style>
<div class="title-container">
    <h1 class="modern-title">スタフォシミュレーター</h1>
    <p class="modern-subtitle">★ 30星対応版 ★</p>
</div>
""", unsafe_allow_html=True)

# 方法1: カラムを使用して左右にスペースを作る
left_space, center, right_space = st.columns([1, 18, 1])  # 左:中央:右の比率を調整できる

with center:
    start_star_num = st.slider("開始スタフォ星数", 15, 30, 17)
    target_star_num = st.slider("目標スタフォ星数", 16, 30, 22)
    equipment_level = st.slider("装備レベル", 100, 250, 250, step=10)
    penalty = st.number_input("装備破壊時のペナルティ(m)", value=5000)
    simulation_num = st.number_input("シミュレーション回数", value=1000)

    shining_cost = st.checkbox("スタフォ費用30%OFF", value=True)
    shining_15to16 = st.checkbox("15→16星 強化100%成功", value=True)
    shining_destroy = st.checkbox("破壊率30%軽減", value=True)
    eighteen_protect = st.checkbox("星18までの破壊防止", value=True)
    catch_succeed = st.checkbox("スターキャッチ絶対成功", value=True)

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
            shining_destroy=shining_destroy,
            eighteen_protect = eighteen_protect,
            catch_succeed = catch_succeed    
        )
        

        st.write("### 📊 シミュレーション結果")
    
    # 結果データフレーム作成
    results_df = pd.DataFrame({
        "パーセンタイル": ["最良", "Top25%", "中央値", "Top75%", "最悪"],
        "合計費用 (m)": [f"{int(cost):,} m" for cost in cost_quantiles],
        "装備破壊回数": [f"{int(count)} 回" for count in destruction_quantiles]
    })
    
    # テーブル表示
    st.dataframe(results_df, use_container_width=True, hide_index=True)
