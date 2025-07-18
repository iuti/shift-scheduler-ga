"""
シフトスケジュールの評価と制約チェック
"""

import numpy as np
from typing import List, Tuple


class ShiftEvaluator:
    """シフトスケジュールの評価と制約チェック"""
    
    def __init__(self, config, data_loader):
        self.config = config
        self.data_loader = data_loader
        self.staff_names = data_loader.get_staff_names()
        self.hope_data = data_loader.get_hope_data()
        self.negative_pairs = data_loader.get_negative_pairs()
    
    def evaluate_fitness(self, individual: List[int]) -> Tuple[float]:
        """適応度評価関数"""
        penalty = 0
        
        # 3次元配列に変換 [staff][day][hour]
        schedule = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        # 各時間帯の人数チェック
        penalty += self._check_staffing_levels(schedule)
        
        # スタッフごとのチェック
        penalty += self._check_staff_constraints(schedule)
        
        # 相性の悪いペアチェック
        penalty += self._check_negative_pairs(schedule)
        
        return (penalty,)
    
    def _check_staffing_levels(self, schedule: np.ndarray) -> float:
        """各時間帯の人数チェック"""
        penalty = 0
        
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule[:, day, hour])
                
                if staff_count < self.config.min_staff_per_hour:
                    penalty -= self.config.penalty_understaffed
                elif staff_count > self.config.max_staff_per_hour:
                    penalty -= self.config.penalty_overstaffed
                    # 最大人数を超えた場合、追加人数に応じてさらにペナルティ
                    excess = staff_count - self.config.max_staff_per_hour
                    penalty -= excess * self.config.penalty_excess_staff
        
        return penalty
    
    def _check_staff_constraints(self, schedule: np.ndarray) -> float:
        """スタッフごとの制約チェック"""
        penalty = 0
        
        for staff_idx in range(self.config.num_staff):
            staff_name = self._get_staff_name(staff_idx)
            
            for day in range(self.config.num_days):
                day_schedule = schedule[staff_idx, day, :]
                
                # 実働時間チェック
                work_hours = np.sum(day_schedule)
                if work_hours > self.config.max_work_hours_per_day:
                    penalty -= self.config.penalty_overwork
                
                # 中抜けチェック
                if self._has_gap(day_schedule):
                    penalty -= self.config.penalty_gap
                
                # 希望との照合
                penalty += self._check_hope_match(staff_name, day + 1, day_schedule)
        
        return penalty
    
    def _check_negative_pairs(self, schedule: np.ndarray) -> float:
        """相性の悪いペアのチェック"""
        penalty = 0
        
        for staff1_name, staff2_name in self.negative_pairs:
            if staff1_name in self.staff_names and staff2_name in self.staff_names:
                staff1_idx = self.staff_names.index(staff1_name)
                staff2_idx = self.staff_names.index(staff2_name)
                
                for day in range(self.config.num_days):
                    for hour in range(self.config.num_hours):
                        # 両方が同じ時間に出勤している場合
                        if (schedule[staff1_idx, day, hour] == 1 and 
                            schedule[staff2_idx, day, hour] == 1):
                            penalty -= self.config.penalty_negative_pair
        
        return penalty
    
    def _has_gap(self, day_schedule: np.ndarray) -> bool:
        """シフトに中抜けがあるかチェック"""
        work_indices = np.where(day_schedule == 1)[0]
        if len(work_indices) <= 1:
            return False
        
        # 連続していない場合は中抜けあり
        for i in range(len(work_indices) - 1):
            if work_indices[i + 1] - work_indices[i] > 1:
                return True
        return False
    
    def _check_hope_match(self, staff_name: str, day: int, day_schedule: np.ndarray) -> float:
        """希望シフトとの照合"""
        penalty = 0
        
        hope_hours = self.data_loader.get_staff_hope_for_day(staff_name, day)
        
        for hour in range(self.config.num_hours):
            # 希望していた時間に出勤していない場合
            if hour in hope_hours and day_schedule[hour] == 0:
                penalty -= self.config.penalty_hope_mismatch
            # 希望していない時間に出勤している場合
            elif hour not in hope_hours and day_schedule[hour] == 1:
                penalty -= self.config.penalty_hope_mismatch
        
        return penalty
    
    def _get_staff_name(self, staff_idx: int) -> str:
        """スタッフインデックスから名前を取得"""
        if staff_idx < len(self.staff_names):
            return self.staff_names[staff_idx]
        return f"Staff{staff_idx}"
    
    def get_schedule_stats(self, individual: List[int]) -> dict:
        """スケジュールの統計情報を取得"""
        schedule = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        stats = {
            'understaffed_count': 0,
            'overstaffed_count': 0,
            'overwork_count': 0,
            'gap_count': 0,
            'negative_pair_violations': 0,
            'staff_work_hours': []
        }
        
        # 人数不足・過多チェック
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule[:, day, hour])
                if staff_count < self.config.min_staff_per_hour:
                    stats['understaffed_count'] += 1
                elif staff_count > self.config.max_staff_per_hour:
                    stats['overstaffed_count'] += 1
        
        # スタッフごとのチェック
        for staff_idx in range(self.config.num_staff):
            total_hours = np.sum(schedule[staff_idx, :, :])
            stats['staff_work_hours'].append(total_hours)
            
            for day in range(self.config.num_days):
                day_hours = np.sum(schedule[staff_idx, day, :])
                if day_hours > self.config.max_work_hours_per_day:
                    stats['overwork_count'] += 1
                
                if self._has_gap(schedule[staff_idx, day, :]):
                    stats['gap_count'] += 1
        
        # 相性の悪いペアチェック
        for staff1_name, staff2_name in self.negative_pairs:
            if staff1_name in self.staff_names and staff2_name in self.staff_names:
                staff1_idx = self.staff_names.index(staff1_name)
                staff2_idx = self.staff_names.index(staff2_name)
                
                for day in range(self.config.num_days):
                    for hour in range(self.config.num_hours):
                        if (schedule[staff1_idx, day, hour] == 1 and 
                            schedule[staff2_idx, day, hour] == 1):
                            stats['negative_pair_violations'] += 1
        
        return stats
