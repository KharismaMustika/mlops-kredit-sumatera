# src/data.py — pemuatan, validasi skema & domain kredit, dan pembagian menurut waktu
import pandas as pd

SKEMA = {
    "pengajuan_id": "object",
    "tanggal_pengajuan": "object",
    "periode": "object",
    "segmen": "object",
    "wilayah": "object",
    "kanal": "object",
    "usia": "int64",
    "tanggungan": "int64",
    "lama_usaha_tahun": "float64",
    "penghasilan_bulanan": "float64",
    "ragam_penghasilan": "float64",
    "plafon_diajukan": "float64",
    "tenor_bulan": "int64",
    "bunga_tahunan": "float64",
    "angsuran_bulanan": "float64",
    "rata_saldo_90h": "float64",
    "jumlah_tunggakan_12b": "int64",
    "gagal_bayar": "int64",
    "status_restrukturisasi": "object",
}

RENTANG = {
    "usia": (17, 75),
    "tenor_bulan": (3, 60),
    "bunga_tahunan": (0.05, 0.40),
    "ragam_penghasilan": (0.0, 1.0),
    "gagal_bayar": (0, 1),
}

MAKS_HILANG = {
    "rata_saldo_90h": 0.20,
    "lama_usaha_tahun": 0.10,
}

NILAI_POSITIF = ("penghasilan_bulanan", "plafon_diajukan", "angsuran_bulanan")

KATEGORI_SAH = {
    "segmen": {"Mikro", "Kecil", "Ultra Mikro"},
    "status_restrukturisasi": {"Tidak", "Pernah", "Sedang"},
}


def muat(jalur: str) -> pd.DataFrame:
    return pd.read_csv(jalur)


def validasi(df: pd.DataFrame) -> list[str]:
    # Mengembalikan daftar pelanggaran kontrak data. Kosong berarti lulus.
    masalah = []
    for kolom, tipe in SKEMA.items():
        if kolom not in df.columns:
            masalah.append(f"kolom hilang: {kolom}")
        elif str(df[kolom].dtype) != tipe:
            masalah.append(f"{kolom}: tipe {df[kolom].dtype}, diharapkan {tipe}")
    for kolom, (bawah, atas) in RENTANG.items():
        if kolom in df:
            luar = ((df[kolom] < bawah) | (df[kolom] > atas)).sum()
            if luar:
                masalah.append(f"{kolom}: {luar} nilai di luar rentang [{bawah}, {atas}]")
    for kolom, maks in MAKS_HILANG.items():
        if kolom in df and df[kolom].isna().mean() > maks:
            masalah.append(f"{kolom}: nilai hilang melampaui batas {maks:.0%}")

    # Aturan tambahan 1: nominal finansial inti wajib bernilai positif (> 0)
    for kolom in NILAI_POSITIF:
        if kolom in df:
            non_positif = (df[kolom] <= 0).sum()
            if non_positif:
                masalah.append(f"{kolom}: {non_positif} nilai tidak positif (<= 0)")

    # Aturan tambahan 2: nilai kolom kategorikal harus sesuai daftar domain sah
    for kolom, daftar_sah in KATEGORI_SAH.items():
        if kolom in df:
            tak_sah = (~df[kolom].dropna().isin(daftar_sah)).sum()
            if tak_sah:
                masalah.append(f"{kolom}: {tak_sah} nilai kategori di luar domain sah")

    return masalah


def bagi_waktu(df: pd.DataFrame, batas_latih: str, batas_validasi: str):
    # Pembagian OUT-OF-TIME. Pembagian acak pada data temporal adalah kesalahan.
    p = df["periode"].astype(str)
    return (
        df[p <= batas_latih],
        df[(p > batas_latih) & (p <= batas_validasi)],
        df[p > batas_validasi],
    )