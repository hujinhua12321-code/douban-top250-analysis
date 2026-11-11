"""主流程：爬虫 -> 清洗 -> 分析 -> 可视化。

用法：
    python main.py            # 离线模式：使用已有 CSV（没有则用内置示例数据）
    python main.py --scrape   # 联网模式：重新抓取豆瓣 Top250 后分析
"""
import shutil
import sys
from pathlib import Path

from analysis import analyze
from scraper import CSV_PATH, save_csv, scrape

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_PATH = BASE_DIR / "data" / "sample_top250.csv"


def main():
    if "--scrape" in sys.argv:
        save_csv(scrape())
    elif not CSV_PATH.exists():
        print("未找到爬取结果，本次使用内置示例数据"
              "（可运行 python main.py --scrape 联网抓取完整数据）")
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SAMPLE_PATH, CSV_PATH)
    analyze(CSV_PATH)


if __name__ == "__main__":
    main()
