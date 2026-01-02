# ⚽ Futbol Ağı Analiz ve Görselleştirme Sistemi (Football Network Analysis)

**Ders:** Yazılım Geliştirme Laboratuvarı I - Kocaeli Üniversitesi
**Öğrenci:** Muhammed Taha Kızıkoğlu | **No:** 241307121
**Geliştirme Ortamı:** PyCharm IDE
**Veritabanı:** SQLite

---

## 📖 1. Giriş ve Problemin Tanımı

### Problemin Tanımı
Günümüz futbolunda takım mühendisliği, sadece oyuncuların bireysel yeteneklerine değil, birbirleriyle olan uyumlarına ve iletişim ağlarına dayanır. Bu proje, bir futbol takımını **Çizge Teorisi (Graph Theory)** kullanarak modellemeyi amaçlar. Oyuncular **Düğüm (Node)**, aralarındaki pas trafiği ve uyum ise **Kenar (Edge)** olarak temsil edilir.

### Projenin Amacı
Standart bir sosyal ağ analizinin futbol domainine özgü metriklerle (Hız, Pas, Tecrübe vb.) özelleştirilmiş bir analiz aracı sunar.

**Temel Hedefler:**
* **SQLite & JSON Entegrasyonu:** Verilerin kalıcı olarak tutulması ve taşınabilirliği.
* **Dinamik Ağırlıklandırma:** Oyuncular arası uyumun matematiksel formüllerle maliyete dönüştürülmesi.
* **Gelişmiş Algoritma Analizi:** Dijkstra ve A* gibi algoritmaların farklı sezgisel yöntemlerle karşılaştırılması.
* **OOP Mimarisi:** Katmanlı mimari ile sürdürülebilir kod yapısı.

---

##  2. Veri Setleri ve Dinamik Ağırlık Mantığı

Projede kullanılan veri setleri ve matematiksel modelleme, algoritmaların doğru çalışması için kritiktir.

### 2.1. Veri Setleri ve Kullanım Amaçları

Projede 3 temel JSON veri seti kullanılmıştır:

1.  **`besiktas.json` (Ana Veri Seti):**
    * Projenin belkemiğidir. Beşiktaş kadrosundaki gerçek oyuncuları ve mevkilerini içerir.
    * **Amacı:** Futbol domainindeki gerçek dünya senaryolarını test etmek. Örneğin; "Kaleci ile Forvet arasındaki en hızlı pas kanalı kimlerden oluşur?" sorusuna cevap arar.
    
2.  **`compAlgo.json` (Karşılaştırma ve Tuzaklı Yol):**
    * Özel olarak tasarlanmış, yapay engeller ve dolambaçlı yollar içeren bir graftır.
    * **Amacı:** Dijkstra ve A* algoritmalarının farkını göstermek. Dijkstra'nın körlemesine tüm alanı tararken, A*'ın hedefe nasıl yöneldiğini (veya tuzaklara nasıl tepki verdiğini) kanıtlamak için kullanılır.

3.  **`footballNetwork.json` (Yedek/Test):**
    * Sistemin genel testleri ve node ekleme/çıkarma fonksiyonlarının doğrulanması için kullanılan ham veri setidir.

### 2.2. Dinamik Ağırlık Hesaplama Formülü

İki oyuncu (düğüm) arasındaki kenarın maliyeti (Weight), statik bir sayı değil; oyuncuların özniteliklerine dayalı **Öklid Benzerliği** ile hesaplanan dinamik bir değerdir.

$$Ağırlık_{i,j} = 1 + \sqrt{\sum (Özellik_i - Özellik_j)^2}$$

**Formülün Yorumlanması:**
* **Düşük Ağırlık (Örn: 1.2):** İki oyuncunun özellikleri (Hız, Pas, Oyun Görüşü) birbirine çok yakındır. Bu, **yüksek uyum** ve **kolay pas** anlamına gelir. Algoritmalar bu yolu tercih eder.
* **Yüksek Ağırlık (Örn: 15.0):** Oyuncular uyumsuzdur. Pas hatası riski yüksektir. Algoritmalar mecbur kalmadıkça bu yolu seçmez.

---

## 3. Sınıf Yapısı ve Mimari 

Proje, **Clean Architecture** prensiplerine sadık kalarak 3 ana katmana ayrılmıştır. Bu yapı sayesinde veritabanı, iş mantığı ve arayüz birbirinden bağımsız yönetilebilir.

### Mimari Detayları
* **`DataManager`:** SQLite veritabanı ile Python nesneleri arasındaki ORM (Object Relational Mapping) köprüsüdür.
* **`BaseAlgorithm`:** Tüm algoritmalar bu soyut sınıftan türetilmiştir (Strategy Pattern). Bu sayede sisteme yeni bir algoritma eklemek, mevcut kodu bozmaz.
* **`Visualizer`:** UI katmanıdır. Matplotlib'i Tkinter içine gömerek (embedding) interaktif bir tuval sunar.

<img width="1326" height="847" alt="Ekran görüntüsü 2026-01-02 024642" src="https://github.com/user-attachments/assets/8043026e-d9d3-4f93-8133-5a012f411995" />

> *Yukarıdaki diyagramda BaseAlgorithm sınıfından türeyen algoritmalar ve DataManager ilişkisi görülmektedir.*

Proje Klasör Yapısı (Folder Structure)

Proje, sürdürülebilirliği sağlamak ve karmaşıklığı önlemek adına **Clean Architecture (Temiz Mimari)** prensiplerine uygun olarak modüler bir yapıda tasarlanmıştır. Veri, İş Mantığı (Logic) ve Arayüz (UI) katmanları fiziksel olarak birbirinden ayrılmıştır.

<img width="1253" height="394" alt="Ekran görüntüsü 2026-01-02 024713" src="https://github.com/user-attachments/assets/629c2310-96c4-4ab9-a4f8-f7b9cec8cf5d" />

* **`data/`**: Projenin veri katmanıdır. Analiz edilen JSON dosyaları (`besiktas.json`, `compAlgo.json`) ve SQLite veritabanı (`social_network.db`) burada tutulur.
* **`src/core/`**: Uygulamanın beyni olan mantık katmanıdır.
    * `algorithms/`: BFS, DFS, Dijkstra, A* ve Renklendirme algoritmalarının saf Python kodlarını içerir.
    * `model/`: Veritabanı tablolarını temsil eden `Node` ve `Edge` sınıfları buradadır.
    * `data_manager.py`: Veritabanı işlemlerini yönetir.
* **`src/ui/`**: Kullanıcı arayüzü katmanıdır. `Visualizer` sınıfı, algoritmaların sonuçlarını ekrana çizer.
* **`main.py`**: Uygulamanın giriş noktasıdır (Entry Point).
---

## ⚙️ 4. Algoritmalar ve Literatür Analizi

Bu bölümde algoritmaların çalışma mantığı, karmaşıklık analizleri ve projeye özgü uyarlamaları detaylandırılmıştır.

### 4.1. Genişlik ve Derinlik Öncelikli Arama (BFS & DFS)

* **BFS (Breadth-First Search):** Başlangıç düğümünden dalga dalga yayılarak ilerler. Ağırlıksız graflarda en kısa yolu garanti eder.
    * *Karmaşıklık:* $O(V + E)$
    * Mantığı: İlk giren ilk çıkar (FIFO - First In First Out). Bu sayede algoritma bir düğümün önce tüm komşularını bitirir, sonra derinleşir (Dalga dalga yayılır).
<img width="777" height="904" alt="Ekran görüntüsü 2026-01-02 024206" src="https://github.com/user-attachments/assets/d1de4eaa-a0b4-40fd-89f1-ae17828aa9e4" />

  
* **DFS (Depth-First Search):** Bir daldan gidebildiği son noktaya kadar gider. Grafın derinliklerini ve döngülerini keşfetmek için idealdir.
    * *Karmaşıklık:* $O(V + E)$
    * Mantığı: Son giren ilk çıkar (LIFO - Last In First Out). Bu sayede algoritma bir yolda gidebildiği en son noktaya kadar dalar, sonra geri döner.
<img width="608" height="914" alt="Ekran görüntüsü 2026-01-02 024255" src="https://github.com/user-attachments/assets/ea79b01b-a0c5-4d08-a565-4ef54ec07922" />

### 4.2. Dijkstra Algoritması (En Kısa Yol)

**Literatür:** Dijkstra, "Greedy" (Açgözlü) bir yaklaşımla çalışır. Başlangıç düğümünden itibaren, o ana kadar keşfedilen en düşük maliyetli düğümü seçerek ilerler.
**Projeredeki Yeri:** Tüm kenar ağırlıklarını (uyum maliyetlerini) hesaba katarak **kesin en kısa yolu** bulur. Ancak hedefin nerede olduğunu bilmediği için tüm yönlere eşit şekilde yayılır (Blind Search).

* **Zaman Karmaşıklığı:** $O(E + V \log V)$ (Priority Queue ile)

### 4.3. A* (A-Star) Algoritması ve Sezgisel Farklılıklar

**Literatür:** A*, Dijkstra'nın geliştirilmiş halidir. $f(n) = g(n) + h(n)$ formülünü kullanır.
* **$g(n)$:** Başlangıçtan şu ana kadar olan gerçek maliyet.
* **$h(n)$ (Heuristic):** Hedefe kalan tahmini maliyet.

**Farkı Nedir?** Dijkstra körlemesine her yeri ararken, A* $h(n)$ fonksiyonunu kullanarak aramayı **hedefe doğru yönlendirir**. Projede kullanıcıya 4 farklı sezgisel mod sunulmuştur. Bu modlar, algoritmanın izlediği yolu ve toplam maliyeti doğrudan değiştirir:

#### A. Standart Mod (Dengeli)
Varsayılan heuristic kullanılır. Yolun fiziksel uzunluğunu veya index farkını baz alır.
> <img width="1386" height="1138" alt="image" src="https://github.com/user-attachments/assets/f819c4a9-72d3-4124-bde6-c425ca2cf447" />


> *Standart modda algoritma en dengeli yolu izler.*

#### B. Hız Odaklı Mod (Speed Heuristic)
Algoritma, **Hız** özelliği yüksek olan oyuncular üzerinden gitmeye çalışır. Hızlı oyunculara ulaşmanın maliyeti sezgisel olarak düşürülür.
> <img width="1431" height="1048" alt="image" src="https://github.com/user-attachments/assets/cb440e1c-6917-4f03-b674-d399bcb18a37" />
<img width="932" height="1086" alt="image" src="https://github.com/user-attachments/assets/e1b9b6a9-f3ac-4ae3-a704-79e1c47218bb" />


> *Hız odaklı modda, yol daha hızlı oyuncular üzerinden kıvrılarak gider.*

#### C. Pas Odaklı Mod (Passing Heuristic)
Algoritma, **Pas** yeteneği yüksek olan "Oyun Kurucu" oyuncuları tercih eder. Bu mod, top kaybı riskini en aza indiren güvenli yolu bulur.
> <img width="1433" height="1103" alt="image" src="https://github.com/user-attachments/assets/53b8dd8e-d11e-4082-a8d5-d90178419068" />

> *Pas odaklı modda, teknik kapasitesi yüksek oyuncular tercih edilmiştir.*

#### D. Tecrübe Odaklı Mod (Experience Heuristic)
Algoritma, yaşı ve **Tecrübesi** yüksek oyunculara öncelik verir. Kritik anlarda topun tecrübeli ayaklarda kalmasını simüle eder.
> <img width="1430" height="1100" alt="image" src="https://github.com/user-attachments/assets/86a74d6f-3f27-4eab-a6bb-b7b4a68d9ec7" />

> *Tecrübe modunda, genç oyuncular yerine deneyimli oyuncular üzerinden bir hat çizilir.*

A* algoritması, $h(n)$ (sezgisel) fonksiyonu sayesinde sadece en kısa yolu bulmakla kalmayıp, seçilen moda göre bir teknik direktör gibi farklı oyun taktikleri uygular. Standart Mod, maçın genel akışında dengeli bir oyun kurmak için fiziksel olarak en verimli ve optimum yolu hedefler. Hız Odaklı Mod, skor üretmek için acil gole ihtiyaç duyulan anlarda, yol maliyeti artsa bile en süratli oyuncular üzerinden bir "Kontra Atak" planlar. Rakip savunmayı açmak veya topa sahip olmak istendiğinde devreye giren Pas Odaklı Mod, teknik kapasitesi yüksek oyuncularla güvenli bir "Set Hücumu" kurgular. Son olarak Tecrübe Odaklı Mod, maçın sonlarında skoru korumak amacıyla risk almadan topu takımın en deneyimli ve soğukkanlı isimlerinde tutar. Bu sayede sistem, statik bir matematiksel hesaplamanın ötesine geçerek saha içindeki dinamik senaryolara akıllıca adapte olur.

### 4.4. Dijkstra vs A* Karşılaştırması (Tuzaklı Yol Analizi)

`compAlgo.json` veri seti üzerinde yapılan testlerde:
* **Dijkstra:** Hedefe ulaşana kadar tüm haritayı taramış ve çok daha fazla düğümü ziyaret etmiştir.

> <img width="1353" height="1062" alt="image" src="https://github.com/user-attachments/assets/4b57f1fe-89ce-4c86-ac5e-bb1feedd4d0e" />
<img width="1319" height="1038" alt="image" src="https://github.com/user-attachments/assets/a189d99e-ab05-4c5b-9c00-487cf2d4be34" />


* **A*:** Sezgisel fonksiyon sayesinde tuzaklara girmeden doğrudan hedefe yönelmiş ve sonuca ulaşmıştır.
<img width="1355" height="1058" alt="image" src="https://github.com/user-attachments/assets/142c74a3-eef1-470e-9377-44c8eebccf33" />

> *İki algoritmanın da çalışma mekanizması farklıdır.*

---

## 📱 5. Kullanıcı Arayüzü ve Özellikler

Uygulama arayüzü, kullanıcı deneyimi ön planda tutularak tasarlanmıştır.

### 5.1. Düğüm Detay Görüntüleme
Kullanıcı, graf üzerindeki herhangi bir oyuncuya (düğüme) tıkladığında, o oyuncunun tüm nitelikleri (Hız, Pas, Şut vb.) ve veritabanı bilgileri dinamik bir pop-up penceresinde gösterilir.

> <img width="691" height="469" alt="image" src="https://github.com/user-attachments/assets/45e994d3-51a8-4130-9a87-4191425dfb31" />


### 5.2. Welsh-Powell Renklendirme
Mevki veya grup çakışmalarını önlemek için graf renklendirme algoritması uygulanmıştır. Komşu düğümler asla aynı renge boyanmaz.

> <img width="1292" height="1027" alt="image" src="https://github.com/user-attachments/assets/9c946d36-eee3-44e8-99f8-a2d931aa8f07" />

### 5.3. Bağlı Bileşenler ve Ayrık Gruplar Analizi (Connected Components)
Bu algoritma, graf üzerindeki birbirinden tamamen kopuk olan ve aralarında hiçbir kenar (pas/ilişki) bağlantısı bulunmayan alt grafikleri (Sub-graphs) tespit eder.

**Futbol Analizindeki Önemi:**
* Takım içinde pas trafiğine dahil olmayan izole oyuncuları belirlemek.
* Birbirinden kopuk "gruplaşmaları" (klikleşme) tespit etmek.
* Birden fazla takımı aynı veri setinde analiz ederken takımları otomatik olarak ayırt etmek.

> <img width="1303" height="1035" alt="image" src="https://github.com/user-attachments/assets/b12cd70a-4bf5-4827-a5c9-c879168a11cd" />

> *Yukarıdaki görselde, birbirinden bağımsız oyuncu grupları farklı renk kümeleri halinde tespit edilmiştir.*


---
## 🏆 6. Sonuç ve Tartışma

### 6.1. Proje Çıktıları ve Başarılar
Bu proje kapsamında, proje isterlerinde belirtilen **"Futbol Ağı Analiz ve Görselleştirme Sistemi"** başarıyla geliştirilmiş ve istenen tüm fonksiyonlar (Algoritmalar, CRUD işlemleri, Görselleştirme, Raporlama) eksiksiz olarak yerine getirilmiştir.

* **Tamamlanan İsterler:** BFS, DFS, Dijkstra, A* (farklı sezgisel modlarla), Welsh-Powell Renklendirme ve Bağlı Bileşen analizi algoritmaları sorunsuz çalışmaktadır.
* **Mimari Başarı:** Proje, tek bir dosya içinde karmaşık kodlar (spagetti kod) yerine; Modellerin, Arayüzün ve Algoritmaların ayrıldığı **Katmanlı Bir Mimari (OOP)** üzerine inşa edilmiştir.

### 6.2. Karşılaşılan Zorluklar ve Çözümler
Proje geliştirme sürecinde ekibimizi en çok zorlayan ve geliştiren alanlar şunlar olmuştur:

1.  **Arayüz Görselleştirmesi ve Entegrasyon:**
    Kağıt üzerinde veya konsolda çalışan bir graf yapısını, kullanıcı arayüzünde (GUI) interaktif bir şekilde göstermek sürecin en zorlu kısmıydı. Özellikle **`Matplotlib`** kütüphanesini **`Tkinter`** içerisine gömmek (embedding) ve algoritmaların çalışma anını (animasyonlu boyama işlemi) arayüz donmadan kullanıcıya izletmek için `thread` yönetimi ve güncelleme mekanizmaları üzerine yoğunlaştık.

2.  **Sınıf Yapısı ve OOP Mimarisi Kurmak:**
    Başlangıçta kodları doğrudan fonksiyonlar halinde yazmak kolay gelse de, projenin büyüyebileceğini öngörerek **BaseAlgorithm** gibi soyut sınıflar (Abstract Base Class) kurmak ve tüm algoritmaları buradan türetmek başlarda karmaşık geldi. Ancak bu yapıyı kurduktan sonra yeni bir algoritma eklemenin ne kadar kolay olduğunu deneyimleyerek OOP'nin gücünü anladık.

3.  **Algoritma Mantığını Kodlama:**
    Dijkstra veya A* gibi algoritmaların teorik mantığını derste öğrenmiş olsak da, bunları Python'da **Priority Queue (Öncelik Kuyruğu)** ve **Heap** yapılarını kullanarak hatasız kod
