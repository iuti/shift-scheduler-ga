"""
遺伝的アルゴリズムによるシフト最適化
"""

import numpy as np
import random
from typing import List, Tuple
from deap import base, creator, tools


class ShiftOptimizer:
    """遺伝的アルゴリズムによるシフト最適化"""
    
    def __init__(self, config, evaluator):
        self.config = config
        self.evaluator = evaluator
        self.toolbox = None
        self._setup_ga()
    
    def _setup_ga(self) -> None:
        """遺伝的アルゴリズムの設定"""
        # 既存の型定義をクリア
        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "Individual"):
            del creator.Individual
            
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        
        # 遺伝子の長さ = スタッフ数 × 日数 × 時間数
        gene_length = self.config.num_staff * self.config.num_days * self.config.num_hours
        
        # 個体生成
        self.toolbox.register("attr_bool", random.randint, 0, 1)
        self.toolbox.register("individual_random", tools.initRepeat, creator.Individual,
                             self.toolbox.attr_bool, gene_length)
        self.toolbox.register("individual_smart", tools.initIterate, creator.Individual,
                             self._create_smart_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual_smart)
        
        # 遺伝操作
        self.toolbox.register("evaluate", self.evaluator.evaluate_fitness)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=self.config.tournament_size)
    
    def optimize(self) -> Tuple[tools.Logbook, List[int]]:
        """最適化を実行"""
        # 初期個体群の生成
        population = self._create_initial_population()
        
        # 統計情報の記録
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        
        # 進化履歴
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + stats.fields
        
        # 初期評価
        self._evaluate_population(population)
        
        record = stats.compile(population)
        logbook.record(gen=0, nevals=len(population), **record)
        print(f"世代 0: 最大適応度 = {record['max']:.2f}, 平均適応度 = {record['avg']:.2f}")
        
        # 世代ループ
        for generation in range(1, self.config.generations + 1):
            population = self._evolve_generation(population)
            
            # 統計情報の記録
            record = stats.compile(population)
            logbook.record(gen=generation, nevals=len(population), **record)
            
            if generation % self.config.progress_display_interval == 0:
                print(f"世代 {generation}: 最大適応度 = {record['max']:.2f}, 平均適応度 = {record['avg']:.2f}")
        
        # 最良個体の取得
        best_individual = tools.selBest(population, 1)[0]
        
        return logbook, best_individual
    
    def _create_initial_population(self) -> List:
        """初期個体群の生成"""
        smart_count = int(self.config.population_size * self.config.smart_generation_ratio)
        random_count = self.config.population_size - smart_count
        
        population = []
        
        # スマート生成
        for _ in range(smart_count):
            ind = creator.Individual(self._create_smart_individual())
            population.append(ind)
        
        # ランダム生成
        for _ in range(random_count):
            ind = self.toolbox.individual_random()
            population.append(ind)
        
        # 初期個体群の修復
        for i, ind in enumerate(population):
            population[i] = creator.Individual(self._repair_individual(ind))
        
        return population
    
    def _evaluate_population(self, population: List) -> None:
        """個体群の評価"""
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
    
    def _evolve_generation(self, population: List) -> List:
        """一世代の進化"""
        # 選択
        offspring = self.toolbox.select(population, len(population))
        offspring = list(map(self.toolbox.clone, offspring))
        
        # 交叉
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < self.config.crossover_prob:
                self.toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        
        # 突然変異
        for mutant in offspring:
            if random.random() < self.config.mutation_prob:
                if random.random() < 0.5:
                    # 通常の突然変異
                    self.toolbox.mutate(mutant)
                else:
                    # スマートな突然変異
                    mutant[:] = self._smart_mutate(mutant)
                del mutant.fitness.values
        
        # 修復オペレータの適用
        for ind in offspring:
            if random.random() < self.config.repair_probability:
                ind[:] = self._repair_individual(ind)
                if hasattr(ind, 'fitness'):
                    del ind.fitness.values
        
        # 評価
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        return offspring
    
    def _create_smart_individual(self) -> List[int]:
        """制約を考慮したスマートな個体生成"""
        schedule = np.zeros((self.config.num_staff, self.config.num_days, self.config.num_hours), dtype=int)
        
        # 各時間帯で適切な人数になるように配置
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                target_staff = np.random.randint(
                    self.config.min_staff_per_hour, 
                    self.config.max_staff_per_hour + 1
                )
                
                # 利用可能なスタッフをリストアップ
                available_staff = self._get_available_staff(schedule, day, hour)
                
                # 利用可能なスタッフから選択
                if len(available_staff) >= target_staff:
                    selected = np.random.choice(available_staff, size=target_staff, replace=False)
                    for staff_idx in selected:
                        schedule[staff_idx, day, hour] = 1
                elif len(available_staff) > 0:
                    # 利用可能なスタッフが少ない場合は全員配置
                    for staff_idx in available_staff:
                        schedule[staff_idx, day, hour] = 1
        
        return schedule.flatten().tolist()
    
    def _get_available_staff(self, schedule: np.ndarray, day: int, hour: int) -> List[int]:
        """指定された時間帯で利用可能なスタッフを取得"""
        available_staff = []
        
        for staff_idx in range(self.config.num_staff):
            # 1日の最大労働時間以下かつ中抜けにならないかチェック
            if np.sum(schedule[staff_idx, day, :]) < self.config.max_work_hours_per_day:
                # 中抜けチェック
                temp_schedule = schedule[staff_idx, day, :].copy()
                temp_schedule[hour] = 1
                if not self.evaluator._has_gap(temp_schedule):
                    available_staff.append(staff_idx)
        
        return available_staff
    
    def _repair_individual(self, individual: List[int]) -> List[int]:
        """個体の制約違反を修復"""
        schedule = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        # 人数過多の修正
        self._fix_overstaffing(schedule)
        
        # シフト中抜けの修正
        self._fix_gaps(schedule)
        
        # 人数不足の修正
        self._fix_understaffing(schedule)
        
        return schedule.flatten().tolist()
    
    def _fix_overstaffing(self, schedule: np.ndarray) -> None:
        """人数過多の修正"""
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule[:, day, hour])
                if staff_count > self.config.max_staff_per_hour:
                    working_staff = np.where(schedule[:, day, hour] == 1)[0]
                    excess = staff_count - self.config.max_staff_per_hour
                    to_remove = np.random.choice(working_staff, size=excess, replace=False)
                    for staff_idx in to_remove:
                        schedule[staff_idx, day, hour] = 0
    
    def _fix_gaps(self, schedule: np.ndarray) -> None:
        """シフト中抜けの修正"""
        for staff_idx in range(self.config.num_staff):
            for day in range(self.config.num_days):
                day_schedule = schedule[staff_idx, day, :]
                if self.evaluator._has_gap(day_schedule):
                    self._fix_staff_gap(day_schedule)
    
    def _fix_staff_gap(self, day_schedule: np.ndarray) -> None:
        """スタッフの中抜けを修正"""
        work_indices = np.where(day_schedule == 1)[0]
        if len(work_indices) > 1:
            # 最初と最後の勤務時間の間を全て勤務にする
            start_hour = work_indices[0]
            end_hour = work_indices[-1]
            for hour in range(start_hour, end_hour + 1):
                day_schedule[hour] = 1
            
            # 最大労働時間を超える場合は調整
            if np.sum(day_schedule) > self.config.max_work_hours_per_day:
                excess = np.sum(day_schedule) - self.config.max_work_hours_per_day
                if np.random.random() < 0.5:
                    # 前を削る
                    for i in range(excess):
                        if start_hour + i < self.config.num_hours:
                            day_schedule[start_hour + i] = 0
                else:
                    # 後ろを削る
                    for i in range(excess):
                        if end_hour - i >= 0:
                            day_schedule[end_hour - i] = 0
    
    def _fix_understaffing(self, schedule: np.ndarray) -> None:
        """人数不足の修正"""
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule[:, day, hour])
                if staff_count < self.config.min_staff_per_hour:
                    self._add_staff_to_slot(schedule, day, hour, staff_count)
    
    def _add_staff_to_slot(self, schedule: np.ndarray, day: int, hour: int, current_count: int) -> None:
        """指定された時間帯にスタッフを追加"""
        off_staff = np.where(schedule[:, day, hour] == 0)[0]
        if len(off_staff) > 0:
            needed = min(self.config.min_staff_per_hour - current_count, len(off_staff))
            
            # 1日の労働時間が最大以下のスタッフを優先
            candidates = []
            for staff_idx in off_staff:
                if np.sum(schedule[staff_idx, day, :]) < self.config.max_work_hours_per_day:
                    candidates.append(staff_idx)
            
            if len(candidates) >= needed:
                to_add = np.random.choice(candidates, size=needed, replace=False)
            else:
                # 適切なスタッフが足りない場合は、全体から選ぶ
                to_add = np.random.choice(off_staff, size=needed, replace=False)
            
            for staff_idx in to_add:
                schedule[staff_idx, day, hour] = 1
    
    def _smart_mutate(self, individual: List[int]) -> List[int]:
        """スマートな突然変異（制約違反を減らす方向）"""
        schedule = np.array(individual).reshape(
            self.config.num_staff, self.config.num_days, self.config.num_hours
        )
        
        # 人数過多の時間帯から人を減らす
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule[:, day, hour])
                if staff_count > self.config.max_staff_per_hour and np.random.random() < 0.3:
                    working_staff = np.where(schedule[:, day, hour] == 1)[0]
                    if len(working_staff) > 0:
                        to_remove = np.random.choice(working_staff)
                        schedule[to_remove, day, hour] = 0
        
        # 人数不足の時間帯に人を追加
        for day in range(self.config.num_days):
            for hour in range(self.config.num_hours):
                staff_count = np.sum(schedule[:, day, hour])
                if staff_count < self.config.min_staff_per_hour and np.random.random() < 0.3:
                    off_staff = np.where(schedule[:, day, hour] == 0)[0]
                    available_staff = []
                    for staff_idx in off_staff:
                        if np.sum(schedule[staff_idx, day, :]) < self.config.max_work_hours_per_day:
                            available_staff.append(staff_idx)
                    
                    if len(available_staff) > 0:
                        to_add = np.random.choice(available_staff)
                        schedule[to_add, day, hour] = 1
        
        return schedule.flatten().tolist()
