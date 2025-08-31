"""
シンプルExcel範囲比較プログラム
既に開いているExcelファイルから範囲を選択して比較する
"""

import win32com.client
import tkinter as tk
from tkinter import messagebox, filedialog
try:
    from tkinter import simpledialog
except ImportError:
    # Windows環境でsimpledialogが見つからない場合の代替処理
    simpledialog = None
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SimpleRangeComparator:
    """シンプルな範囲比較クラス"""
    
    def __init__(self):
        """初期化"""
        self.excel_app = None
        self.results = []
        self.workbook_data = {}  # ファイル情報を格納
        
    def connect_to_excel(self):
        """Excelアプリケーションに接続または新規起動"""
        try:
            # 既存のExcelインスタンスに接続を試行
            self.excel_app = win32com.client.GetActiveObject("Excel.Application")
            print(f"✅ 既存のExcelアプリケーションに接続成功")
            print(f"📊 開いているワークブック数: {self.excel_app.Workbooks.Count}")
            
            # 開いているワークブックを表示
            if self.excel_app.Workbooks.Count > 0:
                for i, wb in enumerate(self.excel_app.Workbooks, 1):
                    print(f"  {i}. {wb.Name}")
            
            return True
            
        except:
            # 既存のExcelがない場合は新規起動
            try:
                print("📝 既存のExcelが見つからないため、新規起動します...")
                self.excel_app = win32com.client.Dispatch("Excel.Application")
                self.excel_app.Visible = True
                print("✅ Excelアプリケーションを新規起動しました")
                return True
                
            except Exception as e:
                print(f"❌ Excelアプリケーションの起動に失敗: {e}")
                return False
    
    def use_existing_files_or_open_new(self):
        """既に開いているファイルを使用するか新しく開くかを選択"""
        # 既に開いているファイルをチェック
        if self.excel_app.Workbooks.Count >= 2:
            root = tk.Tk()
            root.withdraw()
            
            use_existing = messagebox.askyesno(
                "ファイル選択",
                f"既に {self.excel_app.Workbooks.Count} 個のExcelファイルが開いています。\n\n" +
                "これらのファイルを使用しますか？\n\n" +
                "「はい」= 既存ファイルを使用\n" +
                "「いいえ」= 新しいファイルを選択"
            )
            
            root.destroy()
            
            if use_existing:
                return self.use_existing_files()
            else:
                return self.open_excel_files()
        else:
            return self.open_excel_files()
    
    def use_existing_files(self):
        """既に開いているファイルを使用"""
        workbooks = list(self.excel_app.Workbooks)
        
        if len(workbooks) >= 2:
            # 最初の2つのファイルを自動選択
            self.workbook_data['file1'] = {
                'path': workbooks[0].FullName,
                'name': workbooks[0].Name,
                'workbook': workbooks[0]
            }
            
            self.workbook_data['file2'] = {
                'path': workbooks[1].FullName,
                'name': workbooks[1].Name,
                'workbook': workbooks[1]
            }
            
            print(f"✅ ファイル1（既存）: {self.workbook_data['file1']['name']}")
            print(f"✅ ファイル2（既存）: {self.workbook_data['file2']['name']}")
            
            return True
        else:
            print("❌ 十分なファイルが開いていません")
            return False

    def open_excel_files(self):
        """2つのExcelファイルを開く"""
        print("\n📁 新しいExcelファイルを開きます...")
        
        root = tk.Tk()
        root.withdraw()
        
        # 1つ目のファイル
        file1_path = filedialog.askopenfilename(
            title="1つ目のExcelファイルを選択",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not file1_path:
            root.destroy()
            raise ValueError("1つ目のファイル選択がキャンセルされました")
        
        # 2つ目のファイル
        file2_path = filedialog.askopenfilename(
            title="2つ目のExcelファイルを選択",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not file2_path:
            root.destroy()
            raise ValueError("2つ目のファイル選択がキャンセルされました")
        
        root.destroy()
        
        # ファイルを開く
        try:
            workbook1 = self.excel_app.Workbooks.Open(file1_path)
            workbook2 = self.excel_app.Workbooks.Open(file2_path)
            
            # ファイル情報を保存
            self.workbook_data['file1'] = {
                'path': file1_path,
                'name': Path(file1_path).name,
                'workbook': workbook1
            }
            
            self.workbook_data['file2'] = {
                'path': file2_path,
                'name': Path(file2_path).name,
                'workbook': workbook2
            }
            
            print(f"✅ ファイル1を開きました: {self.workbook_data['file1']['name']}")
            print(f"✅ ファイル2を開きました: {self.workbook_data['file2']['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ ファイルを開くのに失敗しました: {e}")
            return False
    
    def select_workbook_and_range(self, file_key: str, label: str) -> Dict:
        """指定されたファイルからセル範囲を選択"""
        if file_key not in self.workbook_data:
            raise ValueError(f"ファイル '{file_key}' が見つかりません")
        
        file_info = self.workbook_data[file_key]
        selected_wb = file_info['workbook']
        
        print(f"📄 {label}: {file_info['name']}")
        
        # 範囲選択
        range_msg = f"""{label}のセル範囲を選択してください

Excelシート上でセル範囲をマウスで選択してから「OK」を押してください。

例: A1:C10, B2:F20 など"""
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("範囲選択", range_msg)
        
        # InputBoxで範囲選択
        selected_range = self.excel_app.InputBox(
            f"{label}の範囲を選択してください",
            f"{label} 範囲選択", 
            Type=8  # Range型
        )
        
        if selected_range == False:
            root.destroy()
            raise ValueError("範囲選択がキャンセルされました")
        
        # 範囲情報を取得
        if hasattr(selected_range, 'Address'):
            range_address = selected_range.Address
            worksheet = selected_range.Worksheet
        else:
            # 文字列で返された場合の処理
            range_address = str(selected_range)
            worksheet = selected_wb.ActiveSheet
            selected_range = worksheet.Range(range_address)
        
        print(f"📍 選択された範囲: {range_address}")
        print(f"📊 サイズ: {selected_range.Rows.Count}行 x {selected_range.Columns.Count}列")
        
        root.destroy()
        
        return {
            'workbook': selected_wb,
            'worksheet': worksheet,
            'range': selected_range,
            'address': range_address,
            'values': self._extract_values(selected_range)
        }
    
    def _extract_values(self, range_obj) -> List[List[str]]:
        """範囲からセル値を抽出"""
        values = []
        
        if range_obj.Rows.Count == 1 and range_obj.Columns.Count == 1:
            # 単一セルの場合
            values = [[str(range_obj.Value or "")]]
        elif range_obj.Rows.Count == 1:
            # 単一行の場合
            row_values = []
            for col in range(1, range_obj.Columns.Count + 1):
                cell_value = range_obj.Cells(1, col).Value
                row_values.append(str(cell_value or ""))
            values = [row_values]
        elif range_obj.Columns.Count == 1:
            # 単一列の場合
            for row in range(1, range_obj.Rows.Count + 1):
                cell_value = range_obj.Cells(row, 1).Value
                values.append([str(cell_value or "")])
        else:
            # 複数行列の場合
            for row in range(1, range_obj.Rows.Count + 1):
                row_values = []
                for col in range(1, range_obj.Columns.Count + 1):
                    cell_value = range_obj.Cells(row, col).Value
                    row_values.append(str(cell_value or ""))
                values.append(row_values)
        
        return values
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """テキストの類似度を計算 (0-100)"""
        if not text1 and not text2:
            return 100.0
        if not text1 or not text2:
            return 0.0
        
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        return similarity * 100
    
    def compare_ranges(self, range1_data: Dict, range2_data: Dict) -> List[Dict]:
        """2つの範囲を比較"""
        print("\\n🔍 範囲比較を開始...")
        
        values1 = range1_data['values']
        values2 = range2_data['values']
        
        max_rows = max(len(values1), len(values2))
        max_cols = max(
            max(len(row) for row in values1) if values1 else 0,
            max(len(row) for row in values2) if values2 else 0
        )
        
        results = []
        
        for row in range(max_rows):
            for col in range(max_cols):
                # セル値を取得（範囲外の場合は空文字）
                value1 = ""
                value2 = ""
                
                if row < len(values1) and col < len(values1[row]):
                    value1 = values1[row][col]
                
                if row < len(values2) and col < len(values2[row]):
                    value2 = values2[row][col]
                
                # 類似度計算
                similarity = self.calculate_similarity(value1, value2)
                
                # 位置情報
                position = f"({row+1},{col+1})"
                
                # 比較結果
                if similarity == 100.0:
                    status = "完全一致"
                elif similarity >= 80:
                    status = "高類似"
                elif similarity >= 50:
                    status = "中類似"
                else:
                    status = "低類似/相違"
                
                result = {
                    'position': position,
                    'value1': value1,
                    'value2': value2,
                    'similarity': similarity,
                    'status': status
                }
                
                results.append(result)
        
        return results
    
    def display_results(self, results: List[Dict], range1_data: Dict, range2_data: Dict):
        """比較結果を表示"""
        print("\\n" + "="*80)
        print("📊 比較結果")
        print("="*80)
        
        print(f"📄 ファイル1: {range1_data['workbook'].Name}")
        print(f"📍 範囲1: {range1_data['address']}")
        print(f"📄 ファイル2: {range2_data['workbook'].Name}")
        print(f"📍 範囲2: {range2_data['address']}")
        print()
        
        # 統計情報
        total_cells = len(results)
        perfect_match = len([r for r in results if r['similarity'] == 100.0])
        high_similarity = len([r for r in results if 80 <= r['similarity'] < 100])
        medium_similarity = len([r for r in results if 50 <= r['similarity'] < 80])
        low_similarity = len([r for r in results if r['similarity'] < 50])
        
        print("📈 統計情報:")
        print(f"  総セル数: {total_cells}")
        print(f"  完全一致: {perfect_match}セル ({perfect_match/total_cells*100:.1f}%)")
        print(f"  高類似: {high_similarity}セル ({high_similarity/total_cells*100:.1f}%)")
        print(f"  中類似: {medium_similarity}セル ({medium_similarity/total_cells*100:.1f}%)")
        print(f"  低類似/相違: {low_similarity}セル ({low_similarity/total_cells*100:.1f}%)")
        print()
        
        # 詳細結果（相違のみ）
        differences = [r for r in results if r['similarity'] < 100.0]
        if differences:
            print(f"🔍 相違点詳細 ({len(differences)}件):")
            print("-" * 80)
            for result in differences[:20]:  # 最初の20件のみ表示
                print(f"位置 {result['position']} | {result['status']} ({result['similarity']:.1f}%)")
                print(f"  ファイル1: '{result['value1']}'")
                print(f"  ファイル2: '{result['value2']}'")
                print()
                
            if len(differences) > 20:
                print(f"... 他 {len(differences) - 20} 件の相違点があります")
        else:
            print("✅ すべてのセルが完全一致しています！")
        
        print("="*80)
    
    def run(self):
        """メイン実行"""
        print("🚀 シンプルExcel範囲比較プログラム")
        print("-" * 40)
        
        try:
            # 1. Excelに接続
            if not self.connect_to_excel():
                return
            
            # 2. ファイルを選択または開く
            if not self.use_existing_files_or_open_new():
                return
            
            # 3. 範囲1選択
            print("\\n📍 1つ目の範囲を選択...")
            range1_data = self.select_workbook_and_range("file1", "1つ目のファイル")
            
            # 4. 範囲2選択  
            print("\\n📍 2つ目の範囲を選択...")
            range2_data = self.select_workbook_and_range("file2", "2つ目のファイル")
            
            # 5. 比較実行
            results = self.compare_ranges(range1_data, range2_data)
            
            # 6. 結果表示
            self.display_results(results, range1_data, range2_data)
            
            # 7. 完了確認
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("完了", "比較処理が完了しました！\\n結果はコンソールに表示されています。")
            root.destroy()
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            root = tk.Tk() 
            root.withdraw()
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\\n{e}")
            root.destroy()


def main():
    """メイン関数"""
    comparator = SimpleRangeComparator()
    comparator.run()


if __name__ == "__main__":
    main()