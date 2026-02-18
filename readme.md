# BTK Akademi Video İndirici

Python tabanlı, BTK Akademi üzerindeki kurs videolarını kolayca indirmenizi sağlayan bir araç.

---

## Gereksinimler

- Python 3.11+
- `requests` kütüphanesi
- `yt-dlp` kütüphanesi

Gerekli kütüphaneleri yüklemek için:

```bash
pip install requests yt-dlp
```

---

## Access Token Nasıl Alınır?

1. [BTK Akademi](https://www.btkakademi.gov.tr) sitesine giriş yapın.
2. Klavyenizde **CTRL + SHIFT + I** tuşlarına basarak tarayıcı geliştirici araçlarını açın.
3. Üst menüden **Application** sekmesine tıklayın.
4. Sol panelde **Local Storage** → `https://www.btkakademi.gov.tr` seçeneğine tıklayın.
5. Listede **access_token** anahtarını bulun ve değerini kopyalayın.

>  Token'ınızı kimseyle paylaşmayın. Hesabınıza ait özel bir kimlik bilgisidir.

---

##  Kurulum

1. Bu repoyu klonlayın veya dosyaları indirin:

   ```bash
   git clone https://github.com/kullanici-adi/btk-indirici.git
   cd btk-indirici
   ```

2. `indir.py` dosyasını bir metin editörüyle açın.

3. Dosyanın üst kısmındaki `ACCESS_TOKEN` değişkenini bulun ve kopyaladığınız token ile değiştirin:

   ```python
   ACCESS_TOKEN = "buraya_token_yapistirin"
   ```

---

##  Kullanım

1. Terminali açın ve betiği çalıştırın:

   ```bash
   python indir.py
   ```

2. Terminal sizden **kurs URL'sini** girmenizi isteyecektir. BTK Akademi'deki ilgili kursun sayfasını açın ve URL'yi kopyalayıp yapıştırın:

   ```
   Kurs URL: https://www.btkakademi.gov.tr/portal/course/yapay-zeka-12345
   ```

3. Ardından terminal size **bölüm listesini** gösterecektir. İndirmek istediğiniz bölümün numarasını girin:

   ```
   1- Giriş
   2- Sağlıkta Yapay Zeka
   ...
   Bölüm seçin: 1
   ```

4. Son olarak terminal size **ders listesini** gösterecektir. İndirmek istediğiniz dersin numarasını girin:

   ```
   1- Yapay Zekaya Giriş
   2- Temel Kavramlar
   ...
   Ders seçin: 1
   ```

5. Video otomatik olarak bulunduğunuz dizine indirilecektir. 

---

## Çıktı

İndirilen videolar betiği çalıştırdığınız klasöre `.mp4` formatında kaydedilir. Dosya adı, video'nun kendi adını taşır.

---

## Sık Karşılaşılan Hatalar

| Hata | Açıklama | Çözüm |
|------|----------|-------|
| `HTTP Error 403: Forbidden` | CDN erişimi reddetti | Token'ın güncel olduğundan emin olun |
| `ACCESS_TOKEN eksik veya geçersiz!` | Token hatalı veya süresi dolmuş | Adımları tekrarlayarak yeni token alın |
| `Video URL bulunamadı!` | Video ID alınamadı | Kursa kayıtlı olduğunuzdan emin olun |

---

## Notlar

- Token'ın bir **geçerlilik süresi** vardır. Hata alırsanız yeni bir token alın.
- Yalnızca **kayıtlı olduğunuz** kursların videolarını indirebilirsiniz.
- İndirilen içerikler yalnızca **kişisel kullanım** içindir.
