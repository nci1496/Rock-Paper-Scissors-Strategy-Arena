from .adaptive_mix_agent import AdaptiveMixAgent



from .anti_frequency_agent import AntiFrequencyAgent



from .anti_markov_agent import AntiMarkovAgent



from .anti_mirror_agent import AntiMirrorAgent



from .bait_agent import BaitAgent



from .beat_last_winner_agent import BeatLastWinnerAgent



from .biased_random_agent import BiasedRandomAgent






from .cycle_agent import CycleAgent



from .cycle_detector_agent import CycleDetectorAgent



from .delayed_counter_agent import DelayedCounterAgent



from .ensemble_agent import EnsembleAgent



from .epsilon_greedy_agent import EpsilonGreedyAgent



from .exploit_detector_agent import ExploitDetectorAgent



from .fake_pattern_agent import FakePatternAgent



from .frequency_counter_agent import FrequencyCounterAgent



from .lose_shift_win_stay_agent import LoseShiftWinStayAgent



from .markov1_agent import Markov1Agent



from .markov2_agent import Markov2Agent



from .markov3_agent import Markov3Agent



from .mirror_agent import MirrorAgent



from .q_learning_agent import QLearningAgent



from .random_agent import RandomAgent

from .regret_matching_agent import RegretMatchingAgent



from .rock_only_agent import RockOnlyAgent



from .score_based_agent import ScoreBasedAgent



from .strategy_pool_agent import StrategyPoolAgent



from .window_counter_agent import WindowCounterAgent







AVAILABLE_AGENTS = [



    RandomAgent,



    RockOnlyAgent,



    CycleAgent,



    BiasedRandomAgent,



    FrequencyCounterAgent,



    WindowCounterAgent,



    AdaptiveMixAgent,



    Markov1Agent,



    Markov2Agent,



    Markov3Agent,



    CycleDetectorAgent,



    MirrorAgent,



    AntiMirrorAgent,



    BeatLastWinnerAgent,



    LoseShiftWinStayAgent,



    AntiFrequencyAgent,



    AntiMarkovAgent,



    ExploitDetectorAgent,



    EpsilonGreedyAgent,



    StrategyPoolAgent,



    EnsembleAgent,



    QLearningAgent,

    RegretMatchingAgent,



    ScoreBasedAgent,



    FakePatternAgent,



    DelayedCounterAgent,



    BaitAgent,






]







AGENT_DESCRIPTIONS = {



    "RandomAgent": "每局等概率随机出拳，常作为基线对照组。",



    "RockOnlyAgent": "始终出石头，适合测试策略是否能被稳定利用。",



    "CycleAgent": "按 Rock -> Paper -> Scissors 固定循环。",



    "BiasedRandomAgent": "带偏置的随机策略（Rock 50%，Paper/Scissors 各25%）。",



    "FrequencyCounterAgent": "统计对手历史高频手势并出克制手。",



    "WindowCounterAgent": "只看最近窗口（默认5步）做频率反制，更偏短期响应。",



    "AdaptiveMixAgent": "融合全局频率与短期频率加权决策。",



    "Markov1Agent": "一阶马尔可夫：基于对手上一手预测下一手。",



    "Markov2Agent": "二阶马尔可夫：基于对手前两手预测下一手。",



    "Markov3Agent": "Third-order Markov predictor with backoff to lower orders.",



    "CycleDetectorAgent": "检测对手是否存在短周期循环并尝试反制。",



    "MirrorAgent": "模仿对手上一手。",



    "AntiMirrorAgent": "针对模仿逻辑，出能赢对手上一手的手势。",



    "BeatLastWinnerAgent": "假设对手会重复刚刚奏效的手势，进行反制。",



    "LoseShiftWinStayAgent": "Win-Stay/Lose-Shift：赢或平则延续，输则切换。",



    "AntiFrequencyAgent": "扰乱自身手势分布，降低被频率模型利用的概率。",



    "AntiMarkovAgent": "减少可预测转移，避免被马尔可夫模型锁定。",



    "ExploitDetectorAgent": "检测连续被针对迹象，必要时提升随机性。",



    "EpsilonGreedyAgent": "大部分按当前最优反制，小概率随机探索。",



    "StrategyPoolAgent": "在随机/频率/Markov子策略池中动态抽取。",



    "EnsembleAgent": "多个子策略同时给建议，按投票输出。",



    "QLearningAgent": "极简Q学习，按对局反馈更新动作价值。",

    "RegretMatchingAgent": "Regret matching with probability proportional to positive regret.",



    "ScoreBasedAgent": "维护多种子策略评分，按历史表现偏向高分策略。",



    "FakePatternAgent": "先制造规律再打断，诱导对手模型过拟合。",



    "DelayedCounterAgent": "前期观望，延迟进入针对性反制。",



    "BaitAgent": "前期诱导，后期针对对手形成的模式反打。",






}