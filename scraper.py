"""豆瓣电影 Top250 爬虫：抓取排名、名称、年份、地区、评分等信息。"""
from __future__ import annotations

import csv
import random
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://movie.douban.com/top250"
DATA_DIR = Path(__file__).resolve().parent / "data"
CSV_PATH = DATA_DIR / "douban_top250.csv"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

FIELDS = ["rank", "title", "year", "region", "genres", "rating", "quote", "link"]


def fetch_page(start: int) -> str:
    """抓取一页（25 条）Top250 列表，start 为起始名次。"""
    resp = requests.get(BASE_URL, params={"start": start},
                        headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_page(html: str) -> list[dict]:
    """解析一页 HTML，返回电影记录列表。"""
    soup = BeautifulSoup(html, "html.parser")
    movies = []
    for item in soup.select("div.item"):
        rank = item.select_one("em").get_text(strip=True)
        title = item.select_one("span.title").get_text(strip=True)
        rating = item.select_one("span.rating_num").get_text(strip=True)
        link = item.select_one("div.hd a")["href"]

        # 信息行形如：1994 / 美国 / 犯罪 剧情
        info_line = item.select_one("div.bd p").get_text("\n", strip=True)
        parts = [p.strip() for p in info_line.split("\n")[1].split("/")]
        year = re.sub(r"\D", "", parts[0]) if parts else ""
        region = parts[1] if len(parts) > 1 else ""
        genres = parts[2] if len(parts) > 2 else ""

        quote_node = item.select_one("span.inq")
        quote = quote_node.get_text(strip=True) if quote_node else ""

        movies.append({
            "rank": int(rank),
            "title": title,
            "year": year,
            "region": region,
            "genres": genres,
            "rating": float(rating),
            "quote": quote,
            "link": link,
        })
    return movies


def scrape(pages: int = 10, delay: tuple = (1.0, 2.5)) -> list[dict]:
    """抓取前 pages 页数据（默认 10 页 = 250 条），随机延时防止请求过快。"""
    movies: list[dict] = []
    for page in range(pages):
        start = page * 25
        print(f"正在抓取第 {page + 1}/{pages} 页 (start={start}) ...")
        movies.extend(parse_page(fetch_page(start)))
        if page < pages - 1:
            time.sleep(random.uniform(*delay))
    return movies


def save_csv(movies: list[dict], path: Path = CSV_PATH) -> Path:
    """保存为 CSV（utf-8-sig 方便 Excel 直接打开）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(movies)
    print(f"已保存 {len(movies)} 条记录到 {path}")
    return path


if __name__ == "__main__":
    save_csv(scrape())
