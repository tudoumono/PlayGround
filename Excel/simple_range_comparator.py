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
    
    def _create_topmost_window(self):
        """常に最前面に表示されるtkinterウィンドウを作成"""
        root = tk.Tk()
        root.withdraw()  # ウィンドウを隠す
        
        try:
            # 基本設定
            root.attributes('-topmost', True)  # 最前面に表示
            root.lift()  # ウィンドウを前面に
            root.focus_force()  # フォーカスを強制取得
            
            # Windowsの場合の追加設定
            try:
                root.wm_attributes('-toolwindow', True)  # タスクバーに表示しない
            except:
                pass
            
            # ダイアログを目立たせるための設定
            try:
                # ウィンドウの背景色を設定（ダイアログにも影響）
                root.configure(bg='#FF6B6B')  # 鮮やかな赤
                # システムフォントサイズを大きく
                root.option_add('*Font', ('MS Sans Serif', 10, 'bold'))
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ トップモストウィンドウ設定エラー: {e}")
        
        return root
    
    def _create_custom_dialog(self, title: str, message: str, dialog_type: str = "info"):
        """カスタムダイアログを作成（より目立つスタイル）"""
        # より安全な実装
        root = self._create_topmost_window()
        
        try:
            dialog = tk.Toplevel(root)
            dialog.title(title)
            dialog.attributes('-topmost', True)
            dialog.lift()
            dialog.focus_force()
            
            # ウィンドウサイズと位置（画面中央に配置）
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width - 450) // 2
            y = (screen_height - 250) // 2
            dialog.geometry(f"450x250+{x}+{y}")
            dialog.resizable(False, False)
            
            # 背景色を目立つ色に
            if dialog_type == "error":
                bg_color = "#FF4444"  # 赤
                text_color = "white"
            elif dialog_type == "warning":
                bg_color = "#FFA500"  # オレンジ
                text_color = "black"
            elif dialog_type == "success":
                bg_color = "#00AA00"  # 緑
                text_color = "white"
            else:
                bg_color = "#4A90E2"  # 青
                text_color = "white"
            
            dialog.configure(bg=bg_color)
            
            # 太い枠線を追加
            frame = tk.Frame(dialog, bg="black", relief="raised", bd=5)
            frame.pack(fill="both", expand=True, padx=8, pady=8)
            
            inner_frame = tk.Frame(frame, bg=bg_color)
            inner_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # メッセージラベル
            label = tk.Label(
                inner_frame, 
                text=message, 
                bg=bg_color, 
                fg=text_color,
                font=("MS Sans Serif", 11, "bold"),
                wraplength=400,
                justify="center"
            )
            label.pack(pady=25, padx=20, expand=True)
            
            # ボタンフレーム
            button_frame = tk.Frame(inner_frame, bg=bg_color)
            button_frame.pack(pady=15)
            
            result = {"value": None}
            
            def safe_close():
                """安全にダイアログを閉じる"""
                try:
                    dialog.grab_release()
                    dialog.destroy()
                except:
                    pass
                try:
                    self._safe_destroy(root)
                except:
                    pass
            
            def on_yes():
                result["value"] = True
                safe_close()
            
            def on_no():
                result["value"] = False
                safe_close()
            
            def on_cancel():
                result["value"] = None
                safe_close()
            
            def on_ok():
                result["value"] = True
                safe_close()
            
            # 閉じるボタン処理
            def on_window_close():
                result["value"] = None if dialog_type in ["yesnocancel"] else False
                safe_close()
            
            dialog.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # ボタンスタイル
            button_style = {
                "font": ("MS Sans Serif", 10, "bold"),
                "width": 10,
                "height": 2,
                "relief": "raised",
                "bd": 3
            }
            
            if dialog_type == "yesnocancel":
                tk.Button(button_frame, text="はい", command=on_yes, 
                         bg="#00DD00", fg="black", **button_style).pack(side="left", padx=8)
                tk.Button(button_frame, text="いいえ", command=on_no, 
                         bg="#DDDD00", fg="black", **button_style).pack(side="left", padx=8)
                tk.Button(button_frame, text="キャンセル", command=on_cancel, 
                         bg="#DD0000", fg="white", **button_style).pack(side="left", padx=8)
            elif dialog_type == "yesno":
                tk.Button(button_frame, text="はい", command=on_yes, 
                         bg="#00DD00", fg="black", **button_style).pack(side="left", padx=8)
                tk.Button(button_frame, text="いいえ", command=on_no, 
                         bg="#DDDD00", fg="black", **button_style).pack(side="left", padx=8)
            else:
                tk.Button(button_frame, text="OK", command=on_ok, 
                         bg="#00DD00", fg="black", **button_style).pack(padx=8)
            
            # キーバインド
            dialog.bind('<Return>', lambda e: on_yes() if dialog_type in ["yesnocancel", "yesno"] else on_ok())
            dialog.bind('<Escape>', lambda e: on_cancel() if dialog_type == "yesnocancel" else on_no() if dialog_type == "yesno" else on_ok())
            
            # モーダル表示
            dialog.transient(root)
            dialog.grab_set()
            
            # 中央に配置してフォーカス
            dialog.update_idletasks()
            dialog.focus_set()
            
            # 安全なメインループ待機
            try:
                root.wait_window(dialog)
            except:
                pass
            
            return result.get("value", None)
            
        except Exception as e:
            print(f"⚠️ カスタムダイアログエラー: {e}")
            # フォールバック: 標準メッセージボックス
            try:
                self._safe_destroy(root)
            except:
                pass
            
            if dialog_type == "yesnocancel":
                return messagebox.askyesnocancel(title, message)
            elif dialog_type == "yesno":
                return messagebox.askyesno(title, message)
            elif dialog_type == "error":
                messagebox.showerror(title, message)
                return True
            else:
                messagebox.showinfo(title, message)
                return True
    
    def _show_custom_info(self, title: str, message: str):
        """カスタム情報ダイアログ"""
        # 一時的に標準ダイアログを使用（安定性重視）
        root = self._create_topmost_window()
        result = messagebox.showinfo(title, message, parent=root)
        self._safe_destroy(root)
        return result
    
    def _show_custom_warning(self, title: str, message: str):
        """カスタム警告ダイアログ"""
        root = self._create_topmost_window()
        result = messagebox.showwarning(title, message, parent=root)
        self._safe_destroy(root)
        return result
    
    def _show_custom_error(self, title: str, message: str):
        """カスタムエラーダイアログ"""
        root = self._create_topmost_window()
        result = messagebox.showerror(title, message, parent=root)
        self._safe_destroy(root)
        return result
    
    def _show_custom_yesno(self, title: str, message: str):
        """カスタムYes/Noダイアログ"""
        root = self._create_topmost_window()
        result = messagebox.askyesno(title, message, parent=root)
        self._safe_destroy(root)
        return result
    
    def _show_custom_yesnocancel(self, title: str, message: str):
        """カスタムYes/No/Cancelダイアログ"""
        root = self._create_topmost_window()
        result = messagebox.askyesnocancel(title, message, parent=root)
        self._safe_destroy(root)
        return result
    
    def _safe_destroy(self, root):
        """安全なtkinterウィンドウ破棄"""
        if root is None:
            return
            
        try:
            # ウィンドウが存在するかチェック
            if hasattr(root, 'winfo_exists') and root.winfo_exists():
                root.quit()  # メインループを終了
                root.destroy()  # ウィンドウを破棄
        except tk.TclError:
            # TclError は既にウィンドウが破棄されている場合に発生
            pass
        except Exception as e:
            # その他の予期しないエラー
            print(f"⚠️ ウィンドウ破棄エラー: {e}")
            pass
        
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
            use_existing = self._show_custom_yesno(
                "📁 ファイル選択",
                f"既に {self.excel_app.Workbooks.Count} 個のExcelファイルが開いています。\n\n" +
                "これらのファイルを使用しますか？\n\n" +
                "「はい」= 既存ファイルを使用\n" +
                "「いいえ」= 新しいファイルを選択"
            )
            
            if use_existing:
                return self.use_existing_files()
            else:
                return self.open_excel_files()
        else:
            # ファイルが足りない場合は強制的に新規選択
            print(f"📝 開いているファイル数が不足しています（{self.excel_app.Workbooks.Count}/2）")
            print("📁 新しいファイルを選択します...")
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

    def open_and_process_files_sequentially(self):
        """ファイルを順次開いて処理する（メモリ効率向上）"""
        print("\n📁 ファイルを順次処理します...")
        
        # 1つ目のファイル処理
        print("\n🗂️ === 1つ目のファイル処理 ===")
        file1_data = self.process_single_file("1つ目のExcelファイルを選択", "1つ目のファイル")
        if not file1_data:
            return False
            
        # 2つ目のファイル処理
        print("\n🗂️ === 2つ目のファイル処理 ===")
        file2_data = self.process_single_file("2つ目のExcelファイルを選択", "2つ目のファイル")
        if not file2_data:
            return False
        
        # データを保存
        self.workbook_data['file1'] = file1_data
        self.workbook_data['file2'] = file2_data
        
        return True
    
    def process_single_file(self, dialog_title: str, label: str) -> Dict:
        """1つのファイルを開いて範囲選択し、データを抽出してから閉じる"""
        # ファイル選択
        root = self._create_topmost_window()
        file_path = filedialog.askopenfilename(
            parent=root,
            title=dialog_title,
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        self._safe_destroy(root)
        
        if not file_path:
            print(f"❌ {label}の選択がキャンセルされました")
            return None
        
        print(f"📂 ファイルを開いています: {Path(file_path).name}")
        
        try:
            # ファイルを開く
            workbook = self.excel_app.Workbooks.Open(file_path)
            print(f"✅ ファイルオープン成功: {workbook.Name}")
            
            # シート選択
            worksheet = self.select_worksheet(workbook, label)
            if not worksheet:
                workbook.Close(SaveChanges=False)
                print(f"❌ シート選択に失敗: {label}")
                return None
                
            # 範囲選択とデータ抽出
            range_data = self.select_range_and_extract_data(worksheet, label, Path(file_path).name)
            
            # データを安全にコピー（参照を切る）
            extracted_data = {
                'path': file_path,
                'name': Path(file_path).name,
                'worksheet_name': worksheet.Name,
                'address': range_data['address'],
                'values': range_data['values'].copy(),  # データをコピー
                'workbook': None,  # 後で閉じるので参照は保持しない
                'worksheet': None
            }
            
            # ワークブックを閉じる
            workbook.Close(SaveChanges=False)
            print(f"📄 ファイルを閉じました: {Path(file_path).name}")
            print(f"💾 データ保存完了: {len(extracted_data['values'])}行 x {len(extracted_data['values'][0]) if extracted_data['values'] else 0}列")
            
            return extracted_data
            
        except Exception as e:
            print(f"❌ ファイル処理エラー ({label}): {e}")
            try:
                if 'workbook' in locals():
                    workbook.Close(SaveChanges=False)
            except:
                pass
            return None
    
    def select_range_and_extract_data(self, worksheet, label: str, filename: str) -> Dict:
        """範囲選択とデータ抽出を行う"""
        print(f"📄 {label}: {filename}")
        print(f"📊 作業シート: {worksheet.Name}")
        
        # 自動範囲提案
        try:
            used_range = worksheet.UsedRange
            if used_range:
                suggested_address = used_range.Address
                print(f"📊 推奨範囲: {suggested_address}")
            else:
                suggested_address = "A1:H50"
        except:
            suggested_address = "A1:H50"
        
        # 範囲選択方法の確認
        choice = self._show_custom_yesnocancel(
            f"📊 {label} - 範囲選択方法",
            f"📄 ファイル: {filename}\n" +
            f"📊 推奨範囲: {suggested_address}\n\n" +
            f"範囲選択方法を選択してください:\n\n" +
            f"「はい」 = 推奨範囲を使用\n" +
            f"「いいえ」 = マウスで範囲選択\n" +
            f"「キャンセル」 = 処理中止"
        )
        
        if choice is None:  # キャンセル
            raise ValueError("範囲選択がキャンセルされました")
        
        elif choice:  # はい - 推奨範囲使用
            range_address = suggested_address
            selected_range = worksheet.Range(range_address)
            print(f"✅ 推奨範囲を使用: {range_address}")
            
        else:  # いいえ - マウス選択
            # より安全なInputBox使用
            try:
                print(f"🖱️ Excelで範囲を選択してください...")
                
                # Excelを前面に表示
                self.excel_app.Visible = True
                worksheet.Activate()
                
                # 改善された範囲選択ダイアログ
                print(f"🖱️ {label}の範囲を選択してください...")
                print(f"📋 推奨範囲: {suggested_address}")
                
                # より明確な指示でInputBoxを表示
                instruction_message = f"""{label}の範囲を選択してください

【操作方法】
1. マウスでセル範囲を選択（ドラッグ）
2. 選択されたアドレスを確認
3. 下の入力欄にそのアドレスを入力
4. OKボタンを押してください

推奨範囲: {suggested_address}
例: A1:C10, B2:F20, A:A（列全体）

⚠️ セルの値ではなく範囲アドレスを入力してください"""

                # セル値参照を回避した堅牢な範囲選択処理
                print(f"🎯 キーボード入力方式で範囲選択を実行...")
                
                # まず、操作説明を表示
                root = self._create_topmost_window()
                messagebox.showinfo(
                    "範囲入力の注意", 
                    f"次のダイアログで範囲アドレスを直接入力してください。\n\n"
                    f"推奨範囲: {suggested_address}\n\n"
                    f"⚠️ 重要: マウスでのドラッグ選択は使用しないでください\n"
                    f"（セル値が参照されてしまいます）\n\n"
                    f"キーボードで直接入力例:\n"
                    f"• A1:F59\n"
                    f"• $A$1:$F$59",
                    parent=root
                )
                self._safe_destroy(root)
                
                try:
                    input_result = self.excel_app.InputBox(
                        f"{instruction_message}\n\n" +
                        f"⚠️ マウス選択禁止：キーボードで範囲アドレスを直接入力してください\n" +
                        f"推奨: {suggested_address}",
                        f"{label} 範囲入力（キーボード入力専用）",
                        suggested_address,
                        Type=2  # 文字列型（セル値参照を完全回避）
                    )
                    
                    print(f"🔍 キーボード入力 戻り値: '{input_result}' (型: {type(input_result)})")
                    
                    # 文字列として処理（Type=2なので必ず文字列）
                    if isinstance(input_result, str):
                        range_str = str(input_result).strip()
                        print(f"📝 入力された文字列: '{range_str}'")
                        
                        # 空の場合は推奨範囲を使用
                        if not range_str:
                            range_str = suggested_address
                            print(f"🔧 空入力のため推奨範囲使用: '{range_str}'")
                        
                        # 先頭の = を除去（念のため）
                        if range_str.startswith('='):
                            range_str = range_str[1:]
                            print(f"🔧 '=' プレフィックス除去: '{range_str}'")
                        
                        # 正規化処理
                        range_address = self._normalize_range_string(range_str)
                        print(f"🔧 正規化結果: '{range_address}'")
                        
                        # 有効性チェック
                        if self._is_valid_range_address(range_address):
                            print(f"✅ 有効な範囲アドレス確認: '{range_address}'")
                        else:
                            print(f"⚠️ 無効な範囲のため推奨範囲使用: '{range_address}' → '{suggested_address}'")
                            range_address = suggested_address
                    else:
                        print(f"⚠️ 予期しない戻り値型のため推奨範囲使用: {type(input_result)}")
                        range_address = suggested_address
                        
                except Exception as input_error:
                    print(f"❌ キーボード入力エラー: {input_error}")
                    print(f"🔧 推奨範囲にフォールバック: {suggested_address}")
                    range_address = suggested_address
                
                # キャンセルチェック
                if range_address == False or range_address is False:
                    raise ValueError("範囲選択がキャンセルされました")
                
                # 最終的な範囲アドレス検証
                if not range_address or range_address in ['False', False, 'No.']:
                    print(f"⚠️ 無効な最終範囲アドレス: '{range_address}' → 推奨範囲使用")
                    range_address = suggested_address
                
                # もう一度"="を確実に除去（安全性向上）
                if isinstance(range_address, str) and range_address.startswith('='):
                    range_address = range_address[1:]
                    print(f"🔧 最終確認で'='除去: '{range_address}'")
                
                # 範囲オブジェクトを作成（既に range_address が決定済み）
                try:
                    selected_range = worksheet.Range(range_address)
                    print(f"✅ 範囲オブジェクト作成成功: {range_address}")
                except Exception as range_error:
                    print(f"❌ 範囲作成エラー: {range_error}")
                    print(f"🔧 推奨範囲にフォールバック: {suggested_address}")
                    range_address = suggested_address
                    selected_range = worksheet.Range(range_address)
                
                print(f"✅ 最終選択範囲: {range_address}")
                
            except Exception as e:
                print(f"❌ 範囲選択エラー: {e}")
                print(f"🔧 推奨範囲を使用します: {suggested_address}")
                range_address = suggested_address
                selected_range = worksheet.Range(range_address)
        
        print(f"📍 最終範囲: {range_address}")
        print(f"📊 サイズ: {selected_range.Rows.Count}行 x {selected_range.Columns.Count}列")
        
        # データ抽出
        print(f"📊 データ抽出中...")
        values = self._extract_values_enhanced(selected_range, range_address)
        print(f"✅ データ抽出完了: {len(values)}行 x {len(values[0]) if values else 0}列")
        
        return {
            'address': range_address,
            'values': values
        }
    
    def _is_likely_cell_value(self, text: str) -> bool:
        """文字列がセルの値である可能性が高いかを判定（=$A$1:$F$59は除外）"""
        if not text or len(text) < 2:
            return True
            
        # =$A$1:$F$59 のような形式は範囲アドレスなのでセル値ではない
        cleaned_text = str(text).strip()
        if cleaned_text.startswith('=') and ':' in cleaned_text:
            # = で始まって : が含まれる場合は範囲の可能性が高い
            range_part = cleaned_text[1:]  # = を除去
            if self._is_valid_range_address(range_part):
                return False  # 有効な範囲アドレスなのでセル値ではない
            
        # セルの値らしい特徴
        cell_value_indicators = [
            # 日本語文字が含まれる
            lambda x: any(ord(c) > 127 for c in x),
            # 長い文字列（通常の範囲指定より長い）
            lambda x: len(x) > 20,
            # 範囲指定にない文字（「」など）
            lambda x: any(c in x for c in "「」（）<>"),
            # スペースが多い
            lambda x: x.count(' ') > 2,
        ]
        
        for indicator in cell_value_indicators:
            try:
                if indicator(text):
                    return True
            except:
                continue
                
        return False
    
    def _is_valid_range_address(self, text: str) -> bool:
        """文字列が有効な範囲アドレスかどうかを判定（=$A$1:$F$59対応）"""
        if not text:
            return False
            
        # 基本的な清理
        cleaned = str(text).strip()
        if len(cleaned) < 2:
            return False
            
        # 先頭の'='を除去してから判定（マウス選択の =$A$1:$F$59 形式）
        if cleaned.startswith('='):
            cleaned = cleaned[1:]
            
        # 明らかに範囲アドレスではないパターン
        invalid_patterns = [
            # 日本語が含まれている
            lambda x: any(ord(c) > 127 for c in x),
            # 長すぎる（通常の範囲指定は30文字以内）
            lambda x: len(x) > 30,
            # 範囲指定にない特殊文字
            lambda x: any(c in x for c in "「」（）<>"),
            # スペースが多すぎる
            lambda x: x.count(' ') > 3,
        ]
        
        # 無効パターンに該当する場合はFalse
        for pattern in invalid_patterns:
            try:
                if pattern(cleaned):
                    return False
            except:
                continue
        
        # 有効な範囲アドレスのパターン
        import re
        valid_patterns = [
            # A1:B10 形式
            r'^[A-Za-z]+\d+:[A-Za-z]+\d+$',
            # A:A 形式（列全体）
            r'^[A-Za-z]+:[A-Za-z]+$',
            # 1:1 形式（行全体）
            r'^\d+:\d+$',
            # A1 形式（単一セル）
            r'^[A-Za-z]+\d+$',
            # $A$1:$B$10 形式（絶対参照）
            r'^\$?[A-Za-z]+\$?\d+:\$?[A-Za-z]+\$?\d+$',
        ]
        
        # どれか一つでもマッチすれば有効
        for pattern in valid_patterns:
            try:
                if re.match(pattern, cleaned):
                    return True
            except:
                continue
        
        return False
    
    def _manual_range_input(self, label: str, suggested_address: str) -> str:
        """手動範囲入力ダイアログ"""
        root = self._create_topmost_window()
        
        # より詳しい説明付きダイアログ
        manual_message = f"""範囲アドレスを手動で入力してください

【有効な範囲形式の例】
✅ A1:C10    (A1からC10までの範囲)
✅ B:B       (B列全体)
✅ 1:1       (1行目全体)
✅ A1        (A1セルのみ)
✅ $A$1:$C$10 (絶対参照)

【無効な例】
❌ <サービス名・会社名> セキュリティチェックシート
❌ 項目1
❌ 回答欄

推奨範囲: {suggested_address}"""
        
        try:
            from tkinter import simpledialog
            result = simpledialog.askstring(
                title=f"{label} 範囲手動入力",
                prompt=manual_message,
                initialvalue=suggested_address,
                parent=root
            )
        except:
            # simpledialogが使えない場合のフォールバック
            result = suggested_address
        
        self._safe_destroy(root)
        return result
    
    def open_excel_files(self):
        """従来の2ファイル同時オープン（後方互換性のため残す）"""
        return self.open_and_process_files_sequentially()
    
    def startup_file_selection(self):
        """起動時のファイル選択処理"""
        root = self._create_topmost_window()
        
        # 既存ファイルがある場合の選択肢を提示
        if self.excel_app.Workbooks.Count >= 2:
            existing_files = [wb.Name for wb in self.excel_app.Workbooks][:2]
            
            choice = messagebox.askyesnocancel(
                "ファイル選択オプション",
                f"📊 既に開いているExcelファイル:\n" +
                f"  1. {existing_files[0]}\n" +
                f"  2. {existing_files[1]}\n\n" +
                f"どちらを使用しますか？\n\n" +
                f"「はい」 = 既存ファイルを使用\n" +
                f"「いいえ」 = 新しいファイルを選択\n" +
                f"「キャンセル」 = プログラム終了",
                parent=root
            )
            
            if choice is None:  # キャンセル
                self._safe_destroy(root)
                print("🔚 プログラムを終了します")
                return False
            elif choice:  # はい - 既存ファイル使用
                self._safe_destroy(root)
                return self.use_existing_files()
            else:  # いいえ - 新しいファイル選択
                self._safe_destroy(root)
                return self.open_excel_files()
        
        elif self.excel_app.Workbooks.Count == 1:
            existing_file = self.excel_app.Workbooks[0].Name
            
            choice = messagebox.askyesnocancel(
                "ファイル選択オプション", 
                f"📊 既に開いているExcelファイル:\n" +
                f"  1. {existing_file}\n\n" +
                f"1つのファイルが開いています。\n" +
                f"もう1つのファイルを選択してください。\n\n" +
                f"「はい」 = 2つ目のファイルを選択\n" +
                f"「いいえ」 = 2つのファイルを新規選択\n" +
                f"「キャンセル」 = プログラム終了"
            )
            
            if choice is None:  # キャンセル
                self._safe_destroy(root)
                print("🔚 プログラムを終了します")
                return False
            elif choice:  # はい - 2つ目のファイルのみ選択
                self._safe_destroy(root)
                return self.select_second_file_only()
            else:  # いいえ - 2つとも新規選択
                self._safe_destroy(root)
                return self.open_excel_files()
        
        else:
            # 既存ファイルなし - 必ず新規選択
            messagebox.showinfo(
                "ファイル選択", 
                "📁 2つのExcelファイルを選択してください",
                parent=root
            )
            self._safe_destroy(root)
            return self.open_excel_files()
    
    def select_second_file_only(self):
        """1つ目は既存ファイル、2つ目のみ新規選択"""
        # 1つ目は既存ファイルを使用
        existing_wb = list(self.excel_app.Workbooks)[0]
        self.workbook_data['file1'] = {
            'path': existing_wb.FullName,
            'name': existing_wb.Name,
            'workbook': existing_wb
        }
        
        print(f"✅ ファイル1（既存）: {self.workbook_data['file1']['name']}")
        
        # 2つ目のファイルを選択
        root = tk.Tk()
        root.withdraw()
        
        file2_path = filedialog.askopenfilename(
            title="2つ目のExcelファイルを選択",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not file2_path:
            self._safe_destroy(root)
            print("❌ 2つ目のファイル選択がキャンセルされました")
            return False
        
        self._safe_destroy(root)
        
        try:
            workbook2 = self.excel_app.Workbooks.Open(file2_path)
            
            self.workbook_data['file2'] = {
                'path': file2_path,
                'name': Path(file2_path).name,
                'workbook': workbook2
            }
            
            print(f"✅ ファイル2を開きました: {self.workbook_data['file2']['name']}")
            return True
            
        except Exception as e:
            print(f"❌ 2つ目のファイルを開くのに失敗しました: {e}")
            return False
    
    def select_workbook_and_range(self, file_key: str, label: str) -> Dict:
        """指定されたファイルからセル範囲を選択（順次処理対応）"""
        if file_key not in self.workbook_data:
            raise ValueError(f"ファイル '{file_key}' が見つかりません")
        
        file_info = self.workbook_data[file_key]
        
        # 順次処理では既にデータが抽出済み
        if file_info.get('values') is not None:
            print(f"📄 {label}: {file_info['name']} (データ使用済み)")
            print(f"📊 シート: {file_info.get('worksheet_name', 'Unknown')}")
            print(f"📍 範囲: {file_info['address']}")
            print(f"📊 サイズ: {len(file_info['values'])}行 x {len(file_info['values'][0]) if file_info['values'] else 0}列")
            
            # 従来の形式に合わせて返す
            return {
                'workbook': type('MockWorkbook', (), {'Name': file_info['name']})(),
                'worksheet': type('MockWorksheet', (), {'Name': file_info.get('worksheet_name', 'Unknown')})(),
                'range': None,  # 順次処理では不要
                'address': file_info['address'],
                'values': file_info['values']
            }
        
        # 従来の処理（既に開いているファイル用）
        selected_wb = file_info['workbook']
        print(f"📄 {label}: {file_info['name']}")
        
        # シート選択
        worksheet = self.select_worksheet(selected_wb, label)
        
        # 自動範囲提案
        try:
            used_range = worksheet.UsedRange
            if used_range:
                suggested_address = used_range.Address
                print(f"📊 推奨範囲: {suggested_address}")
            else:
                suggested_address = "A1:H50"
        except:
            suggested_address = "A1:H50"
        
        # 範囲選択
        root = self._create_topmost_window()
        
        # 方法選択ダイアログ
        self._safe_destroy(root)
        choice = self._show_custom_yesnocancel(
            f"📊 {label} - 範囲選択方法",
            f"📄 ファイル: {file_info['name']}\n" +
            f"📊 推奨範囲: {suggested_address}\n\n" +
            f"範囲選択方法を選択してください:\n\n" +
            f"「はい」 = 推奨範囲を使用\n" +
            f"「いいえ」 = マウスで範囲選択\n" +
            f"「キャンセル」 = 処理中止"
        )
        
        if choice is None:  # キャンセル
            raise ValueError("範囲選択がキャンセルされました")
        
        elif choice:  # はい - 推奨範囲使用
            range_address = suggested_address
            selected_range = worksheet.Range(range_address)
            print(f"✅ 推奨範囲を使用: {range_address}")
            
        else:  # いいえ - マウス選択
            
            # より安全なInputBox使用
            try:
                print(f"🖱️ Excelで範囲を選択してください...")
                
                # Excelを前面に表示
                self.excel_app.Visible = True
                worksheet.Activate()
                
                # InputBoxで範囲選択（エラーハンドリング強化）
                selected_range = self.excel_app.InputBox(
                    f"{label}の範囲を選択してください\\n\\n例: A1:C10, B2:F20",
                    f"{label} 範囲選択",
                    suggested_address,  # デフォルト値
                    Type=8  # Range型
                )
                
                if selected_range == False or selected_range is False:
                    raise ValueError("範囲選択がキャンセルされました")
                
                # 範囲情報を取得
                if hasattr(selected_range, 'Address'):
                    range_address = selected_range.Address
                else:
                    # 文字列で返された場合 - 正規化処理
                    original_input = str(selected_range)
                    range_address = self._normalize_range_string(original_input)
                    
                    # 単一の値や無効な範囲の場合は推奨範囲を使用
                    if self._is_invalid_range(range_address):
                        print(f"⚠️ 無効な範囲入力: '{original_input}' → '{range_address}'")
                        print(f"🔧 推奨範囲を使用します: {suggested_address}")
                        range_address = suggested_address
                    
                    try:
                        selected_range = worksheet.Range(range_address)
                    except Exception as e:
                        print(f"❌ 範囲オブジェクト作成エラー: {e}")
                        print(f"🔧 正規化された範囲: '{range_address}'")
                        # より安全な範囲作成を試行
                        selected_range = self._create_safe_range(worksheet, range_address)
                    
                print(f"✅ 選択範囲: {range_address}")
                
            except Exception as e:
                print(f"❌ 範囲選択エラー: {e}")
                # フォールバック: 手動入力
                root = tk.Tk()
                root.withdraw()
                
                manual_range = tk.simpledialog.askstring(
                    "範囲入力",
                    f"範囲選択でエラーが発生しました。\\n" +
                    f"範囲を手動で入力してください:\\n\\n" +
                    f"例: A1:C10, B2:F20\\n" +
                    f"推奨: {suggested_address}",
                    initialvalue=suggested_address
                ) if simpledialog else None
                
                if not manual_range:
                    self._safe_destroy(root)
                    raise ValueError("範囲入力がキャンセルされました")
                
                range_address = self._normalize_range_string(manual_range)
                selected_range = worksheet.Range(range_address)
                print(f"✅ 手動入力範囲: {range_address}")
                self._safe_destroy(root)
        
        self._safe_destroy(root)
        
        print(f"📍 選択された範囲: {range_address}")
        print(f"📊 サイズ: {selected_range.Rows.Count}行 x {selected_range.Columns.Count}列")
        
        self._safe_destroy(root)
        
        # データ抽出の進捗表示
        print(f"📊 データ抽出中...")
        values = self._extract_values_enhanced(selected_range, range_address)
        print(f"✅ データ抽出完了: {len(values)}行 x {len(values[0]) if values else 0}列")
        
        return {
            'workbook': selected_wb,
            'worksheet': worksheet,
            'range': selected_range,
            'address': range_address,
            'values': values
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
    
    def _normalize_range_string(self, range_str: str) -> str:
        """範囲文字列を正規化（=$A$1:$F$59 → A1:F59）"""
        if not range_str:
            return range_str
            
        # 基本的なクリーンアップ
        normalized = str(range_str).strip()
        
        # 先頭の"="を除去（マウス選択時の =$A$1:$F$59 形式に対応）
        if normalized.startswith('='):
            normalized = normalized[1:]
            print(f"🔧 '=' プレフィックス除去: '{range_str}' → '{normalized}'")
        
        # シート名を除去（例: Sheet1!A1:C10 → A1:C10）
        # 複雑なシート名（引用符、日本語、特殊文字を含む）に対応
        if '!' in normalized:
            # 最後の!で分割（シート名に!が含まれる可能性を考慮）
            last_exclamation = normalized.rfind('!')
            sheet_part = normalized[:last_exclamation]
            range_part = normalized[last_exclamation + 1:]
            
            # シート名から引用符を除去
            if sheet_part.startswith("'") and sheet_part.endswith("'"):
                sheet_part = sheet_part[1:-1]
            
            normalized = range_part
            print(f"📄 シート名除去: '{range_str}' → シート部分: '{sheet_part}', 範囲部分: '{range_part}'")
        
        # $記号（絶対参照）を除去
        normalized = normalized.replace('$', '')
        
        print(f"🔧 範囲正規化: '{range_str}' → '{normalized}'")
        
        return normalized
    
    def _extract_values_enhanced(self, range_obj, range_address: str) -> List[List[str]]:
        """拡張値抽出 - 列・行・シート全体指定に対応"""
        values = []
        
        # シート全体指定（ : のみ）
        if range_address.strip() == ':':
            print(f"📋 シート全体指定を検出: {range_address}")
            return self._extract_sheet_all(range_obj)
        
        # 範囲のタイプを判定
        if ':' in range_address:
            parts = range_address.split(':')
            start_part = parts[0].strip()
            end_part = parts[1].strip()
            
            # 空の部分がある場合（例: :C10, A1:）
            if not start_part or not end_part:
                print(f"📋 部分的なシート指定を検出: {range_address}")
                return self._extract_partial_sheet(range_obj, start_part, end_part)
            
            # 列全体指定（例: A:C, B:B）
            elif start_part.isalpha() and end_part.isalpha():
                print(f"📋 列全体指定を検出: {range_address}")
                return self._extract_column_range(range_obj, start_part, end_part)
            
            # 行全体指定（例: 1:5, 3:3）
            elif start_part.isdigit() and end_part.isdigit():
                print(f"📋 行全体指定を検出: {range_address}")
                return self._extract_row_range(range_obj, int(start_part), int(end_part))
        
        # 単一列指定（例: A, B, AA）
        elif range_address.isalpha():
            print(f"📋 単一列指定を検出: {range_address}")
            return self._extract_column_range(range_obj, range_address, range_address)
        
        # 単一行指定（例: 1, 5, 100）
        elif range_address.isdigit():
            print(f"📋 単一行指定を検出: {range_address}")
            return self._extract_row_range(range_obj, int(range_address), int(range_address))
        
        # 通常の範囲選択（A1:C10など）
        return self._extract_normal_range(range_obj)
    
    def _extract_column_range(self, range_obj, start_col: str, end_col: str) -> List[List[str]]:
        """列範囲からデータを抽出（使用範囲内のみ）"""
        worksheet = range_obj.Worksheet
        
        # 使用範囲を取得して行数を制限
        try:
            used_range = worksheet.UsedRange
            if used_range:
                last_row = used_range.Row + used_range.Rows.Count - 1
                # 最大1000行に制限（パフォーマンス対策）
                last_row = min(last_row, 1000)
            else:
                last_row = 100  # デフォルト
        except:
            last_row = 100
        
        # 列番号を数値に変換
        start_col_num = self._column_letter_to_number(start_col)
        end_col_num = self._column_letter_to_number(end_col)
        
        print(f"📊 列抽出: {start_col}({start_col_num}) - {end_col}({end_col_num}), 行数: 1-{last_row}")
        
        values = []
        for row in range(1, last_row + 1):
            row_values = []
            for col_num in range(start_col_num, end_col_num + 1):
                try:
                    cell_value = worksheet.Cells(row, col_num).Value
                    row_values.append(str(cell_value or ""))
                except:
                    row_values.append("")
            values.append(row_values)
        
        return values
    
    def _extract_row_range(self, range_obj, start_row: int, end_row: int) -> List[List[str]]:
        """行範囲からデータを抽出（使用範囲内のみ）"""
        worksheet = range_obj.Worksheet
        
        # 巨大範囲の制限（パフォーマンス保護）
        MAX_ROWS = 10000  # 最大10000行
        if end_row - start_row + 1 > MAX_ROWS:
            print(f"⚠️ 巨大範囲検出: {start_row}:{end_row} ({end_row - start_row + 1}行)")
            print(f"📊 パフォーマンス保護により使用範囲に制限します")
            
            # 使用範囲に基づいて制限
            try:
                used_range = worksheet.UsedRange
                if used_range:
                    used_start_row = used_range.Row
                    used_end_row = used_start_row + used_range.Rows.Count - 1
                    
                    # 指定範囲と使用範囲の交差部分を使用
                    actual_start_row = max(start_row, used_start_row)
                    actual_end_row = min(end_row, used_end_row)
                    
                    # さらに最大行数で制限
                    if actual_end_row - actual_start_row + 1 > MAX_ROWS:
                        actual_end_row = actual_start_row + MAX_ROWS - 1
                    
                    print(f"🔧 制限後範囲: {actual_start_row}:{actual_end_row}")
                    start_row, end_row = actual_start_row, actual_end_row
                else:
                    # 使用範囲が見つからない場合はデフォルト
                    end_row = min(start_row + MAX_ROWS - 1, 1000)
                    print(f"🔧 デフォルト制限: {start_row}:{end_row}")
            except Exception as e:
                end_row = min(start_row + MAX_ROWS - 1, 1000)
                print(f"🔧 エラー時制限: {start_row}:{end_row} (エラー: {e})")
        
        # 使用範囲を取得して列数を制限
        try:
            used_range = worksheet.UsedRange
            if used_range:
                last_col = used_range.Column + used_range.Columns.Count - 1
                # 最大100列に制限（パフォーマンス対策）
                last_col = min(last_col, 100)
            else:
                last_col = 26  # A-Z
        except:
            last_col = 26
        
        print(f"📊 行抽出: {start_row} - {end_row}, 列数: 1-{last_col}")
        
        values = []
        for row in range(start_row, end_row + 1):
            row_values = []
            for col in range(1, last_col + 1):
                try:
                    cell_value = worksheet.Cells(row, col).Value
                    row_values.append(str(cell_value or ""))
                except:
                    row_values.append("")
            values.append(row_values)
        
        return values
    
    def _extract_normal_range(self, range_obj) -> List[List[str]]:
        """通常の範囲からデータを抽出"""
        values = []
        
        if range_obj.Rows.Count == 1 and range_obj.Columns.Count == 1:
            # 単一セル
            values = [[str(range_obj.Value or "")]]
        elif range_obj.Rows.Count == 1:
            # 単一行
            row_values = []
            for col in range(1, range_obj.Columns.Count + 1):
                cell_value = range_obj.Cells(1, col).Value
                row_values.append(str(cell_value or ""))
            values = [row_values]
        elif range_obj.Columns.Count == 1:
            # 単一列
            for row in range(1, range_obj.Rows.Count + 1):
                cell_value = range_obj.Cells(row, 1).Value
                values.append([str(cell_value or "")])
        else:
            # 複数行列
            for row in range(1, range_obj.Rows.Count + 1):
                row_values = []
                for col in range(1, range_obj.Columns.Count + 1):
                    cell_value = range_obj.Cells(row, col).Value
                    row_values.append(str(cell_value or ""))
                values.append(row_values)
        
        return values
    
    def _column_letter_to_number(self, col_letter: str) -> int:
        """列文字を数値に変換 (A=1, B=2, ..., AA=27)"""
        col_letter = col_letter.upper()
        result = 0
        for char in col_letter:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
    
    def _extract_sheet_all(self, range_obj) -> List[List[str]]:
        """シート全体からデータを抽出（使用範囲のみ）"""
        worksheet = range_obj.Worksheet
        
        try:
            used_range = worksheet.UsedRange
            if not used_range:
                print("📊 使用範囲が見つかりません。デフォルト範囲 A1:Z100 を使用")
                return self._extract_default_range(worksheet)
            
            print(f"📊 シート全体抽出: 使用範囲 {used_range.Address}")
            
            # 使用範囲をそのまま抽出
            return self._extract_normal_range(used_range)
            
        except Exception as e:
            print(f"❌ シート全体抽出エラー: {e}")
            return self._extract_default_range(worksheet)
    
    def _extract_partial_sheet(self, range_obj, start_part: str, end_part: str) -> List[List[str]]:
        """部分的なシート指定を処理（例: :C10, A1:）"""
        worksheet = range_obj.Worksheet
        
        try:
            used_range = worksheet.UsedRange
            if not used_range:
                return self._extract_default_range(worksheet)
            
            # 使用範囲の境界を取得
            used_start_row = used_range.Row
            used_start_col = used_range.Column
            used_end_row = used_start_row + used_range.Rows.Count - 1
            used_end_col = used_start_col + used_range.Columns.Count - 1
            
            if not start_part:  # :C10 の場合
                print(f"📊 部分指定（開始なし）: 使用範囲開始から {end_part} まで")
                if end_part.isalpha():  # 列指定
                    end_col_num = self._column_letter_to_number(end_part)
                    end_col_num = min(end_col_num, used_end_col)
                    return self._extract_range_by_coords(worksheet, used_start_row, used_start_col, used_end_row, end_col_num)
                else:  # セル指定（例: :C10）
                    # end_partをパースしてセル座標を取得
                    end_range = worksheet.Range(end_part)
                    return self._extract_range_by_coords(worksheet, used_start_row, used_start_col, end_range.Row, end_range.Column)
            
            elif not end_part:  # A1: の場合
                print(f"📊 部分指定（終了なし）: {start_part} から使用範囲終了まで")
                if start_part.isalpha():  # 列指定
                    start_col_num = self._column_letter_to_number(start_part)
                    start_col_num = max(start_col_num, used_start_col)
                    return self._extract_range_by_coords(worksheet, used_start_row, start_col_num, used_end_row, used_end_col)
                else:  # セル指定（例: A1:）
                    start_range = worksheet.Range(start_part)
                    return self._extract_range_by_coords(worksheet, start_range.Row, start_range.Column, used_end_row, used_end_col)
            
        except Exception as e:
            print(f"❌ 部分シート抽出エラー: {e}")
            return self._extract_default_range(worksheet)
    
    def _extract_range_by_coords(self, worksheet, start_row: int, start_col: int, end_row: int, end_col: int) -> List[List[str]]:
        """座標指定でデータを抽出"""
        values = []
        total_rows = end_row - start_row + 1
        total_cols = end_col - start_col + 1
        total_cells = total_rows * total_cols
        
        print(f"📊 座標抽出: R{start_row}C{start_col}:R{end_row}C{end_col}")
        print(f"📊 抽出対象: {total_rows}行 x {total_cols}列 = {total_cells:,}セル")
        
        # 大量データの場合は進捗表示
        show_progress = total_rows > 500
        
        for row_idx, row in enumerate(range(start_row, end_row + 1)):
            if show_progress and row_idx % 100 == 0 and row_idx > 0:
                progress = (row_idx / total_rows) * 100
                print(f"⏳ 抽出進捗: {row_idx}/{total_rows}行 ({progress:.1f}%)")
                
            row_values = []
            for col in range(start_col, end_col + 1):
                try:
                    cell_value = worksheet.Cells(row, col).Value
                    row_values.append(str(cell_value or ""))
                except:
                    row_values.append("")
            values.append(row_values)
        
        if show_progress:
            print(f"✅ 抽出完了: {len(values)}行のデータを取得")
        
        return values
    
    def select_worksheet(self, workbook, label: str):
        """ワークブックからシートを選択"""
        sheets = list(workbook.Worksheets)
        
        if len(sheets) == 1:
            print(f"📄 単一シート: {sheets[0].Name}")
            return sheets[0]
        
        # 複数シートの場合は選択ダイアログ
        root = self._create_topmost_window()
        
        # シート一覧を表示
        sheet_names = [sheet.Name for sheet in sheets]
        sheet_list = "\n".join([f"  {i+1}. {name}" for i, name in enumerate(sheet_names)])
        
        # アクティブシートを推奨
        active_sheet = workbook.ActiveSheet
        active_index = next((i for i, sheet in enumerate(sheets) if sheet.Name == active_sheet.Name), 0)
        
        self._safe_destroy(root)
        choice = self._show_custom_yesnocancel(
            f"📚 {label} - シート選択",
            f"ワークブックに複数のシートがあります:\n\n{sheet_list}\n\n" +
            f"現在のアクティブシート: {active_sheet.Name}\n\n" +
            f"どのシートを使用しますか？\n\n" +
            f"「はい」 = アクティブシート ({active_sheet.Name}) を使用\n" +
            f"「いいえ」 = シートを手動選択\n" +
            f"「キャンセル」 = 処理中止"
        )
        
        if choice is None:  # キャンセル
            raise ValueError("シート選択がキャンセルされました")
        
        elif choice:  # はい - アクティブシートを使用
            print(f"✅ アクティブシート選択: {active_sheet.Name}")
            return active_sheet
        
        else:  # いいえ - 手動選択
            return self.manual_sheet_selection(sheets, label)
    
    def manual_sheet_selection(self, sheets, label: str):
        """手動でシートを選択"""
        root = self._create_topmost_window()
        
        # シート選択番号を入力
        sheet_names = [sheet.Name for sheet in sheets]
        sheet_options = "\n".join([f"{i+1}: {name}" for i, name in enumerate(sheet_names)])
        
        if simpledialog:
            choice_str = simpledialog.askstring(
                "シート選択",
                f"{label}\n\n利用可能なシート:\n{sheet_options}\n\n" +
                f"シート番号を入力してください (1-{len(sheets)}):",
                parent=root
            )
        else:
            self._safe_destroy(root)
            # simpledialogが使用できない場合はアクティブシートを使用
            print(f"⚠️ 手動選択機能が利用できません。アクティブシートを使用します")
            return sheets[0] if sheets else None
        
        if not choice_str:
            self._safe_destroy(root)
            raise ValueError("シート選択がキャンセルされました")
        
        try:
            choice_num = int(choice_str.strip())
            if 1 <= choice_num <= len(sheets):
                selected_sheet = sheets[choice_num - 1]
                print(f"✅ 手動シート選択: {selected_sheet.Name}")
                self._safe_destroy(root)
                return selected_sheet
            else:
                self._safe_destroy(root)
                raise ValueError(f"無効なシート番号: {choice_num} (1-{len(sheets)}の範囲で入力)")
        
        except ValueError as e:
            self._safe_destroy(root)
            print(f"❌ シート選択エラー: {e}")
            # エラー時はアクティブシートを使用
            print(f"🔧 アクティブシートを使用します: {sheets[0].Name}")
            return sheets[0] if sheets else None
    
    def _extract_default_range(self, worksheet) -> List[List[str]]:
        """デフォルト範囲（A1:Z100）を抽出"""
        print("📊 デフォルト範囲抽出: A1:Z100")
        return self._extract_range_by_coords(worksheet, 1, 1, 100, 26)
    
    def _create_safe_range(self, worksheet, range_address: str):
        """安全な範囲オブジェクト作成"""
        try:
            print(f"🔧 安全範囲作成を試行: '{range_address}'")
            
            # 巨大範囲や特殊範囲を使用範囲に制限
            if range_address in ['1:1048576', ':'] or '1048576' in range_address:
                print("📊 巨大/全体範囲を使用範囲に制限")
                used_range = worksheet.UsedRange
                if used_range:
                    return used_range
                else:
                    return worksheet.Range("A1:Z100")  # デフォルト範囲
            
            # 行全体指定の場合
            if ':' in range_address and range_address.replace(':', '').isdigit():
                parts = range_address.split(':')
                start_row = int(parts[0]) if parts[0] else 1
                end_row = int(parts[1]) if parts[1] else start_row
                
                # 巨大行範囲を制限
                if end_row > 10000:
                    end_row = min(10000, worksheet.UsedRange.Row + worksheet.UsedRange.Rows.Count - 1 if worksheet.UsedRange else 1000)
                
                return worksheet.Range(f"{start_row}:{end_row}")
            
            # 通常範囲として再試行
            return worksheet.Range(range_address)
            
        except Exception as e:
            print(f"❌ 安全範囲作成も失敗: {e}")
            print("🔧 デフォルト範囲 A1:Z100 を使用")
            return worksheet.Range("A1:Z100")
    
    def _is_invalid_range(self, range_address: str) -> bool:
        """無効な範囲かどうかを判定"""
        if not range_address:
            return True
        
        # 単一の文字列値（範囲ではない）をチェック
        invalid_patterns = [
            # 数値のみ（例: "123"）
            lambda x: x.isdigit() and len(x) > 2,
            # 日本語や文字列（例: "No.", "データ", "項目"）  
            lambda x: any(ord(c) > 127 for c in x),  # 非ASCII文字
            # 記号のみ（例: ".", "-", "_"）
            lambda x: all(c in ".-_()[]{}!@#$%^&*+=|\\/<>?~`" for c in x),
            # 長い文字列（範囲ではなく値）
            lambda x: len(x) > 50,
            # スペースを含む文字列
            lambda x: ' ' in x and ':' not in x,
        ]
        
        for pattern in invalid_patterns:
            try:
                if pattern(range_address):
                    return True
            except:
                continue
        
        # 有効な範囲パターンかチェック
        valid_patterns = [
            # A1形式（例: A1, B2, AA10）
            r'^[A-Z]+[0-9]+$',
            # 範囲形式（例: A1:C10, B:D, 1:5）
            r'^[A-Z]*[0-9]*:[A-Z]*[0-9]*$',
            # 列のみ（例: A, B, AA）
            r'^[A-Z]+$',
            # 行のみ（例: 1, 10, 100）
            r'^[0-9]+$',
            # シート全体
            r'^:$'
        ]
        
        import re
        for pattern in valid_patterns:
            if re.match(pattern, range_address):
                return False
        
        return True
    
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
        import time
        start_time = time.time()
        
        print("\\n🔍 範囲比較を開始...")
        
        values1 = range1_data['values']
        values2 = range2_data['values']
        
        max_rows = max(len(values1), len(values2))
        max_cols = max(
            max(len(row) for row in values1) if values1 else 0,
            max(len(row) for row in values2) if values2 else 0
        )
        
        total_cells = max_rows * max_cols
        print(f"📊 比較対象: {max_rows}行 x {max_cols}列 = {total_cells:,}セル")
        
        # 大量データの場合は詳細進捗を表示
        show_progress = total_cells > 10000
        if show_progress:
            print("⏳ 大量データのため、進捗を表示します...")
        
        results = []
        processed_cells = 0
        
        for row in range(max_rows):
            # 進捗表示（100行ごと）
            if show_progress and row % 100 == 0 and row > 0:
                progress = (processed_cells / total_cells) * 100
                elapsed_time = time.time() - start_time
                estimated_total = elapsed_time / progress * 100 if progress > 0 else 0
                remaining_time = estimated_total - elapsed_time
                print(f"⏳ 進捗: {row}/{max_rows}行 ({progress:.1f}%) | 経過: {elapsed_time:.1f}秒 | 残り推定: {remaining_time:.1f}秒")
            
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
                processed_cells += 1
        
        # 比較完了
        total_time = time.time() - start_time
        speed = processed_cells / total_time if total_time > 0 else 0
        print(f"✅ 比較完了: {processed_cells:,}セル処理済み | 処理時間: {total_time:.2f}秒 | 処理速度: {speed:.0f}セル/秒")
        return results
    
    def display_results(self, results: List[Dict], range1_data: Dict, range2_data: Dict):
        """比較結果を表示"""
        print("\\n" + "="*80)
        print("📊 比較結果")
        print("="*80)
        
        print(f"📄 ファイル1: {range1_data['workbook'].Name}")
        print(f"📊 シート1: {range1_data['worksheet'].Name}")
        print(f"📍 範囲1: {range1_data['address']}")
        print(f"📄 ファイル2: {range2_data['workbook'].Name}")
        print(f"📊 シート2: {range2_data['worksheet'].Name}")
        print(f"📍 範囲2: {range2_data['address']}")
        print()
        
        # 統計情報
        total_cells = len(results)
        perfect_match = len([r for r in results if r['similarity'] == 100.0])
        high_similarity = len([r for r in results if 80 <= r['similarity'] < 100])
        medium_similarity = len([r for r in results if 50 <= r['similarity'] < 80])
        low_similarity = len([r for r in results if r['similarity'] < 50])
        
        stats = {
            'total_cells': total_cells,
            'perfect_match': perfect_match,
            'high_similarity': high_similarity,
            'medium_similarity': medium_similarity,
            'low_similarity': low_similarity
        }
        
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
        
        # 詳細HTMLレポート作成の提案
        self._create_html_report(results, range1_data, range2_data, stats)
    
    def _create_html_report(self, results: List[Dict], range1_data: Dict, range2_data: Dict, stats: Dict):
        """詳細HTMLレポート作成"""
        try:
            # レポート作成確認
            root = self._create_topmost_window()
            create_report = messagebox.askyesno(
                "📄 HTMLレポート作成",
                "比較結果を見やすいHTMLレポートとして保存しますか？\n\n" +
                "レポートには以下が含まれます:\n" +
                "• 比較サマリー（表形式）\n" +
                "• 詳細な相違点一覧（色分け表示）\n" +
                "• 統計情報（グラフィカル表示）\n" +
                "• 完全一致データ（オプション）\n\n" +
                "ブラウザで見やすく表示されます！",
                parent=root
            )
            self._safe_destroy(root)
            
            if not create_report:
                return
            
            # 保存場所選択
            from tkinter import filedialog
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Excel比較レポート_{timestamp}.html"
            
            root = self._create_topmost_window()
            report_path = filedialog.asksaveasfilename(
                title="HTMLレポート保存先",
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                initialfile=default_filename,
                parent=root
            )
            self._safe_destroy(root)
            
            if not report_path:
                return
            
            print(f"\n🌐 HTMLレポートを作成中: {Path(report_path).name}")
            
            # HTMLレポート内容作成
            html_content = self._generate_html_report_content(results, range1_data, range2_data, stats)
            
            # ファイル書き込み
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTMLレポート作成完了: {report_path}")
            
            # ファイル確認の提案
            root = self._create_topmost_window()
            open_file = messagebox.askyesno(
                "📊 レポート作成完了",
                f"見やすいHTMLレポートを作成しました！\n\n"
                f"保存先: {report_path}\n\n"
                f"ブラウザで開いて確認しますか？",
                parent=root
            )
            self._safe_destroy(root)
            
            if open_file:
                try:
                    import os
                    os.startfile(report_path)  # Windows
                except:
                    try:
                        import subprocess
                        subprocess.run(['open', report_path])  # Mac
                    except:
                        try:
                            import webbrowser
                            webbrowser.open(report_path)  # Cross-platform
                        except:
                            print(f"ℹ️ 手動でファイルを開いてください: {report_path}")
            
        except Exception as report_error:
            print(f"❌ HTMLレポート作成エラー: {report_error}")
    
    def _generate_html_report_content(self, results: List[Dict], range1_data: Dict, range2_data: Dict, stats: Dict) -> str:
        """HTMLレポートの内容を生成（シンプル版）"""
        from datetime import datetime
        
        # データ準備
        differences = [r for r in results if r['similarity'] < 100.0]
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 統計データ
        total_cells = stats['total_cells']
        perfect_count = stats['perfect_match']
        perfect_percent = (perfect_count / total_cells * 100) if total_cells > 0 else 0
        high_count = stats['high_similarity']
        high_percent = (high_count / total_cells * 100) if total_cells > 0 else 0
        medium_count = stats['medium_similarity']
        medium_percent = (medium_count / total_cells * 100) if total_cells > 0 else 0
        low_count = stats['low_similarity']
        low_percent = (low_count / total_cells * 100) if total_cells > 0 else 0
        
        # HTMLファイル内容を構築
        html_parts = []
        
        # HTML開始
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="ja">')
        html_parts.append('<head>')
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('    <title>Excel範囲比較レポート</title>')
        html_parts.append('    <style>')
        html_parts.append('        body { font-family: "Segoe UI", Arial, sans-serif; margin: 20px; background: #f5f5f5; }')
        html_parts.append('        .container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }')
        html_parts.append('        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }')
        html_parts.append('        .header h1 { margin: 0; font-size: 2.2em; }')
        html_parts.append('        .content { padding: 30px; }')
        html_parts.append('        .section { margin-bottom: 30px; }')
        html_parts.append('        .section h2 { color: #4f46e5; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }')
        html_parts.append('        .file-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }')
        html_parts.append('        .file-card { background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #4f46e5; }')
        html_parts.append('        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }')
        html_parts.append('        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; border-top: 4px solid; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
        html_parts.append('        .stat-card.perfect { border-top-color: #10b981; }')
        html_parts.append('        .stat-card.high { border-top-color: #f59e0b; }')
        html_parts.append('        .stat-card.medium { border-top-color: #3b82f6; }')
        html_parts.append('        .stat-card.low { border-top-color: #ef4444; }')
        html_parts.append('        .stat-number { font-size: 1.8em; font-weight: bold; margin-bottom: 5px; }')
        html_parts.append('        .table-container { max-height: 600px; overflow-y: auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
        html_parts.append('        .table { width: 100%; border-collapse: collapse; margin-top: 15px; }')
        html_parts.append('        .table th { background: #4f46e5; color: white; padding: 12px; text-align: left; position: sticky; top: 0; z-index: 10; }')
        html_parts.append('        .table td { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }')
        html_parts.append('        .table tr:nth-child(even) { background: #f9fafb; }')
        html_parts.append('        .table tr:hover { background-color: #e5e7eb; }')
        html_parts.append('        .similarity-high { background: #fef3c7 !important; }')
        html_parts.append('        .similarity-medium { background: #dbeafe !important; }')
        html_parts.append('        .similarity-low { background: #fecaca !important; }')
        html_parts.append('        .no-diff { text-align: center; padding: 40px; background: #f0fdf4; border-radius: 8px; border: 2px solid #10b981; }')
        html_parts.append('        .footer { background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }')
        html_parts.append('    </style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('    <div class="container">')
        
        # ヘッダー
        html_parts.append('        <div class="header">')
        html_parts.append('            <h1>📊 Excel範囲比較レポート</h1>')
        html_parts.append(f'            <div>作成日時: {timestamp}</div>')
        html_parts.append('        </div>')
        
        html_parts.append('        <div class="content">')
        
        # ファイル情報
        html_parts.append('            <div class="section">')
        html_parts.append('                <h2>📁 比較対象ファイル</h2>')
        html_parts.append('                <div class="file-grid">')
        html_parts.append('                    <div class="file-card">')
        html_parts.append('                        <h3>📄 ファイル1</h3>')
        html_parts.append(f'                        <p><strong>ファイル名:</strong> {range1_data.get("file_name", "不明")}</p>')
        html_parts.append(f'                        <p><strong>シート:</strong> {range1_data.get("worksheet_name", "不明")}</p>')
        html_parts.append(f'                        <p><strong>範囲:</strong> {range1_data["address"]}</p>')
        size1 = f"{len(range1_data['values'])}行 x {len(range1_data['values'][0]) if range1_data['values'] else 0}列"
        html_parts.append(f'                        <p><strong>サイズ:</strong> {size1}</p>')
        html_parts.append('                    </div>')
        html_parts.append('                    <div class="file-card">')
        html_parts.append('                        <h3>📄 ファイル2</h3>')
        html_parts.append(f'                        <p><strong>ファイル名:</strong> {range2_data.get("file_name", "不明")}</p>')
        html_parts.append(f'                        <p><strong>シート:</strong> {range2_data.get("worksheet_name", "不明")}</p>')
        html_parts.append(f'                        <p><strong>範囲:</strong> {range2_data["address"]}</p>')
        size2 = f"{len(range2_data['values'])}行 x {len(range2_data['values'][0]) if range2_data['values'] else 0}列"
        html_parts.append(f'                        <p><strong>サイズ:</strong> {size2}</p>')
        html_parts.append('                    </div>')
        html_parts.append('                </div>')
        html_parts.append('            </div>')
        
        # 統計情報
        html_parts.append('            <div class="section">')
        html_parts.append('                <h2>📈 比較結果統計</h2>')
        html_parts.append('                <div class="stats-grid">')
        html_parts.append('                    <div class="stat-card perfect">')
        html_parts.append(f'                        <div class="stat-number">{perfect_count:,}</div>')
        html_parts.append(f'                        <div>完全一致 ({perfect_percent:.1f}%)</div>')
        html_parts.append('                    </div>')
        html_parts.append('                    <div class="stat-card high">')
        html_parts.append(f'                        <div class="stat-number">{high_count:,}</div>')
        html_parts.append(f'                        <div>高類似度 ({high_percent:.1f}%)</div>')
        html_parts.append('                    </div>')
        html_parts.append('                    <div class="stat-card medium">')
        html_parts.append(f'                        <div class="stat-number">{medium_count:,}</div>')
        html_parts.append(f'                        <div>中類似度 ({medium_percent:.1f}%)</div>')
        html_parts.append('                    </div>')
        html_parts.append('                    <div class="stat-card low">')
        html_parts.append(f'                        <div class="stat-number">{low_count:,}</div>')
        html_parts.append(f'                        <div>相違 ({low_percent:.1f}%)</div>')
        html_parts.append('                    </div>')
        html_parts.append('                </div>')
        html_parts.append(f'                <p style="text-align: center; margin-top: 20px;"><strong>総セル数: {total_cells:,}件</strong></p>')
        html_parts.append('            </div>')
        
        # 相違点詳細
        html_parts.append('            <div class="section">')
        if differences:
            html_parts.append(f'                <h2>🔍 相違点詳細 ({len(differences)}件)</h2>')
            html_parts.append('                <div class="table-container">')
            html_parts.append('                    <table class="table">')
            html_parts.append('                        <thead>')
            html_parts.append('                            <tr>')
            html_parts.append('                                <th style="width: 60px;">#</th>')
            html_parts.append('                                <th style="width: 100px;">位置</th>')
            html_parts.append('                                <th style="width: 80px;">類似度</th>')
            html_parts.append('                                <th style="width: 40%;">ファイル1の値</th>')
            html_parts.append('                                <th style="width: 40%;">ファイル2の値</th>')
            html_parts.append('                            </tr>')
            html_parts.append('                        </thead>')
            html_parts.append('                        <tbody>')
            
            # すべての相違点を出力（制限なし）
            print(f"📝 HTMLレポート: {len(differences)}件の相違点を全て出力中...")
            
            for i, diff in enumerate(differences, 1):  # 全件出力
                similarity = diff['similarity']
                if similarity >= 80:
                    row_class = 'similarity-high'
                elif similarity >= 50:
                    row_class = 'similarity-medium'
                else:
                    row_class = 'similarity-low'
                
                # HTMLエスケープ処理
                value1 = str(diff['value1']).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                value2 = str(diff['value2']).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                
                # 長いテキストは省略表示（ツールチップで全文表示）
                display_value1 = value1[:100] + ('...' if len(value1) > 100 else '')
                display_value2 = value2[:100] + ('...' if len(value2) > 100 else '')
                
                html_parts.append(f'                        <tr class="{row_class}">')
                html_parts.append(f'                            <td>{i}</td>')
                html_parts.append(f'                            <td>{diff["position"]}</td>')
                html_parts.append(f'                            <td>{similarity:.1f}%</td>')
                html_parts.append(f'                            <td title="{value1}">{display_value1}</td>')
                html_parts.append(f'                            <td title="{value2}">{display_value2}</td>')
                html_parts.append('                        </tr>')
                
                # 進捗表示（1000件ごと）
                if i % 1000 == 0:
                    print(f"  ... {i}件 / {len(differences)}件 処理完了")
            
            print(f"✅ HTMLレポート: 全{len(differences)}件の相違点出力完了")
            
            html_parts.append('                    </tbody>')
            html_parts.append('                </table>')
        else:
            html_parts.append('                <div class="no-diff">')
            html_parts.append('                    <div style="font-size: 3em;">✅</div>')
            html_parts.append('                    <h2 style="color: #059669; margin: 10px 0;">完全一致！</h2>')
            html_parts.append('                    <p style="color: #047857;">すべてのセルが完全に一致しています</p>')
            html_parts.append('                </div>')
        html_parts.append('            </div>')
        
        html_parts.append('        </div>')
        
        # フッター
        html_parts.append('        <div class="footer">')
        html_parts.append('            <p>📝 生成プログラム: シンプルExcel範囲比較プログラム</p>')
        html_parts.append('            <p>🕐 レポート生成完了</p>')
        html_parts.append('        </div>')
        
        html_parts.append('    </div>')
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def create_excel_report(self, results: List[Dict], range1_data: Dict, range2_data: Dict, stats: Dict):
        """比較結果のExcelレポートを作成"""
        try:
            from datetime import datetime
            import os
            
            # レポート作成確認
            create_report = self._show_custom_yesno(
                "📊 レポート作成",
                "比較結果をExcelレポートとして保存しますか？\n\n" +
                "レポートには以下が含まれます:\n" +
                "• 比較結果サマリー\n" +
                "• 詳細な相違点一覧\n" +
                "• 統計情報",
            )
            
            if not create_report:
                return
            
            # 保存場所選択
            from tkinter import filedialog
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Excel比較レポート_{timestamp}.xlsx"
            
            report_path = filedialog.asksaveasfilename(
                title="レポート保存先",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if not report_path:
                return
            
            print(f"\n📊 Excelレポートを作成中: {os.path.basename(report_path)}")
            
            # 新しいワークブックを作成
            try:
                print("📝 新しいExcelワークブックを作成中...")
                report_wb = self.excel_app.Workbooks.Add()
                print("✅ 新規ワークブック作成成功")
                
                # 少し待機してワークブックを安定化
                import time
                time.sleep(0.5)
                
                # サマリーシート作成
                print("📊 サマリーシート作成中...")
                self._create_summary_sheet_safe(report_wb, range1_data, range2_data, stats)
                print("✅ サマリーシート作成完了")
                
                # 詳細シート作成
                differences = [r for r in results if r['similarity'] < 100.0]
                if differences:
                    print(f"📋 詳細シート作成中... ({len(differences)}件の相違)")
                    self._create_details_sheet(report_wb, differences)
                    print("✅ 詳細シート作成完了")
                else:
                    print("ℹ️ 相違点がないため詳細シートをスキップ")
                
                # 完全一致データシート（オプション）
                perfect_matches = [r for r in results if r['similarity'] == 100.0]
                if perfect_matches and len(perfect_matches) < 5000:  # データ量制限
                    print(f"✅ 完全一致シート作成中... ({len(perfect_matches)}件)")
                    try:
                        self._create_matches_sheet_safe(report_wb, perfect_matches)
                        print("✅ 完全一致シート作成完了")
                    except Exception as match_error:
                        print(f"⚠️ 完全一致シート作成エラー（無視）: {match_error}")
                else:
                    print("ℹ️ 完全一致データが多いためシートをスキップ")
                
                # レポート保存
                print("💾 レポート保存中...")
                
                # 既存ファイルを削除（より安全な方法）
                try:
                    if os.path.exists(report_path):
                        os.remove(report_path)
                        print(f"🗑️ 既存ファイルを削除: {report_path}")
                except Exception as delete_error:
                    print(f"⚠️ 既存ファイル削除エラー（無視）: {delete_error}")
                
                # 絶対パスに変換して保存
                abs_report_path = os.path.abspath(report_path)
                print(f"💾 保存先（絶対パス）: {abs_report_path}")
                
                # Excelのファイル形式を明示的に指定
                # xlOpenXMLWorkbook = 51 (xlsx形式)
                report_wb.SaveAs(abs_report_path, FileFormat=51)
                print("✅ ファイル保存成功")
                
                report_wb.Close(SaveChanges=False)
                print("✅ ワークブック閉じる成功")
                
            except Exception as wb_error:
                print(f"❌ ワークブック操作エラー: {wb_error}")
                # ワークブックが作成されていれば閉じる
                try:
                    if 'report_wb' in locals():
                        report_wb.Close(SaveChanges=False)
                        print("🔧 エラー時ワークブック閉じる完了")
                except:
                    pass
                raise wb_error
            
            print(f"✅ レポート保存完了: {report_path}")
            
            # 完了通知
            open_file = self._show_custom_yesno(
                "🎉 レポート作成完了",
                f"比較レポートが作成されました！\n\n" +
                f"保存先: {os.path.basename(report_path)}\n\n" +
                f"レポートを開きますか？"
            )
            
            if open_file:
                self.excel_app.Workbooks.Open(report_path)
                print(f"📂 レポートを開きました: {report_path}")
            
        except Exception as e:
            print(f"❌ レポート作成エラー: {e}")
            self._show_custom_error(
                "⚠️ レポート作成エラー",
                f"レポートの作成中にエラーが発生しました:\n{e}"
            )
    
    def _create_summary_sheet_safe(self, report_wb, range1_data: Dict, range2_data: Dict, stats: Dict):
        """安全なサマリーシート作成"""
        # ワークシートの取得と安全な操作
        try:
            # ワークブックを明示的にアクティブ化
            report_wb.Activate()
            ws = report_wb.ActiveSheet
            print(f"📋 アクティブシート取得: {ws.Name}")
            
            # シート名の変更
            try:
                ws.Name = "比較サマリー"
                print("✅ シート名変更成功")
            except Exception as name_error:
                print(f"⚠️ シート名変更エラー（無視）: {name_error}")
            
        except Exception as ws_error:
            print(f"❌ ワークシート取得エラー: {ws_error}")
            return
        
        from datetime import datetime
        
        # 基本情報をテキスト配列として準備
        report_data = []
        report_data.append(("A1", "Excel範囲比較レポート"))
        
        try:
            date_str = datetime.now().strftime('%Y年%m月%d日 %H時%M分%S秒')
            report_data.append(("A2", f"作成日時: {date_str}"))
        except:
            report_data.append(("A2", "作成日時: [取得エラー]"))
        
        # 比較対象情報
        report_data.append(("A4", "📄 比較対象情報"))
        report_data.append(("A5", "ファイル1:"))
        report_data.append(("B5", range1_data.get('name', 'Unknown')))
        report_data.append(("A6", "パス1:"))
        report_data.append(("B6", range1_data.get('path', 'Unknown')))
        report_data.append(("A7", "シート1:"))
        report_data.append(("B7", range1_data.get('worksheet_name', 'Unknown')))
        report_data.append(("A8", "範囲1:"))
        report_data.append(("B8", range1_data.get('address', 'Unknown')))
        
        report_data.append(("A10", "ファイル2:"))
        report_data.append(("B10", range2_data.get('name', 'Unknown')))
        report_data.append(("A11", "パス2:"))
        report_data.append(("B11", range2_data.get('path', 'Unknown')))
        report_data.append(("A12", "シート2:"))
        report_data.append(("B12", range2_data.get('worksheet_name', 'Unknown')))
        report_data.append(("A13", "範囲2:"))
        report_data.append(("B13", range2_data.get('address', 'Unknown')))
        
        # 統計情報
        report_data.append(("A15", "📈 比較結果統計"))
        report_data.append(("A16", f"総セル数: {stats.get('total_cells', 0)}"))
        report_data.append(("A17", f"完全一致: {stats.get('perfect_match', 0)}"))
        report_data.append(("A18", f"高類似: {stats.get('high_similarity', 0)}"))
        report_data.append(("A19", f"中類似: {stats.get('medium_similarity', 0)}"))
        report_data.append(("A20", f"低類似/相違: {stats.get('low_similarity', 0)}"))
        
        # データを安全に書き込み
        successful_writes = 0
        for cell_address, value in report_data:
            try:
                # セル参照を行列番号に変換
                col_letter = cell_address[0]
                row_num = int(cell_address[1:])
                col_num = ord(col_letter) - ord('A') + 1
                
                # 値を安全に変換
                safe_value = str(value)[:32767] if value is not None else ""
                
                # セルに値を設定
                ws.Cells[row_num, col_num].Value = safe_value
                successful_writes += 1
                
            except Exception as cell_error:
                print(f"⚠️ セル書き込みエラー({cell_address}): {cell_error}")
                continue
        
        print(f"✅ セル書き込み完了: {successful_writes}/{len(report_data)}")
        
        # フォント設定を試行（エラーがあっても継続）
        try:
            ws.Cells[1, 1].Font.Size = 16
            ws.Cells[1, 1].Font.Bold = True
        except:
            pass
    
    def _create_details_sheet(self, report_wb, differences: List[Dict]):
        """詳細相違点シートを作成（一括書き込み版）"""
        try:
            ws = report_wb.Worksheets.Add()
            ws.Name = "相違点詳細"
            print(f"📝 詳細シート作成開始: {len(differences)}件")
            
            # ヘッダー準備
            headers = ["位置", "ステータス", "類似度(%)", "ファイル1の値", "ファイル2の値"]
            
            # データ制限（COM エラー回避）
            max_rows = min(len(differences), 5000)  # 制限を5000に縮小
            print(f"📊 処理対象: {max_rows}件（制限適用）")
            
            # 全データを2次元配列として準備
            data = []
            
            # ヘッダー行
            data.append(headers)
            
            # データ行
            for i, diff in enumerate(differences[:max_rows]):
                try:
                    # None値や特殊文字を安全に処理
                    position = str(diff.get('position', ''))[:255] if diff.get('position') else ''
                    status = str(diff.get('status', ''))[:255] if diff.get('status') else ''
                    similarity = f"{diff.get('similarity', 0):.1f}"  # %記号を削除
                    value1 = str(diff.get('value1', ''))[:1000] if diff.get('value1') is not None else ''  # 文字数制限
                    value2 = str(diff.get('value2', ''))[:1000] if diff.get('value2') is not None else ''  # 文字数制限
                    
                    # 特殊文字をサニタイズ
                    value1 = value1.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    value2 = value2.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    
                    data.append([position, status, similarity, value1, value2])
                    
                except Exception as data_error:
                    print(f"⚠️ データ{i}準備エラー（スキップ）: {data_error}")
                    data.append([f"行{i}", "エラー", "0", "データ読込エラー", "データ読込エラー"])
                    continue
            
            # 一括書き込み（範囲指定）
            if data:
                try:
                    rows = len(data)
                    cols = len(headers)
                    
                    # 範囲を指定して一括書き込み
                    range_address = f"A1:{chr(64 + cols)}{rows}"
                    target_range = ws.Range(range_address)
                    
                    print(f"📝 一括書き込み範囲: {range_address} ({rows}行 x {cols}列)")
                    target_range.Value = data
                    print("✅ 一括書き込み完了")
                    
                    # ヘッダー行のフォーマット
                    header_range = ws.Range(f"A1:{chr(64 + cols)}1")
                    header_range.Font.Bold = True
                    header_range.Interior.Color = 12632256  # 薄いグレー
                    
                    # 列幅自動調整
                    ws.Columns.AutoFit()
                    print("✅ フォーマット適用完了")
                    
                except Exception as write_error:
                    print(f"❌ 一括書き込みエラー: {write_error}")
                    # フォールバック: 個別書き込み（少数のデータのみ）
                    self._create_details_sheet_fallback(ws, headers, differences[:100])
            
        except Exception as sheet_error:
            print(f"❌ 詳細シート作成エラー: {sheet_error}")
            raise
    
    def _create_details_sheet_fallback(self, ws, headers, differences):
        """詳細シートのフォールバック作成（個別書き込み・少数データ）"""
        print(f"🔄 フォールバック詳細シート作成: {len(differences)}件")
        
        # ヘッダー
        try:
            for col, header in enumerate(headers, 1):
                ws.Cells[1, col].Value = header
                ws.Cells[1, col].Font.Bold = True
                ws.Cells[1, col].Interior.Color = 12632256
        except:
            print("⚠️ ヘッダー設定エラー（無視）")
        
        # データ行（少数のみ）
        written_rows = 0
        for row, diff in enumerate(differences[:100], 2):  # 最大100件
            try:
                position = str(diff.get('position', ''))[:50] if diff.get('position') else f'R{row-1}'
                status = str(diff.get('status', ''))[:20] if diff.get('status') else '不明'
                similarity = f"{diff.get('similarity', 0):.1f}"
                value1 = str(diff.get('value1', ''))[:100] if diff.get('value1') is not None else ''
                value2 = str(diff.get('value2', ''))[:100] if diff.get('value2') is not None else ''
                
                ws.Cells[row, 1].Value = position
                ws.Cells[row, 2].Value = status  
                ws.Cells[row, 3].Value = similarity
                ws.Cells[row, 4].Value = value1
                ws.Cells[row, 5].Value = value2
                written_rows += 1
                
            except Exception as cell_error:
                print(f"⚠️ フォールバック行{row}エラー: {cell_error}")
                break  # エラーが続く場合は中断
                
        print(f"✅ フォールバック完了: {written_rows}行書き込み")
    
    def _create_matches_sheet_safe(self, report_wb, matches: List[Dict]):
        """安全な完全一致データシート作成"""
        try:
            print("📋 完全一致シート作成開始...")
            
            # 新しいワークシートを追加
            ws = report_wb.Worksheets.Add()
            print(f"✅ 新しいシート追加成功")
            
            # シート名を設定
            try:
                ws.Name = "完全一致データ"
                print("✅ シート名設定成功")
            except Exception as name_error:
                print(f"⚠️ シート名設定エラー（無視）: {name_error}")
            
            # ヘッダーを安全に設定
            headers = [("A1", "位置"), ("B1", "値")]
            successful_headers = 0
            
            for cell_pos, header in headers:
                try:
                    col_letter = cell_pos[0]
                    row_num = int(cell_pos[1:])
                    col_num = ord(col_letter) - ord('A') + 1
                    
                    ws.Cells[row_num, col_num].Value = header
                    successful_headers += 1
                except Exception as header_error:
                    print(f"⚠️ ヘッダー設定エラー({cell_pos}): {header_error}")
            
            print(f"✅ ヘッダー設定完了: {successful_headers}/{len(headers)}")
            
            # データ行を安全に設定（最大1000件）
            data_limit = min(len(matches), 1000)
            successful_data = 0
            
            for i, match in enumerate(matches[:data_limit]):
                try:
                    row_num = i + 2  # ヘッダーの次の行から
                    position = str(match.get('position', ''))[:255] if match.get('position') else ''
                    value = str(match.get('value1', ''))[:1000] if match.get('value1') is not None else ''  # 1000文字制限
                    
                    ws.Cells[row_num, 1].Value = position
                    ws.Cells[row_num, 2].Value = value
                    successful_data += 1
                    
                except Exception as data_error:
                    print(f"⚠️ データ行{i+2}エラー（スキップ）: {data_error}")
                    continue
            
            print(f"✅ データ書き込み完了: {successful_data}/{data_limit}")
            
            # 列幅調整を試行
            try:
                ws.Columns.AutoFit()
                print("✅ 列幅調整完了")
            except:
                print("⚠️ 列幅調整エラー（無視）")
                
        except Exception as sheet_error:
            print(f"❌ 完全一致シート作成エラー: {sheet_error}")
            raise sheet_error
    
    def run(self):
        """メイン実行"""
        print("🚀 シンプルExcel範囲比較プログラム")
        print("-" * 40)
        
        try:
            # 1. Excelに接続
            if not self.connect_to_excel():
                return
            
            # 2. 起動時に必ずファイル選択
            print("\n📋 アプリケーション起動時のファイル選択")
            if not self.startup_file_selection():
                return
            
            # 3. 範囲1選択
            print("\\n📍 1つ目の範囲を選択...")
            range1_data = self.select_workbook_and_range("file1", "1つ目のファイル")
            
            # 4. 範囲2選択  
            print("\\n📍 2つ目の範囲を選択...")
            range2_data = self.select_workbook_and_range("file2", "2つ目のファイル")
            
            # 5. 比較実行
            results = self.compare_ranges(range1_data, range2_data)
            
            # 6. 結果表示とレポート作成
            self.display_results(results, range1_data, range2_data)
            
            # 7. 完了確認
            self._show_custom_info("🎉 処理完了", "比較処理が完了しました！\n結果はコンソールに表示されています。")
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            self._show_custom_error("⚠️ エラー", f"処理中にエラーが発生しました:\n{e}")


def main():
    """メイン関数（繰り返し実行対応）"""
    print("🚀 シンプルExcel範囲比較プログラム を起動します...")
    print("="*60)
    
    comparator = SimpleRangeComparator()
    
    try:
        while True:
            print(f"\n{'='*60}")
            print("🔄 新しい比較を開始します")
            print(f"{'='*60}")
            
            try:
                # 比較実行
                comparator.run()
                
                print(f"\n{'='*60}")
                print("✅ 比較処理が完了しました")
                print(f"{'='*60}")
                
            except Exception as run_error:
                print(f"\n❌ 比較処理中にエラーが発生しました: {run_error}")
                print("🔄 プログラムを継続します...")
            
            # 継続確認
            root = comparator._create_topmost_window()
            continue_app = messagebox.askyesno(
                "🔄 継続確認",
                "もう一度比較を実行しますか？\n\n" +
                "「はい」: 新しい比較を開始\n" +
                "「いいえ」: プログラムを終了",
                parent=root
            )
            comparator._safe_destroy(root)
            
            if not continue_app:
                print("\n👋 プログラムを終了します...")
                break
                
        # Excel アプリケーションのクリーンアップ
        if comparator.excel_app:
            try:
                # 開いているファイルを閉じる（保存なし）
                for file_key in ['file1', 'file2']:
                    if file_key in comparator.workbook_data and 'workbook' in comparator.workbook_data[file_key]:
                        try:
                            comparator.workbook_data[file_key]['workbook'].Close(SaveChanges=False)
                        except:
                            pass
                
                print("🧹 Excel アプリケーションをクリーンアップしました")
            except Exception as cleanup_error:
                print(f"⚠️ クリーンアップ中にエラー: {cleanup_error}")
        
        print("✅ プログラムが正常に終了しました")
        
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
    except Exception as main_error:
        print(f"\n❌ プログラム実行中に予期しないエラー: {main_error}")
        input("エラー確認のためEnterキーを押してください...")
    finally:
        print("🏁 プログラム終了")


if __name__ == "__main__":
    main()