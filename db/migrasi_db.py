import sqlite3

# Python migrasi otomatis Coach!

def migrate_tables():
    db_path = "D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Kinerja Bulanan
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS kinerja_bulanan_new (
        kpknl TEXT,
        tahun INTEGER,
        bulan INTEGER,
        frek_lelang INTEGER,
        frek_lot INTEGER,
        pokok_lelang REAL,
        pnbp_lelang REAL,
        pph REAL,
        bphtb REAL
    );

    INSERT INTO kinerja_bulanan_new
    SELECT kpknl, tahun, bulan, frek_lelang, frek_lot,
           CAST(pokok_lelang AS REAL),
           CAST(pnbp_lelang AS REAL),
           CAST(pph AS REAL),
           CAST(bphtb AS REAL)
    FROM kinerja_bulanan;

    DROP TABLE kinerja_bulanan;
    ALTER TABLE kinerja_bulanan_new RENAME TO kinerja_bulanan;
    ''')

    # Target Lelang
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS target_lelang_new (
        kpknl TEXT,
        tahun INTEGER,
        pokok_q1 REAL,
        pokok_q2 REAL,
        pokok_q3 REAL,
        pokok_q4 REAL,
        pnbp_q1 REAL,
        pnbp_q2 REAL,
        pnbp_q3 REAL,
        pnbp_q4 REAL
    );

    INSERT INTO target_lelang_new
    SELECT kpknl, tahun,
           CAST(pokok_q1 AS REAL),
           CAST(pokok_q2 AS REAL),
           CAST(pokok_q3 AS REAL),
           CAST(pokok_q4 AS REAL),
           CAST(pnbp_q1 AS REAL),
           CAST(pnbp_q2 AS REAL),
           CAST(pnbp_q3 AS REAL),
           CAST(pnbp_q4 AS REAL)
    FROM target_lelang;

    DROP TABLE target_lelang;
    ALTER TABLE target_lelang_new RENAME TO target_lelang;
    ''')

    conn.commit()
    conn.close()
    print("Migrasi selesai! Struktur tabel sudah pakai REAL.")

if __name__ == "__main__":
    migrate_tables()
