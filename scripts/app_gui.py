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
        
        # ========= bikin aktif area tabel untuk keperluan CRUD ============
        self.df_kinerja = pd.DataFrame()
        
        crud_kinerja = QtWidgets.QHBoxLayout()
        self.add_kinerja_btn = QtWidgets.QPushButton("Add")
        self.edit_kinerja_btn = QtWidgets.QPushButton("Edit")
        self.delete_kinerja_btn = QtWidgets.QPushButton("Delete")
        self.save_kinerja_btn = QtWidgets.QPushButton("Save")

        # Warna tombol
        self.add_kinerja_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.edit_kinerja_btn.setStyleSheet("background-color: #FFC107; color: white;")
        self.delete_kinerja_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.save_kinerja_btn.setStyleSheet("background-color: #2196F3; color: white;")

        # Hubungkan aksi
        self.add_kinerja_btn.clicked.connect(self.add_kinerja)
        self.edit_kinerja_btn.clicked.connect(self.edit_kinerja)
        self.delete_kinerja_btn.clicked.connect(self.delete_kinerja)
        self.save_kinerja_btn.clicked.connect(self.save_kinerja)

        crud_kinerja.addWidget(self.add_kinerja_btn)
        crud_kinerja.addWidget(self.edit_kinerja_btn)
        crud_kinerja.addWidget(self.delete_kinerja_btn)
        crud_kinerja.addWidget(self.save_kinerja_btn)
        self.main_layout.addLayout(crud_kinerja)

        # ================= Target Table, CRUD =========================
        self.table_target = QtWidgets.QTableView()
        self.main_layout.addWidget(self.table_target)

        # ======== bikin aktif area tabel untuk CRUD ========
        self.df_target = pd.DataFrame()

        crud_target = QtWidgets.QHBoxLayout()
        self.add_target_btn = QtWidgets.QPushButton("Add")
        self.edit_target_btn = QtWidgets.QPushButton("Edit")
        self.delete_target_btn = QtWidgets.QPushButton("Delete")
        self.save_target_btn = QtWidgets.QPushButton("Save")

        # Warna tombol
        self.add_target_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.edit_target_btn.setStyleSheet("background-color: #FFC107; color: white;")
        self.delete_target_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.save_target_btn.setStyleSheet("background-color: #2196F3; color: white;")

        # Sambungkan ke method
        self.add_target_btn.clicked.connect(self.add_target)
        self.edit_target_btn.clicked.connect(self.edit_target)
        self.delete_target_btn.clicked.connect(self.delete_target)
        self.save_target_btn.clicked.connect(self.save_target)

        crud_target.addWidget(self.add_target_btn)
        crud_target.addWidget(self.edit_target_btn)
        crud_target.addWidget(self.delete_target_btn)
        crud_target.addWidget(self.save_target_btn)
        self.main_layout.addLayout(crud_target)

        # === JSON & Push ===
        self.hitung_btn = QtWidgets.QPushButton("Hitung dan Update JSON")
        self.hitung_btn.setFixedSize(200, 40)
        self.hitung_btn.clicked.connect(self.hitung_json)

        self.status_label = QtWidgets.QLabel("Status Internet: Checking...")

        self.push_btn = QtWidgets.QPushButton("Push JSON")
        self.push_btn.setFixedSize(120, 40)
        self.push_btn.clicked.connect(self.push_json)

        self.goto_web_btn = QtWidgets.QPushButton("Go to Web")
        self.goto_web_btn.setFixedSize(120, 40)
        self.goto_web_btn.clicked.connect(lambda: webbrowser.open("https://shoimrachmanto.github.io/monalisa-sjb/"))

        # === Layout satu baris ===
        json_push_layout = QtWidgets.QHBoxLayout()
        json_push_layout.addStretch()
        json_push_layout.addWidget(self.hitung_btn)
        json_push_layout.addSpacing(20)  # Jarak antar widget
        json_push_layout.addWidget(self.status_label)
        json_push_layout.addSpacing(20)
        json_push_layout.addWidget(self.push_btn)
        json_push_layout.addSpacing(20)
        json_push_layout.addWidget(self.goto_web_btn)
        json_push_layout.addStretch()

        # Tambahkan ke main layout
        self.main_layout.addLayout(json_push_layout)

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
        conn.close()

        if table_name == "kinerja_bulanan":
            self.df_kinerja = df.copy()
        elif table_name == "target_lelang":
            self.df_target = df.copy()

        model = PandasModel(df)
        view.setModel(model)

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

    # ===== Def untuk CRUD ========
    def add_kinerja(self):
        dialog = AddKinerjaDialog(self.df_kinerja.columns)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            # Tambah ke DB langsung
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
            df_new = pd.DataFrame([data])
            df_new.to_sql("kinerja_bulanan", conn, if_exists="append", index=False)
            conn.close()
            # Reload tabel
            self.load_table("kinerja_bulanan", self.table_kinerja)
            QtWidgets.QMessageBox.information(self, "Tambah", "Data berhasil ditambahkan!")

    def edit_kinerja(self):
        # Aktifkan mode editable
        model = PandasModel(self.df_kinerja, editable=True)
        self.table_kinerja.setModel(model)
        QtWidgets.QMessageBox.information(self, "Edit", "Tabel kinerja sekarang bisa diedit langsung!")

    def delete_kinerja(self):
        index = self.table_kinerja.currentIndex()
        if index.isValid():
            row = index.row()
            self.df_kinerja = self.df_kinerja.drop(self.df_kinerja.index[row]).reset_index(drop=True)
            # Langsung commit ke DB
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
            self.df_kinerja.to_sql("kinerja_bulanan", conn, if_exists="replace", index=False)
            conn.close()
            # Reload
            self.table_kinerja.setModel(PandasModel(self.df_kinerja))
            QtWidgets.QMessageBox.information(self, "Hapus", "Baris berhasil dihapus & DB diupdate!")
        else:
            QtWidgets.QMessageBox.warning(self, "Hapus", "Pilih baris dulu untuk dihapus!")

    def save_kinerja(self):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        self.df_kinerja.to_sql("kinerja_bulanan", conn, if_exists="replace", index=False)
        conn.close()
        QtWidgets.QMessageBox.information(self, "Save", "Perubahan berhasil disimpan ke database!")

    def add_target(self):
        dialog = AddTargetDialog(self.df_target.columns)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            # Insert ke database
            conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
            df_new = pd.DataFrame([data])
            df_new.to_sql("target_lelang", conn, if_exists="append", index=False)
            conn.close()
            # Reload tabel
            self.load_table("target_lelang", self.table_target)
            QtWidgets.QMessageBox.information(self, "Tambah", "Data Target berhasil ditambahkan!")

    def edit_target(self):
        # Aktifkan mode editable untuk tabel target_lelang
        model = PandasModel(self.df_target, editable=True)
        self.table_target.setModel(model)
        QtWidgets.QMessageBox.information(self, "Edit", "Tabel target lelang sekarang bisa diedit langsung!")

    def delete_target(self):
        index = self.table_target.currentIndex()
        if index.isValid():
            row = index.row()
            self.df_target = self.df_target.drop(self.df_target.index[row]).reset_index(drop=True)
            self.table_target.setModel(PandasModel(self.df_target))
        else:
            QtWidgets.QMessageBox.warning(self, "Delete", "Pilih baris yang mau dihapus dulu!")

    def save_target(self):
        conn = sqlite3.connect("D:/WongsoApps/monalisa-sjb/db/kinerja_sjb.db")
        self.df_target.to_sql("target_lelang", conn, if_exists="replace", index=False)
        conn.close()
        QtWidgets.QMessageBox.information(self, "Save", "Data Target berhasil disimpan ke database!")

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None, editable=False):
        super(PandasModel, self).__init__(parent)
        self._df = df.apply(pd.to_numeric, errors='ignore')
        self.editable = editable
        self.format_columns = {
            "pokok_lelang",
            "pokok_q1", "pokok_q2", "pokok_q3", "pokok_q4",
            "pnbp_lelang", "pnbp_q1", "pnbp_q2", "pnbp_q3", "pnbp_q4",
            "pph",
            "bphtb"
        }

    def flags(self, index):
        flags = super().flags(index)
        if self.editable:
            flags |= QtCore.Qt.ItemIsEditable
        else:
            flags &= ~QtCore.Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            value = self._df.iloc[index.row(), index.column()]
            col_name = self._df.columns[index.column()]

            if role == QtCore.Qt.TextAlignmentRole:
                if col_name in self.format_columns:
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

            if role == QtCore.Qt.DisplayRole:
                if col_name in self.format_columns:
                    try:
                        if pd.isna(value):
                            return ""
                        return f"{int(float(value)):,}"
                    except:
                        return ""
                return str(value)
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            self._df.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._df.columns[col]
        return None

# ====== membuka jendela TAMBAH data kinerja =============
class AddKinerjaDialog(QtWidgets.QDialog):
    def __init__(self, columns):
        super().__init__()
        self.setWindowTitle("Tambah Data Kinerja")
        self.layout = QtWidgets.QFormLayout(self)
        self.inputs = {}
        for col in columns:
            line_edit = QtWidgets.QLineEdit()
            self.layout.addRow(col, line_edit)
            self.inputs[col] = line_edit

        self.submit_btn = QtWidgets.QPushButton("Tambah")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addRow(self.submit_btn)

    def get_data(self):
        return {col: self.inputs[col].text() for col in self.inputs}

# ========= membuka windows tambah data target ==============
class AddTargetDialog(QtWidgets.QDialog):
    def __init__(self, columns):
        super().__init__()
        self.setWindowTitle("Tambah Data Target Lelang")
        self.layout = QtWidgets.QFormLayout(self)
        self.inputs = {}
        for col in columns:
            line_edit = QtWidgets.QLineEdit()
            self.layout.addRow(col, line_edit)
            self.inputs[col] = line_edit

        self.submit_btn = QtWidgets.QPushButton("Tambah")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addRow(self.submit_btn)

    def get_data(self):
        return {col: self.inputs[col].text() for col in self.inputs}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonalisaSJB()
    window.show()
    sys.exit(app.exec_())
