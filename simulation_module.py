import pandas as pd
import numpy as np

def compute_cost(star, equipment_level=250, shining_cost=False):
    denom = 200
    if star == 17:
        denom = 150
    elif star == 18:
        denom = 70
    elif star == 19:
        denom = 45
    elif star == 21:
        denom = 125
    cost = (equipment_level ** 3 * (star + 1) ** 2.7) / denom
    cost = cost//1_000_000
    if shining_cost:
        cost *= 0.7
    return cost


def make_df(equipment_level=250, shining_cost=False, shining_15to16=False, shining_destroy=False):
    stars = list(range(15, 30))
    # 各星に対して費用を計算（小数点以下は四捨五入して整数に）
    costs = [round(compute_cost(star, equipment_level, shining_cost=shining_cost)) for star in stars]

    # スタフォ分岐（星15～29に対応）
    success_rate = [0.30, 0.30, 0.15, 0.15, 0.15, 0.30, 0.15, 0.15, 0.10, 0.10, 0.10, 0.07, 0.05, 0.03, 0.01]
    retention_rate = [0.679, 0.679, 0.782, 0.782, 0.765, 0.595, 0.7225, 0.68, 0.72, 0.72, 0.72, 0.744, 0.76, 0.776, 0.792]
    destroy_rate = [0.021, 0.021, 0.068, 0.068, 0.085, 0.105, 0.1275, 0.17, 0.18, 0.18, 0.18, 0.186, 0.19, 0.194, 0.198]

    # shining_destroy のオプション: 全ての星の破壊率を0.7倍にし、その分を維持率に追加
    if shining_destroy:
        for i in range(len(stars)):
            original_destroy = destroy_rate[i]
            destroy_rate[i] = original_destroy * 0.7
            retention_rate[i] += original_destroy * 0.3

    # shining_15to16 のオプション: 星15の成功率を1.0、維持率と破壊率を0に変更
    if shining_15to16:
        success_rate[0] = 1.0
        retention_rate[0] = 0.0
        destroy_rate[0] = 0.0

    data = {
        "星": stars,
        "成功率": success_rate,
        "維持率": retention_rate,
        "破壊率": destroy_rate,
        "費用(m)": costs
    }
    df = pd.DataFrame(data)
    return df


def simulate_star_enhancement(target_star,
                              equipment_level=250,
                              penalty=5000,
                              simulations=1000,
                              shining_cost=False,
                              shining_15to16=False,
                              shining_destroy=False,
                              seed=None,
                              verbose=False
                              ):
    """
    指定した目標星（例：30）に到達するまでのシミュレーションを行います。
    各試行は、現在の星に対応する成功率・維持率・破壊率で判定し、
      ・成功: 星が+1される
      ・維持: 星の数は変わらず（費用だけ消費）
      ・破壊: 破壊ペナルティとして5000加算、星は15にリセット
    を行います。
    1000回のシミュレーション結果（合計費用、破壊回数）をリストとして返します。
    """
    df = make_df(equipment_level=equipment_level,
                 shining_cost=shining_cost,
                 shining_15to16=shining_15to16,
                 shining_destroy=shining_destroy)


    if seed is not None:
        np.random.seed(seed)

    # DataFrameから各パラメータの配列を作成（星15～29が対応）
    cost_arr      = df["費用(m)"].values
    success_arr   = df["成功率"].values
    maintain_arr  = df["維持率"].values
    destruction_arr = df["破壊率"].values

    base_star = 15  # 初期の星
    results = []

    for sim in range(simulations):
        if verbose:
            print(f"{sim}回目の挑戦です")
        current_star = base_star
        total_cost = 0
        destruction_count = 0

        # 目標星に到達するまでループ
        while current_star < target_star:
            idx = current_star - base_star  # 例：星15ならインデックス0
            total_cost += cost_arr[idx]

            r = np.random.rand()
            if r < success_arr[idx]:
                current_star += 1
                if verbose:
                    print(f"成功。星の数={current_star}")
            elif r < success_arr[idx] + maintain_arr[idx]:
                # 維持の場合は何もしない（費用は既に加算済み）
                pass
            else:
                # 破壊の場合はペナルティ加算、カウンタ更新、星15にリセット
                total_cost += penalty
                destruction_count += 1
                current_star = base_star
                if verbose:
                    print("失敗。破壊されました")
        results.append((total_cost, destruction_count))
    return results


def main(target_star_num=22, equipment_level=250, penalty=5000, simulation_num=1000, shining_cost=False, shining_15to16=False, shining_destroy=False):
    # ユーザーから目標星を入力（例：30）
    target_star = target_star_num
    print(target_star)

    # 1000回のシミュレーション実行
    sim_results = simulate_star_enhancement(target_star=target_star,
                                            equipment_level=equipment_level,
                                            penalty=penalty,
                                            simulations=simulation_num,
                                            shining_cost=shining_cost,
                                            shining_15to16=shining_15to16,
                                            shining_destroy=shining_destroy)

    # 結果をDataFrameに変換
    res_df = pd.DataFrame(sim_results, columns=["total_cost", "destruction_count"])

    # 各四分位点（0, 25, 50, 75, 100パーセンタイル）を計算
    percentiles = [0, 25, 50, 75, 100]
    cost_quantiles = np.percentile(res_df["total_cost"], percentiles)
    destruction_quantiles = np.percentile(res_df["destruction_count"], percentiles)

    quantile_df = pd.DataFrame({
    "percentile": percentiles,
    "合計費用 (m)": [f"{int(cost):,} m" for cost in cost_quantiles],
    "装備破壊回数 (回)": [f"{int(count)} 回" for count in destruction_quantiles]
    })

    print("\nシミュレーション結果（四分位ごとの合計費用と破壊回数）:")
    print(quantile_df)
    return cost_quantiles, destruction_quantiles