"""
シフトデータ処理クラス
"""

import os
import re
from typing import Dict, List, Tuple, Optional


class ShiftDataLoader:
    """シフトデータの読み込みと管理"""
    
    def __init__(self, config):
        self.config = config
        self.staff_names: List[str] = []
        self.hope_data: Dict[str, Dict[int, List[int]]] = {}
        self.negative_pairs: List[Tuple[str, str]] = []
    
    def load_all_data(self) -> None:
        """全てのデータを読み込み"""
        self.load_hope_data()
        self.load_negative_pairs()
    
    def load_hope_data(self) -> None:
        """希望シフトデータを読み込み"""
        try:
            print(f"希望シフトファイルを読み込み中: {self.config.hope_data_file}")
            
            with open(self.config.hope_data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # キッチンスタッフのみ抽出
            kitchen_section = content.split('#各従業員のシフト希望（ホールの役割の人）')[0]
            
            current_staff = None
            for line in kitchen_section.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # スタッフ名の行（「○さん」の形式）
                if line.endswith('さん'):
                    current_staff = line
                    self.staff_names.append(current_staff)
                    self.hope_data[current_staff] = {}
                elif current_staff and ':' in line:
                    # シフト希望データの解析
                    self._parse_shift_line(current_staff, line)
            
            print(f"読み込み完了: {len(self.staff_names)}人のスタッフ")
            
        except FileNotFoundError as e:
            print(f"希望シフトファイルが見つかりません: {e}")
            print(f"現在の作業ディレクトリ: {os.getcwd()}")
            print("dataディレクトリの内容を確認してください")
            self._init_default_data()
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
            self._init_default_data()
    
    def _parse_shift_line(self, staff: str, line: str) -> None:
        """シフト希望行を解析"""
        # 10/1: 16:00-22:00, 10/2: 10:00-18:00 のような形式を解析
        pattern = r'10/(\d+):\s*(\d+):00-(\d+):00'
        matches = re.findall(pattern, line)
        
        for day, start_hour, end_hour in matches:
            day = int(day)
            start_hour = int(start_hour)
            end_hour = int(end_hour)
            
            if day not in self.hope_data[staff]:
                self.hope_data[staff][day] = []
            
            # 希望時間帯を記録
            for hour in range(start_hour, end_hour):
                if self.config.start_hour <= hour <= self.config.end_hour - 1:
                    # 0から始まるインデックスに変換
                    self.hope_data[staff][day].append(hour - self.config.start_hour)
    
    def load_negative_pairs(self) -> None:
        """相性の悪いペアを読み込み"""
        try:
            print(f"相性ペアファイルを読み込み中: {self.config.negative_pairs_file}")
            
            with open(self.config.negative_pairs_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '-' in line:
                    staff1, staff2 = line.split('-')
                    # スタッフ名に「さん」を付けて正規化
                    staff1 = staff1.strip() + 'さん'
                    staff2 = staff2.strip() + 'さん'
                    self.negative_pairs.append((staff1, staff2))
            
            print(f"相性の悪いペア: {len(self.negative_pairs)}組")
            
        except FileNotFoundError as e:
            print(f"相性ペアファイルが見つかりません: {e}")
            print(f"現在の作業ディレクトリ: {os.getcwd()}")
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
    
    def _init_default_data(self) -> None:
        """デフォルトデータで初期化"""
        self.staff_names = []
        self.hope_data = {}
        
        for i in range(self.config.num_staff):
            staff_name = f"{chr(65+i)}さん"
            self.staff_names.append(staff_name)
            self.hope_data[staff_name] = {}
    
    def get_staff_names(self) -> List[str]:
        """スタッフ名のリストを取得"""
        return self.staff_names.copy()
    
    def get_hope_data(self) -> Dict[str, Dict[int, List[int]]]:
        """希望データを取得"""
        return self.hope_data.copy()
    
    def get_negative_pairs(self) -> List[Tuple[str, str]]:
        """相性の悪いペアを取得"""
        return self.negative_pairs.copy()
    
    def get_staff_hope_for_day(self, staff_name: str, day: int) -> List[int]:
        """特定のスタッフの特定の日の希望時間を取得"""
        if staff_name in self.hope_data and day in self.hope_data[staff_name]:
            return self.hope_data[staff_name][day]
        return []
