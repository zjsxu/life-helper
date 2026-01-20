"""
GUI interface for Personal Life Decision-Support System (PL-DSS)
Simple Tkinter-based interface for evaluating user state
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
import sys
import os

# Add parent directory to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pl_dss.config import load_config
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.recovery import check_recovery


class PLDSS_GUI:
    """Main GUI application for PL-DSS"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("个人决策支持系统 (PL-DSS)")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # Load configuration
        try:
            self.config = load_config()
        except Exception as e:
            messagebox.showerror("配置错误", f"无法加载配置文件:\n{str(e)}")
            sys.exit(1)
        
        self._create_widgets()
        self._apply_styles()
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="个人决策支持系统",
            font=("Helvetica", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="评估你的当前状态，获取行为建议",
            font=("Helvetica", 12)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="输入数据", padding="15")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        # Deadlines input
        ttk.Label(input_frame, text="未来14天的固定截止日期数量:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.deadlines_var = tk.StringVar(value="0")
        deadlines_spinbox = ttk.Spinbox(
            input_frame,
            from_=0,
            to=20,
            textvariable=self.deadlines_var,
            width=10
        )
        deadlines_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Domains input
        ttk.Label(input_frame, text="当前高负荷生活领域数量:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.domains_var = tk.StringVar(value="0")
        domains_spinbox = ttk.Spinbox(
            input_frame,
            from_=0,
            to=20,
            textvariable=self.domains_var,
            width=10
        )
        domains_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Energy scores input
        ttk.Label(input_frame, text="最近3天的能量评分 (1-5):").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        
        energy_frame = ttk.Frame(input_frame)
        energy_frame.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.energy_vars = []
        for i in range(3):
            var = tk.StringVar(value="3")
            self.energy_vars.append(var)
            spinbox = ttk.Spinbox(
                energy_frame,
                from_=1,
                to=5,
                textvariable=var,
                width=5
            )
            spinbox.grid(row=0, column=i, padx=(0, 5))
            ttk.Label(energy_frame, text=f"第{i+1}天").grid(row=1, column=i, padx=(0, 5))
        
        # Help text
        help_text = ttk.Label(
            input_frame,
            text="提示: 高负荷领域包括工作项目、家庭危机、健康问题等",
            font=("Helvetica", 9),
            foreground="gray"
        )
        help_text.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Evaluate button
        self.eval_button = ttk.Button(
            main_frame,
            text="评估状态",
            command=self._evaluate,
            style="Accent.TButton"
        )
        self.eval_button.grid(row=3, column=0, pady=(0, 20))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="评估结果", padding="15")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=("Courier", 11),
            state=tk.DISABLED
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.rowconfigure(0, weight=1)
        
        # Configure text tags for colored output
        self.results_text.tag_config("title", font=("Courier", 12, "bold"))
        self.results_text.tag_config("normal", foreground="green")
        self.results_text.tag_config("stressed", foreground="orange")
        self.results_text.tag_config("overloaded", foreground="red")
        self.results_text.tag_config("section", font=("Courier", 11, "bold"))
    
    def _apply_styles(self):
        """Apply custom styles to widgets"""
        style = ttk.Style()
        
        # Try to use a modern theme if available
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")
        
        # Custom button style
        style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))
    
    def _evaluate(self):
        """Evaluate user state and display results"""
        try:
            # Parse inputs
            deadlines = int(self.deadlines_var.get())
            domains = int(self.domains_var.get())
            energy_scores = [int(var.get()) for var in self.energy_vars]
            
            # Create inputs object
            inputs = StateInputs(
                fixed_deadlines_14d=deadlines,
                active_high_load_domains=domains,
                energy_scores_last_3_days=energy_scores
            )
            
            # Evaluate state
            state_result = evaluate_state(inputs, self.config)
            
            # Get active rules
            rules_result = get_active_rules(state_result.state, self.config)
            
            # Check recovery
            recovery_result = check_recovery(inputs, state_result.state, self.config)
            
            # Display results
            self._display_results(state_result, rules_result, recovery_result)
            
        except ValueError as e:
            messagebox.showerror("输入错误", f"请输入有效的数字:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("评估错误", f"评估过程中出错:\n{str(e)}")
    
    def _display_results(self, state_result, rules_result, recovery_result):
        """Display evaluation results in the text area"""
        # Enable text widget for editing
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Title
        self.results_text.insert(tk.END, "=" * 60 + "\n", "title")
        self.results_text.insert(tk.END, "评估结果\n", "title")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n", "title")
        
        # Current state
        self.results_text.insert(tk.END, "当前状态: ", "section")
        
        state_tag = "normal"
        if state_result.state == "STRESSED":
            state_tag = "stressed"
            state_text = "压力 (STRESSED)"
        elif state_result.state == "OVERLOADED":
            state_tag = "overloaded"
            state_text = "过载 (OVERLOADED)"
        else:
            state_text = "正常 (NORMAL)"
        
        self.results_text.insert(tk.END, state_text + "\n", state_tag)
        self.results_text.insert(tk.END, f"原因: {state_result.explanation}\n\n")
        
        if state_result.conditions_met:
            self.results_text.insert(tk.END, "满足的条件:\n", "section")
            for condition in state_result.conditions_met:
                self.results_text.insert(tk.END, f"  • {condition}\n")
            self.results_text.insert(tk.END, "\n")
        
        # Active rules
        if rules_result.active_rules:
            self.results_text.insert(tk.END, "激活的行为规则:\n", "section")
            for rule in rules_result.active_rules:
                self.results_text.insert(tk.END, f"  • {rule}\n")
            self.results_text.insert(tk.END, "\n")
        
        # Recovery status
        self.results_text.insert(tk.END, "恢复状态: ", "section")
        if recovery_result.can_recover:
            self.results_text.insert(tk.END, "已就绪 ✓\n", "normal")
            self.results_text.insert(tk.END, f"{recovery_result.explanation}\n")
        else:
            self.results_text.insert(tk.END, "未就绪 ✗\n", "overloaded")
            self.results_text.insert(tk.END, f"{recovery_result.explanation}\n")
            if recovery_result.blocking_conditions:
                self.results_text.insert(tk.END, "\n阻塞条件:\n")
                for condition in recovery_result.blocking_conditions:
                    self.results_text.insert(tk.END, f"  • {condition}\n")
        
        # Disable text widget to prevent editing
        self.results_text.config(state=tk.DISABLED)


def main():
    """Launch the GUI application"""
    root = tk.Tk()
    app = PLDSS_GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
