import pandas as pd
import streamlit as st
from simulation_module import main

# ページ設定（タイトル、アイコン、レイアウトなど）
st.set_page_config(
    page_title="★30対応版- スタフォシミュレーター",
    page_icon="✨",
    layout="centered"
)

# セッション状態の初期化
if 'results_calculated' not in st.session_state:
    st.session_state.results_calculated = False
if 'cost_quantiles' not in st.session_state:
    st.session_state.cost_quantiles = None
if 'destruction_quantiles' not in st.session_state:
    st.session_state.destruction_quantiles = None

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


# 主要設定
start_star_num = st.slider("開始スタフォ星数", 15, 30, 17)
target_star_num = st.slider("目標スタフォ星数", 16, 30, 22)
equipment_level = st.slider("装備レベル", 100, 250, 200, step=10)
penalty = st.number_input("装備破壊時のペナルティ(m)", value=5000)
simulation_num = st.number_input("シミュレーション回数", value=1000)

# オプション
shining_cost = st.checkbox("[シャイニング]スタフォ費用30%OFF", value=True)
shining_15to16 = st.checkbox("[シャイニング]15→16星 強化100%成功", value=True)
shining_destroy = st.checkbox("[シャイニング]21星以下の破壊率30%DOWN", value=True)
eighteen_protect = st.checkbox("星18までの破壊防止", value=True)
catch_succeed = st.checkbox("スターキャッチ絶対成功", value=True)

# シミュレーション実行関数
def run_simulation():
    with st.spinner('シミュレーション中...'):
        st.session_state.cost_quantiles, st.session_state.destruction_quantiles, st.session_state.cost_table = main(
            start_star_num=start_star_num,
            target_star_num=target_star_num,
            equipment_level=equipment_level,
            penalty=penalty,
            simulation_num=simulation_num,
            shining_cost=shining_cost,
            shining_15to16=shining_15to16,
            shining_destroy=shining_destroy,
            eighteen_protect=eighteen_protect,
            catch_succeed=catch_succeed    
        )
        st.session_state.results_calculated = True

# シミュレーションボタン
if st.button("シミュレーション実行"):
    run_simulation()

# 結果表示（セッション状態に保存された結果があれば表示）
if st.session_state.results_calculated:
    st.write("### 📊 シミュレーション結果")
    
    # 結果データフレーム作成
    results_df = pd.DataFrame({
        "パーセンタイル": ["最良", "Top25%", "中央値", "Top75%", "最悪", "平均(参考)"],
        "合計費用 (m)": [f"{int(cost):,} m" for cost in st.session_state.cost_quantiles],
        "装備破壊回数": [f"{count:.1f} 回" for count in st.session_state.destruction_quantiles]
    })
    
    # テーブル表示
    st.dataframe(results_df, use_container_width=True, hide_index=True)

    cost_table_df = st.session_state.cost_table.copy()
    # "星" 列の変換処理
    cost_table_df["星"] = cost_table_df["星"].astype(int)
    cost_table_df["星"] = cost_table_df["星"].astype(str) + " → " + (cost_table_df["星"].astype(int) + 1).astype(str)
    # "成功率", "維持率", "破壊率" の変換処理
    for col in ["成功率", "維持率", "破壊率"]:
        cost_table_df[col] = cost_table_df[col].mul(100).round(2).astype(str) + "%"

    # テーブルを表示
    st.write("##### (参考)今回のスタフォテーブル")
    st.dataframe(cost_table_df, use_container_width=True, hide_index=True)