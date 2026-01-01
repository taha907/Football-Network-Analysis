import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
#NetworkX çizim yapmaz, sadece hesaplama yapar.
#matplotlib, veri görselleştirme ve grafik çizim kütüphanesi
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import math
import json

# --- MODERN VE FUTBOL TEMALI RENK PALETİ ---
BG_MAIN = "#f0f2f5"
SIDEBAR_BG = "#ffffff"
ACCENT_PRIMARY = "#1a73e8"  # Google Blue
ACCENT_SECONDARY = "#2ecc71"  # Saha Yeşili
TEXT_MAIN = "#202124"
TEXT_LIGHT = "#7f8c8d"


class SocialNetworkVisualizer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("Futbolcu Sinerji ve Taktik Analiz Sistemi v4.0")
        self.master.geometry("1450x950")
        self.master.configure(bg=BG_MAIN)

        # Veri Yöneticisini Başlat
        from core.data_manager import DataManager
        self.dm = DataManager()

        # --- MEVKİ NORMALİZASYON STRATEJİSİ ---
        self.position_map = {
            "Kaleci": 0.1, "Defans": 0.2, "Orta Saha": 0.3, "Forvet": 0.4
        }
        self.color_palette = ["#e74c3c", "#3498db", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22", "#2ecc71", "#34495e"]

        # --- KONTROL DEĞİŞKENLERİ ---
        self.details_window = None
        self.is_paused = False
        self.animation_duration = tk.IntVar(value=5)  # Varsayılan 5 saniye

        self.pack(fill="both", expand=True)
        self.setup_styles()
        self.create_layout()
        self.refresh_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG_MAIN)
        style.configure("Sidebar.TFrame", background=SIDEBAR_BG, relief="flat")
        style.configure("TLabel", background=SIDEBAR_BG, foreground=TEXT_MAIN, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=ACCENT_PRIMARY)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9, "bold"), foreground=TEXT_LIGHT)
        style.configure("Action.TButton", font=("Segoe UI", 9), padding=5)

    def create_layout(self):
        # 1. SOL PANEL
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", padding=15)
        self.sidebar.pack(side=tk.LEFT, fill="y", padx=5, pady=5)

        ttk.Label(self.sidebar, text="⚽ Futbolcu Yönetimi", style="Header.TLabel").pack(fill="x", pady=(0, 10))

        # Kullanıcı İşlemleri
        ttk.Label(self.sidebar, text="Kadro İşlemleri", style="SubHeader.TLabel").pack(anchor="w")
        ops = [
            ("+ Yeni Futbolcu", self.add_node_dialog),
            ("✎ Bilgileri Güncelle", self.update_selected_node_dialog),
            ("🗑 Kadrodan Çıkar", self.delete_selected_node)
        ]
        for txt, cmd in ops: ttk.Button(self.sidebar, text=txt, command=cmd).pack(fill="x", pady=2)

        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)

        # Bağlantı İşlemleri
        ttk.Label(self.sidebar, text="Pas & Uyum Bağlantıları", style="SubHeader.TLabel").pack(anchor="w")
        ops_edge = [
            ("🔗 Bağlantı Kur", self.add_edge_dialog),
            ("✂ Bağlantı Kopar", self.delete_edge_dialog)
        ]
        for txt, cmd in ops_edge: ttk.Button(self.sidebar, text=txt, command=cmd).pack(fill="x", pady=2)

        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)

        # Analizler
        ttk.Label(self.sidebar, text="Taktiksel Analiz & AI", style="SubHeader.TLabel").pack(anchor="w")
        analizler = [
            ("🔍 BFS (Pas Erişimi)", self.run_bfs),
            ("🔍 DFS (Derin Tarama)", self.run_dfs),
            ("📍 Dijkstra (En Uyumlu Hat)", self.run_dijkstra),
            ("📍 A* (Akıllı Pas Rotası)", self.run_astar),
            ("🎨 Welsh-Powell (Mevki Boyama)", self.run_coloring),
            ("🌐 Ayrık Topluluk Bul", self.run_connected_components),
            ("🏆 En Etkili 5 Oyuncu", self.show_top_users)
        ]
        for txt, cmd in analizler: ttk.Button(self.sidebar, text=txt, command=cmd).pack(fill="x", pady=2)

        # --- ANİMASYON KONTROLÜ (GERİ EKLENDİ) ---
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)
        anim_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        anim_frame.pack(fill="x", pady=5)
        ttk.Label(anim_frame, text="Hız (sn):").pack(side=tk.LEFT)
        self.duration_combo = ttk.Combobox(anim_frame, values=[5, 10, 15], textvariable=self.animation_duration,
                                           width=3, state="readonly")
        self.duration_combo.pack(side=tk.LEFT, padx=5)
        self.pause_btn = ttk.Button(anim_frame, text="⏸ Duraklat", command=self.toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)

        # Dosya İşlemleri
        ttk.Label(self.sidebar, text="Veri Yönetimi", style="SubHeader.TLabel").pack(anchor="w")
        ttk.Button(self.sidebar, text="📥 JSON Yükle", command=self.import_json).pack(fill="x", pady=2)
        ttk.Button(self.sidebar, text="💾 JSON Kaydet", command=self.export_json).pack(fill="x", pady=2)

        # Kadro Listesi
        ttk.Label(self.sidebar, text="Kadro Listesi", style="SubHeader.TLabel").pack(anchor="w", pady=(10, 0))
        self.node_tree = ttk.Treeview(self.sidebar, columns=("ID", "İsim", "Mevki"), show="headings", height=15)
        self.node_tree.heading("ID", text="ID");
        self.node_tree.heading("İsim", text="İsim");
        self.node_tree.heading("Mevki", text="Mevki")
        self.node_tree.column("ID", width=30, anchor="center");
        self.node_tree.column("İsim", width=100);
        self.node_tree.column("Mevki", width=70, anchor="center")
        self.node_tree.pack(fill="both", expand=True, pady=5)

        # 2. SAĞ PANEL
        self.viz_panel = ttk.Frame(self, padding=0)
        self.viz_panel.pack(side=tk.RIGHT, fill="both", expand=True)

        # Üst Bar
        top_bar = ttk.Frame(self.viz_panel)
        top_bar.pack(fill="x", pady=(10, 5), padx=15)
        ttk.Label(top_bar, text="Saha Diziliş Grafiği", font=("Segoe UI", 16, "bold"), foreground=TEXT_MAIN).pack(
            side=tk.LEFT)
        ttk.Button(top_bar, text="🔄 Görünümü Yenile", command=self.refresh_ui).pack(side=tk.RIGHT)

        self.fig, self.ax = plt.subplots(figsize=(12, 9), facecolor=BG_MAIN)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_node_click)

        self.detail_frame = ttk.LabelFrame(self.viz_panel, text="📌 Durum Paneli", padding=10)
        self.detail_frame.pack(fill="x", side=tk.BOTTOM, padx=15, pady=(0, 15))
        self.detail_label = ttk.Label(self.detail_frame, text="Analiz yapmak için bir algoritma seçin.",
                                      font=("Segoe UI", 10, "italic"))
        self.detail_label.pack(anchor="w")

    # --- CORE METOTLAR ---
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_btn.config(text="▶ Devam Et" if self.is_paused else "⏸ Duraklat")

    def refresh_ui(self):
        self.load_nodes_to_list()
        self.update_graph_visualization()

    def load_nodes_to_list(self):
        for i in self.node_tree.get_children(): self.node_tree.delete(i)
        for n in self.dm.get_all_nodes():
            self.node_tree.insert("", "end", values=(n.node_id, n.name, getattr(n, 'mevki', '-')))


    # veritabanındaki ham futbolcu verilerini ve ilişkilerini, NetworkX kütüphanesinin anlayacağı ve
    # algoritmaların üzerinde çalışabileceği matematiksel bir Graf nesnesine dönüştürür.
    def get_nx_graph(self):
        # yönsüz ok kullanımı için Graph() kullandım
        G = nx.Graph()
        # veri setinden nodeların tamamını dic yapısında liste halinde aldım
        nodes = {n.node_id: n for n in self.dm.get_all_nodes()}

        # add_node döngüsü hiç yazmasaydık veri tabanına eklenen ve bağlantısı olmayan düğüm sahnemizde görünmezdi
        # yani, bağlantısı olsun ya da olmasın, kadrodaki herkesi sahaya (grafa) yerleştir
        for n_id in nodes:
            G.add_node(n_id)
        for e in self.dm.get_all_edges():
            if e.node1_id in nodes and e.node2_id in nodes:
                n1, n2 = nodes[e.node1_id], nodes[e.node2_id]
                m1 = self.position_map.get(getattr(n1, 'mevki', 'Defans'), 0.2)
                m2 = self.position_map.get(getattr(n2, 'mevki', 'Defans'), 0.2)
                #try -> veri setinde eksik bilgi olması veya matematiksel hata asonucu çökmeyi önlemek için
                try:
                    diffs = [(getattr(n1, k, 0.5) - getattr(n2, k, 0.5)) ** 2 for k in
                             ['hiz', 'pas', 'sut', 'defans', 'fizik', 'tecrube']]
                    diffs.append((m1 - m2) ** 2)
                    w = 1 + math.sqrt(sum(diffs))
                # programın çalışmaya devam etmesi için otomatik değer w = 1
                except:
                    w = 1.0
                G.add_edge(e.node1_id, e.node2_id, weight=w)
        return G

    def update_graph_visualization(self, node_colors_dict=None, highlight_path=None, highlight_nodes=None,
                                   highlight_edges=None, is_search_phase=False, search_color="#e74c3c"):
        self.ax.clear()
        G = self.get_nx_graph()
        if not G.nodes(): self.canvas.draw(); return

        # 1. POZİSYON HESAPLAMA
        all_nodes = {n.node_id: n for n in self.dm.get_all_nodes()}
        positions_groups = {"Kaleci": [], "Defans": [], "Orta Saha": [], "Forvet": []}
        unknown_nodes = []

        for n_id in G.nodes():
            if n_id in all_nodes:
                mevki = getattr(all_nodes[n_id], 'mevki', 'Bilinmiyor')
                m_lower = mevki.lower() if mevki else ""
                if "kaleci" in m_lower or "gk" in m_lower:
                    positions_groups["Kaleci"].append(n_id)
                elif "defans" in m_lower or "bek" in m_lower:
                    positions_groups["Defans"].append(n_id)
                elif "orta" in m_lower or "mid" in m_lower:
                    positions_groups["Orta Saha"].append(n_id)
                elif "forvet" in m_lower or "fw" in m_lower:
                    positions_groups["Forvet"].append(n_id)
                else:
                    unknown_nodes.append(n_id)
            else:
                unknown_nodes.append(n_id)

        pos = {}
        y_levels = {"Kaleci": 0.1, "Defans": 0.35, "Orta Saha": 0.6, "Forvet": 0.85}
        for p_name, p_list in positions_groups.items():
            if not p_list: continue
            count = len(p_list)
            for i, node_id in enumerate(sorted(p_list)):
                pos[node_id] = ((i + 1) / (count + 1), y_levels[p_name])

        if unknown_nodes:
            spring_pos = nx.spring_layout(G, k=0.5, seed=42)
            for n in unknown_nodes: pos[n] = spring_pos[n]
        if not pos: pos = nx.spring_layout(G, k=2.0, seed=42)
        self.pos = pos

        # 2. RENKLENDİRME
        node_size = 2800
        final_path_set = set(highlight_path) if highlight_path else set()
        visited_set = set(highlight_nodes) if highlight_nodes else set()

        path_edges_set = set()
        if highlight_path:
            path_edges_set = set(
                tuple(sorted((highlight_path[i], highlight_path[i + 1]))) for i in range(len(highlight_path) - 1))

        visited_edges_set = set()
        if highlight_edges:
            visited_edges_set = set(tuple(sorted((u, v))) for u, v in highlight_edges)

        node_colors = []
        for node in G.nodes():
            if node in final_path_set:
                node_colors.append("#e67e22")  # SONUÇ (Turuncu)
            elif node in visited_set:
                # Parametre olarak gelen rengi kullan
                node_colors.append(search_color if is_search_phase else "#bdc3c7")
            elif node_colors_dict and node in node_colors_dict:
                node_colors.append(self.color_palette[node_colors_dict[node] % len(self.color_palette)])
            else:
                node_colors.append("#ecf0f1")

        edge_colors, edge_widths = [], []
        for u, v in G.edges():
            edge_key = tuple(sorted((u, v)))
            if edge_key in path_edges_set:
                edge_colors.append("#e67e22");
                edge_widths.append(4.0)
            elif edge_key in visited_edges_set:
                edge_colors.append(search_color);
                edge_widths.append(2.0)
            else:
                edge_colors.append("#bdc3c7");
                edge_widths.append(1.5)

        # 3. ÇİZİM
        self.ax.axhline(y=0.48, color='#bdc3c7', linestyle='--', alpha=0.3)
        self.ax.text(0.02, 0.02, "KALE", fontsize=9, color='#95a5a6')
        self.ax.text(0.02, 0.95, "FORVET", fontsize=9, color='#95a5a6')

        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_size=node_size, node_color=node_colors, edgecolors="#7f8c8d",
                               linewidths=1.5)
        nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color=edge_colors, width=edge_widths, alpha=0.7)

        labels = {}
        for n in self.dm.get_all_nodes():
            if n.node_id in G:
                clean_name = n.name.split(" ")[0] if " " in n.name else n.name
                if len(clean_name) > 9: clean_name = clean_name[:7] + ".."
                labels[n.node_id] = f"{n.node_id}\n{clean_name}"

        nx.draw_networkx_labels(G, pos, labels=labels, ax=self.ax, font_size=9, font_color="#2c3e50",
                                font_weight="bold")
        edge_labels = {k: f"{v:.1f}" for k, v in nx.get_edge_attributes(G, 'weight').items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax, font_size=7, font_color="#e74c3c",
                                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        self.ax.axis("off");
        self.canvas.draw();
        self.master.update()

    # ---  DETAYLI SONUÇ EKRANI YARDIMCISI ---
    def show_detailed_result(self, title, stats, description, path_list=None, visited_list=None):
        """
        stats: { 'Süre': float, 'Gezilen': int, 'Yol': int, 'Maliyet': float }
        description: Algoritmanın çalışma mantığı hakkında analiz metni.
        """
        res_win = tk.Toplevel(self)
        res_win.title(title)
        res_win.geometry("650x700")
        res_win.configure(bg="#f8f9fa")

        # Üst Başlık
        header_frame = tk.Frame(res_win, bg="#ffffff", pady=10)
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text=title, font=("Segoe UI", 16, "bold"), foreground=ACCENT_PRIMARY,
                  background="#ffffff").pack()

        # --- SEKMELER ---
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[10, 5])

        tab_control = ttk.Notebook(res_win)
        tab_ozet = ttk.Frame(tab_control)
        tab_yol = ttk.Frame(tab_control)
        tab_gecmis = ttk.Frame(tab_control)  # Visited

        tab_control.add(tab_ozet, text='📊 Analiz Özeti')
        if path_list: tab_control.add(tab_yol, text='📍 Sonuç Rotası')
        if visited_list: tab_control.add(tab_gecmis, text='🔍 Tarama Geçmişi')

        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # --- SEKME 1: ÖZET VE DEĞERLENDİRME ---
        f_ozet = ttk.Frame(tab_ozet, padding=20)
        f_ozet.pack(fill="both", expand=True)

        # 1. Metrikler Tablosu
        lbl_metrics = ttk.LabelFrame(f_ozet, text="Performans Metrikleri", padding=15)
        lbl_metrics.pack(fill="x", pady=(0, 20))

        metrics_display = [
            ("⏱️ Çalışma Süresi (Çekirdek)", f"{stats.get('Süre', 0):.7f} saniye"),
            ("💰 Toplam Yol Maliyeti", f"{stats.get('Maliyet', 0):.2f} birim"),
            ("🔍 Gezilen Düğüm Sayısı", f"{stats.get('Gezilen', 0)} adet"),
            ("🏁 Sonuç Yol Uzunluğu", f"{stats.get('Yol', 0)} adım")
        ]

        for i, (k, v) in enumerate(metrics_display):
            ttk.Label(lbl_metrics, text=k, font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            ttk.Label(lbl_metrics, text=v, font=("Segoe UI", 10), foreground="#2c3e50").grid(row=i, column=1,
                                                                                             sticky="e", padx=30)

        # 2. Algoritma Değerlendirmesi (Text Area)
        lbl_desc = ttk.LabelFrame(f_ozet, text="🤖 Algoritma Değerlendirmesi", padding=10)
        lbl_desc.pack(fill="both", expand=True)

        txt_desc = tk.Text(lbl_desc, wrap="word", height=8, font=("Segoe UI", 10), bg="#f8f9fa", relief="flat")
        txt_desc.insert("1.0", description)
        txt_desc.config(state="disabled")  # Salt okunur
        txt_desc.pack(fill="both", expand=True)

        # --- SEKME 2 & 3 İÇİN ORTAK LİSTE YARDIMCISI ---
        def create_treeview(parent, columns):
            tree = ttk.Treeview(parent, columns=columns, show="headings")
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)
            return tree

        # --- SEKME 2: SONUÇ YOLU ---
        if path_list:
            cols = ("Sira", "ID", "Oyuncu", "Mevki")
            tree_yol = create_treeview(tab_yol, cols)
            tree_yol.heading("Sira", text="Sıra")
            tree_yol.heading("ID", text="ID")
            tree_yol.heading("Oyuncu", text="Oyuncu Adı")
            tree_yol.heading("Mevki", text="Mevki")

            tree_yol.column("Sira", width=50, anchor="center")
            tree_yol.column("ID", width=50, anchor="center")

            nodes_obj = {n.node_id: n for n in self.dm.get_all_nodes()}
            for i, nid in enumerate(path_list):
                n = nodes_obj.get(nid)
                tree_yol.insert("", "end",
                                values=(i + 1, nid, n.name if n else "?", getattr(n, 'mevki', '-') if n else '-'))

        # --- SEKME 3: TARAMA GEÇMİŞİ ---
        if visited_list:
            cols = ("Sira", "ID", "Oyuncu", "Durum")
            tree_hist = create_treeview(tab_gecmis, cols)
            tree_hist.heading("Sira", text="Ziyaret Sırası")
            tree_hist.heading("ID", text="ID")
            tree_hist.heading("Oyuncu", text="Oyuncu Adı")
            tree_hist.heading("Durum", text="Analiz")

            tree_hist.column("Sira", width=80, anchor="center")
            tree_hist.column("ID", width=50, anchor="center")

            nodes_obj = {n.node_id: n for n in self.dm.get_all_nodes()}
            path_set = set(path_list) if path_list else set()

            for i, nid in enumerate(visited_list):
                n = nodes_obj.get(nid)
                status = "✅ Rota Üzerinde" if nid in path_set else "👁️ İncelendi"
                tree_hist.insert("", "end", values=(i + 1, nid, n.name if n else "?", status))

        # Alt Buton
        ttk.Button(res_win, text="Raporu Kapat", command=res_win.destroy).pack(pady=10)
    # --- ALGORİTMALAR ---

    def run_bfs(self):
        u = simpledialog.askinteger("BFS", "Başlangıç ID:")
        # v (Hedef) sormuyoruz!

        G = self.get_nx_graph()
        if not u or u not in G: return
        self.is_paused = False

        # --- HESAPLAMA ---
        cpu_start = time.perf_counter()

        # Hedef olmadığı için 'path' tutmamıza gerek yok, sadece gezilenleri tutuyoruz
        queue = [u]
        visited = {u}
        visited_list = [u]  # Rapor için sıralı liste
        visited_edges = []
        animation_frames = []

        while queue:
            current = queue.pop(0)

            # Anlık durumu kaydet
            animation_frames.append({'nodes': list(visited), 'edges': list(visited_edges)})

            for neighbor in G.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    visited_list.append(neighbor)
                    visited_edges.append((current, neighbor))
                    queue.append(neighbor)

        cpu_end = time.perf_counter()

        # --- ANİMASYON ---
        total_duration = self.animation_duration.get()
        delay = total_duration / len(animation_frames) if len(animation_frames) > 0 else 0.5

        for frame in animation_frames:
            while self.is_paused: self.master.update(); time.sleep(0.1)
            self.update_graph_visualization(
                highlight_nodes=frame['nodes'],
                highlight_edges=frame['edges'],
                is_search_phase=True,
                search_color="#3498db"  # BFS için Mavi (Farklılık olsun)
            )
            self.master.update();
            time.sleep(delay)

        # Sonuçta spesifik bir yol çizmiyoruz, çünkü tüm ağı gezdik.
        # Son kareyi ekranda bırakıyoruz.

        # --- RAPORLAMA ---
        description = (
            "📌 BFS (Keşif Modu):\n"
            "- Hedef belirtilmediği için algoritma, başlangıç düğümünden ulaşılabilen TÜM düğümleri gezdi.\n"
            "- Bu analiz, seçilen oyuncunun ağ içerisindeki 'Erişim Gücünü' ve 'Bağlantı Genişliğini' gösterir.\n"
            "- Katman katman (dalga gibi) yayılarak ilerlemiştir."
        )

        stats = {
            'Süre': cpu_end - cpu_start,
            'Gezilen': len(visited),
            'Yol': 0,  # Yol yok
            'Maliyet': 0  # Maliyet hesaplanmadı
        }
        # path_list=None gönderiyoruz
        self.show_detailed_result("BFS Tam Keşif Raporu", stats, description, None, visited_list)
    # -------------------------------------------------------------------------
    # 2. DFS (DERİNLİK ÖNCELİKLİ)
    # -------------------------------------------------------------------------
    def run_dfs(self):
        u = simpledialog.askinteger("DFS", "Başlangıç ID:")
        # Hedef yok

        G = self.get_nx_graph()
        if not u or u not in G: return
        self.is_paused = False

        cpu_start = time.perf_counter()

        stack = [u]
        visited = set()
        visited_list = []
        visited_edges = []
        animation_frames = []

        while stack:
            current = stack.pop()

            if current not in visited:
                visited.add(current)
                visited_list.append(current)

                # Görselleştirme karesi
                animation_frames.append({'nodes': list(visited), 'edges': list(visited_edges)})

                # Komşuları ekle
                # Ters sıralıyoruz ki, stack'ten çekince küçükten büyüğe veya mantıklı bir sırada gelsin
                neighbors = sorted(G.neighbors(current), reverse=True)

                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)
                        # Kenarı görselleştirmek için (DFS'de tam kenar takibi zordur, yaklaşık olarak ekliyoruz)
                        if neighbor not in visited:
                            visited_edges.append((current, neighbor))

        cpu_end = time.perf_counter()

        # --- ANİMASYON ---
        total_duration = self.animation_duration.get()
        delay = total_duration / len(animation_frames) if len(animation_frames) > 0 else 0.5

        for frame in animation_frames:
            while self.is_paused: self.master.update(); time.sleep(0.1)
            self.update_graph_visualization(
                highlight_nodes=frame['nodes'],
                highlight_edges=frame['edges'],
                is_search_phase=True,
                search_color="#e67e22"  # DFS için Turuncu
            )
            self.master.update();
            time.sleep(delay)

        description = (
            "📌 DFS (Keşif Modu):\n"
            "- Algoritma, ağın en uç noktalarına kadar gidip geri dönerek (Backtracking) tüm yapıyı taradı.\n"
            "- Bu mod, tüm oyuncu havuzunun birbirine ne kadar bağlı olduğunu test etmek için kullanılır.\n"
            "- Stack (Yığın) mantığıyla çalıştığı için son keşfedilen yoldan ilerlemeye öncelik verdi."
        )

        stats = {
            'Süre': cpu_end - cpu_start,
            'Gezilen': len(visited),
            'Yol': 0,
            'Maliyet': 0
        }
        self.show_detailed_result("DFS Tam Keşif Raporu", stats, description, None, visited_list)

    # -------------------------------------------------------------------------
    # 3. DIJKSTRA (EN UYGUN HAT)
    # -------------------------------------------------------------------------
    def run_dijkstra(self):
        u = simpledialog.askinteger("Dijkstra", "Başlangıç ID:")
        v = simpledialog.askinteger("Dijkstra", "Hedef ID:")
        G = self.get_nx_graph()
        if not u or not v or u not in G or v not in G: return
        self.is_paused = False;
        import heapq

        cpu_start = time.perf_counter()
        queue = [(0, u, [u])];
        visited = set();
        visited_list = [];
        visited_edges = []
        animation_frames = [];
        final_path = None;
        final_cost = 0

        while queue:
            (cost, current, path) = heapq.heappop(queue)
            if current in visited: continue
            visited.add(current);
            visited_list.append(current)
            animation_frames.append({'nodes': list(visited), 'edges': list(visited_edges)})
            if current == v: final_path = path; final_cost = cost; break
            for neighbor, data in G[current].items():
                if neighbor not in visited:
                    visited_edges.append((current, neighbor))
                    heapq.heappush(queue, (cost + data.get('weight', 1.0), neighbor, path + [neighbor]))

        cpu_end = time.perf_counter()
        if not final_path: messagebox.showinfo("Sonuç", "Hedefe ulaşılamadı."); return

        total_duration = self.animation_duration.get()
        delay = total_duration / len(animation_frames) if len(animation_frames) > 0 else 0.5

        for frame in animation_frames:
            while self.is_paused: self.master.update(); time.sleep(0.1)
            self.update_graph_visualization(highlight_nodes=frame['nodes'], highlight_edges=frame['edges'],
                                            is_search_phase=True, search_color="#9b59b6")
            self.master.update();
            time.sleep(delay)

        self.update_graph_visualization(highlight_path=final_path)

        description = (
            "📌 Dijkstra Algoritması Analizi:\n"
            "- Algoritma, başlangıçtan itibaren kümülatif maliyeti (Cost) en düşük olan yolu garanti etti.\n"
            "- Herhangi bir sezgisel (heuristic) tahmin kullanmadığı için hedefi bulana kadar dairesel olarak genişledi.\n"
            "- Sonuç kesinlikle matematiksel olarak en verimli yoldur, ancak A*'a göre daha fazla düğüm gezmiş olabilir."
        )

        stats = {
            'Süre': cpu_end - cpu_start,
            'Gezilen': len(visited),
            'Yol': len(final_path),
            'Maliyet': final_cost
        }
        self.show_detailed_result("Dijkstra Analiz Raporu", stats, description, final_path, visited_list)

    # -------------------------------------------------------------------------
    # 4. A* (STRATEJİK HEDEF ODAKLI)
    # -------------------------------------------------------------------------
    def run_astar(self):
        u = simpledialog.askinteger("A*", "Başlangıç ID:")
        v = simpledialog.askinteger("A*", "Hedef ID:")
        G = self.get_nx_graph()
        if not u or not v or u not in G or v not in G: return

        # --- STRATEJİ SEÇİM PENCERESİ ---
        selection_win = tk.Toplevel(self)
        selection_win.title("A* Modu Seç")
        selection_win.geometry("350x220")
        selection_win.configure(bg="#f0f2f5")

        ttk.Label(selection_win, text="Arama Stratejisi Seçin:", font=("Segoe UI", 11, "bold"),
                  background="#f0f2f5").pack(pady=10)

        # Varsayılan: Standart Mod
        strategy_var = tk.StringVar(value="standart")

        # Seçenekler: (Görünen İsim, Değer)
        strategies = [
            ("📏 Standart A* (En Kısa Yol / Dijkstra Benzeri)", "standart"),
            ("⚡ Hızlı Hücum Odaklı (Hız)", "hiz"),
            ("🎯 Oyun Kurma Odaklı (Pas)", "pas"),
            ("🧠 Liderlik Odaklı (Tecrübe)", "tecrube")
        ]

        for text, val in strategies:
            # Standart mod için farklı renk veya stil yapılabilir ama basit tutuyoruz
            ttk.Radiobutton(selection_win, text=text, variable=strategy_var, value=val).pack(anchor="w", padx=20,
                                                                                             pady=2)

        ttk.Button(selection_win, text="Analizi Başlat", command=selection_win.destroy).pack(pady=15)

        self.wait_window(selection_win)
        selected_mode = strategy_var.get()

        # --- ALGORİTMA HAZIRLIĞI ---
        self.is_paused = False
        import heapq
        nodes_obj = {n.node_id: n for n in self.dm.get_all_nodes()}

        # --- DİNAMİK HEURISTIC FONKSİYONU ---
        def heuristic(id1, id2):
            if id1 not in nodes_obj or id2 not in nodes_obj: return 0
            n1, n2 = nodes_obj[id1], nodes_obj[id2]

            # 1. STANDART MOD (Optimal Yol)
            if selected_mode == "standart":
                # Standart A*'da heuristic, graf üzerindeki tahmini mesafedir.
                # Burada 'hiz' farkını düşük bir katsayıyla kullanarak
                # "Kabul Edilebilir" (Admissible) bir tahmin yapıyoruz.
                # Katsayı 1.0 veya daha düşük olmalı ki maliyeti (weight) ezmesin.
                return abs(getattr(n1, 'hiz', 0) - getattr(n2, 'hiz', 0)) * 1.0

                # 2. STRATEJİK MODLAR (Agresif / Greedy)
            else:
                # Seçilen özellik (hiz, pas, tecrube)
                attr = selected_mode
                val1 = getattr(n1, attr, 0)
                val2 = getattr(n2, attr, 0)

                # Katsayı 100.0: Maliyeti (g) önemsiz kılar, sadece özelliğe (h) odaklanır.
                return abs(val1 - val2) * 100.0

        # --- HESAPLAMA ---
        cpu_start = time.perf_counter()

        queue = [(0, 0, u, [u])]  # (f_score, g_score, current_node, path)
        visited = set();
        visited_list = [];
        visited_edges = []
        animation_frames = [];
        final_path = None;
        final_cost = 0

        while queue:
            (_, cost, current, path) = heapq.heappop(queue)

            if current in visited: continue
            visited.add(current);
            visited_list.append(current)

            animation_frames.append({'nodes': list(visited), 'edges': list(visited_edges)})

            if current == v:
                final_path = path;
                final_cost = cost;
                break

            for neighbor, data in G[current].items():
                if neighbor not in visited:
                    visited_edges.append((current, neighbor))

                    weight = data.get('weight', 1.0)
                    new_cost = cost + weight  # g(n)

                    h = heuristic(neighbor, v)  # h(n)
                    total_score = new_cost + h  # f(n) = g(n) + h(n)

                    heapq.heappush(queue, (total_score, new_cost, neighbor, path + [neighbor]))

        cpu_end = time.perf_counter()
        if not final_path: messagebox.showinfo("Sonuç", "Hedefe ulaşılamadı."); return

        # --- ANİMASYON ---
        total_duration = self.animation_duration.get()
        delay = total_duration / len(animation_frames) if len(animation_frames) > 0 else 0.5

        # Renk seçimi: Standart ise Kırmızı, Stratejik ise daha koyu bir ton veya farklı renk olabilir
        draw_color = "#e74c3c" if selected_mode == "standart" else "#d35400"

        for frame in animation_frames:
            while self.is_paused: self.master.update(); time.sleep(0.1)
            self.update_graph_visualization(
                highlight_nodes=frame['nodes'],
                highlight_edges=frame['edges'],
                is_search_phase=True,
                search_color=draw_color
            )
            self.master.update();
            time.sleep(delay)

        self.update_graph_visualization(highlight_path=final_path)

        # --- RAPORLAMA ---
        total_nodes = len(G.nodes())

        titles = {
            "standart": "Standart A* (En Kısa Yol)",
            "hiz": "A* (Hızlı Hücum Stratejisi)",
            "pas": "A* (Oyun Kurma Stratejisi)",
            "tecrube": "A* (Liderlik Stratejisi)"
        }

        # Açıklama metnini moda göre dinamik yap
        if selected_mode == "standart":
            desc = (
                "📌 Standart A* Analizi:\n"
                "- Bu modda algoritma, 'Kabul Edilebilir' (Admissible) bir sezgisel fonksiyon kullandı.\n"
                "- Sonuç: Dijkstra ile AYNI (En Düşük) maliyetli yolu buldu.\n"
                "- Fark: Hedefe yönelik tahmin yaptığı için Dijkstra'ya göre daha az düğüm gezerek sonuca ulaştı."
            )
        else:
            desc = (
                f"📌 Stratejik A* Analizi ({titles[selected_mode]}):\n"
                "- Bu modda algoritma 'Agresif' (Greedy) davrandı.\n"
                "- Maliyeti (Yol Uzunluğunu) ikinci plana atıp, seçilen özelliği hedef oyuncuya en yakın olan rotayı tercih etti.\n"
                "- Sonuç: Matematiksel olarak en kısa yol olmayabilir ama stratejik açıdan en uygun yoldur."
            )

        stats = {
            'Süre': cpu_end - cpu_start,
            'Gezilen': len(visited),
            'Yol': len(final_path),
            'Maliyet': final_cost
        }

        self.show_detailed_result(titles[selected_mode], stats, desc, final_path, visited_list)
    def run_coloring(self):
        from core.algorithms.coloring import WelshPowellAlgorithm
        G = self.get_nx_graph()
        t_start = time.perf_counter()
        color_map = WelshPowellAlgorithm(G).execute()
        t_total = time.perf_counter() - t_start
        self.update_graph_visualization(node_colors_dict=color_map)

        metrics = {
            "⏱️ İşlem Süresi": f"{t_total:.6f} saniye",
            "🌈 Kullanılan Renk Sayısı": f"{len(set(color_map.values()))}",
            "✅ Çatışma Durumu": "0 Çatışma (Başarılı)"
        }
        res_win = tk.Toplevel(self);
        res_win.title("Welsh-Powell");
        res_win.geometry("500x450")
        ttk.Label(res_win, text="Mevki Boyama Sonuçları", font=("Segoe UI", 12, "bold")).pack(pady=10)
        f = ttk.Frame(res_win);
        f.pack(fill="x", padx=20)
        for k, v in metrics.items(): ttk.Label(f, text=f"{k}: {v}").pack(anchor="w")
        tree = ttk.Treeview(res_win, columns=("ID", "Isim", "Grup"), show="headings")
        tree.heading("ID", text="ID");
        tree.heading("Isim", text="İsim");
        tree.heading("Grup", text="Renk")
        nodes_obj = {n.node_id: n for n in self.dm.get_all_nodes()}
        for nid, c in color_map.items():
            n = nodes_obj.get(nid)
            tree.insert("", "end", values=(nid, n.name if n else "", f"Grup {c}"))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def run_connected_components(self):
        G = self.get_nx_graph()
        t_start = time.perf_counter()
        comps = list(nx.connected_components(G))
        t_total = time.perf_counter() - t_start
        color_map = {n: i for i, c in enumerate(comps) for n in c}
        self.update_graph_visualization(node_colors_dict=color_map)

        res_win = tk.Toplevel(self);
        res_win.title("Topluluklar");
        res_win.geometry("500x400")
        ttk.Label(res_win, text=f"Ayrık Grup Sayısı: {len(comps)} (Süre: {t_total:.6f}s)",
                  font=("Segoe UI", 12, "bold")).pack(pady=10)
        tree = ttk.Treeview(res_win, columns=("Grup", "Oyuncular", "Sayi"), show="headings")
        tree.heading("Grup", text="Grup");
        tree.heading("Oyuncular", text="Üyeler");
        tree.heading("Sayi", text="Kişi")
        tree.column("Grup", width=80);
        tree.column("Oyuncular", width=300);
        tree.column("Sayi", width=50)
        nodes_obj = {n.node_id: n for n in self.dm.get_all_nodes()}
        for i, c in enumerate(comps):
            names = ", ".join([nodes_obj[n].name[:10] for n in list(c)[:4] if n in nodes_obj])
            tree.insert("", "end", values=(f"Takım {i + 1}", names + "...", len(c)))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def show_top_users(self):
        G = self.get_nx_graph()
        t_start = time.perf_counter()
        centrality = nx.degree_centrality(G)
        top_5 = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        t_total = time.perf_counter() - t_start

        res_win = tk.Toplevel(self);
        res_win.title("En Etkili Oyuncular");
        res_win.geometry("500x350")
        ttk.Label(res_win, text=f"En Etkili 5 Oyun Kurucu (Süre: {t_total:.6f}s)", font=("Segoe UI", 12, "bold")).pack(
            pady=10)
        tree = ttk.Treeview(res_win, columns=("Sira", "Isim", "Mevki", "Skor"), show="headings")
        tree.heading("Sira", text="#");
        tree.heading("Isim", text="İsim");
        tree.heading("Mevki", text="Mevki");
        tree.heading("Skor", text="Merkezilik")
        nodes_obj = {n.node_id: n for n in self.dm.get_all_nodes()}
        for i, (nid, score) in enumerate(top_5):
            n = nodes_obj.get(nid)
            tree.insert("", "end", values=(i + 1, n.name if n else str(nid), getattr(n, 'mevki', '-') if n else '-',
                                           f"{score:.4f}"))
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    # --- CRUD ve DİĞER ---
    def on_node_click(self, event):
        if event.xdata and event.ydata and hasattr(self, 'pos'):
            for nid, (x, y) in self.pos.items():
                if (event.xdata - x) ** 2 + (event.ydata - y) ** 2 < 0.05:
                    self.show_node_details(nid);
                    break

    def show_node_details(self, node_id):
        from core.node import Node
        node = self.dm.session.query(Node).filter_by(node_id=node_id).first()
        if not node: return
        info = f"👤 {node.name}\n🆔 {node.node_id} | 🏟️ {getattr(node, 'mevki', '-')}\n" + \
               f"🏃 Hız: {getattr(node, 'hiz', 0):.2f} | 🎯 Pas: {getattr(node, 'pas', 0):.2f}\n" + \
               f"⚽ Şut: {getattr(node, 'sut', 0):.2f} | 🛡️ Def: {getattr(node, 'defans', 0):.2f}"

        if self.details_window is None or not self.details_window.winfo_exists():
            self.details_window = tk.Toplevel(self);
            self.details_window.title(f"Oyuncu: {node.name}")
            self.details_window.geometry("350x250");
            self.details_window.attributes('-topmost', True)
            self.details_info_label = ttk.Label(self.details_window, text=info, padding=20, font=("Segoe UI", 11));
            self.details_info_label.pack()
        else:
            self.details_info_label.config(text=info); self.details_window.lift()
        self.update_graph_visualization(highlight_nodes=[node_id])

    def add_node_dialog(self):
        # DÜZELTME: self.open_form -> self.open_node_form
        d = self.open_node_form("Ekle");
        if d:
            try:
                from core.node import Node
                n = Node(d['id'], d['name']);
                for k, v in d.items(): setattr(n, k, v)
                self.dm.add_node(n);
                self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def update_selected_node_dialog(self):
        sel = self.node_tree.selection()
        if sel:
            nid = self.node_tree.item(sel[0])['values'][0]
            n = next((x for x in self.dm.get_all_nodes() if x.node_id == nid), None)
            if n:
                # DÜZELTME: self.open_form -> self.open_node_form
                d = self.open_node_form("Güncelle",
                                   {"id": n.node_id, "name": n.name, "hiz": n.hiz, "pas": n.pas, "sut": n.sut,
                                    "defans": n.defans, "fizik": n.fizik, "tecrube": n.tecrube, "mevki": n.mevki})
                if d:
                    for k, v in d.items(): setattr(n, k, v)
                    self.dm.session.commit();
                    self.refresh_ui()

    def delete_selected_node(self):
        sel = self.node_tree.selection()
        if sel and messagebox.askyesno("Sil", "Silinsin mi?"):
            self.dm.delete_node(self.node_tree.item(sel[0])['values'][0]);
            self.refresh_ui()

    def add_edge_dialog(self):
        u, v = simpledialog.askinteger("1", "Kaynak:"), simpledialog.askinteger("2", "Hedef:")
        if u and v:
            try:
                self.dm.add_edge(u, v); self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def delete_edge_dialog(self):
        u, v = simpledialog.askinteger("1", "Kaynak:"), simpledialog.askinteger("2", "Hedef:")
        if u and v:
            try:
                self.dm.delete_edge(u, v); self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def import_json(self):
        fn = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if fn:
            try:
                with open(fn, encoding="utf-8") as f:
                    self.dm.import_from_extended_json(json.load(f))
                self.refresh_ui();
                messagebox.showinfo("OK", "Yüklendi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def export_json(self):
        fn = filedialog.asksaveasfilename(defaultextension=".json")
        if fn: self.dm.export_to_json(fn); messagebox.showinfo("OK", "Kaydedildi.")

    def open_node_form(self, title, init=None):
        win = tk.Toplevel(self);
        win.title(title);
        win.geometry("300x550");
        win.grab_set()
        es = {}
        for k, l in [("id", "ID"), ("name", "İsim"), ("hiz", "Hız"), ("pas", "Pas"), ("sut", "Şut"),
                     ("defans", "Defans"), ("fizik", "Fizik"), ("tecrube", "Tecrübe")]:
            ttk.Label(win, text=l).pack()
            e = ttk.Entry(win);
            e.pack();
            if init: e.insert(0, str(init.get(k, "")))
            if k == "id" and init: e.config(state="disabled")
            es[k] = e
        ttk.Label(win, text="Mevki").pack()
        cb = ttk.Combobox(win, values=list(self.position_map.keys()));
        cb.pack();
        cb.set(init.get("mevki", "Defans") if init else "Defans")
        res = {}

        def save():
            try:
                for k, e in es.items(): res[k] = int(e.get()) if k == "id" else (
                    e.get() if k == "name" else float(e.get()))
                res["mevki"] = cb.get();
                win.destroy()
            except:
                messagebox.showerror("Hata", "Veri hatası")

        ttk.Button(win, text="Kaydet", command=save).pack(pady=10)
        self.master.wait_window(win);
        return res if res else None