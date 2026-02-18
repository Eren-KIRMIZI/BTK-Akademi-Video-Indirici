import requests
from yt_dlp import YoutubeDL
from os import system
from time import sleep

ACCESS_TOKEN = ""
BASE_URL = "https://www.btkakademi.gov.tr/api/service/v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}

CINEMA8_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Referer": "https://cinema8.com/",
    "Origin": "https://cinema8.com",
}


def register_course(course_id):
    url = f"{BASE_URL}/course/registration/register/{course_id}?language=tr"
    response = requests.post(url, headers=HEADERS, json={"demandForm": {}})
    return response.json().get("status", "Error")


def get_syllabus(course_id):
    url = f"{BASE_URL}/public/51/course/details/program/syllabus/{course_id}?language=tr"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def select_option(options, prompt):
    for index, option in enumerate(options, start=1):
        print(f"{index}- {option['title']}")
    choice = int(input(f"\n{prompt}: ")) - 1
    return choice


def start_lesson(course_id, lesson_id):
    url = f"{BASE_URL}/course/deliver/start/{lesson_id}"
    response = requests.post(url, headers=HEADERS, json={"programId": int(course_id)})
    data = response.json()
    return data.get("remoteCourseReference", "")


def get_video_url(video_id):
    """
    cinema8 API'den video bilgilerini çeker.
    Önce flavor endpoint'ini dener, başarısız olursa
    doğrudan video sayfası URL'ini döner.
    """
    api_url = f"https://cinema8.com/api/v1/uscene/rawvideo/flavor/{video_id}"
    try:
        response = requests.get(api_url, headers=CINEMA8_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        name = data.get("name", "video.mp4")
        hls_url = data.get("hlsUrl", "")
        if hls_url:
            return name, hls_url
    except Exception as e:
        print(f"Flavor API hatası: {e}")

    # Fallback: cinema8 video sayfasını yt-dlp ile dene
    fallback_url = f"https://cinema8.com/video/{video_id}"
    return "video.mp4", fallback_url


def get_cinema8_cookies(video_id):
    """
    cinema8 video sayfasını ziyaret ederek çerez alır.
    Bu, CDN 403 hatasını aşmak için gereklidir.
    """
    session = requests.Session()
    page_url = f"https://cinema8.com/video/{video_id}"
    try:
        session.get(page_url, headers=CINEMA8_HEADERS, timeout=10)
    except Exception as e:
        print(f"Cookie alınamadı: {e}")
    return session.cookies.get_dict()


def build_ydl_opts(output_template, cookies: dict, referer: str):
    """yt-dlp ayarlarını oluşturur."""
    http_headers = {
        "User-Agent": CINEMA8_HEADERS["User-Agent"],
        "Referer": referer,
        "Origin": "https://cinema8.com",
    }

    # Çerezleri tek satıra dönüştür
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    if cookie_str:
        http_headers["Cookie"] = cookie_str

    return {
        "outtmpl": output_template,
        "http_headers": http_headers,
        "hls_prefer_native": False,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "retries": 5,
        "fragment_retries": 5,
        "concurrent_fragment_downloads": 4,
        "quiet": False,
        "no_warnings": False,
    }


def download_video(video_name, video_url, video_id):
    if not video_url:
        print("Video URL bulunamadı!")
        return

    output_template = video_name.replace(".mp4", "") + ".mp4"
    referer = f"https://cinema8.com/video/{video_id}"

    print("Oturum çerezleri alınıyor...")
    cookies = get_cinema8_cookies(video_id)

    opts = build_ydl_opts(output_template, cookies, referer)

    with YoutubeDL(opts) as ydl:
        print(f"\n{video_name} indiriliyor...\n")
        try:
            ydl.download([video_url])
            print("\nİndirme tamamlandı!")
        except Exception as e:
            print(f"\nHata: {e}")
            print("\nAlternatif yöntem deneniyor (cinema8 sayfa URL'i)...")
            fallback_url = f"https://cinema8.com/video/{video_id}"
            opts_fallback = build_ydl_opts(output_template, cookies, referer)
            with YoutubeDL(opts_fallback) as ydl2:
                ydl2.download([fallback_url])


# --- Ana akış ---

course_url = input("Kurs URL: ").strip()
course_id = course_url.split("-")[-1]
system("cls||clear")

print("Kursa kaydolma durumu: ", register_course(course_id))
sleep(1.5)
system("cls||clear")

syllabus = get_syllabus(course_id)
section_index = select_option(syllabus, "Bölüm seçin")
system("cls||clear")

lesson_index = select_option(syllabus[section_index]["courses"], "Ders seçin")
lesson_id = str(syllabus[section_index]["courses"][lesson_index]["id"])
system("cls||clear")

video_id = start_lesson(course_id, lesson_id)
if not video_id:
    print("ACCESS_TOKEN eksik veya geçersiz!")
    sleep(2)
    exit()

video_name, video_url = get_video_url(video_id)
print(f"Video ID  : {video_id}")
print(f"Video Adı : {video_name}")
print(f"Video URL : {video_url}\n")

download_video(video_name, video_url, video_id)
