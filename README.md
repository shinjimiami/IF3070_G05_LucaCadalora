# LucaCadalora - Optimasi Muatan Kapal

Tugas Besar 1 IF3070 Dasar Inteligensi Artifisial. Program Python mengoptimalkan total ShippingFee kendaraan di geladak grid dua dimensi dengan constraint boundary, overlap, dan kapasitas berat.

## Instalasi (Windows / VS Code)

Python **3.10 atau lebih baru** dan Git diperlukan. Buka terminal VS Code di folder tempat proyek akan disimpan.

```powershell
git clone --branch syauqi-visualisasi https://github.com/shinjimiami/IF3070_G05_LucaCadalora.git
cd IF3070_G05_LucaCadalora
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

Perintah memakai interpreter environment secara langsung sehingga aktivasi PowerShell tidak diperlukan. Jika `py` tidak tersedia tetapi `python --version` menunjukkan versi yang sesuai, gunakan `python -m venv .venv`. Di VS Code, pilih interpreter `.venv` melalui **Python: Select Interpreter**. Menu terminal meminta algoritma dan, untuk HC, varian; input default adalah `input/example.json`.

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/main.py
```

## Jalankan tanpa menu

Contoh berikut memakai `python`; di Windows ganti dengan `.\.venv\Scripts\python.exe` jika environment belum diaktifkan.

```bash
python src/main.py --algorithm hc --variant steepest --seed 2026
python src/main.py --algorithm hc --variant sideways --max-sideways 20
python src/main.py --algorithm hc --variant random_restart --max-restart 5
python src/main.py --algorithm sa --max-iterations 1000 --temperature 100 --cooling-rate 0.995
python src/main.py --algorithm ga --population 30 --generations 100
python src/main.py --algorithm hc --input input/demo_compact.json --seed 2026
python -m src.main --algorithm ga --population 10 --generations 20
python src/main.py --help
```

HC mendukung `first_improvement`, `steepest`, `stochastic`, `sideways`, dan `random_restart`.
Gunakan `--objective shipping_fee` untuk requirement wajib. Mode bonus `fee_per_area` dan `fee_with_eta` dipisahkan; jangan membandingkan skor antar-mode seolah satuan skornya sama.

Parameter lanjutan dapat diberikan melalui `--params input/parameter_saya.json`. Isi file berupa object parameter fungsi algoritma, misalnya `{"mutation_rate": 0.3, "elitism_count": 1, "tournament_size": 2}` untuk GA. Nilainya mengoverride flag CLI; parameter yang tidak dikenal ditolak oleh fungsi. Untuk populasi 2, sesuaikan elitism dan tournament di file parameter karena default core adalah 2 dan 3.

## Output

Default: `output/<timestamp>_<algoritma>/`. Gunakan `--output output/nama_run_baru` untuk folder eksplisit. CLI menolak folder yang sudah berisi file agar hasil lama tetap tersedia.

| File | Isi |
| --- | --- |
| `initial_state.png` | Grid konfigurasi awal dan ringkasan muatan |
| `final_state.png` | Grid solusi terbaik yang dikembalikan algoritma |
| `objective_plot.png` | HC/SA: objective sepanjang history |
| `probability_plot.png` | SA: probabilitas penerimaan kandidat serta penanda penolakan |
| `fitness_max_average_plot.png` | GA: fitness maksimum dan rata-rata setiap generasi |
| `result.json` | State lengkap, history, metrik, dan parameter run tunggal |
| `history.csv` | History angka untuk analisis lebih lanjut |

Grid: titik `(0,0)` kiri bawah, sumbu x = `width`, sumbu y = `length`. H memakai width/length asli; V menukarnya. Warna ID konsisten untuk initial/final state dengan urutan kendaraan yang sama. Label H/V adalah orientasi model, bukan jaminan sisi panjang selalu horizontal/vertikal. Panel mencatat kendaraan inside/outside, skor objective, ShippingFee mentah, berat, dan validitas.

## Input JSON

```json
{
  "ship": {"width": 8, "length": 8, "maxCapacity": 650},
  "vehicles": [
    {"id":"A", "width":3, "length":4, "shippingFee":180, "weight":200, "ETA":2},
    {"id":"B", "width":2, "length":5, "shippingFee":160, "weight":180, "ETA":1}
  ]
}
```

Dimensi harus integer positif, ID unik, angka finite, nilai berat/fee/ETA dan kapasitas tidak negatif. Minimal satu kendaraan. ETA opsional dengan default 0 mengikuti model. Ukuran melebihi kapal diperbolehkan; kendaraan tersebut tetap outside jika tidak bisa ditempatkan. Loader menerima nama atribut camelCase maupun snake_case yang didukung core.

`input/example.json` berasal dari Anggota 2; `input/demo_compact.json` merupakan contoh tambahan untuk melihat persaingan muatan di kapal yang lebih terbatas. Dataset contoh bukan bukti kualitas algoritma pada semua persoalan.

## Eksperimen dan ekspor grafik

```bash
python src/main.py --experiments --input input/example.json --config input/experiment_config.json
```

Konfigurasi bawaan menjalankan 3 HC, 3 SA, dan 18 GA = 24 run. Konfigurasi eksperimen ada pada `input/experiment_config.json`, dengan default tambahan dari `src/experiments/config.py`. Flag parameter run tunggal tidak digunakan pada mode eksperimen; edit konfigurasi untuk mengganti variannya. Runner Anggota 2 digunakan sebagaimana adanya.

Output tambahan:

- `experiments.json`: seluruh hasil dan konfigurasi.
- `results.csv`: baris ringkasan per run, seed, objective, ShippingFee, durasi, dan validitas.
- Subfolder per run: initial/final state, grafik algoritma, JSON, dan history CSV.
- `ga_iteration_comparison.png` dan `ga_population_comparison.png`: mean objective terbaik dan simpangan baku sampel, disertai titik setiap run.

Ekspor JSON eksperimen yang sudah tersedia tanpa mengulang pencarian:

```bash
python src/main.py --render-experiments output/hasil_lama/experiments.json --output output/grafik_baru
```

## Membaca metrik dengan benar

- SA mengembalikan **best state**, bukan selalu current state pada titik history terakhir. Grafik memperlihatkan current dan best objective.
- `stuck_count` SA mengikuti implementasi Anggota 2: jumlah interval `stuck_threshold` tanpa kenaikan best objective. Ini indikator stagnasi, bukan pembuktian local optimum matematis.
- GA initial state adalah satu individual masukan, sedangkan generasi 0 mencakup populasi random yang bisa sudah memiliki fitness lebih tinggi. GA mencatat `generations`, bukan `iterations`; visualisasi membaca field aslinya.
- HC random restart memakai indeks history global yang mencakup initial state setiap restart. Jumlah titik history tidak sama dengan jumlah langkah pencarian; garis vertikal menandai restart.
- `duration` menggunakan nilai yang diberikan fungsi algoritma. Ekspor gambar tidak termasuk. GA saat ini mulai menghitung durasi setelah inisialisasi populasi; perbandingan durasi antaralgoritma perlu menyebut batas pengukuran ini.
- Seed HC/SA disamakan per run oleh runner, sedangkan GA memakai offset seed per konfigurasi. Seed disimpan agar dapat direproduksi, tetapi konfigurasi GA tidak memakai initial population identik.
- Solusi valid atau terbaik yang ditemukan belum membuktikan global optimum.

## Struktur dan pembagian kerja

```text
input/                  JSON dataset dan konfigurasi eksperimen
src/main.py             CLI dan integrasi (Anggota 3)
src/models/             Ship, Vehicle, Placement, State (Anggota 1)
src/core/               Constraint, objective, initial state, neighbor (Anggota 1)
src/algorithms/         HC (Anggota 1), SA/GA (Anggota 2)
src/experiments/        Konfigurasi dan runner (Anggota 2)
src/visualization/      Grid, plot, ekspor (Anggota 3)
tests/                  Tes core, algoritma, dan integrasi visualisasi
docs/                   Catatan implementasi / laporan kelompok
output/                 Hasil lokal (diabaikan Git)
```

Anggota 3: Muhammad Syauqi Azizi (18224046). Nama lengkap anggota lain pada laporan mengikuti pembagian final kelompok.

Branch `syauqi-visualisasi` dimulai dari commit `e3cd60b` pada `athar` yang sudah menyertakan core dan HC. Kode algoritma/core teman dipertahankan. Integrasikan melalui PR setelah pemeriksaan kelompok; `main` tidak diubah oleh pekerjaan visualisasi ini.

## Pengujian

```bash
python -m unittest discover -s tests -v
```

Tes tambahan memastikan rotasi menghasilkan dimensi rectangle yang benar, state dapat diserialisasi/dipulihkan, ketiga algoritma dapat dipanggil lewat CLI dan menghasilkan output, serta input dimensi pecahan/ID duplikat ditolak.

## Catatan pengerjaan dan penggunaan AI

CLI, visualisasi, ekspor, contoh dataset tambahan, pengujian integrasi, dan dokumentasi Anggota 3 disiapkan dengan bantuan ChatGPT/Codex. Anggota kelompok perlu memeriksa dan memahami hasil serta mencatat penggunaan sebenarnya pada Form Penggunaan Generative AI. Model/core dan algoritma menggunakan kode yang sudah ada di branch teman. Penjelasan algoritma dan referensinya menjadi tanggung jawab pemilik algoritma sesuai panduan kelompok.
