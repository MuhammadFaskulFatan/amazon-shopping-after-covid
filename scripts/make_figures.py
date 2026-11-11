import textwrap
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

src = Path("results")
out = Path("figures")
out.mkdir(parents=True, exist_ok=True)

NAVY, GREY, ORANGE, TEAL, DARK = "#1F4E79", "#9AA5B1", "#C55A11", "#2F7D6D", "#5B6470"
INK = "#1A1A1A"
plt.rcParams.update({
    "font.family": ["Arial", "Liberation Sans", "DejaVu Sans"], "font.size": 12, "axes.edgecolor": "#444444",
    "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 13,
})
SOURCE = ("Data: Open e-commerce 1.0 (Berke et al., 2024, CC BY 4.0). 5,014 US Amazon accounts, Jan 2018 to Oct 2022, "
          "gift cards removed. Amounts in 2019 dollars (US CPI-U, BLS via FRED).")


def frame(fig, num, title, subtitle, how):
    h = fig.get_figheight()
    fig.text(0.045, 1 - 0.28 / h, f"Figure {num}.  {title}", fontsize=18, fontweight="bold", color=INK, va="top")
    fig.text(0.045, 1 - 0.68 / h, subtitle, fontsize=12, color=DARK, va="top")
    fig.text(0.045, 0.66 / h, textwrap.fill("How to read this: " + how, 118), fontsize=10.5, color=INK, va="bottom",
             linespacing=1.35)
    fig.text(0.045, 0.2 / h, textwrap.fill(SOURCE, 160), fontsize=8.5, color="#6B7280", va="bottom")


def new(w=10, h=6.9):
    return plt.figure(figsize=(w, h), facecolor="white")


def spread(vals, gap):
    # push label positions apart so names do not overlap
    order = np.argsort(vals)
    pos = np.array(vals, dtype=float)
    for k in range(1, len(order)):
        a, b = order[k - 1], order[k]
        if pos[b] - pos[a] < gap:
            pos[b] = pos[a] + gap
    shift = (np.mean(vals) - np.mean(pos))
    return pos + shift


# ---------------- Figure 1 ----------------
head = pd.read_csv(src / "01_headline.csv")
q = pd.read_csv(src / "01b_quarterly.csv")
r20 = head[head["year"] == 2020].iloc[0]
g = (1 + r20["vs_2019_pct"] / 100) / (1 + r20["vs_old_trend_pct"] / 100) - 1       # 2018 -> 2019 growth
q["yr"] = q["q"].str[:4].astype(int)
q["qn"] = q["q"].str[-1].astype(int)
y19 = q[q["yr"] == 2019].set_index("qn")["real_spend_per_customer"]
q["path"] = np.where(q["yr"] >= 2020, q["qn"].map(y19) * (1 + g) ** (q["yr"] - 2019), np.nan)
x = np.arange(len(q))
i20 = int(q.index[q["q"] == "2020Q1"][0])

fig = new()
ax = fig.add_axes([0.085, 0.27, 0.78, 0.55])
ax.plot(x, q["real_spend_per_customer"], color=NAVY, lw=3, zorder=3)
xp = x[i20 - 1:]
pp = np.r_[q["real_spend_per_customer"].iloc[i20 - 1], q["path"].iloc[i20:].values]
ax.plot(xp, pp, color=DARK, lw=2.2, ls=(0, (5, 3)), zorder=2)
act = q["real_spend_per_customer"].values[i20 - 1:]
ax.fill_between(xp, pp, act, where=act >= pp, color=NAVY, alpha=0.13, zorder=1, interpolate=True)
ax.axvline(i20 + 0.5, color="#444444", lw=1, ls=":")
ax.text(i20 + 0.35, 590, "March 2020:\nCOVID begins", fontsize=11, va="top", ha="right", color=INK)
ax.set_ylim(180, 600)
ax.set_xlim(-0.4, len(q) - 0.4)
ax.set_xticks([i for i in range(len(q)) if q["qn"].iloc[i] == 1])
ax.set_xticklabels(q["yr"][q["qn"] == 1].astype(str))
ax.tick_params(axis="x", length=0, labelsize=12)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"${v:,.0f}"))
ax.grid(axis="y", color="#E5E7EB", lw=0.8)
ax.set_axisbelow(True)
ax.text(len(q) - 0.2, q["real_spend_per_customer"].iloc[-1], " Actual", color=NAVY, fontsize=12, va="center",
        fontweight="bold")
ax.text(len(q) - 0.2, q["path"].iloc[-1] - 12, " Old\n path", color=DARK, fontsize=11, va="center")
i21 = int(q.index[q["q"] == "2021Q2"][0])
ax.annotate("2021: about 38% above\nthe old path", (i21, q["real_spend_per_customer"].iloc[i21]),
            (i21 - 0.7, 592), fontsize=11.5, color=NAVY, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=NAVY, lw=1))
i22 = int(q.index[q["q"] == "2022Q2"][0])
ax.annotate("2022: about 11% above,\nmostly faded", (i22, q["real_spend_per_customer"].iloc[i22]),
            (len(q) - 0.5, 262), fontsize=11.5, ha="right", color=NAVY, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=NAVY, lw=1))
ax.annotate("Q4 peaks are\nholiday shopping", (3, q["real_spend_per_customer"].iloc[3]), (0.2, 330), fontsize=10.5,
            color=DARK, arrowprops=dict(arrowstyle="-", color=DARK, lw=0.8))
ax.text(i20 + 0.9, 236, "Shaded area: the extra\nabove the old path", fontsize=10.5, color=NAVY)
frame(fig, 1, "Spending was already climbing before COVID",
      "Average real spend per customer, per quarter (2019 dollars)",
      "The solid line is what customers actually spent. The dashed line is where spending would have been from 2020 "
      "if it had kept growing at its 2018 to 2019 pace (about 13% a year). The 38% and 11% are for January to September.")
fig.savefig(out / "figure1_trend.png", dpi=200)
plt.close(fig)

# ---------------- Figure 2 ----------------
tr = pd.read_csv(src / "02b_trajectories.csv")
pers = pd.read_csv(src / "02_persistence.csv")
kept = pers.iloc[0]["uplift_still_there_pct"]
up = tr[tr["group"] == "Spent more in 2020"]
dn = tr[tr["group"] == "Did not spend more in 2020"]
fig = new()
ax = fig.add_axes([0.085, 0.27, 0.62, 0.55])
for d, c in ((up, NAVY), (dn, ORANGE)):
    ax.fill_between(d["year"], d["lo"], d["hi"], color=c, alpha=0.15)
    ax.plot(d["year"], d["index_2018_19"], color=c, lw=3, marker="o", ms=7, zorder=3)
ax.axhline(100, color="#444444", lw=1, ls=":")
ax.text(2017.9, 120, "Normal level (100)", fontsize=10.5, color=DARK)
ax.set_xticks([2018, 2019, 2020, 2021, 2022])
ax.set_xlim(2017.8, 2022.3)
ax.set_ylim(20, 270)
ax.tick_params(axis="x", length=0, labelsize=12)
ax.grid(axis="y", color="#E5E7EB", lw=0.8)
ax.set_axisbelow(True)
ax.set_ylabel("Spend compared with normal (100 = normal)", fontsize=11.5)
v_up20 = up[up["year"] == 2020]["index_2018_19"].iloc[0]
v_dn20 = dn[dn["year"] == 2020]["index_2018_19"].iloc[0]
ax.text(2020, v_up20 + 9, f"{v_up20/100:.1f}\u00d7 normal", ha="center", fontsize=11.5, color=NAVY, fontweight="bold")
ax.text(2020, v_dn20 - 19, f"{v_dn20:.0f}% of normal", ha="center", fontsize=11.5, color=ORANGE, fontweight="bold")
v_up22 = up[up["year"] == 2022]["index_2018_19"].iloc[0]
v_dn22 = dn[dn["year"] == 2022]["index_2018_19"].iloc[0]
fig.text(0.725, 0.64, f"Spent more in 2020\n({up['customers_pct'].iloc[0]:.0f}% of customers)", color=NAVY,
         fontsize=12.5, fontweight="bold", va="center")
fig.text(0.725, 0.56, f"Still {v_up22/100:.1f}\u00d7 normal in 2022,\nkeeping {kept:.0f}% of the extra", color=NAVY,
         fontsize=11.5, va="center")
fig.text(0.725, 0.40, f"Did not\n({dn['customers_pct'].iloc[0]:.0f}% of customers)", color=ORANGE,
         fontsize=12.5, fontweight="bold", va="center")
fig.text(0.725, 0.325, "Back to normal by 2022", color=ORANGE, fontsize=11.5, va="center")
frame(fig, 2, "Two in three customers changed their habits and kept them",
      "Real spend per customer, compared with each group's own normal level in 2018 and 2019",
      "Each line follows one group of customers. 100 means the group's normal level; 200 means double. "
      "The group is customers who spent more in 2020 than they normally did (blue) or did not (orange). "
      "Shaded bands show how much the lines could move by chance.")
fig.savefig(out / "figure2_habits.png", dpi=200)
plt.close(fig)

# ---------------- Figure 3 ----------------
dr = pd.read_csv(src / "03_growth_drivers.csv")
dr["pct"] = (np.exp(dr["log_change_pct"] / 100) - 1) * 100
drv = ["Share of customers active", "Shopping days per active customer", "Spend per shopping day"]
v20 = [dr[(dr["vs 2019"] == 2020) & (dr["driver"] == d)]["pct"].iloc[0] for d in drv]
v22 = [dr[(dr["vs 2019"] == 2022) & (dr["driver"] == d)]["pct"].iloc[0] for d in drv]
dec = [1, 0, 1]
fig = new()
ax = fig.add_axes([0.06, 0.27, 0.90, 0.55])
xs = np.arange(3)
b1 = ax.bar(xs - 0.2, v20, width=0.36, color="#8FB1D1")
b2 = ax.bar(xs + 0.2, v22, width=0.36, color=NAVY)
for bars, vals in ((b1, v20), (b2, v22)):
    for b, v, d in zip(bars, vals, dec):
        s = f"{'+' if v >= 0 else chr(8722)}{abs(v):.{d}f}%"
        ax.text(b.get_x() + b.get_width() / 2, v + (2.0 if v >= 0 else -2.0), s, ha="center",
                va="bottom" if v >= 0 else "top", fontsize=13, fontweight="bold", color=INK)
ax.axhline(0, color="#444444", lw=1)
ax.set_xticks(xs)
ax.set_xticklabels(["More customers\nshopped at all", "Active customers\nshopped on more days",
                    "Spend on each\nshopping day"], fontsize=12.5)
ax.tick_params(axis="x", length=0, pad=8)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.set_ylim(-12, 62)
ax.text(2.45, 55, "2020 vs 2019", color="#6B93BD", fontsize=12.5, fontweight="bold", ha="right")
ax.text(2.45, 49, "2022 vs 2019", color=NAVY, fontsize=12.5, fontweight="bold", ha="right")
h20, h22 = head.set_index("year").loc[2020, "vs_2019_pct"], head.set_index("year").loc[2022, "vs_2019_pct"]
ax.text(-0.45, 52, f"Together, spend per customer rose\n{h20:.0f}% in 2020 and {h22:.0f}% in 2022",
        fontsize=12, color=INK, va="top")
frame(fig, 3, "They shop more often, not with bigger orders",
      "Change compared with 2019, January to September, in three parts",
      "Spend per customer = how many customers shop \u00d7 how many days they shop \u00d7 how much they spend each day. "
      "A shopping day is any day with at least one order. The tall bars on shopping days are what drove growth.")
fig.savefig(out / "figure3_drivers.png", dpi=200)
plt.close(fig)

# ---------------- Figure 4 ----------------
cat = pd.read_csv(src / "04_categories.csv").set_index("name")
panels = [
    ("1.  Gained share and kept it", NAVY,
     {"Medication": "Medication", "Coffee": "Coffee", "Food": "Food", "Drink Flavored": "Flavored drinks",
      "Cleaning Agent": "Cleaning products"}),
    ("2.  Gained share in 2020, then mostly gave it back", ORANGE,
     {"Chair": "Chairs", "Toy Building Block": "Building blocks",
      "Thermometer": "Thermometers", "String Light": "String lights"}),
    ("3.  Lost share in 2020, then got it back", TEAL,
     {"Dress": "Dresses", "Shirt": "Shirts", "Swimwear": "Swimwear", "Sandal": "Sandals"}),
    ("4.  Losing share for years", DARK,
     {"Books": "Books", "Physical Movie": "Physical movies",
      "Physical Video Game Software": "Physical video games"}),
]
cols = [f"share_{y}" for y in range(2018, 2023)]
H4 = 9.4
fig = new(11, H4)
pos = [(0.075, 0.585), (0.57, 0.585), (0.075, 0.235), (0.57, 0.235)]
for (title, col, items), (px, py) in zip(panels, pos):
    ax = fig.add_axes([px, py, 0.265, 0.255])
    ends, names = [], []
    for k, lab in items.items():
        s_ = cat.loc[k, cols].astype(float).values
        idx = s_ / s_[1] * 100
        ax.plot(range(2018, 2023), idx, color=col, lw=2.2, alpha=0.9)
        ax.scatter([2022], [idx[-1]], color=col, s=20, zorder=3)
        ends.append(idx[-1])
        names.append(lab)
    ax.axhline(100, color="#999999", lw=0.8, ls=":")
    ax.axvline(2020, color="#CCCCCC", lw=0.8)
    ax.set_xlim(2017.8, 2022.2)
    ax.set_xticks([2018, 2020, 2022])
    ax.set_xticks([2019, 2021], minor=True)
    ax.tick_params(axis="x", labelsize=11, length=3)
    ax.tick_params(axis="y", labelsize=10.5)
    ax.grid(axis="y", color="#EEEEEE", lw=0.7)
    ax.set_axisbelow(True)
    y0, y1 = ax.get_ylim()
    lp = spread(ends, (y1 - y0) * 0.1)
    for nm, e, p in zip(names, ends, lp):
        ax.plot([2022.05, 2022.35], [e, p], color=col, lw=0.8, clip_on=False)
        ax.text(2022.4, p, nm, fontsize=10.5, color=col, va="center", fontweight="bold", clip_on=False)
    ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", color=INK, pad=10, x=-0.1)
fig.text(0.045, 1 - 0.28 / H4, "Figure 4.  Most categories stayed put. These are the ones that moved", fontsize=18,
         fontweight="bold", color=INK, va="top")
fig.text(0.045, 1 - 0.68 / H4, "Share of total spend by category, 2018 to 2022 (2019 = 100). Categories bought by 100+ "
         "customers every year.", fontsize=12, color=DARK, va="top")
fig.text(0.045, 0.66 / H4, textwrap.fill(
    "How to read this: each line is one category's share of total spend, set to 100 in 2019. A line at 200 means the "
    "category's share doubled. Share is not dollars: everything was growing, so a category can lose share and still "
    "grow in dollars (spend on shoes rose 42%, slower than the 60% average).", 128),
         fontsize=10.5, color=INK, va="bottom", linespacing=1.35)
fig.text(0.045, 0.2 / H4, textwrap.fill(SOURCE, 170), fontsize=8.5, color="#6B7280", va="bottom")
fig.savefig(out / "figure4_categories.png", dpi=200)
plt.close(fig)

# ---------------- Figure 5 ----------------
rfm = pd.read_csv(src / "05_rfm.csv")
nm = {"Champions": "Best customers\n(Champions)", "Loyal": "Regular customers\n(Loyal)",
      "At risk": "Quiet high spenders\n(At risk)", "Need attention": "Occasional customers\n(Need attention)",
      "Recent, low frequency": "Recent but light shoppers\n(Recent, low frequency)",
      "Hibernating": "Rare shoppers\n(Hibernating)"}
rfm = rfm.sort_values("pct_of_spend", ascending=True).reset_index(drop=True)
fig = new(10, 6.9)
ax = fig.add_axes([0.25, 0.27, 0.72, 0.55])
yy = np.arange(len(rfm))
ax.barh(yy + 0.19, rfm["pct_of_customers"], height=0.36, color=GREY)
ax.barh(yy - 0.19, rfm["pct_of_spend"], height=0.36, color=NAVY)
for i, r in rfm.iterrows():
    ax.text(r["pct_of_customers"] + 0.8, i + 0.19, f"{r['pct_of_customers']:.0f}%", va="center", fontsize=11.5, color=DARK)
    ax.text(r["pct_of_spend"] + 0.8, i - 0.19, f"{r['pct_of_spend']:.0f}%", va="center", fontsize=12, color=NAVY,
            fontweight="bold")
ax.set_yticks(yy)
ax.set_yticklabels([nm[s] for s in rfm["segment"]], fontsize=11.5, linespacing=1.15)
ax.tick_params(axis="y", length=0)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.set_xlim(0, 100)
ar = rfm[rfm["segment"] == "At risk"].iloc[0]
ia = int(rfm.index[rfm["segment"] == "At risk"][0])
ax.text(14, ia - 0.02, f"{ar['customers']:.0f} customers, about USD {round(ar['median_spend'], -2):,.0f} a year each,\n"
        f"quiet for about {ar['avg_recency_days']/7:.0f} weeks. The best group to win back.", fontsize=10.5, color=ORANGE,
        va="center", fontweight="bold")
ic = int(rfm.index[rfm["segment"] == "Champions"][0])
ax.text(66, ic + 0.0, "26% of customers\nbring more than half\nof all spend", fontsize=11.5, color=NAVY, va="center",
        fontweight="bold")
h1 = plt.Rectangle((0.0, 0.0), 1, 1, color=GREY)
h2 = plt.Rectangle((0.0, 0.0), 1, 1, color=NAVY)
ax.legend([h1, h2], ["% of customers in the group", "% of all spend"], loc="lower right", frameon=False, fontsize=11.5)
frame(fig, 5, "A quarter of customers bring more than half of the spend",
      "Customers grouped by how recently, how often and how much they bought (RFM), last 12 months to 30 Sep 2022",
      "Grey bar: how many customers are in the group. Blue bar: how much of the spend they bring. 3% of customers made "
      "no purchase in the last 12 months and are not shown. Top 1 in 5 customers = 58% of spend.")
fig.savefig(out / "figure5_customers.png", dpi=200)
plt.close(fig)
print("done")
