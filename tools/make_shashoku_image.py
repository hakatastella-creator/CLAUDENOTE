#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""社食候補のまとめ表を1枚の画像(PNG)にする。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 日本語フォント設定
fp = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
font_manager.fontManager.addfont(fp)
jp = font_manager.FontProperties(fname=fp)
plt.rcParams["font.family"] = jp.get_name()

fig = plt.figure(figsize=(11.5, 11), dpi=160)
fig.patch.set_facecolor("white")

# タイトル
fig.text(0.5, 0.975, "博多ステラ歯科・矯正歯科クリニック　社食候補まとめ",
         ha="center", va="top", fontsize=19, fontweight="bold", color="#1f3a5f")
fig.text(0.5, 0.945,
         "福岡市博多区上川端町（櫛田神社前駅すぐ）／ スタッフ約6人体制・昼1食・月20営業日で試算",
         ha="center", va="top", fontsize=10.5, color="#444")

NAVY = "#1f3a5f"
ROW_A = "#eef4fb"
ROW_B = "#fafafa"
HEAD_BG = "#1f3a5f"


def make_table(ax, title, emoji_title, cols, rows, widths):
    ax.axis("off")
    ax.set_title(emoji_title, fontsize=14, fontweight="bold",
                 color=NAVY, loc="left", pad=10)
    tbl = ax.table(cellText=rows, colLabels=cols, cellLoc="center",
                   loc="center", colWidths=widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.scale(1, 1.7)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#cfd8e3")
        if r == 0:
            cell.set_facecolor(HEAD_BG)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(ROW_A if r % 2 else ROW_B)
        if c == 0:
            cell.set_text_props(ha="left")
            cell.PAD = 0.03
    return tbl


# 部門① 持ってくる弁当
ax1 = fig.add_axes([0.04, 0.60, 0.92, 0.27])
cols1 = ["サービス", "1食目安", "安", "近", "おいしい・特徴"]
rows1 = [
    ["くるめし弁当", "500円〜", "◎", "◎", "ワンコイン〜会議弁当。コスパ重視"],
    ["ごちクル", "1,000円前後", "△", "◎", "有名店・ミシュランも。約1,900商品"],
    ["博多松美屋", "法人価格", "〇", "◎", "会議用仕出しに強い"],
    ["マンジャ(MANGIA)", "中価格帯", "〇", "◎", "手作り弁当・オードブル・寿司"],
    ["二兎屋", "中価格帯", "〇", "◎", "会社昼食のまとめ発注向け"],
]
make_table(ax1, "", "部門① 持ってきてくれる（できたて宅配弁当）",
           cols1, rows1, [0.20, 0.14, 0.06, 0.06, 0.54])

# 部門② チンして食べる
ax2 = fig.add_axes([0.04, 0.27, 0.92, 0.27])
cols2 = ["サービス", "1食/料金目安", "安", "近", "おいしい・特徴"]
rows2 = [
    ["オフィスおかん", "1品100円", "◎", "◎", "管理栄養士監修・24h・3名〜OK"],
    ["office nosh", "500円以下", "◎", "〇", "弁当まるごとチンで1食完結"],
    ["プレミアムフローズン", "月39,600円〜", "〇", "◎", "冷凍弁当設置・補充集金込み"],
    ["OFFICE DE YASAI", "1品100円〜", "◎", "〇", "野菜・サラダ中心で健康志向"],
    ["nosh(個人宅配)", "620円〜(最安499)", "〇", "◎", "メニュー豊富・糖質塩分配慮"],
]
make_table(ax2, "", "部門② 電子レンジでチンして食べる（冷凍・チルド）",
           cols2, rows2, [0.20, 0.16, 0.06, 0.06, 0.52])

# 6人試算＆結論
ax3 = fig.add_axes([0.04, 0.045, 0.92, 0.17])
ax3.axis("off")
ax3.set_title("6人体制の月額めやす ／ おすすめ", fontsize=14,
              fontweight="bold", color=NAVY, loc="left", pad=8)
cols3 = ["用途", "おすすめ", "月額めやす"]
rows3 = [
    ["安く毎日まとめて（①）", "くるめし弁当(ワンコイン)", "約60,000円＋配送料"],
    ["無駄なく置いておく（②）", "オフィスプレミアムフローズン", "39,600円〜"],
    ["少人数で柔軟に（②）", "オフィスおかん（3名〜）", "5〜6万円台＋喫食分"],
]
t3 = ax3.table(cellText=rows3, colLabels=cols3, cellLoc="center",
               loc="center", colWidths=[0.34, 0.40, 0.26])
t3.auto_set_font_size(False)
t3.set_fontsize(9.5)
t3.scale(1, 1.7)
for (r, c), cell in t3.get_celld().items():
    cell.set_edgecolor("#cfd8e3")
    if r == 0:
        cell.set_facecolor("#2e7d32")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#eef7ee" if r % 2 else "#fafafa")

fig.text(0.04, 0.022,
         "※ 6人は置き型社食がいちばんハマる規模。固定費の低い置き型をベースに、忙しい日は①弁当をスポット併用が現実的。",
         ha="left", fontsize=9, color="#555")
fig.text(0.96, 0.005, "評価: ◎>〇>△　価格・配送料・最低注文数は要確認（更新 2026-05-31）",
         ha="right", fontsize=8, color="#999")

out = "/home/user/CLAUDENOTE/docs/shashoku/summary.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
