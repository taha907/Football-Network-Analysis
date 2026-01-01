# ⚽ Futbol Ağı Analiz ve Görselleştirme Sistemi (Football Network Analysis)

**Ders:** Yazılım Geliştirme Laboratuvarı I - Kocaeli Üniversitesi
**Öğrenci:** Muhammed Taha Kızıkoğlu | **No:** 241307121

---

## 📖 1. Giriş ve Problemin Tanımı

### Problemin Tanımı
Günümüz futbolunda oyuncular arasındaki pas trafiği, uyum ve pozisyonel ilişkiler karmaşık bir ağ yapısı oluşturur. Bu ilişkilerin sadece istatistiksel tablolarla anlaşılması zordur. Bu proje, futbolcuları birer **Düğüm (Node)**, aralarındaki ilişkileri (pas, uyum vb.) ise **Kenar (Edge)** olarak modelleyerek, bu yapıyı Çizge Teorisi (Graph Theory) algoritmalarıyla analiz etmeyi amaçlar.

### Projenin Amacı
* Futbolcu verilerini JSON ve SQLite veritabanı üzerinden dinamik olarak yönetmek.
* Oyuncu ağını (Graph) görsel arayüz (GUI) üzerinde interaktif olarak çizmek.
* **En Kısa Yol (Shortest Path)** algoritmaları ile en hızlı pas trafiğini ve oyun kurma stratejilerini bulmak.
* **Topluluk Algılama (Community Detection)** ile birbirine bağlı oyuncu gruplarını tespit etmek.
* **Renklendirme (Coloring)** algoritmaları ile mevki veya rakip çakışmalarını analiz etmek.
* **OOP (Nesne Yönelimli Programlama)** prensiplerine tam uyumlu, katmanlı (MVC) bir mimari geliştirmek.

---

## ⚙️ 2. Gerçeklenen Algoritmalar ve Analizler

Projede kullanılan temel algoritmalar aşağıda detaylandırılmıştır. Her algoritma `BaseAlgorithm` sınıfından türetilmiştir.

### 2.1. Genişlik Öncelikli Arama (BFS - Breadth-First Search)
**Çalışma Mantığı:** Başlangıç düğümünden başlayarak önce o düğümün tüm komşularını, ardından komşuların komşularını ziyaret eder. Ağın "yayılma" kapasitesini ölçmek için kullanılır.
**Karmaşıklık:** $O(V + E)$ (V: Düğüm, E: Kenar Sayısı)

![BFS Flowchart](https://github.com/user-attachments/assets/0d135a8c-6ae6-4a53-9021-8d415b9a73b6)

### 2.2. Derinlik Öncelikli Arama (DFS - Depth-First Search)
**Çalışma Mantığı:** Bir yolda gidebileceği en son noktaya kadar derinlemesine gider, çıkmaz sokağa girince geri döner (backtracking). Ağdaki kopuklukları veya derin ilişkileri bulmak için kullanılır.
**Karmaşıklık:** $O(V + E)$

![DFS Flowchart](https://github.com/user-attachments/assets/fed3f548-33d2-4c8d-9ab8-d20f1b028c07)

### 2.3. Dijkstra En Kısa Yol Algoritması
**Çalışma Mantığı:** Ağırlıklı graflarda (Weighted Graphs) iki düğüm arasındaki minimum maliyetli yolu bulur. Projede "en az top kaybı" veya "en hızlı pas" senaryosu için kullanılmıştır. Priority Queue (Öncelik Kuyruğu) kullanılarak optimize edilmiştir.
**Karmaşıklık:** $O(E + V \log V)$

### 2.4. A* (A-Star) Algoritması
**Çalışma Mantığı:** Dijkstra'ya ek olarak bir "Heuristic" (Tahmin) fonksiyonu kullanır. Hedefe ne kadar yaklaşıldığını tahmin ederek (Örneğin oyuncunun hızı veya tecrübesi kullanılarak) daha akıllı ve hedef odaklı arama yapar.
**Karmaşıklık:** Heuristic fonksiyonuna bağlı olarak değişir, en kötü durumda $O(E)$.

### 2.5. Welsh-Powell (Graf Renklendirme)
**Çalışma Mantığı:** Graf üzerindeki komşu düğümlerin aynı renge sahip olmamasını sağlar. Düğümleri derecelerine (degree) göre büyükten küçüğe sıralar ve çakışmayacak şekilde boyar. Mevki çakışmalarını önlemek için kullanılır.
**Karmaşıklık:** $O(V^2 + E)$

### 2.6. Connected Components (Bağlı Bileşenler)
**Çalışma Mantığı:** Graf üzerindeki birbirinden kopuk alt grafikleri (takımları veya grupları) bulur. Birbirinden izole oyuncu gruplarını tespit etmekte kullanılır.

---

## 🏗️ 3. Sınıf Yapısı ve Mimari (Architecture)

Proje, sürdürülebilirlik ve temiz kod prensipleri gereği **MVC (Model-View-Controller)** benzeri katmanlı bir yapıda geliştirilmiştir. Mantıksal işlemler (Logic) ile Arayüz (UI) tamamen birbirinden ayrılmıştır.

### Klasör Yapısı
* **`src/core/algorithms`**: BFS, DFS, Dijkstra, A*, Coloring gibi algoritmaların bulunduğu mantık katmanı.
* **`src/core/model`**: `Node` (Düğüm) ve `Edge` (Kenar) veri yapılarını tutan sınıflar.
* **`src/ui`**: Tkinter arayüz kodları ve Matplotlib görselleştirme modülleri.
* **`src/data`**: Veritabanı (SQLite) bağlantıları ve JSON okuma/yazma işlemleri.

#### Proje Klasör Ağacı
![Folder Structure](https://github.com/user-attachments/assets/77f49605-bc3c-4413-9515-69479fb520b2)

#### Sınıf Diyagramı (Class Diagram)
Aşağıdaki diyagramda `BaseAlgorithm` soyut sınıfından türeyen algoritmalar ve `DataManager` ile `Visualizer` arasındaki ilişki görülmektedir.

![Class Diagram](https://github.com/user-attachments/assets/11336eb4-92e3-4d59-ab0c-97f6a32c66cc)

---

## 🧪 4. Uygulama Detayları ve Test Senaryoları

### 4.1. Dinamik Ağırlık Hesaplama (Dynamic Weighting)
Proje isterlerine uygun olarak, iki oyuncu arasındaki kenar ağırlığı (maliyet) statik değil, oyuncuların özelliklerine göre **dinamik** olarak hesaplanmaktadır.

Kullanılan Formül:
$$Ağırlık_{i,j} = 1 + \sqrt{(Aktiflik_i - Aktiflik_j)^2 + (Etkileşim_i - Etkileşim_j)^2 + (Bağlantı_i - Bağlantı_j)^2}$$

Bu formül sayesinde benzer özelliklere sahip oyuncular arasındaki "pas maliyeti" daha düşük çıkar, yani birbirlerine daha yakın kabul edilirler.

### 4.2. Test Senaryoları ve Sonuçlar
* **Test 1 (En Kısa Yol):** Kaleci ile forvet arasındaki en güvenli pas kanalı Dijkstra algoritması ile test edilmiş ve en düşük maliyetli yol başarıyla görselleştirilmiştir.
* **Test 2 (Renklendirme):** Welsh-Powell algoritması ile birbirine pas atan oyuncuların farklı renklere boyanması sağlanmış, böylece görsel karmaşıklık önlenmiştir.
* **Test 3 (Veri Yönetimi):** JSON dosyasından yüklenen veriler üzerinde değişiklik yapılıp tekrar kaydedildiğinde veri bütünlüğünün korunduğu doğrulanmıştır.

---

## 🏆 5. Sonuç ve Değerlendirme

### Başarılar
* **Temiz Mimari:** Algoritmalar, arayüzden tamamen bağımsız sınıflar (Classes) haline getirildi.
* **Görselleştirme:** Ağ yapısı `matplotlib` entegrasyonu ile interaktif hale getirildi (Zoom/Pan özellikleri).
* **Veri Yönetimi:** JSON ve SQLite kullanılarak esnek bir veri yapısı kuruldu.

### Sınırlılıklar
* Veriler şu an için statik JSON dosyalarından çekilmektedir, canlı maç verisi (API) entegrasyonu yoktur.
* 1000+ düğümlü çok büyük ağlarda çizim performansı, Python'un grafik kütüphanesi limitlerine takılabilir.

### Gelecek Çalışmalar
* Gerçek zamanlı maç verisi çeken bir "Scraper" modülü eklenebilir.
* Arayüz Web tabanlı (Flask/Django veya React) hale getirilebilir.
