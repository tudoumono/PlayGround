"""
Excel Book全体比較プログラム（セルずれ対応版）
2つのExcel Bookを意味的に比較し、差分に色付けして保存

色分けルール：
- 淡い緑色: 完全一致 (100%) - チェック済み表示
- 黄色: 高類似度 (80-99%)
- 青色: 中類似度 (50-79%)
- 赤色: 低類似度 (30-49%)
- 緑色: 新規セル（2つ目のみに存在）
- オレンジ色: コピーされたセル（1つ目から2つ目にコピー）
- ピンク色: 削除されたセル（レポートで報告）
"""

import win32com.client
import tkinter as tk
from tkinter import messagebox, filedialog
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import shutil
import os


class ExcelBookComparator:
    """Excel Book全体比較クラス"""
    
    def __init__(self):
        """初期化"""
        self.excel_app = None
        self.workbook_data = {}
        self.match_threshold = 30  # マッチング閾値（30%以上で有効マッチ）
        
        # 色設定（Excel色番号）
        self.colors = {
            'perfect': 15134419,      # 淡い緑色 (RGB: 235,255,235) - 完全一致（チェック済み表示）
            'high': 65535,            # 黄色 (RGB: 255,255,0)
            'medium': 16776960,       # 青色 (RGB: 0,176,240) 
            'low': 255,               # 赤色 (RGB: 255,0,0)
            'new': 5287936,           # 緑色 (RGB: 0,176,80) - 新規
            'removed': 13408767,      # ピンク (RGB: 255,192,203) - 削除
            'copied': 16750899        # オレンジ色 (RGB: 255,165,19) - コピーされたセル
        }
    
    def _create_topmost_window(self):
        """常に最前面に表示されるtkinterウィンドウを作成"""
        root = tk.Tk()
        root.withdraw()
        
        try:
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()
            
            try:
                root.wm_attributes('-toolwindow', True)
            except:
                pass
            
            try:
                root.configure(bg='#FF6B6B')
                root.option_add('*Font', ('MS Sans Serif', 10, 'bold'))
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ トップモストウィンドウ設定エラー: {e}")
        
        return root

    def start_excel_application(self):
        """Excel アプリケーションを起動"""
        try:
            print("🚀 Excel アプリケーションを起動中...")
            self.excel_app = win32com.client.Dispatch("Excel.Application")
            self.excel_app.Visible = True
            self.excel_app.DisplayAlerts = False
            print("✅ Excel アプリケーション起動完了")
            return True
        except Exception as e:
            messagebox.showerror("エラー", f"Excel の起動に失敗しました：{e}")
            return False

    def select_excel_files(self):
        """2つのExcelファイルを選択"""
        print("\\n📁 Excel Bookファイルを選択します...")
        
        # 1つ目のファイル選択
        print("\\n🗂️ === 比較元ファイル（昨年度等）選択 ===")
        root = self._create_topmost_window()
        file1_path = filedialog.askopenfilename(
            parent=root,
            title="比較元のExcel Bookを選択",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        root.destroy()
        
        if not file1_path:
            print("❌ 比較元ファイル選択がキャンセルされました")
            return False
        
        # 2つ目のファイル選択
        print("\\n🗂️ === 比較先ファイル（今年度等）選択 ===")
        root = self._create_topmost_window()
        file2_path = filedialog.askopenfilename(
            parent=root,
            title="比較先のExcel Bookを選択",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        root.destroy()
        
        if not file2_path:
            print("❌ 比較先ファイル選択がキャンセルされました")
            return False
        
        # ファイル情報を保存
        self.workbook_data['file1'] = {
            'path': file1_path,
            'name': Path(file1_path).name
        }
        self.workbook_data['file2'] = {
            'path': file2_path,
            'name': Path(file2_path).name
        }
        
        print(f"✅ 比較元ファイル: {self.workbook_data['file1']['name']}")
        print(f"✅ 比較先ファイル: {self.workbook_data['file2']['name']}")
        
        return True

    def create_backup_copy(self):
        """比較先ファイルのバックアップコピーを作成"""
        try:
            original_path = self.workbook_data['file2']['path']
            original_name = Path(original_path)
            
            # バックアップファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{original_name.stem}_比較結果_{timestamp}{original_name.suffix}"
            backup_path = original_name.parent / backup_name
            
            print(f"\\n📋 バックアップコピーを作成中...")
            print(f"  元ファイル: {original_name.name}")
            print(f"  コピー先: {backup_name}")
            
            shutil.copy2(original_path, backup_path)
            
            # コピー先情報を保存
            self.workbook_data['backup'] = {
                'path': str(backup_path),
                'name': backup_name
            }
            
            print(f"✅ バックアップコピーを作成しました: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ バックアップコピー作成エラー: {e}")
            messagebox.showerror("エラー", f"バックアップコピーの作成に失敗しました：{e}")
            return False

    def extract_all_worksheets_data(self, file_path: str, file_label: str) -> Dict:
        """Excel Book全体からすべてのワークシートデータを抽出"""
        try:
            print(f"\\n📊 {file_label}を開いてデータを抽出中...")
            workbook = self.excel_app.Workbooks.Open(file_path)
            
            all_data = {
                'sheets': {},
                'workbook_name': workbook.Name
            }
            
            sheet_count = workbook.Worksheets.Count
            print(f"📋 ワークシート数: {sheet_count}枚")
            
            for i in range(1, sheet_count + 1):
                worksheet = workbook.Worksheets(i)
                sheet_name = worksheet.Name
                print(f"  📄 シート {i}/{sheet_count}: {sheet_name}")
                
                # 使用範囲を取得
                used_range = worksheet.UsedRange
                if used_range is not None:
                    # UsedRangeの開始位置を取得
                    start_row = used_range.Row  # 1-based
                    start_col = used_range.Column  # 1-based
                    
                    # データを取得
                    values = used_range.Value
                    
                    # 2次元配列に正規化
                    if values is None:
                        values = []
                    elif not isinstance(values, (list, tuple)):
                        values = [[values]]
                    elif not isinstance(values[0], (list, tuple)):
                        values = [list(values)]
                    else:
                        values = [list(row) for row in values]
                    
                    # None を空文字に変換
                    normalized_values = []
                    for row in values:
                        normalized_row = []
                        for cell in row:
                            if cell is None:
                                normalized_row.append("")
                            else:
                                normalized_row.append(str(cell))
                        normalized_values.append(normalized_row)
                    
                    all_data['sheets'][sheet_name] = {
                        'values': normalized_values,
                        'address': used_range.Address,
                        'start_row': start_row,  # UsedRangeの開始行（1-based）
                        'start_col': start_col,  # UsedRangeの開始列（1-based）
                        'rows': len(normalized_values),
                        'cols': len(normalized_values[0]) if normalized_values else 0
                    }
                    
                    print(f"    💾 {len(normalized_values)}行 x {len(normalized_values[0]) if normalized_values else 0}列のデータを取得")
                else:
                    print(f"    📝 空のシート")
                    all_data['sheets'][sheet_name] = {
                        'values': [],
                        'address': '',
                        'start_row': 1,  # デフォルト値
                        'start_col': 1,  # デフォルト値
                        'rows': 0,
                        'cols': 0
                    }
            
            # ファイルを閉じる
            workbook.Close(SaveChanges=False)
            print(f"✅ {file_label}のデータ抽出完了")
            
            return all_data
            
        except Exception as e:
            print(f"❌ {file_label}のデータ抽出エラー: {e}")
            messagebox.showerror("エラー", f"{file_label}のデータ抽出に失敗しました：{e}")
            return None

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """類似度を計算（0-100%）"""
        if not text1 and not text2:
            return 100.0
        if not text1 or not text2:
            return 0.0
        
        # 前後の空白を除去して比較
        text1 = str(text1).strip()
        text2 = str(text2).strip()
        
        if text1 == text2:
            return 100.0
        
        # difflib.SequenceMatcherで類似度計算
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        return similarity * 100

    def compare_worksheets(self, data1: Dict, data2: Dict) -> Dict:
        """2つのワークブック全体を比較"""
        import time
        start_time = time.time()
        
        print("\\n🧠 Excel Book全体の意味的比較を開始...")
        print(f"🎯 マッチング閾値: {self.match_threshold}%以上")
        
        comparison_results = {
            'matched_sheets': {},
            'new_sheets': [],
            'removed_sheets': [],
            'statistics': {
                'total_comparisons': 0,
                'matched_cells': 0,
                'new_cells': 0,
                'removed_cells': 0,
                'copied_cells': 0,
                'perfect_match': 0,
                'high_similarity': 0,
                'medium_similarity': 0,
                'low_similarity': 0
            }
        }
        
        sheets1 = data1['sheets']  # 比較元
        sheets2 = data2['sheets']  # 比較先
        
        print(f"📊 比較元: {len(sheets1)}シート")
        print(f"📊 比較先: {len(sheets2)}シート")
        
        # 各比較先シートに対して比較元から最適なシートを探す
        used_sheet1_names = set()
        
        for sheet2_name, sheet2_data in sheets2.items():
            print(f"\\n🔍 比較先シート '{sheet2_name}' の処理...")
            
            best_match_sheet = None
            best_match_score = 0
            best_match_name = None
            
            # 比較元の全シートから最適マッチを探す
            for sheet1_name, sheet1_data in sheets1.items():
                if sheet1_name in used_sheet1_names:
                    continue
                
                # シート名の類似度も考慮
                name_similarity = self.calculate_similarity(sheet1_name, sheet2_name)
                
                # 各シートの内容を比較（サンプリング）
                content_similarity = self._compare_sheet_content_sample(sheet1_data, sheet2_data)
                
                # 総合スコア（シート名50% + 内容50%）
                total_score = (name_similarity * 0.5) + (content_similarity * 0.5)
                
                if total_score > best_match_score:
                    best_match_score = total_score
                    best_match_sheet = sheet1_data
                    best_match_name = sheet1_name
            
            # 閾値以上の場合はマッチとして処理
            if best_match_sheet and best_match_score >= self.match_threshold:
                print(f"  ✅ '{best_match_name}' とマッチ (スコア: {best_match_score:.1f}%)")
                
                # セル単位の詳細比較
                cell_comparison = self._compare_sheet_cells(best_match_sheet, sheet2_data, best_match_name, sheet2_name)
                
                comparison_results['matched_sheets'][sheet2_name] = {
                    'matched_with': best_match_name,
                    'match_score': best_match_score,
                    'cell_results': cell_comparison
                }
                
                # 統計更新
                stats = comparison_results['statistics']
                stats['matched_cells'] += cell_comparison['matched_cells']
                stats['new_cells'] += cell_comparison['new_cells']
                stats['removed_cells'] += cell_comparison['removed_cells']
                stats['perfect_match'] += cell_comparison['perfect_match']
                stats['high_similarity'] += cell_comparison['high_similarity']
                stats['medium_similarity'] += cell_comparison['medium_similarity']
                stats['low_similarity'] += cell_comparison['low_similarity']
                stats['copied_cells'] = stats.get('copied_cells', 0) + len(cell_comparison.get('unmatched_cells1', []))
                
                used_sheet1_names.add(best_match_name)
            else:
                print(f"  🆕 新規シート")
                comparison_results['new_sheets'].append({
                    'name': sheet2_name,
                    'data': sheet2_data
                })
        
        # マッチしなかった比較元シート
        for sheet1_name in sheets1:
            if sheet1_name not in used_sheet1_names:
                print(f"🗑️ 削除されたシート: {sheet1_name}")
                comparison_results['removed_sheets'].append({
                    'name': sheet1_name,
                    'data': sheets1[sheet1_name]
                })
        
        elapsed_time = time.time() - start_time
        print(f"\\n⏱️ Excel Book比較完了: {elapsed_time:.2f}秒")
        
        # 統計サマリー表示
        self._display_comparison_summary(comparison_results)
        
        return comparison_results

    def _compare_sheet_content_sample(self, sheet1_data: Dict, sheet2_data: Dict, sample_size: int = 50) -> float:
        """シート内容のサンプル比較（高速化のため）"""
        values1 = sheet1_data.get('values', [])
        values2 = sheet2_data.get('values', [])
        
        if not values1 and not values2:
            return 100.0
        if not values1 or not values2:
            return 0.0
        
        # 各シートからランダムなセルをサンプリング
        cells1 = []
        cells2 = []
        
        # フラット化して非空セルを取得
        for row in values1:
            for cell in row:
                if cell and str(cell).strip():
                    cells1.append(str(cell).strip())
        
        for row in values2:
            for cell in row:
                if cell and str(cell).strip():
                    cells2.append(str(cell).strip())
        
        if not cells1 and not cells2:
            return 100.0
        if not cells1 or not cells2:
            return 0.0
        
        # サンプリング
        import random
        sample1 = random.sample(cells1, min(sample_size, len(cells1)))
        sample2 = random.sample(cells2, min(sample_size, len(cells2)))
        
        # 文字列結合して比較
        text1 = ' '.join(sample1)
        text2 = ' '.join(sample2)
        
        return self.calculate_similarity(text1, text2)

    def _compare_sheet_cells(self, sheet1_data: Dict, sheet2_data: Dict, sheet1_name: str, sheet2_name: str) -> Dict:
        """シート内のセル単位での詳細比較"""
        print(f"    🔍 セル単位比較: {sheet1_name} vs {sheet2_name}")
        
        values1 = sheet1_data.get('values', [])  # 比較元
        values2 = sheet2_data.get('values', [])  # 比較先
        
        # UsedRangeの開始位置を取得
        start_row1 = sheet1_data.get('start_row', 1) - 1  # 0-basedに変換
        start_col1 = sheet1_data.get('start_col', 1) - 1  # 0-basedに変換
        start_row2 = sheet2_data.get('start_row', 1) - 1  # 0-basedに変換
        start_col2 = sheet2_data.get('start_col', 1) - 1  # 0-basedに変換
        
        # 全セルを1次元リストに展開（位置情報付き）
        cells1 = []
        cells2 = []
        
        for row_idx, row in enumerate(values1):
            for col_idx, value in enumerate(row):
                if value and str(value).strip():
                    # 実際Excel座標を計算（0-based）
                    actual_row = start_row1 + row_idx
                    actual_col = start_col1 + col_idx
                    cells1.append({
                        'position': (row_idx, col_idx),  # 配列内の位置
                        'excel_position': (actual_row, actual_col),  # 実際Excel座標（0-based）
                        'value': str(value).strip(),
                        'address': self._get_cell_address(actual_row, actual_col)
                    })
        
        for row_idx, row in enumerate(values2):
            for col_idx, value in enumerate(row):
                if value and str(value).strip():
                    # 実際Excel座標を計算（0-based）
                    actual_row = start_row2 + row_idx
                    actual_col = start_col2 + col_idx
                    cells2.append({
                        'position': (row_idx, col_idx),  # 配列内の位置
                        'excel_position': (actual_row, actual_col),  # 実際Excel座標（0-based）
                        'value': str(value).strip(),
                        'address': self._get_cell_address(actual_row, actual_col)
                    })
        
        # マッチング処理
        matched_pairs = []
        used_cell1_indices = set()
        
        for cell2 in cells2:
            best_match = None
            best_similarity = 0
            best_index = -1
            
            for i, cell1 in enumerate(cells1):
                if i in used_cell1_indices:
                    continue
                
                similarity = self.calculate_similarity(cell1['value'], cell2['value'])
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = cell1
                    best_index = i
            
            if best_match and best_similarity >= self.match_threshold:
                matched_pairs.append({
                    'cell1': best_match,
                    'cell2': cell2,
                    'similarity': best_similarity
                })
                used_cell1_indices.add(best_index)
        
        # 統計計算
        new_cells = len(cells2) - len(matched_pairs)
        removed_cells = len(cells1) - len(matched_pairs)
        
        perfect_match = len([p for p in matched_pairs if p['similarity'] == 100.0])
        high_similarity = len([p for p in matched_pairs if 80 <= p['similarity'] < 100])
        medium_similarity = len([p for p in matched_pairs if 50 <= p['similarity'] < 80])
        low_similarity = len([p for p in matched_pairs if 30 <= p['similarity'] < 50])
        
        print(f"      📊 マッチ: {len(matched_pairs)}, 新規: {new_cells}, 削除: {removed_cells}")
        
        # マッチしなかった1つ目（比較元）のセル
        unmatched_cells1 = []
        for i, cell1 in enumerate(cells1):
            if i not in used_cell1_indices:
                unmatched_cells1.append(cell1)
        
        return {
            'matched_pairs': matched_pairs,
            'matched_cells': len(matched_pairs),
            'new_cells': new_cells,
            'removed_cells': removed_cells,
            'perfect_match': perfect_match,
            'high_similarity': high_similarity,
            'medium_similarity': medium_similarity,
            'low_similarity': low_similarity,
            'cells1': cells1,
            'cells2': cells2,
            'used_cell1_indices': used_cell1_indices,
            'unmatched_cells1': unmatched_cells1  # コピー対象セル
        }

    def _get_cell_address(self, row_idx: int, col_idx: int) -> str:
        """行列番号からExcelアドレスを生成（A1形式）"""
        col_letter = ""
        col_num = col_idx + 1
        while col_num > 0:
            col_num -= 1
            col_letter = chr(col_num % 26 + ord('A')) + col_letter
            col_num //= 26
        
        return f"{col_letter}{row_idx + 1}"

    def _find_empty_positions(self, worksheet, values2: List[List], unmatched_count: int) -> List[Tuple]:
        """2つ目のワークシートで空いている位置を見つける"""
        empty_positions = []
        
        # 既存データの最大行・列を取得
        max_row = len(values2) if values2 else 0
        max_col = max(len(row) for row in values2) if values2 else 0
        
        # まず既存データの空いているセルを探す
        for row_idx in range(max_row):
            for col_idx in range(max_col):
                if col_idx < len(values2[row_idx]):
                    cell_value = values2[row_idx][col_idx]
                    if not cell_value or str(cell_value).strip() == "":
                        empty_positions.append((row_idx, col_idx))
                        if len(empty_positions) >= unmatched_count:
                            return empty_positions
                else:
                    empty_positions.append((row_idx, col_idx))
                    if len(empty_positions) >= unmatched_count:
                        return empty_positions
        
        # 既存データの右側に追加
        if len(empty_positions) < unmatched_count:
            for row_idx in range(max_row):
                empty_positions.append((row_idx, max_col))
                if len(empty_positions) >= unmatched_count:
                    return empty_positions
        
        # 既存データの下側に追加
        if len(empty_positions) < unmatched_count:
            for additional_idx in range(unmatched_count - len(empty_positions)):
                empty_positions.append((max_row + additional_idx, 0))
        
        return empty_positions[:unmatched_count]

    def _display_comparison_summary(self, results: Dict):
        """比較結果のサマリーを表示"""
        print("\\n📊 === Excel Book比較結果サマリー ===")
        
        matched_sheets = len(results['matched_sheets'])
        new_sheets = len(results['new_sheets'])
        removed_sheets = len(results['removed_sheets'])
        
        print(f"📋 シート比較:")
        print(f"  ✅ マッチしたシート: {matched_sheets}個")
        print(f"  🆕 新規シート: {new_sheets}個")
        print(f"  🗑️ 削除されたシート: {removed_sheets}個")
        
        stats = results['statistics']
        print(f"\\n💾 セル比較:")
        print(f"  📊 マッチしたセル: {stats['matched_cells']:,}個")
        print(f"    ✅ 完全一致: {stats['perfect_match']:,}個")
        print(f"    🟡 高類似度: {stats['high_similarity']:,}個")
        print(f"    🔵 中類似度: {stats['medium_similarity']:,}個")
        print(f"    🟠 低類似度: {stats['low_similarity']:,}個")
        print(f"  🆕 新規セル: {stats['new_cells']:,}個")
        print(f"  📋 コピーされたセル: {stats['copied_cells']:,}個")
        print(f"  🗑️ 削除されたセル: {stats['removed_cells']:,}個")

    def apply_color_coding(self, results: Dict):
        """比較結果に基づいて色付けを適用"""
        try:
            print("\\n🎨 バックアップファイルに色付けを適用中...")
            
            # バックアップファイルを開く
            backup_path = self.workbook_data['backup']['path']
            workbook = self.excel_app.Workbooks.Open(backup_path)
            
            # 比較元ファイルも開いて座標を正確に取得
            source_path = self.workbook_data['file1']['path']
            source_workbook = self.excel_app.Workbooks.Open(source_path)
            
            total_colored_cells = 0
            
            # マッチしたシートの処理
            for sheet_name, match_info in results['matched_sheets'].items():
                print(f"  🎨 シート '{sheet_name}' の色付け...")
                
                try:
                    worksheet = workbook.Worksheets(sheet_name)
                    cell_results = match_info['cell_results']
                    
                    # すべてのマッチしたセルに色付け（完全一致も含む）
                    for pair in cell_results['matched_pairs']:
                        row, col = pair['cell2']['position']
                        cell = worksheet.Cells(row + 1, col + 1)
                        
                        similarity = pair['similarity']
                        if similarity == 100.0:
                            color = self.colors['perfect']
                            comment_text = f"✅ 完全一致\\n比較元: {pair['cell1']['value'][:50]}"
                        elif similarity >= 80:
                            color = self.colors['high']
                            comment_text = f"類似度: {similarity:.1f}%\\n比較元: {pair['cell1']['value'][:50]}"
                        elif similarity >= 50:
                            color = self.colors['medium']
                            comment_text = f"類似度: {similarity:.1f}%\\n比較元: {pair['cell1']['value'][:50]}"
                        else:
                            color = self.colors['low']
                            comment_text = f"類似度: {similarity:.1f}%\\n比較元: {pair['cell1']['value'][:50]}"
                        
                        cell.Interior.Color = color
                        total_colored_cells += 1
                        
                        # コメント追加
                        try:
                            if cell.Comment is not None:
                                cell.Comment.Delete()
                            cell.AddComment(comment_text)
                        except:
                            pass  # コメント追加失敗は無視
                    
                    # 新規セル（比較元にないセル）の色付け
                    used_indices = cell_results['used_cell1_indices']
                    for i, cell2 in enumerate(cell_results['cells2']):
                        # マッチしなかったセルを新規として色付け
                        is_matched = any(pair['cell2']['address'] == cell2['address'] 
                                       for pair in cell_results['matched_pairs'])
                        
                        if not is_matched:
                            row, col = cell2['position']
                            cell = worksheet.Cells(row + 1, col + 1)
                            cell.Interior.Color = self.colors['new']
                            total_colored_cells += 1
                            
                            # 新規セルのコメント
                            try:
                                if cell.Comment is not None:
                                    cell.Comment.Delete()
                                cell.AddComment("新規追加されたセル")
                            except:
                                pass
                    
                    # 1つ目にあって2つ目にないセルをコピー
                    unmatched_cells1 = cell_results.get('unmatched_cells1', [])
                    if unmatched_cells1:
                        print(f"      📋 シート '{sheet_name}' に{len(unmatched_cells1)}個のセルをコピー中...")
                        
                        # ワークシートの使用範囲を取得
                        used_range = worksheet.UsedRange
                        if used_range is not None:
                            # UsedRangeの開始位置も考慮
                            first_row = used_range.Row
                            first_col = used_range.Column
                            max_row = first_row + used_range.Rows.Count - 1
                            max_col = first_col + used_range.Columns.Count - 1
                            print(f"        📐 使用範囲: R{first_row}C{first_col}:R{max_row}C{max_col}")
                        else:
                            max_row = 1
                            max_col = 1
                            print(f"        📐 空のシート、デフォルト位置を使用")
                        
                        # コピー先位置を決定（既存データの右側に2列空けて配置）
                        copy_start_col = max_col + 3  # 2列空ける
                        copy_start_row = 1  # 1行目から開始
                        
                        print(f"        📍 コピー先開始位置: R{copy_start_row}C{copy_start_col}")
                        
                        # 比較元シートを開いて実際のセル値を検証
                        try:
                            source_sheet = source_workbook.Worksheets(match_info['matched_with'])
                        except:
                            print(f"        ❌ 比較元シート '{match_info['matched_with']}' が見つかりません")
                            source_sheet = None
                        
                        for i, cell1 in enumerate(unmatched_cells1):
                            # 配置位置計算（縦に並べる）
                            target_row = copy_start_row + i
                            target_col = copy_start_col
                            
                            # Excel座標情報を取得
                            if 'excel_position' in cell1:
                                excel_row_0based, excel_col_0based = cell1['excel_position']
                                expected_address = cell1['address']
                                
                                # 実際の比較元セルの値を検証
                                if source_sheet:
                                    try:
                                        # 0ベース座標を1ベースExcel座標に変換
                                        excel_row = excel_row_0based + 1
                                        excel_col = excel_col_0based + 1
                                        actual_cell = source_sheet.Cells(excel_row, excel_col)
                                        actual_value = str(actual_cell.Value) if actual_cell.Value else ""
                                        actual_address = actual_cell.Address(False, False)  # 相対参照でアドレス取得
                                        
                                        print(f"        🔍 座標検証:")
                                        print(f"          Excel座標(0-based): ({excel_row_0based},{excel_col_0based})")
                                        print(f"          Excel座標(1-based): R{excel_row}C{excel_col}")
                                        print(f"          期待アドレス: {expected_address}")
                                        print(f"          実際アドレス: {actual_address}")
                                        print(f"          期待値: '{cell1['value'][:30]}...'")
                                        print(f"          実際値: '{actual_value[:30]}...'")
                                        
                                        # 値やアドレスが一致しない場合は修正
                                        if actual_address != expected_address or actual_value.strip() != cell1['value'].strip():
                                            print(f"        🔧 座標/値を修正: {expected_address} → {actual_address}")
                                            cell1['value'] = actual_value
                                            cell1['address'] = actual_address
                                            
                                    except Exception as verify_err:
                                        print(f"        ❌ 座標検証エラー: {verify_err}")
                            else:
                                # 旧形式でexcel_positionがない場合のフォールバック
                                orig_row, orig_col = cell1['position']
                                expected_address = cell1['address']
                                print(f"        ⚠️ 旧形式データでexcel_positionがありません: {expected_address}")
                            
                            # Excelのセル参照（1ベース）
                            target_cell = worksheet.Cells(target_row, target_col)
                            target_address = self._get_cell_address(target_row - 1, target_col - 1)
                            
                            print(f"        📋 {cell1['address']} → {target_address}(R{target_row}C{target_col}): '{cell1['value'][:30]}...'")
                            
                            # セルの値をコピー
                            target_cell.Value = cell1['value']
                            target_cell.Interior.Color = self.colors['copied']
                            total_colored_cells += 1
                            
                            # コピー元情報をコメントに追加
                            try:
                                if target_cell.Comment is not None:
                                    target_cell.Comment.Delete()
                                comment_text = f"📋 コピー元シート: {match_info['matched_with']}\\n元の位置: {cell1['address']}\\n内容: {cell1['value'][:50]}"
                                target_cell.AddComment(comment_text)
                            except Exception as comment_err:
                                print(f"        ⚠️ コメント追加エラー: {comment_err}")
                        
                        print(f"      ✅ {len(unmatched_cells1)}個のセルをコピー完了")
                    
                    total_processed_cells = len(cell_results['matched_pairs']) + len(unmatched_cells1)
                    print(f"      ✅ {total_processed_cells}個のセルを処理完了")
                    
                except Exception as e:
                    print(f"      ❌ シート '{sheet_name}' の色付けエラー: {e}")
            
            # 新規シートの処理
            for new_sheet in results['new_sheets']:
                sheet_name = new_sheet['name']
                print(f"  🆕 新規シート '{sheet_name}' の色付け...")
                
                try:
                    worksheet = workbook.Worksheets(sheet_name)
                    # シート全体を新規色で色付け
                    used_range = worksheet.UsedRange
                    if used_range is not None:
                        used_range.Interior.Color = self.colors['new']
                        total_colored_cells += used_range.Cells.Count
                        
                        # シートレベルのコメント（A1セルに）
                        try:
                            if worksheet.Cells(1, 1).Comment is not None:
                                worksheet.Cells(1, 1).Comment.Delete()
                            worksheet.Cells(1, 1).AddComment("🆕 新規追加されたシート")
                        except:
                            pass
                    
                    print(f"      ✅ 新規シート全体を緑色で色付け")
                    
                except Exception as e:
                    print(f"      ❌ 新規シート '{sheet_name}' の色付けエラー: {e}")
            
            # ファイルを保存
            workbook.Save()
            workbook.Close()
            
            # 比較元ファイルも閉じる
            source_workbook.Close(SaveChanges=False)
            
            print(f"\\n✅ 色付け完了: {total_colored_cells:,}個のセルに色を適用")
            print(f"🎨 色付け済みファイル: {self.workbook_data['backup']['name']}")
            
        except Exception as e:
            print(f"❌ 色付け処理エラー: {e}")
            messagebox.showerror("エラー", f"色付け処理でエラーが発生しました：{e}")

    def generate_html_report(self, results: Dict):
        """HTML形式の詳細レポートを生成"""
        print("\\n📄 HTMLレポートを生成中...")
        
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        filename = f"ExcelBook比較レポート_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # HTMLコンテンツを構築
        html_content = self._build_html_content(results, timestamp)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 HTMLレポートを保存しました: {filename}")
            
            # 統計JSON出力
            json_filename = f"ExcelBook比較統計_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_data = {
                'timestamp': datetime.now().isoformat(),
                'file1': self.workbook_data['file1']['name'],
                'file2': self.workbook_data['file2']['name'],
                'backup': self.workbook_data['backup']['name'],
                'summary': results['statistics'],
                'sheet_summary': {
                    'matched_sheets': len(results['matched_sheets']),
                    'new_sheets': len(results['new_sheets']),
                    'removed_sheets': len(results['removed_sheets'])
                }
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"📊 統計データを保存しました: {json_filename}")
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")

    def _build_html_content(self, results: Dict, timestamp: str) -> str:
        """HTMLコンテンツを構築"""
        html_parts = []
        
        # HTMLヘッダー
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="ja">')
        html_parts.append('<head>')
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('    <title>Excel Book全体比較レポート</title>')
        html_parts.append('    <style>')
        html_parts.append('        body { font-family: "Yu Gothic", "Meiryo", sans-serif; margin: 0; padding: 20px; background: #f8fafc; }')
        html_parts.append('        .container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }')
        html_parts.append('        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }')
        html_parts.append('        .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }')
        html_parts.append('        .content { padding: 30px; }')
        html_parts.append('        .section { margin-bottom: 40px; }')
        html_parts.append('        .section h2 { color: #4f46e5; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }')
        html_parts.append('        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }')
        html_parts.append('        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; border-top: 4px solid; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
        html_parts.append('        .stat-card.perfect { border-top-color: #10b981; }')
        html_parts.append('        .stat-card.high { border-top-color: #f59e0b; }')
        html_parts.append('        .stat-card.medium { border-top-color: #3b82f6; }')
        html_parts.append('        .stat-card.low { border-top-color: #ef4444; }')
        html_parts.append('        .stat-card.new { border-top-color: #22c55e; }')
        html_parts.append('        .stat-card.removed { border-top-color: #dc2626; }')
        html_parts.append('        .stat-card.copied { border-top-color: #f97316; }')
        html_parts.append('        .stat-number { font-size: 1.8em; font-weight: bold; margin-bottom: 5px; }')
        html_parts.append('        .sheet-list { background: #f8fafc; padding: 20px; border-radius: 8px; margin: 10px 0; }')
        html_parts.append('        .sheet-item { background: white; margin: 10px 0; padding: 15px; border-radius: 6px; border-left: 4px solid; }')
        html_parts.append('        .sheet-item.matched { border-left-color: #10b981; }')
        html_parts.append('        .sheet-item.new { border-left-color: #22c55e; }')
        html_parts.append('        .sheet-item.removed { border-left-color: #dc2626; }')
        html_parts.append('        .footer { background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }')
        html_parts.append('    </style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # ヘッダー
        html_parts.append('    <div class="container">')
        html_parts.append('        <div class="header">')
        html_parts.append('            <h1>📚 Excel Book全体比較レポート</h1>')
        html_parts.append(f'            <p>生成日時: {timestamp}</p>')
        html_parts.append('        </div>')
        
        html_parts.append('        <div class="content">')
        
        # ファイル情報
        html_parts.append('            <div class="section">')
        html_parts.append('                <h2>📁 比較対象ファイル</h2>')
        html_parts.append(f'                <p><strong>比較元ファイル:</strong> {self.workbook_data["file1"]["name"]}</p>')
        html_parts.append(f'                <p><strong>比較先ファイル:</strong> {self.workbook_data["file2"]["name"]}</p>')
        html_parts.append(f'                <p><strong>色付け済みファイル:</strong> {self.workbook_data["backup"]["name"]}</p>')
        html_parts.append('            </div>')
        
        # 統計情報
        stats = results['statistics']
        html_parts.append('            <div class="section">')
        html_parts.append('                <h2>📊 比較結果統計</h2>')
        html_parts.append('                <div class="stats-grid">')
        
        html_parts.append('                    <div class="stat-card perfect">')
        html_parts.append(f'                        <div class="stat-number">{stats["perfect_match"]:,}</div>')
        html_parts.append('                        <div>完全一致</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                    <div class="stat-card high">')
        html_parts.append(f'                        <div class="stat-number">{stats["high_similarity"]:,}</div>')
        html_parts.append('                        <div>高類似度 (80-99%)</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                    <div class="stat-card medium">')
        html_parts.append(f'                        <div class="stat-number">{stats["medium_similarity"]:,}</div>')
        html_parts.append('                        <div>中類似度 (50-79%)</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                    <div class="stat-card low">')
        html_parts.append(f'                        <div class="stat-number">{stats["low_similarity"]:,}</div>')
        html_parts.append('                        <div>低類似度 (30-49%)</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                    <div class="stat-card new">')
        html_parts.append(f'                        <div class="stat-number">{stats["new_cells"]:,}</div>')
        html_parts.append('                        <div>新規セル</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                    <div class="stat-card removed">')
        html_parts.append(f'                        <div class="stat-number">{stats["removed_cells"]:,}</div>')
        html_parts.append('                        <div>削除されたセル</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                    <div class="stat-card copied">')
        html_parts.append(f'                        <div class="stat-number">{stats.get("copied_cells", 0):,}</div>')
        html_parts.append('                        <div>コピーされたセル</div>')
        html_parts.append('                    </div>')
        
        html_parts.append('                </div>')
        html_parts.append('            </div>')
        
        # シート比較結果
        html_parts.append('            <div class="section">')
        html_parts.append('                <h2>📋 シート比較詳細</h2>')
        
        # マッチしたシート
        if results['matched_sheets']:
            html_parts.append('                <h3>✅ マッチしたシート</h3>')
            html_parts.append('                <div class="sheet-list">')
            for sheet_name, match_info in results['matched_sheets'].items():
                html_parts.append(f'                    <div class="sheet-item matched">')
                html_parts.append(f'                        <strong>{sheet_name}</strong> ⇔ <strong>{match_info["matched_with"]}</strong>')
                html_parts.append(f'                        <br>マッチスコア: {match_info["match_score"]:.1f}%')
                cell_results = match_info["cell_results"]
                html_parts.append(f'                        <br>セル詳細: マッチ{cell_results["matched_cells"]}個, 新規{cell_results["new_cells"]}個, 削除{cell_results["removed_cells"]}個')
                html_parts.append('                    </div>')
            html_parts.append('                </div>')
        
        # 新規シート
        if results['new_sheets']:
            html_parts.append('                <h3>🆕 新規シート</h3>')
            html_parts.append('                <div class="sheet-list">')
            for sheet in results['new_sheets']:
                html_parts.append(f'                    <div class="sheet-item new">')
                html_parts.append(f'                        <strong>{sheet["name"]}</strong>')
                html_parts.append(f'                        <br>サイズ: {sheet["data"]["rows"]}行 x {sheet["data"]["cols"]}列')
                html_parts.append('                    </div>')
            html_parts.append('                </div>')
        
        # 削除されたシート
        if results['removed_sheets']:
            html_parts.append('                <h3>🗑️ 削除されたシート</h3>')
            html_parts.append('                <div class="sheet-list">')
            for sheet in results['removed_sheets']:
                html_parts.append(f'                    <div class="sheet-item removed">')
                html_parts.append(f'                        <strong>{sheet["name"]}</strong>')
                html_parts.append(f'                        <br>サイズ: {sheet["data"]["rows"]}行 x {sheet["data"]["cols"]}列')
                html_parts.append('                    </div>')
            html_parts.append('                </div>')
        
        html_parts.append('            </div>')
        
        html_parts.append('        </div>')
        
        # フッター
        html_parts.append('        <div class="footer">')
        html_parts.append('            <p>📚 Excel Book全体比較プログラム</p>')
        html_parts.append('            <p>意味的マッチング・セルずれ対応・色付け機能付き</p>')
        html_parts.append('        </div>')
        
        html_parts.append('    </div>')
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\\n'.join(html_parts)

    def run_comparison(self):
        """比較処理のメイン実行"""
        try:
            # ファイル選択
            if not self.select_excel_files():
                return False
            
            # バックアップコピー作成
            if not self.create_backup_copy():
                return False
            
            # データ抽出
            print("\\n📊 === データ抽出フェーズ ===")
            data1 = self.extract_all_worksheets_data(
                self.workbook_data['file1']['path'], 
                "比較元ファイル"
            )
            if not data1:
                return False
            
            data2 = self.extract_all_worksheets_data(
                self.workbook_data['file2']['path'], 
                "比較先ファイル"
            )
            if not data2:
                return False
            
            # 比較実行
            print("\\n🔍 === 比較実行フェーズ ===")
            results = self.compare_worksheets(data1, data2)
            
            # 色付け適用
            print("\\n🎨 === 色付けフェーズ ===")
            self.apply_color_coding(results)
            
            # レポート生成
            print("\\n📄 === レポート生成フェーズ ===")
            self.generate_html_report(results)
            
            return True
            
        except Exception as e:
            messagebox.showerror("エラー", f"比較処理でエラーが発生しました：{e}")
            return False

    def main_loop(self):
        """メインループ（繰り返し比較可能）"""
        while True:
            print("\\n" + "="*80)
            print("📚 Excel Book全体比較プログラム（意味的マッチング対応）")
            print("="*80)
            
            # 比較実行
            success = self.run_comparison()
            
            if success:
                print("\\n✅ Excel Book比較処理が完了しました！")
                print("🎨 色付け済みファイルをExcelで確認してください")
            else:
                print("\\n❌ Excel Book比較処理が中断されました")
            
            # 継続確認
            root = self._create_topmost_window()
            continue_choice = messagebox.askyesno(
                "継続確認",
                "別のExcel Bookを比較しますか？\\n\\n「はい」: 新しい比較を開始\\n「いいえ」: プログラムを終了",
                parent=root
            )
            root.destroy()
            
            if not continue_choice:
                print("\\n👋 プログラムを終了します")
                break
            else:
                print("\\n🔄 新しいExcel Book比較を開始します...")

    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            if self.excel_app:
                print("🔄 Excelアプリケーションを終了中...")
                # 開いているワークブックをすべて閉じる
                for i in range(self.excel_app.Workbooks.Count, 0, -1):
                    try:
                        self.excel_app.Workbooks(i).Close(SaveChanges=False)
                    except:
                        pass
                
                self.excel_app.Quit()
                self.excel_app = None
                print("✅ Excelアプリケーションを終了しました")
        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")


def main():
    """メイン関数"""
    comparator = ExcelBookComparator()
    
    try:
        # Excel起動
        if not comparator.start_excel_application():
            return
        
        # メインループ実行
        comparator.main_loop()
        
    except KeyboardInterrupt:
        print("\\n🛑 ユーザーによって中断されました")
    except Exception as e:
        print(f"\\n❌ 予期しないエラーが発生しました: {e}")
        messagebox.showerror("エラー", f"予期しないエラーが発生しました：{e}")
    finally:
        # クリーンアップ
        comparator.cleanup()


if __name__ == "__main__":
    main()