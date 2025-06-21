import sys
import os
import sqlite3
import pandas as pd
import requests
import webbrowser
from PyQt5 import QtWidgets, QtGui, QtCore

class MonalisaSJB(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monalisa-SJB Dashboard Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Buat root layout dengan nama aman
        self.main_layout = QtWidgets.QVBoxLayout()

        layout = QtWidgets.QVBoxLayout()

        # === Export Import ===
        export_import_layout = QtWidgets.QHBoxLayout()
        self.export_btn = QtWidgets.QPushButton("Export to Excel")
        self.import_btn = QtWidgets.QPushButton("Import from Excel")
        self.export_btn.clicked.connect(self.export_excel)
        self.import_btn.clicked.connect(self.import_excel)
        import_label = QtWidgets.QLabel("Excel file: D:/WongsoApps/monalisa-sjb/data")
        export_import_layout.addWidget(self.export_btn)
        export_import_layout.addWidget(self.import_btn)
        export_import_layout.addWidget(import_label)
        self.main_layout.addLayout(export_import_layout)

        # === Kinerja Filter, Table, CRUD ===
        self.main_layout.addWidget(QtWidgets.QLabel("Tabel: kinerja_bulanan"))

        filter_row_kinerja = QtWidgets.QHBoxLayout()
        filter_row_kinerja.addWidget(QtWidgets.QLabel("KPKNL:"))
        self.filter_kpknl_kinerja = QtWidgets.QComboBox()
        filter_row_kinerja.addWidget(self.filter_kpknl_kinerja)

        filter_row_kinerja.addWidget(QtWidgets.QLabel("Tahun:"))
        self.filter_tahun_kinerja = QtWidgets.QSpinBox()
        self.filter_tahun_kinerja.setRange(2000, 2100)
        self.filter_tahun_kinerja.setValue(2025)
        filter_row_kinerja.addWidget(self.filter_tahun_kinerja)

        self.apply_filter_both = QtWidgets.QPushButton("Apply Filter")
        self.apply_filter_both.clicked.connect(self.apply_filter_both_tables)
        filter_row_kinerja.addWidget(self.apply_filter_both)
        self.main_layout.addLayout(filter_row_kinerja)

        self.table_kinerja = QtWidgets.QTableView()
        self.main_layout.addWidget(self.table_kinerja)

        crud_kinerja = QtWidgets.QHBoxLayout()
        for text, color in zip(["Add", "Edit", "Delete", "Save"],
                                ["#4CAF50", "#FFC107", "#F44336", "#2196F3"]):
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet(f"background-color: {color}; color: white;")
            crud_kinerja.addWidget(btn)
        self.main_layout.addLayout(crud_kinerja)

        # === Table, CRUD ===
        self.table_target = QtWidgets.QTableView()
        self.main_layout.addWidget(self.table_target)

        crud_target = QtWidgets.QHBoxLayout()
        for text, color in zip(["Add", "Edit", "Delete", "Save"],
                                ["#4CAF50", "#FFC107", "#F44336", "#2196F3"]):
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet(f"background-color: {color}; color: white;")
            crud_target.addWidget(btn)
        self.main_layout.addLayout(crud_target)

        # === JSON & Push ===
        self.hitung_btn = QtWidgets.QPushButton("Hitung dan Update JSON")
        self.hitung_btn.clicked.connect(self.hitung_json)
        self.main_layout.addWidget(self.hitung_btn)

        self.status_label = QtWidgets.QLabel("Status Internet: Checking...")
        self.push_btn = QtWidgets.QPushButton("Push JSON")
        self.goto_web_btn = QtWidgets.QPushButton("Go to Web")
        self.push_btn.clicked.connect(self.push_json)
        self.goto_web_btn.clicked.connect(lambda: webbrowser.open("https://shoimrachmanto.github.io/monalisa-sjb/"))
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.push_btn)
        self.main_layout.addWidget(self.goto_web_btn)

        self.setLayout(self.main_layout)

        self.populate_kpknl_comboboxes()
        self.load_table("kinerja_bulanan", self.table_kinerja)
        self.load_table("target_lelang", self.table_target)
        self.check_internet()

    def populate_kpknl_comboboxes(self):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        kpknl_list = pd.read_sql_query("SELECT DISTINCT kpknl FROM kinerja_bulanan", conn)['kpknl'].dropna().unique().tolist()
        conn.close()

        for box in [self.filter_kpknl_kinerja]:
            box.clear()
            box.addItem("All")
            for kpknl in sorted(kpknl_list):
                box.addItem(kpknl)

    def apply_filter_both_tables(self):
        try:
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
            kpknl = self.filter_kpknl_kinerja.currentText()
            tahun = self.filter_tahun_kinerja.value()

            # Kinerja
            query1 = "SELECT * FROM kinerja_bulanan WHERE 1=1"
            params1 = []
            if kpknl != "All":
                query1 += " AND kpknl = ?"
                params1.append(kpknl)
            if tahun:
                query1 += " AND tahun = ?"
                params1.append(tahun)
            df1 = pd.read_sql_query(query1, conn, params=params1)
            self.table_kinerja.setModel(PandasModel(df1))

            # Target
            query2 = "SELECT * FROM target_lelang WHERE 1=1"
            params2 = []
            if kpknl != "All":
                query2 += " AND kpknl = ?"
                params2.append(kpknl)
            if tahun:
                query2 += " AND tahun = ?"
                params2.append(tahun)
            df2 = pd.read_sql_query(query2, conn, params=params2)
            self.table_target.setModel(PandasModel(df2))

            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Filter Error", str(e))

    def load_table(self, table_name, view):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        model = PandasModel(df)
        view.setModel(model)
        conn.close()

    def check_internet(self):
        try:
            requests.get("https://google.com", timeout=3)
            self.status_label.setText("Status Internet: Connected ✅")
        except:
            self.status_label.setText("Status Internet: Disconnected ❌")

    def export_excel(self):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        df1 = pd.read_sql_query("SELECT * FROM kinerja_bulanan", conn)
        df2 = pd.read_sql_query("SELECT * FROM target_lelang", conn)
        with pd.ExcelWriter("D:/WongsoApps/monalisa-sjb/data/monalisa_sjb.xlsx") as writer:
            df1.to_excel(writer, sheet_name="kinerja_bulanan", index=False)
            df2.to_excel(writer, sheet_name="target_lelang", index=False)
        conn.close()
        QtWidgets.QMessageBox.information(self, "Export", "Export sukses!")

    def import_excel(self):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        xls = pd.ExcelFile("D:/WongsoApps/monalisa-sjb/data/monalisa_sjb.xlsx")
        pd.read_excel(xls, "kinerja_bulanan").to_sql("kinerja_bulanan", conn, if_exists="replace", index=False)
        pd.read_excel(xls, "target_lelang").to_sql("target_lelang", conn, if_exists="replace", index=False)
        conn.close()
        self.load_table("kinerja_bulanan", self.table_kinerja)
        self.load_table("target_lelang", self.table_target)
        QtWidgets.QMessageBox.information(self, "Import", "Import sukses!")

    def hitung_json(self):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        df = pd.read_sql_query("""
            SELECT k.kpknl, k.tahun, k.bulan, k.pokok_lelang,
                   t.pokok_q1, t.pokok_q2, t.pokok_q3, t.pokok_q4
            FROM kinerja_bulanan k
            LEFT JOIN target_lelang t ON k.kpknl = t.kpknl AND k.tahun = t.tahun
        """, conn)
        output = []
        for _, row in df.iterrows():
            q = (row['bulan'] - 1) // 3 + 1
            target = row[f'pokok_q{q}'] if f'pokok_q{q}' in row else 0
            persen = round(row['pokok_lelang'] / target * 100, 2) if target else 0
            output.append({"kpknl": row['kpknl'], "tahun": row['tahun'], "bulan": row['bulan'],
                           "pokok_lelang": row['pokok_lelang'], "pokok_target_q": target, "persentase": persen})
        pd.DataFrame(output).to_json("D:/WongsoApps/monalisa-sjb/data/output.json", orient="records", indent=2)
        conn.close()
        QtWidgets.QMessageBox.information(self, "Hitung JSON", "JSON berhasil diperbarui!")

    def push_json(self):
        QtWidgets.QMessageBox.information(self, "Push", "Push JSON belum diimplementasi.")

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(PandasModel, self).__init__(parent)
        try:
            self._df = df.apply(pd.to_numeric)
        except Exception:
            self._df = df.copy()

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            value = self._df.iloc[index.row(), index.column()]
            col_name = self._df.columns[index.column()].lower()
            if role == QtCore.Qt.TextAlignmentRole:
                if any(key in col_name for key in ['pokok', 'pnbp', 'pph', 'bphtb']):
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
            if role == QtCore.Qt.DisplayRole:
                if isinstance(value, (int, float)) and any(key in col_name for key in ['pokok', 'pnbp', 'pph', 'bphtb']):
                    return f"{int(float(value)):,}".replace(",", ".")
                return str(value)
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._df.columns[col]
        return None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonalisaSJB()
    window.show()
    sys.exit(app.exec_())
