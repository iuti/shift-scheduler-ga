"""
レポート生成とデータ変換
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Dict, Any


class ShiftReportGenerator:
    """シフトレポートの生成"""
    
    def __init__(self, config, data_loader, evaluator):
        self.config = config
        self.data_loader = data_loader
        self.evaluator = evaluator
        self.staff_names = data_loader.get_staff_names()
    
    def schedule_to_dataframe(self, individual: List[int]) -> pd.DataFrame:
        """スケジュールをDataFrameに変換"""
        schedule = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        # 列名の作成（日付と時間）
        columns = []
        for day in range(1, self.config.num_days + 1):
            for hour in range(self.config.start_hour, self.config.end_hour + 1):
                columns.append(f"10/{day} {hour:02d}:00")
        
        # 行名（スタッフ名）
        row_names = self.staff_names[:self.config.num_staff]
        if len(row_names) < self.config.num_staff:
            row_names.extend([f"Staff{i}" for i in range(len(row_names), self.config.num_staff)])
        
        # DataFrameの作成
        data = schedule.reshape(self.config.num_staff, -1)
        df = pd.DataFrame(data, index=row_names, columns=columns)
        
        return df
    
    def plot_evolution(self, logbook) -> None:
        """進化過程のプロット"""
        generations = logbook.select("gen")
        max_fitness = logbook.select("max")
        avg_fitness = logbook.select("avg")
        
        plt.figure(figsize=(10, 6))
        plt.plot(generations, max_fitness, 'b-', label='Max Fitness', linewidth=2)
        plt.plot(generations, avg_fitness, 'r--', label='Average Fitness', linewidth=2)
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title('Evolution of Shift Optimization using Genetic Algorithm')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def save_evolution_graph(self, logbook, filename: str = None) -> None:
        """進化グラフをファイルに保存"""
        if filename is None:
            filename = self.config.output_graph_file
            
        generations = logbook.select("gen")
        max_fitness = logbook.select("max")
        avg_fitness = logbook.select("avg")
        
        plt.figure(figsize=(10, 6))
        plt.plot(generations, max_fitness, 'b-', label='Max Fitness', linewidth=2)
        plt.plot(generations, avg_fitness, 'r--', label='Average Fitness', linewidth=2)
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title('Evolution of Shift Optimization using Genetic Algorithm')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    
    def generate_html_report(self, individual: List[int], logbook, filename: str = None) -> None:
        """HTML形式でシフト表とレポートを生成"""
        if filename is None:
            filename = self.config.output_html_file
            
        # 進化グラフを保存
        self.save_evolution_graph(logbook)
        
        # スケジュールを3次元配列に変換
        schedule_3d = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        # DataFrameに変換
        df = self.schedule_to_dataframe(individual)
        
        # HTMLコンテンツの生成
        html_content = self._generate_html_content(individual, df, schedule_3d)
        
        # HTMLファイルに保存
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTMLレポートを生成しました: {filename}")
    
    def _generate_html_content(self, individual: List[int], df: pd.DataFrame, schedule_3d: np.ndarray) -> str:
        """HTMLコンテンツの生成"""
        negative_pairs = self.data_loader.get_negative_pairs()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>シフト自動生成レポート</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 シフト自動生成レポート</h1>
        
        <div class="summary">
            <h2>📊 実行サマリー</h2>
            <div class="summary-item">実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</div>
            <div class="summary-item">最終適応度: {individual.fitness.values[0]:.0f}</div>
            <div class="summary-item">スタッフ数: {self.config.num_staff}人</div>
            <div class="summary-item">対象期間: 10/1-10/7 (7日間)</div>
            <div class="summary-item">相性ペア: {len(negative_pairs)}組</div>
        </div>
        
        <div class="graph-container">
            <h2>📈 進化過程</h2>
            <img src="{self.config.output_graph_file}" alt="進化グラフ">
        </div>
        
        <h2>📅 最適化されたシフト表</h2>
        {self._generate_shift_table_html(df)}
        
        <h2>📊 時間帯別人数統計</h2>
        {self._generate_time_stats_html(schedule_3d)}
        
        <h2>👥 スタッフ別労働時間</h2>
        {self._generate_staff_stats_html(schedule_3d)}
        
        <h2>⚠️ 制約違反チェック</h2>
        {self._generate_violation_report_html(schedule_3d)}
        
        <div style="margin-top: 50px; text-align: center; color: #7f8c8d;">
            <p>Generated by Genetic Algorithm Shift Scheduler</p>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def _get_css_styles(self) -> str:
        """CSSスタイルを取得"""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .summary {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .summary-item {
            display: inline-block;
            margin: 10px 20px;
            padding: 10px;
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 12px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 4px;
            text-align: center;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }
        .staff-name {
            background-color: #2980b9;
            color: white;
            font-weight: bold;
            text-align: left;
            padding-left: 10px;
        }
        .work-cell {
            background-color: #2ecc71;
            color: white;
            font-weight: bold;
        }
        .off-cell {
            background-color: #ecf0f1;
            color: #7f8c8d;
        }
        .stats-table {
            width: 100%;
            margin: 20px 0;
        }
        .stats-table th {
            background-color: #e74c3c;
        }
        .warning {
            color: #e74c3c;
            font-weight: bold;
        }
        .good {
            color: #27ae60;
            font-weight: bold;
        }
        .graph-container {
            text-align: center;
            margin: 20px 0;
        }
        .graph-container img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .time-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .day-stats {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .staff-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .staff-hours {
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            text-align: center;
        }
        .over-hours {
            background-color: #ffebee;
            border-left: 4px solid #e74c3c;
        }
        .under-hours {
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
        }
        """
    
    def _generate_shift_table_html(self, df: pd.DataFrame) -> str:
        """シフト表のHTML生成"""
        html = '<div style="overflow-x: auto;"><table>'
        
        # ヘッダー行
        html += '<tr><th class="staff-name">スタッフ</th>'
        for col in df.columns:
            html += f'<th>{col}</th>'
        html += '</tr>'
        
        # データ行
        for staff_name in df.index:
            html += f'<tr><td class="staff-name">{staff_name}</td>'
            for col in df.columns:
                value = df.loc[staff_name, col]
                if value == 1:
                    html += '<td class="work-cell">●</td>'
                else:
                    html += '<td class="off-cell">○</td>'
            html += '</tr>'
        
        html += '</table></div>'
        return html
    
    def _generate_time_stats_html(self, schedule_3d: np.ndarray) -> str:
        """時間帯別統計のHTML生成"""
        html = '<div class="time-stats">'
        
        for day in range(self.config.num_days):
            html += f'<div class="day-stats">'
            html += f'<h3>10/{day+1} (Day {day+1})</h3>'
            html += '<table class="stats-table">'
            html += '<tr><th>時間</th><th>人数</th><th>状態</th></tr>'
            
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule_3d[:, day, hour])
                time_str = f"{hour+self.config.start_hour:02d}:00"
                
                if staff_count < self.config.min_staff_per_hour:
                    status = '<span class="warning">⚠️ 人数不足</span>'
                elif staff_count > self.config.max_staff_per_hour:
                    status = '<span class="warning">⚠️ 人数過多</span>'
                else:
                    status = '<span class="good">✅ 適正</span>'
                
                html += f'<tr><td>{time_str}</td><td>{staff_count}</td><td>{status}</td></tr>'
            
            html += '</table></div>'
        
        html += '</div>'
        return html
    
    def _generate_staff_stats_html(self, schedule_3d: np.ndarray) -> str:
        """スタッフ別統計のHTML生成"""
        html = '<div class="staff-stats">'
        
        for staff_idx in range(self.config.num_staff):
            staff_name = self.staff_names[staff_idx] if staff_idx < len(self.staff_names) else f"Staff{staff_idx}"
            total_hours = np.sum(schedule_3d[staff_idx, :, :])
            
            if total_hours > self.config.max_work_hours_per_week:
                css_class = "staff-hours over-hours"
                status = "⚠️ 長時間"
            elif total_hours < self.config.min_work_hours_per_week:
                css_class = "staff-hours under-hours"
                status = "⚠️ 短時間"
            else:
                css_class = "staff-hours"
                status = "✅ 適正"
            
            html += f'<div class="{css_class}">'
            html += f'<strong>{staff_name}</strong><br>'
            html += f'{total_hours}時間<br>'
            html += f'<small>{status}</small>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _generate_violation_report_html(self, schedule_3d: np.ndarray) -> str:
        """制約違反レポートのHTML生成"""
        stats = self.evaluator.get_schedule_stats(schedule_3d.flatten().tolist())
        
        html = '<table class="stats-table">'
        html += '<tr><th>制約項目</th><th>違反回数</th><th>状態</th></tr>'
        
        items = [
            (f"人数不足 ({self.config.min_staff_per_hour}人未満)", stats['understaffed_count']),
            (f"人数過多 ({self.config.max_staff_per_hour}人超過)", stats['overstaffed_count']),
            (f"1日{self.config.max_work_hours_per_day}時間超過", stats['overwork_count']),
            ("シフト中抜け", stats['gap_count']),
            ("相性の悪いペア同時勤務", stats['negative_pair_violations'])
        ]
        
        for item_name, count in items:
            status = "✅ 問題なし" if count == 0 else f"⚠️ {count}件"
            status_class = "good" if count == 0 else "warning"
            html += f'<tr><td>{item_name}</td><td>{count}</td><td><span class="{status_class}">{status}</span></td></tr>'
        
        html += '</table>'
        return html
    
    def print_schedule_summary(self, individual: List[int]) -> None:
        """スケジュールサマリーをコンソールに出力"""
        schedule_3d = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        print("\n=== シフト統計 ===")
        
        # 各日の時間別人数
        print("\n各時間帯の人数:")
        for day in range(self.config.num_days):
            print(f"10/{day+1}:")
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule_3d[:, day, hour])
                print(f"  {hour+self.config.start_hour:02d}:00 - {staff_count}人")
        
        # 各スタッフの労働時間
        print("\n各スタッフの労働時間:")
        for staff_idx in range(self.config.num_staff):
            staff_name = self.staff_names[staff_idx] if staff_idx < len(self.staff_names) else f"Staff{staff_idx}"
            total_hours = np.sum(schedule_3d[staff_idx, :, :])
            print(f"{staff_name}: {total_hours}時間")
