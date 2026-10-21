# Panduan Bagian Syauqi

## File yang perlu dipahami

1. `src/main.py`: menerima argumen/menu, membaca JSON, membuat random initial state, memanggil algoritma, lalu mencetak dan mengekspor hasil.
2. `src/visualization/grid.py`: menggambar setiap Placement inside sebagai Rectangle. Ukuran memakai placed_width/placed_length dari core sehingga rotasi konsisten dengan validasi.
3. `src/visualization/plot.py`: membaca history; format HC/SA memakai iteration/objective, GA memakai generation/max_fitness/average_fitness.
4. `src/visualization/export.py`: mengubah State ke JSON dan sebaliknya, mengekspor per-run, membuat results.csv, serta grafik perbandingan GA.
5. `tests/test_visualization.py`: pemeriksaan integrasi dengan kode algoritma asli.

Visualisasi tidak mengubah State atau menjalankan pencarian tambahan. Nilai objective dihitung dari mode yang sama dengan run; ShippingFee mentah ditampilkan terpisah untuk mode bonus. Gambar disimpan memakai backend Agg agar CLI berjalan tanpa jendela GUI.

## Urutan demo singkat

- Jalankan `python src/main.py` dan pilih HC, lalu steepest.
- Tunjukkan folder yang dicetak terminal; buka initial_state.png dan final_state.png di VS Code.
- Jelaskan inside/outside, orientasi, objective, berat dan status valid.
- Jalankan SA dan tunjukkan probability_plot.png serta objective_plot.png.
- Jalankan GA dan tunjukkan fitness_max_average_plot.png.
- Jika eksperimen sudah tersedia, tunjukkan results.csv dan kedua grafik perbandingan GA.

Gunakan interpreter .venv sesuai README. Jangan mengklaim semua dataset naik skornya; initial state bisa sudah memuat semua kendaraan atau pencarian terhenti pada plateau.

## Setelah clone di laptop

```bash
git branch --show-current
```

Harus menampilkan `syauqi-visualisasi`. Perubahan berikutnya tetap di branch ini. Setelah mengedit file tertentu:

```bash
git status
git add src/visualization/grid.py
git commit -m "fix(visualization): improve vehicle labels"
git push origin syauqi-visualisasi
```

Ganti daftar file dan pesan sesuai perubahan sebenarnya. Commit awal bagian visualisasi sudah tersedia; tidak perlu melakukan commit ulang saat clone. Sebelum PR ke main, fetch perubahan terbaru dan selesaikan integrasi dengan kelompok sesuai guide.

## Batas pekerjaan ini

CLI + Matplotlib sesuai prioritas guide. Animasi, Streamlit, dan multi-kapal tidak termasuk implementasi ini. Laporan akhir, kesimpulan perbandingan pada dataset yang disepakati, Form AI, dan release tetap perlu dikerjakan kelompok. Grafik/CSV dari run contoh adalah verifikasi operasional, bukan analisis final.

## Verifikasi saat implementasi

- 21 tes unittest lulus (18 tes bawaan + 3 tes integrasi baru).
- Konfigurasi eksperimen bawaan berhasil menjalankan 24 run, seluruh final state valid; ekspor menghasilkan 77 PNG dan 25 CSV.
- Random Restart HC pada demo_compact.json, seed 2026, max_restart 2, max_iterations 20: objective awal 430, terbaik 540, berat akhir 600/650, valid.
- Grid dan grafik fitness diperiksa secara visual.
- Verifikasi dilakukan di lingkungan Python Linux, bukan langsung pada laptop Windows pengguna; langkah Windows memakai venv standar dan perlu dijalankan pada laptop untuk konfirmasi instalasi.
