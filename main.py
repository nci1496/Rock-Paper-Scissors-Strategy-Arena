from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from itertools import combinations
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from agent import Agent
from agents import AGENT_DESCRIPTIONS, AVAILABLE_AGENTS
from game import MatchResult, run_match


def _run_pair_worker(
    pair_index: int,
    a_index: int,
    b_index: int,
    rounds: int,
    seed: Optional[int],
) -> tuple[int, int, int, int, int]:
    class_a = AVAILABLE_AGENTS[a_index]
    class_b = AVAILABLE_AGENTS[b_index]
    pair_seed = None if seed is None else seed + pair_index
    result = run_match(class_a(), class_b(), rounds=rounds, seed=pair_seed)
    return a_index, b_index, result.wins_a, result.wins_b, result.draws


class RPSApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Rock-Paper-Scissors AI Arena")
        self.geometry("1080x740")
        self.minsize(980, 680)

        self.agent_classes = list(AVAILABLE_AGENTS)
        self.agent_labels = [cls().name for cls in self.agent_classes]
        self.agent_class_names = [cls.__name__ for cls in self.agent_classes]

        self.stop_event = threading.Event()

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        self.home_frame = HomeFrame(container, self.show_battle_frame)
        self.battle_frame = BattleFrame(
            container,
            self.agent_classes,
            self.agent_labels,
            self.agent_class_names,
            self.stop_event,
        )

        self.home_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.battle_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.show_home_frame()

    def show_home_frame(self) -> None:
        self.home_frame.tkraise()

    def show_battle_frame(self) -> None:
        self.battle_frame.tkraise()


class HomeFrame(tk.Frame):
    def __init__(self, master: tk.Misc, on_enter_battle) -> None:
        super().__init__(master)

        tk.Label(
            self,
            text="Rock-Paper-Scissors Strategy Arena",
            font=("Microsoft YaHei UI", 24, "bold"),
            pady=24,
        ).pack()

        tk.Label(
            self,
            text="Browse agents, run 1v1, all-pairs, or survival mode.",
            font=("Microsoft YaHei UI", 12),
            fg="#2d3748",
        ).pack(pady=(0, 20))

        tk.Button(
            self,
            text="Enter Agent Browser & Battle",
            command=on_enter_battle,
            font=("Microsoft YaHei UI", 12, "bold"),
            padx=24,
            pady=10,
            bg="#2563eb",
            fg="white",
            relief=tk.FLAT,
            activebackground="#1d4ed8",
            activeforeground="white",
        ).pack()


class BattleFrame(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        agent_classes: list[type[Agent]],
        agent_labels: list[str],
        agent_class_names: list[str],
        stop_event: threading.Event,
    ) -> None:
        super().__init__(master)
        self.agent_classes = agent_classes
        self.agent_labels = agent_labels
        self.agent_class_names = agent_class_names
        self.stop_event = stop_event
        self._run_in_progress = False
        self._survival_checkpoint: Optional[dict] = None

        top_bar = tk.Frame(self)
        top_bar.pack(fill=tk.X, padx=14, pady=10)
        tk.Label(top_bar, text="Agent Browser & Battle", font=("Microsoft YaHei UI", 14, "bold")).pack(side=tk.LEFT)

        main_area = tk.Frame(self)
        main_area.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        left = tk.LabelFrame(main_area, text="All Agents", padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.LabelFrame(main_area, text="Description / Battle Setup", padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.agent_listbox = tk.Listbox(left, font=("Consolas", 11), activestyle="none")
        self.agent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(left, orient=tk.VERTICAL, command=self.agent_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.agent_listbox.config(yscrollcommand=scrollbar.set)

        for i, label in enumerate(self.agent_labels, start=1):
            self.agent_listbox.insert(tk.END, f"{i:02d}. {label}")
        self.agent_listbox.bind("<<ListboxSelect>>", self._on_agent_select)

        self.desc_title = tk.Label(right, text="Select an agent from the left", font=("Microsoft YaHei UI", 13, "bold"), anchor="w")
        self.desc_title.pack(fill=tk.X)

        self.desc_text = tk.Text(right, height=10, wrap=tk.WORD, font=("Microsoft YaHei UI", 10))
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(8, 12))
        self._set_desc_text("Click an agent to view its description.")

        form = tk.Frame(right)
        form.pack(fill=tk.X)

        tk.Label(form, text="Agent A", font=("Microsoft YaHei UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        tk.Label(form, text="Agent B", font=("Microsoft YaHei UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        tk.Label(form, text="Rounds", font=("Microsoft YaHei UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        tk.Label(form, text="Seed", font=("Microsoft YaHei UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        tk.Label(form, text="Survival n", font=("Microsoft YaHei UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=4)
        tk.Label(form, text="Survival m", font=("Microsoft YaHei UI", 10, "bold")).grid(row=5, column=0, sticky="w", pady=4)

        self.var_agent_a = tk.StringVar(value=self.agent_labels[0])
        self.var_agent_b = tk.StringVar(value=self.agent_labels[1] if len(self.agent_labels) > 1 else self.agent_labels[0])
        self.var_rounds = tk.StringVar(value="1000")
        self.var_seed = tk.StringVar(value="")
        self.var_survival_n = tk.StringVar(value="5")
        self.var_survival_m = tk.StringVar(value="3")

        ttk.Combobox(form, textvariable=self.var_agent_a, values=self.agent_labels, state="readonly").grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        ttk.Combobox(form, textvariable=self.var_agent_b, values=self.agent_labels, state="readonly").grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)
        tk.Entry(form, textvariable=self.var_rounds).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)
        tk.Entry(form, textvariable=self.var_seed).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)
        tk.Entry(form, textvariable=self.var_survival_n).grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=4)
        tk.Entry(form, textvariable=self.var_survival_m).grid(row=5, column=1, sticky="ew", padx=(8, 0), pady=4)
        form.grid_columnconfigure(1, weight=1)

        button_row = tk.Frame(right)
        button_row.pack(fill=tk.X, pady=(10, 8))

        self.single_battle_button = tk.Button(
            button_row,
            text="Start Battle",
            command=self._run_battle,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#059669",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=7,
        )
        self.single_battle_button.pack(side=tk.LEFT, padx=(0, 6))

        self.all_pairs_button = tk.Button(
            button_row,
            text="Run All-Pairs",
            command=self._run_all_pairs,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#7c3aed",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=7,
        )
        self.all_pairs_button.pack(side=tk.LEFT, padx=6)

        self.survival_button = tk.Button(
            button_row,
            text="Start Survival",
            command=self._run_survival,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#ea580c",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=7,
        )
        self.survival_button.pack(side=tk.LEFT, padx=6)

        self.resume_survival_button = tk.Button(
            button_row,
            text="Resume Survival",
            command=self._resume_survival,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#0f766e",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=7,
            state=tk.DISABLED,
        )
        self.resume_survival_button.pack(side=tk.LEFT, padx=6)

        self.stop_button = tk.Button(
            button_row,
            text="Stop Current Run",
            command=self._stop_current_run,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#dc2626",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=7,
            state=tk.DISABLED,
        )
        self.stop_button.pack(side=tk.LEFT, padx=6)

        result_frame = tk.Frame(right, bd=1, relief=tk.SOLID, bg="#f8fafc")
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, wrap=tk.NONE, font=("Consolas", 10), bg="#f8fafc", padx=10, pady=10)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        result_scroll_y = tk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        result_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=result_scroll_y.set, state=tk.DISABLED)

    def _set_desc_text(self, text: str) -> None:
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", text)
        self.desc_text.config(state=tk.DISABLED)

    def _set_result_text(self, text: str) -> None:
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.see("1.0")
        self.result_text.configure(state=tk.DISABLED)

    def _on_agent_select(self, _event) -> None:
        idxs = self.agent_listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        label = self.agent_labels[idx]
        class_name = self.agent_class_names[idx]
        description = AGENT_DESCRIPTIONS.get(class_name, "No description.")
        self.desc_title.config(text=label)
        self._set_desc_text(description)

    def _build_agent(self, selected_label: str) -> Agent:
        return self.agent_classes[self.agent_labels.index(selected_label)]()

    def _parse_rounds(self) -> int:
        raw = self.var_rounds.get().strip()
        if not raw.isdigit() or int(raw) <= 0:
            raise ValueError("Rounds must be a positive integer.")
        return int(raw)

    def _parse_seed(self) -> Optional[int]:
        raw = self.var_seed.get().strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError as exc:
            raise ValueError("Seed must be an integer or empty.") from exc

    def _parse_survival_params(self) -> tuple[int, int]:
        raw_n = self.var_survival_n.get().strip()
        raw_m = self.var_survival_m.get().strip()
        if not raw_n.isdigit() or int(raw_n) <= 0:
            raise ValueError("Survival n must be a positive integer.")
        if not raw_m.isdigit() or int(raw_m) <= 0:
            raise ValueError("Survival m must be a positive integer.")
        return int(raw_n), int(raw_m)

    def _set_running_state(self, running: bool) -> None:
        self._run_in_progress = running
        run_state = tk.DISABLED if running else tk.NORMAL
        stop_state = tk.NORMAL if running else tk.DISABLED
        self.single_battle_button.config(state=run_state)
        self.all_pairs_button.config(state=run_state)
        self.survival_button.config(state=run_state)
        self.stop_button.config(state=stop_state)
        self._refresh_resume_button_state()

    def _refresh_resume_button_state(self) -> None:
        if self._run_in_progress:
            self.resume_survival_button.config(state=tk.DISABLED)
            return
        self.resume_survival_button.config(state=tk.NORMAL if self._survival_checkpoint else tk.DISABLED)

    def _stop_current_run(self) -> None:
        if self._run_in_progress:
            self.stop_event.set()
            self._set_result_text("Stop requested. Waiting for current workers/stage to finish...")

    def _run_battle(self) -> None:
        try:
            rounds = self._parse_rounds()
            seed = self._parse_seed()
            agent_a = self._build_agent(self.var_agent_a.get())
            agent_b = self._build_agent(self.var_agent_b.get())
            result = run_match(agent_a, agent_b, rounds=rounds, seed=seed)
            self._set_result_text(self._format_single_result(result))
        except Exception as exc:
            messagebox.showerror("Input Error", str(exc))

    def _run_all_pairs(self) -> None:
        try:
            rounds = self._parse_rounds()
            seed = self._parse_seed()
            if len(self.agent_classes) < 2:
                raise ValueError("Need at least two agents.")
        except Exception as exc:
            messagebox.showerror("Input Error", str(exc))
            return

        self.stop_event.clear()
        self._set_running_state(True)
        self._set_result_text("All-pairs running in parallel...\nProgress: 0/0")

        threading.Thread(target=self._run_all_pairs_async, args=(rounds, seed), daemon=True).start()

    def _run_all_pairs_async(self, rounds: int, seed: Optional[int]) -> None:
        class_count = len(self.agent_classes)
        index_pairs = list(combinations(range(class_count), 2))
        total_matches = len(index_pairs)

        scoreboard = {
            idx: {"label": self.agent_labels[idx], "wins": 0, "losses": 0, "draws": 0, "rounds": 0}
            for idx in range(class_count)
        }

        completed = 0
        max_workers = max(1, min(os.cpu_count() or 1, 8))

        try:
            with ProcessPoolExecutor(max_workers=max_workers) as pool:
                futures = [
                    pool.submit(_run_pair_worker, pair_idx, a_idx, b_idx, rounds, seed)
                    for pair_idx, (a_idx, b_idx) in enumerate(index_pairs)
                ]

                for future in as_completed(futures):
                    if self.stop_event.is_set():
                        for f in futures:
                            f.cancel()
                        pool.shutdown(wait=False, cancel_futures=True)
                        break

                    a_idx, b_idx, wins_a, wins_b, draws = future.result()
                    completed += 1
                    scoreboard[a_idx]["wins"] += wins_a
                    scoreboard[a_idx]["losses"] += wins_b
                    scoreboard[a_idx]["draws"] += draws
                    scoreboard[a_idx]["rounds"] += rounds
                    scoreboard[b_idx]["wins"] += wins_b
                    scoreboard[b_idx]["losses"] += wins_a
                    scoreboard[b_idx]["draws"] += draws
                    scoreboard[b_idx]["rounds"] += rounds

                    if completed % 10 == 0 or completed == total_matches:
                        self.after(0, self._set_result_text, f"All-pairs running in parallel...\nProgress: {completed}/{total_matches}")

            text = self._format_basic_scoreboard(
                title="All-Pairs Result",
                scoreboard=scoreboard,
                total_matches=completed,
                rounds_per_match=rounds,
                seed=seed,
                extra=f"Workers: {max_workers}",
                stopped=self.stop_event.is_set(),
            )
            self.after(0, self._set_result_text, text)
        except Exception as exc:
            self.after(0, messagebox.showerror, "Run Error", str(exc))
        finally:
            self.stop_event.clear()
            self.after(0, self._set_running_state, False)

    def _run_survival(self) -> None:
        try:
            rounds = self._parse_rounds()
            seed = self._parse_seed()
            n, m = self._parse_survival_params()
            if len(self.agent_classes) <= 2 * m:
                raise ValueError("Agent count must be greater than 2*m for survival mode.")
            if rounds < n:
                raise ValueError("Rounds must be >= survival n.")
        except Exception as exc:
            messagebox.showerror("Input Error", str(exc))
            return

        self.stop_event.clear()
        self._survival_checkpoint = None
        self._set_running_state(True)
        self._set_result_text("Survival mode started...")
        threading.Thread(target=self._run_survival_async, args=(rounds, n, m, seed, None), daemon=True).start()

    def _resume_survival(self) -> None:
        if self._run_in_progress:
            return
        if not self._survival_checkpoint:
            messagebox.showinfo("Resume Survival", "No paused survival session found.")
            return

        cp = self._survival_checkpoint
        self.stop_event.clear()
        self._set_running_state(True)
        self._set_result_text("Resuming survival mode from checkpoint...")
        threading.Thread(
            target=self._run_survival_async,
            args=(cp["total_rounds"], cp["n"], cp["m"], cp["seed"], cp),
            daemon=True,
        ).start()

    def _run_survival_async(
        self,
        total_rounds: int,
        n: int,
        m: int,
        seed: Optional[int],
        checkpoint: Optional[dict],
    ) -> None:
        base = total_rounds // n
        rem = total_rounds % n

        if checkpoint is None:
            participants = []
            next_id = 1
            for cls in self.agent_classes:
                participants.append(
                    {
                        "id": next_id,
                        "agent": cls(),
                        "label": cls().name,
                        "wins": 0,
                        "losses": 0,
                        "draws": 0,
                        "score": 0,
                        "rounds": 0,
                    }
                )
                next_id += 1
            stage_start = 1
            pair_start = 1
            completed_matches = 0
        else:
            participants = checkpoint["participants"]
            next_id = checkpoint["next_id"]
            stage_start = checkpoint["stage"]
            pair_start = checkpoint["pair"]
            completed_matches = checkpoint["completed_matches"]

        for stage in range(stage_start, n + 1):
            if self.stop_event.is_set():
                break

            stage_rounds = base + (1 if stage <= rem else 0)
            stage_pairs = list(combinations(range(len(participants)), 2))
            stage_total = len(stage_pairs)
            current_pair_start = pair_start if stage == stage_start else 1

            for pair_i in range(current_pair_start, stage_total + 1):
                if self.stop_event.is_set():
                    self._survival_checkpoint = {
                        "total_rounds": total_rounds,
                        "n": n,
                        "m": m,
                        "seed": seed,
                        "participants": participants,
                        "next_id": next_id,
                        "stage": stage,
                        "pair": pair_i,
                        "completed_matches": completed_matches,
                    }
                    final_text = self._format_survival_final(
                        participants,
                        total_rounds,
                        n,
                        m,
                        seed,
                        stopped=True,
                        paused=True,
                    )
                    self.after(0, self._set_result_text, final_text)
                    self.stop_event.clear()
                    self.after(0, self._set_running_state, False)
                    return
                a_idx, b_idx = stage_pairs[pair_i - 1]
                a = participants[a_idx]
                b = participants[b_idx]

                pair_seed = None if seed is None else seed + stage * 100000 + pair_i
                result = run_match(a["agent"], b["agent"], rounds=stage_rounds, seed=pair_seed, reset_agents=False)

                a["wins"] += result.wins_a
                a["losses"] += result.wins_b
                a["draws"] += result.draws
                a["score"] += result.wins_a - result.wins_b
                a["rounds"] += result.rounds

                b["wins"] += result.wins_b
                b["losses"] += result.wins_a
                b["draws"] += result.draws
                b["score"] += result.wins_b - result.wins_a
                b["rounds"] += result.rounds

                completed_matches += 1
                if pair_i % 10 == 0 or pair_i == stage_total:
                    text = self._format_survival_progress(participants, stage, n, pair_i, stage_total)
                    self.after(0, self._set_result_text, text)

            # Eliminate m worst and clone m best (including memory/state via deepcopy).
            if len(participants) > 2 * m:
                participants.sort(key=lambda x: (x["score"], x["wins"] - x["losses"], x["wins"]))
                best = sorted(participants[-m:], key=lambda x: (x["score"], x["wins"] - x["losses"], x["wins"]), reverse=True)
                survivors = participants[m:]

                clones = []
                for p in best:
                    clone = {
                        "id": next_id,
                        "agent": deepcopy(p["agent"]),
                        "label": f"{p['label']}#clone{next_id}",
                        "wins": p["wins"],
                        "losses": p["losses"],
                        "draws": p["draws"],
                        "score": p["score"],
                        "rounds": p["rounds"],
                    }
                    next_id += 1
                    clones.append(clone)

                participants = survivors + clones

        self._survival_checkpoint = None
        final_text = self._format_survival_final(participants, total_rounds, n, m, seed, stopped=False, paused=False)
        self.after(0, self._set_result_text, final_text)
        self.stop_event.clear()
        self.after(0, self._set_running_state, False)

    @staticmethod
    def _format_single_result(result: MatchResult) -> str:
        verdict = "Both agents are balanced"
        if result.net_wins_a > 0:
            verdict = "Agent A is better"
        elif result.net_wins_a < 0:
            verdict = "Agent B is better"
        seed_text = str(result.seed) if result.seed is not None else "system random"
        return (
            "===== Battle Result =====\n"
            f"A: {result.agent_a_name}\n"
            f"B: {result.agent_b_name}\n"
            f"Rounds: {result.rounds}\n"
            f"A Wins: {result.wins_a} ({result.win_rate_a:.2%})\n"
            f"B Wins: {result.wins_b} ({result.win_rate_b:.2%})\n"
            f"Draws: {result.draws} ({result.draw_rate:.2%})\n"
            f"A Net Wins: {result.net_wins_a}\n"
            f"Seed: {seed_text}\n"
            f"Conclusion: {verdict}"
        )

    @staticmethod
    def _format_basic_scoreboard(
        title: str,
        scoreboard: dict[int, dict[str, int | str]],
        total_matches: int,
        rounds_per_match: int,
        seed: Optional[int],
        extra: str,
        stopped: bool,
    ) -> str:
        rows = []
        for _, data in scoreboard.items():
            rounds_total = int(data["rounds"]) or 1
            wins = int(data["wins"])
            losses = int(data["losses"])
            draws = int(data["draws"])
            rows.append((str(data["label"]), wins / rounds_total, losses / rounds_total, draws / rounds_total, wins - losses))
        rows.sort(key=lambda r: (r[1], r[4]), reverse=True)

        lines = [
            f"===== {title} =====",
            "Status: STOPPED" if stopped else "Status: COMPLETED",
            f"Matches finished: {total_matches}",
            f"Rounds per pair: {rounds_per_match}",
            f"Seed: {seed if seed is not None else 'system random'}",
            extra,
            "",
            "Rank  Agent                         Win%    Loss%   Draw%   NetWins",
        ]
        for idx, (label, win_rate, loss_rate, draw_rate, net) in enumerate(rows, start=1):
            lines.append(f"{idx:>2}    {label[:28]:<28} {win_rate:>6.2%}  {loss_rate:>6.2%}  {draw_rate:>6.2%}  {net:>7}")
        return "\n".join(lines)

    @staticmethod
    def _format_survival_progress(participants: list[dict], stage: int, n: int, done: int, total: int) -> str:
        ranked = sorted(participants, key=lambda x: (x["score"], x["wins"] - x["losses"], x["wins"]), reverse=True)
        lines = [
            "===== Survival Running =====",
            f"Stage: {stage}/{n}",
            f"Progress in stage: {done}/{total}",
            "",
            "Top 10 by score:",
            "Rank  Agent                         Score   W-L-D",
        ]
        for i, p in enumerate(ranked[:10], start=1):
            lines.append(f"{i:>2}    {p['label'][:28]:<28} {p['score']:>6}   {p['wins']}-{p['losses']}-{p['draws']}")
        return "\n".join(lines)

    @staticmethod
    def _format_survival_final(
        participants: list[dict],
        total_rounds: int,
        n: int,
        m: int,
        seed: Optional[int],
        stopped: bool,
        paused: bool,
    ) -> str:
        ranked = sorted(participants, key=lambda x: (x["score"], x["wins"] - x["losses"], x["wins"]), reverse=True)
        status = "COMPLETED"
        if paused:
            status = "PAUSED (can resume)"
        elif stopped:
            status = "STOPPED"
        lines = [
            "===== Survival Result =====",
            f"Status: {status}",
            f"Total rounds target: {total_rounds}",
            f"Eliminations: {n}",
            f"Eliminate/clone each time (m): {m}",
            f"Seed: {seed if seed is not None else 'system random'}",
            f"Population: {len(participants)}",
            "",
            "Rank  Agent                         Score   Win%    W-L-D",
        ]
        for i, p in enumerate(ranked, start=1):
            rounds = p["rounds"] or 1
            win_rate = p["wins"] / rounds
            lines.append(f"{i:>2}    {p['label'][:28]:<28} {p['score']:>6}  {win_rate:>6.2%}  {p['wins']}-{p['losses']}-{p['draws']}")
        return "\n".join(lines)


def main() -> None:
    app = RPSApp()
    app.mainloop()


if __name__ == "__main__":
    main()
