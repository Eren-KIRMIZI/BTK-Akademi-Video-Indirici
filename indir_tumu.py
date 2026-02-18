import requests
from yt_dlp import YoutubeDL
from os import system, makedirs
from os.path import join
from time import sleep

# ============================================================
#  BTK Akademi > Application > Local Storage > access_token
# ============================================================
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

# ============================================================

def register_course(course_id):
    url = f"{BASE_URL}/course/registration/register/{course_id}?language=tr"
    response = requests.post(url, headers=HEADERS, json={"demandForm": {}})
    return response.json().get("status", "Error")


def get_syllabus(course_id):
    url = f"{BASE_URL}/public/51/course/details/program/syllabus/{course_id}?language=tr"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def start_lesson(course_id, lesson_id):
    url = f"{BASE_URL}/course/deliver/start/{lesson_id}"
    response = requests.post(url, headers=HEADERS, json={"programId": int(course_id)})
    data = response.json()
    return data.get("remoteCourseReference", "")


def get_video_url(video_id):
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
        print(f"  Flavor API hatası: {e}")
    return "video.mp4", f"https://cinema8.com/video/{video_id}"


def get_cinema8_cookies(video_id):
    session = requests.Session()
    try:
        session.get(f"https://cinema8.com/video/{video_id}", headers=CINEMA8_HEADERS, timeout=10)
    except Exception as e:
        print(f"  Cookie alınamadı: {e}")
    return session.cookies.get_dict()


def build_ydl_opts(output_template, cookies, referer):
    http_headers = {
        "User-Agent": CINEMA8_HEADERS["User-Agent"],
        "Referer": referer,
        "Origin": "https://cinema8.com",
    }
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


def sanitize(name):
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(ch, '_')
    return name.strip()


def download_video(output_path, video_url, video_id):
    referer = f"https://cinema8.com/video/{video_id}"
    cookies = get_cinema8_cookies(video_id)

    print("  Oturum çerezleri alınıyor...")
    opts = build_ydl_opts(output_path, cookies, referer)

    with YoutubeDL(opts) as ydl:
        try:
            ydl.download([video_url])
            return True
        except Exception as e:
            print(f"  Hata: {e}")
            print("  Alternatif yöntem deneniyor (cinema8 sayfa URL'i)...")
            fallback_url = f"https://cinema8.com/video/{video_id}"
            try:
                with YoutubeDL(build_ydl_opts(output_path, cookies, referer)) as ydl2:
                    ydl2.download([fallback_url])
                return True
            except Exception as e2:
                print(f"  Alternatif de başarısız: {e2}")
                return False


# ============================================================
#  ANA AKIŞ
# ============================================================

system("cls||clear")
print("=" * 60)
print("   BTK AKADEMİ - TAM KURS İNDİRİCİ")
print("=" * 60)

course_url = input("\nKurs URL: ").strip()
course_id = course_url.split("-")[-1]
system("cls||clear")

print("Kursa kaydolunuyor...")
print("Kayıt durumu:", register_course(course_id))
sleep(1.5)

print("Müfredat alınıyor...")
syllabus = get_syllabus(course_id)

if not syllabus:
    print("Müfredat alınamadı! Token geçersiz veya kurs bulunamadı.")
    sleep(2)
    exit()

# Klasör adını kurs URL'inden türet
course_slug = course_url.rstrip("/").split("/")[-1]
course_name = sanitize(course_slug.rsplit("-", 1)[0].replace("-", " ").title())
base_dir = course_name
makedirs(base_dir, exist_ok=True)

total_sections = len(syllabus)
total_lessons  = sum(len(s.get("courses", [])) for s in syllabus)

print(f"\nKurs         : {course_name}")
print(f"Bölüm sayısı : {total_sections}")
print(f"Ders sayısı  : {total_lessons}")
print(f"Kaydedilecek : ./{base_dir}/\n")

onay = input("Tüm kurs indirilsin mi? (e/h): ").strip().lower()
if onay != "e":
    print("İptal edildi.")
    exit()

system("cls||clear")

failed = []

for s_idx, section in enumerate(syllabus, start=1):
    section_dir = join(base_dir, f"{s_idx:02d} - {sanitize(section['title'])}")
    makedirs(section_dir, exist_ok=True)

    lessons = section.get("courses", [])

    print(f"\n{'='*60}")
    print(f"Bölüm {s_idx}/{total_sections}: {section['title']}")
    print(f"{'='*60}")

    for l_idx, lesson in enumerate(lessons, start=1):
        lesson_id    = str(lesson["id"])
        lesson_title = sanitize(lesson["title"])

        print(f"\nDers {l_idx}/{len(lessons)}: {lesson['title']}")

        # Video ID al
        video_id = start_lesson(course_id, lesson_id)
        if not video_id:
            print("Video ID alınamadı, ders atlanıyor.")
            failed.append(f"[Bölüm {s_idx}] {lesson['title']}")
            sleep(1)
            continue

        video_name, video_url = get_video_url(video_id)
        output_file = join(section_dir, f"{l_idx:02d} - {lesson_title}.mp4")

        print(f"  Video ID  : {video_id}")
        print(f"  Video Adı : {video_name}")
        print(f"  📥 İndiriliyor → {output_file}")

        success = download_video(output_file, video_url, video_id)

        if success:
            print("Tamamlandı!")
        else:
            print("İndirilemedi.")
            failed.append(f"[Bölüm {s_idx}] {lesson['title']}")

        sleep(1.5)

print(f"\n{'='*60}")
print(f"Tüm işlem tamamlandı!  Konum: ./{base_dir}/")
if failed:
    print(f"\nİndirilemeyen {len(failed)} ders:")
    for f in failed:
        print(f"   - {f}")
print(f"{'='*60}\n")
