# IF3070_G28_eskrim (Tugas Besar 1: Local Search)

Implementasi tiga algoritma *local search* untuk persoalan **Pencarian Solusi Penataan Kendaraan di Geladak Kapal**: menempatkan kendaraan pada grid kapal untuk memaksimalkan total *shipping fee* dengan tetap memenuhi batas kapasitas berat dan tanpa tumpang tindih.

## Algoritma yang diimplementasikan

- Simulated Annealing (SA)
- Hill-Climbing (HC)
- Genetic Algorithm (GA)


## Setup

Dari root repository:

```bash
pip install matplotlib numpy
```

Hanya dua library eksternal yang dibutuhkan; sisanya standar library Python.

## Cara Menjalankan

Jalankan runner dari root repository:

```bash
# jalankan semua algoritma (SA + HC + GA) pada dataset default (sample_medium)
python src/main.py

# jalankan algoritma tertentu
python src/main.py --algo sa
python src/main.py --algo hc
python src/main.py --algo ga
python src/main.py --algo sa hc

# pakai dataset lain
python src/main.py --dataset src/data/sample_small.json

# eksperimen tambahan khusus SA (konsistensi 10 seed, pengaruh alpha/T0, skalabilitas)
python src/main.py --algo sa --extra consistency alpha t0 scaling
```

Hasil per algoritma tersimpan di `output/<algo>/` (JSON + PNG), dan ringkasan lintas-algoritma di `output/ringkasan.csv`.

## Pembagian Tugas

| Nama | NIM | Tugas |
| --- | --- | --- |
| Muthia Ariesta Anggraeni | 18224045 | Simulated Annealing, dokumen |
| Benedicta Sherin C. P. | 18224065 | Genetic Algorithm, dokumen |
| Aisyah Az Zahra | 18224121 | Hill-Climbing, dokumen |