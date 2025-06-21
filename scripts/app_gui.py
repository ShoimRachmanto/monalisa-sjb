import sys
import os
import sqlite3
import pandas as pd
import requests
import webbrowser
from PyQt5 import QtWidgets

class MonalisaSJB(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monalisa-SJB Dashboard Manager")
        self.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout()

        # === Panel Export Import ===
        self.export_btn = QtWidgets.QPushButton("Export to Excel")
        self.import_btn = QtWidgets.QPushButton("Import from Excel")
        self.export_btn.clicked.connect(self.export_excel)
        self.import_btn.clicked.connect(self.import_excel)

        layout.addWidget(self.export_btn)
        layout.addWidget(QtWidgets.QLabel("Letakkan file Excel di D:/WongsoApps/monalisa-sjb/data"))
        layout.addWidget(self.import_btn)

        # === Panel CRUD Placeholder ===
        layout.addWidget(QtWidgets.QLabel("\n--- CRUD kinerja_bulanan & target_lelang (Filter Tahun & KPKNL) ---"))
        self.crud_info = QtWidgets.QLabel("🔧 CRUD detail coming soon")
        layout.addWidget(self.crud_info)

        # === Panel Hitung & JSON ===
        self.hitung_btn = QtWidgets.QPushButton("Hitung dan Update JSON")
        self.hitung_btn.clicked.connect(self.hitung_json)
        layout.addWidget(self.hitung_btn)

        # === Status Internet & Push ===
        self.status_label = QtWidgets.QLabel("Status Internet: Checking...")
        self.push_btn = QtWidgets.QPushButton("Push JSON")
        self.push_btn.clicked.connect(self.push_json)
        self.goto_web_btn = QtWidgets.QPushButton("Go to Web")
        self.goto_web_btn.clicked.connect(lambda: webbrowser.open("https://shoimrachmanto.github.io/monalisa-sjb/"))

        layout.addWidget(self.status_label)
        layout.addWidget(self.push_btn)
        layout.addWidget(self.goto_web_btn)

        self.setLayout(layout)
        self.check_internet()

    def export_excel(self):
        try:
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")

            # 🔑 Query explicit TANPA kolom id
            df1 = pd.read_sql_query("""
                SELECT 
                    kpknl, tahun, bulan,
                    frek_lelang, frek_lot, 
                    pokok_lelang, pnbp_lelang, pph, bphtb
                FROM kinerja_bulanan
            """, conn)

            df2 = pd.read_sql_query("""
                SELECT 
                    kpknl, tahun,
                    pokok_q1, pokok_q2, pokok_q3, pokok_q4,
                    pnbp_q1, pnbp_q2, pnbp_q3, pnbp_q4
                FROM target_lelang
            """, conn)

            export_path = "D:/WongsoApps/monalisa-sjb/data/monalisa_sjb.xlsx"

            with pd.ExcelWriter(export_path) as writer:
                df1.to_excel(writer, sheet_name="kinerja_bulanan", index=False)
                df2.to_excel(writer, sheet_name="target_lelang", index=False)

            conn.close()
            QtWidgets.QMessageBox.information(self, "Export", f"Export sukses ke {export_path}")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Error", str(e))


    def import_excel(self):
        try:
            import_path = "D:/WongsoApps/monalisa-sjb/data/monalisa_sjb.xlsx"
            xls = pd.ExcelFile(import_path)
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
            df1 = pd.read_excel(xls, "kinerja_bulanan")
            df2 = pd.read_excel(xls, "target_lelang")
            df1.to_sql("kinerja_bulanan", conn, if_exists="replace", index=False)
            df2.to_sql("target_lelang", conn, if_exists="replace", index=False)
            conn.commit()
            conn.close()
            QtWidgets.QMessageBox.information(self, "Import", f"Import sukses dari {import_path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Import Error", str(e))

    def hitung_json(self):
        try:
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
            query = """
            SELECT 
                k.kpknl, k.tahun, k.bulan, k.pokok_lelang,
                t.pokok_q1, t.pokok_q2, t.pokok_q3, t.pokok_q4
            FROM kinerja_bulanan k
            LEFT JOIN target_lelang t 
            ON k.kpknl = t.kpknl AND k.tahun = t.tahun
            """
            df = pd.read_sql_query(query, conn)
            output = []
            for _, row in df.iterrows():
                q = (row['bulan'] - 1) // 3 + 1
                pokok_target = row[f'pokok_q{q}'] if f'pokok_q{q}' in row else 0
                persentase = round((row['pokok_lelang'] / pokok_target) * 100, 2) if pokok_target else 0
                output.append({
                    "kpknl": row['kpknl'],
                    "tahun": row['tahun'],
                    "bulan": row['bulan'],
                    "pokok_lelang": row['pokok_lelang'],
                    "pokok_target_q": pokok_target,
                    "persentase": persentase
                })
            json_path = "D:/WongsoApps/monalisa-sjb/data/output.json"
            pd.DataFrame(output).to_json(json_path, orient="records", indent=2)
            conn.close()
            QtWidgets.QMessageBox.information(self, "Hitung JSON", f"JSON sukses diupdate ke {json_path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Hitung JSON Error", str(e))

    def check_internet(self):
        try:
            requests.get("https://google.com", timeout=3)
            self.status_label.setText("Status Internet: Connected ✅")
        except:
            self.status_label.setText("Status Internet: Disconnected ❌")

    def push_json(self):
        QtWidgets.QMessageBox.information(self, "Push", "Fitur push JSON belum di-implement, coming soon!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonalisaSJB()
    window.show()
    sys.exit(app.exec_())
