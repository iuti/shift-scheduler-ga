"""
シフト自動生成システムの設定クラス
"""

class ShiftConfig:
    """シフトスケジューラーの設定パラメータ"""
    
    def __init__(self):
        # 基本設定
        self.num_staff = 26
        self.num_days = 7
        self.num_hours = 13  # 10-22時（13時間）
        self.start_hour = 10
        self.end_hour = 22
        
        # 制約設定
        self.min_staff_per_hour = 2
        self.max_staff_per_hour = 3
        self.max_work_hours_per_day = 8
        self.max_work_hours_per_week = 40
        self.min_work_hours_per_week = 20
        
        # GA設定
        self.population_size = 150
        self.generations = 100
        self.crossover_prob = 0.8
        self.mutation_prob = 0.15
        self.tournament_size = 3
        self.smart_generation_ratio = 0.7
        self.repair_probability = 0.3
        
        # ペナルティ設定
        self.penalty_understaffed = 2000
        self.penalty_overstaffed = 500
        self.penalty_excess_staff = 200
        self.penalty_overwork = 1000
        self.penalty_gap = 300
        self.penalty_hope_mismatch = 50
        self.penalty_negative_pair = 10
        
        # ファイルパス
        self.hope_data_file = 'data/hope_data.txt'
        self.negative_pairs_file = 'data/negative.txt'
        
        # 出力設定
        self.output_html_file = 'shift_report.html'
        self.output_graph_file = 'evolution_graph.png'
        self.progress_display_interval = 10
