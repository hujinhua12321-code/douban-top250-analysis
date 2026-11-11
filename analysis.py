"""数据分析与可视化：读取 CSV，输出统计报告并生成图表。"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 无界面环境下也能正常出图
import matplotlib.pyplot as plt
import pandas as pd

# 中文显示（Windows 优先微软雅黑，其他系统回退黑体类字体）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).resolve().parent
CHART_DIR = BASE_DIR / "charts"


def load_data(csv_path: Path) -> pd.DataFrame:
    """读取并清洗数据：类型转换、剔除缺失关键字段的记录。"""
    df = pd.read_csv(csv_path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["title", "year", "rating"]).reset_index(drop=True)
    df["year"] = df["year"].astype(int)
    return df


def show_summary(df: pd.DataFrame) -> None:
    """打印基础统计报告。"""
    print("=" * 46)
    print(f"样本总量：{len(df)} 部")
    print(f"评分范围：{df['rating'].min()} ~ {df['rating'].max()}，"
          f"平均评分 {df['rating'].mean():.2f}")
    print(f"年份范围：{df['year'].min()} ~ {df['year'].max()}")
    print("\n上榜数量最多的地区 Top5：")
    print(df["region"].value_counts().head(5).to_string())
    print("\n评分最高的 5 部电影：")
    top5 = df.nlargest(5, "rating")[["rank", "title", "year", "rating"]]
    print(top5.to_string(index=False))
    print("=" * 46)


def plot_rating_distribution(df: pd.DataFrame, out_dir: Path) -> Path:
    """评分分布直方图。"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["rating"], bins=16, color="#4C78A8", edgecolor="white")
    ax.set_title("豆瓣 Top250 评分分布")
    ax.set_xlabel("评分")
    ax.set_ylabel("电影数量")
    fig.tight_layout()
    path = out_dir / "rating_distribution.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_decade_trend(df: pd.DataFrame, out_dir: Path) -> Path:
    """各年代上榜电影数量分布。"""
    decade = (df["year"] // 10 * 10).value_counts().sort_index()
    decade.index = decade.index.map(lambda y: f"{y}s")
    fig, ax = plt.subplots(figsize=(8, 5))
    decade.plot.bar(ax=ax, color="#F58518", edgecolor="white")
    ax.set_title("豆瓣 Top250 上榜电影年代分布")
    ax.set_xlabel("年代")
    ax.set_ylabel("电影数量")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    path = out_dir / "decade_trend.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_top_regions(df: pd.DataFrame, out_dir: Path, top_n: int = 8) -> Path:
    """上榜数量最多的地区横向条形图。"""
    regions = df["region"].value_counts().head(top_n).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    regions.plot.barh(ax=ax, color="#54A24B", edgecolor="white")
    ax.set_title(f"上榜数量最多的地区 Top{top_n}")
    ax.set_xlabel("电影数量")
    fig.tight_layout()
    path = out_dir / "top_regions.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def analyze(csv_path: Path) -> list[Path]:
    """完整分析流程：清洗 -> 统计 -> 可视化，返回生成的图表路径列表。"""
    df = load_data(csv_path)
    show_summary(df)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    charts = [
        plot_rating_distribution(df, CHART_DIR),
        plot_decade_trend(df, CHART_DIR),
        plot_top_regions(df, CHART_DIR),
    ]
    for p in charts:
        print(f"图表已生成：{p}")
    return charts
