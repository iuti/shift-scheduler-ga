"""
シフト自動生成システム - リファクタリング版
遺伝的アルゴリズムを使用してシフトスケジュールを自動生成します。
"""

import matplotlib.pyplot as plt
from config import ShiftConfig
from data_loader import ShiftDataLoader
from evaluator import ShiftEvaluator
from optimizer import ShiftOptimizer
from report_generator import ShiftReportGenerator

# 日本語フォント設定（英語ラベルに変更）
plt.rcParams['font.family'] = 'DejaVu Sans'


class ShiftScheduler:
    """シフト自動生成システムのメインクラス"""
    
    def __init__(self):
        # 設定の初期化
        self.config = ShiftConfig()
        
        # データローダーの初期化
        self.data_loader = ShiftDataLoader(self.config)
        self.data_loader.load_all_data()
        
        # 評価器の初期化
        self.evaluator = ShiftEvaluator(self.config, self.data_loader)
        
        # 最適化器の初期化
        self.optimizer = ShiftOptimizer(self.config, self.evaluator)
        
        # レポート生成器の初期化
        self.report_generator = ShiftReportGenerator(self.config, self.data_loader, self.evaluator)
    
    def run_optimization(self):
        """最適化を実行"""
        print("\n遺伝的アルゴリズムを実行中...")
        logbook, best_individual = self.optimizer.optimize()
        
        # 結果の表示
        print(f"\n最終結果:")
        print(f"最高適応度: {best_individual.fitness.values[0]:.2f}")
        
        return logbook, best_individual
    
    def generate_reports(self, individual, logbook):
        """レポートを生成"""
        # グラフの描画
        print("\n進化グラフを表示中...")
        self.report_generator.plot_evolution(logbook)
        
        # HTMLレポートの生成
        print("\nHTMLレポートを生成中...")
        self.report_generator.generate_html_report(individual, logbook)
        
        # 最適なシフトの表示
        print("\n最適化されたシフト表:")
        df = self.report_generator.schedule_to_dataframe(individual)
        print(df)
        
        # シフト統計の表示
        self.report_generator.print_schedule_summary(individual)
    
    def run(self):
        """メインの実行処理"""
        print("シフト自動生成システムを開始します...")
        
        # 最適化の実行
        logbook, best_individual = self.run_optimization()
        
        # レポートの生成
        self.generate_reports(best_individual, logbook)
        
        return best_individual, logbook


def main():
    """メイン関数"""
    try:
        # シフトスケジューラーの初期化と実行
        scheduler = ShiftScheduler()
        best_individual, logbook = scheduler.run()
        
        print("\n✅ シフト自動生成が完了しました！")
        print(f"📊 最終適応度: {best_individual.fitness.values[0]:.2f}")
        print(f"📄 HTMLレポート: {scheduler.config.output_html_file}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()