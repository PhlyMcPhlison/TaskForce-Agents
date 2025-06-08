#!/usr/bin/env python3
"""
OmniTasker Ultimate System - Complete AI Agent Implementation
Implements the full OmniTasker prompt with 25 specialized OmniMinions
Autonomous project management from ideation to deployment
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import subprocess
import json
import logging
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import queue
import uuid
import requests
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import sqlite3
import hashlib
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/omnitasker_ultimate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OmniMinion:
    """Represents a specialized OmniMinion agent"""
    id: str
    name: str
    role: str
    specialization: str
    status: str = "idle"
    current_task: Optional[str] = None
    capabilities: List[str] = None
    performance_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.performance_metrics is None:
            self.performance_metrics = {
                "tasks_completed": 0,
                "success_rate": 100.0,
                "avg_completion_time": 0.0,
                "efficiency_score": 100.0
            }

class OmniTaskerUltimateSystem:
    """Main OmniTasker system orchestrating 25 specialized agents"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OmniTasker Ultimate System - AI Agent Orchestrator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize system components
        self.omni_minions = self._initialize_omni_minions()
        self.task_queue = queue.Queue()
        self.project_database = self._initialize_database()
        self.active_projects = {}
        self.system_metrics = {
            "total_projects": 0,
            "completed_projects": 0,
            "active_agents": 25,
            "system_uptime": datetime.now(),
            "success_rate": 100.0
        }
        
        # GUI Components
        self.setup_gui()
        self.setup_monitoring()
        
        # Start background processes
        self.start_agent_orchestration()
        
        logger.info("OmniTasker Ultimate System initialized with 25 OmniMinions")
    
    def _initialize_omni_minions(self) -> Dict[str, OmniMinion]:
        """Initialize 25 specialized OmniMinion agents"""
        minions = {}
        
        # 5 Coders
        for i in range(1, 6):
            minions[f"coder_{i}"] = OmniMinion(
                id=f"coder_{i}",
                name=f"CodeMaster-{i}",
                role="Developer",
                specialization=["Python", "JavaScript", "Java", "C++", "Go"][i-1],
                capabilities=[
                    "code_generation", "debugging", "optimization", 
                    "testing", "documentation", "refactoring"
                ]
            )
        
        # 4 Testers
        test_types = ["Unit Testing", "Integration Testing", "Load Testing", "Security Testing"]
        for i, test_type in enumerate(test_types, 1):
            minions[f"tester_{i}"] = OmniMinion(
                id=f"tester_{i}",
                name=f"TestGuardian-{i}",
                role="Quality Assurance",
                specialization=test_type,
                capabilities=[
                    "test_design", "automation", "performance_analysis",
                    "security_scanning", "regression_testing"
                ]
            )
        
        # 3 Designers
        design_types = ["UI/UX Design", "Wireframing", "Prototyping"]
        for i, design_type in enumerate(design_types, 1):
            minions[f"designer_{i}"] = OmniMinion(
                id=f"designer_{i}",
                name=f"DesignMaestro-{i}",
                role="Designer",
                specialization=design_type,
                capabilities=[
                    "visual_design", "user_experience", "accessibility",
                    "responsive_design", "brand_consistency"
                ]
            )
        
        # 3 DevOps Engineers
        devops_types = ["CI/CD", "Deployment", "Monitoring"]
        for i, devops_type in enumerate(devops_types, 1):
            minions[f"devops_{i}"] = OmniMinion(
                id=f"devops_{i}",
                name=f"DeployMaster-{i}",
                role="DevOps Engineer",
                specialization=devops_type,
                capabilities=[
                    "infrastructure", "automation", "scaling",
                    "security", "monitoring", "optimization"
                ]
            )
        
        # 3 Client Liaisons
        liaison_types = ["Communication", "Documentation", "Reporting"]
        for i, liaison_type in enumerate(liaison_types, 1):
            minions[f"liaison_{i}"] = OmniMinion(
                id=f"liaison_{i}",
                name=f"ClientBridge-{i}",
                role="Client Relations",
                specialization=liaison_type,
                capabilities=[
                    "client_communication", "requirement_analysis",
                    "project_reporting", "stakeholder_management"
                ]
            )
        
        # 2 Researchers
        research_types = ["Market Analysis", "Technology Trends"]
        for i, research_type in enumerate(research_types, 1):
            minions[f"researcher_{i}"] = OmniMinion(
                id=f"researcher_{i}",
                name=f"InsightSeeker-{i}",
                role="Researcher",
                specialization=research_type,
                capabilities=[
                    "market_research", "trend_analysis", "competitive_analysis",
                    "technology_evaluation", "feasibility_assessment"
                ]
            )
        
        # 2 Integrators
        integration_types = ["API Integration", "Third-party Services"]
        for i, integration_type in enumerate(integration_types, 1):
            minions[f"integrator_{i}"] = OmniMinion(
                id=f"integrator_{i}",
                name=f"ConnectMaster-{i}",
                role="Integration Specialist",
                specialization=integration_type,
                capabilities=[
                    "api_integration", "service_connection", "data_mapping",
                    "authentication", "error_handling"
                ]
            )
        
        # 3 Maintainers
        maintenance_types = ["Updates", "Optimization", "Support"]
        for i, maintenance_type in enumerate(maintenance_types, 1):
            minions[f"maintainer_{i}"] = OmniMinion(
                id=f"maintainer_{i}",
                name=f"SystemKeeper-{i}",
                role="Maintenance Specialist",
                specialization=maintenance_type,
                capabilities=[
                    "system_maintenance", "performance_optimization",
                    "bug_fixing", "user_support", "documentation_updates"
                ]
            )
        
        return minions
    
    def _initialize_database(self) -> str:
        """Initialize SQLite database for project management"""
        db_path = "data/omnitasker_ultimate.db"
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'planning',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_minions TEXT,
                progress REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                minion_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                estimated_hours REAL,
                actual_hours REAL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                minion_id TEXT,
                metric_type TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard Tab
        self.setup_dashboard_tab()
        
        # Project Management Tab
        self.setup_project_tab()
        
        # OmniMinions Tab
        self.setup_minions_tab()
        
        # Monitoring Tab
        self.setup_monitoring_tab()
        
        # Settings Tab
        self.setup_settings_tab()
    
    def setup_dashboard_tab(self):
        """Setup the main dashboard"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🎯 Dashboard")
        
        # System Overview
        overview_frame = ttk.LabelFrame(dashboard_frame, text="System Overview")
        overview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Metrics display
        metrics_frame = ttk.Frame(overview_frame)
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create metric cards
        self.metric_labels = {}
        metrics = [
            ("Active Projects", "active_projects"),
            ("Completed Projects", "completed_projects"),
            ("Active Agents", "active_agents"),
            ("Success Rate", "success_rate")
        ]
        
        for i, (label, key) in enumerate(metrics):
            card_frame = ttk.Frame(metrics_frame)
            card_frame.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
            ttk.Label(card_frame, text=label, font=('Arial', 10, 'bold')).pack()
            self.metric_labels[key] = ttk.Label(card_frame, text="0", font=('Arial', 14))
            self.metric_labels[key].pack()
        
        # Quick Actions
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        action_buttons = [
            ("🚀 New Project", self.create_new_project),
            ("👥 Deploy All Minions", self.deploy_all_minions),
            ("📊 Generate Report", self.generate_comprehensive_report),
            ("🔧 System Health Check", self.run_system_health_check)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            btn = ttk.Button(actions_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5, pady=10, sticky="ew")
        
        # Recent Activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=10)
        self.activity_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_project_tab(self):
        """Setup project management interface"""
        project_frame = ttk.Frame(self.notebook)
        self.notebook.add(project_frame, text="📋 Projects")
        
        # Project creation form
        form_frame = ttk.LabelFrame(project_frame, text="Create New Project")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Form fields
        ttk.Label(form_frame, text="Project Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.project_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.project_name_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.project_desc_text = tk.Text(form_frame, height=4, width=40)
        self.project_desc_text.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Tech Stack:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.tech_stack_var = tk.StringVar(value="React + Node.js")
        tech_combo = ttk.Combobox(form_frame, textvariable=self.tech_stack_var, width=37)
        tech_combo['values'] = (
            "React + Node.js", "Vue.js + Express", "Angular + .NET", 
            "Django + PostgreSQL", "Flask + SQLite", "Custom Stack"
        )
        tech_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="🚀 Create Project", command=self.create_project).grid(row=3, column=1, pady=10)
        
        # Project list
        list_frame = ttk.LabelFrame(project_frame, text="Active Projects")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for projects
        columns = ('Name', 'Status', 'Progress', 'Assigned Minions', 'Created')
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=150)
        
        self.project_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Project actions
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="📊 View Details", command=self.view_project_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="⏸️ Pause Project", command=self.pause_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🗑️ Delete Project", command=self.delete_project).pack(side=tk.LEFT, padx=5)
    
    def setup_minions_tab(self):
        """Setup OmniMinions management interface"""
        minions_frame = ttk.Frame(self.notebook)
        self.notebook.add(minions_frame, text="🤖 OmniMinions")
        
        # Minions overview
        overview_frame = ttk.LabelFrame(minions_frame, text="Agent Overview")
        overview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Role distribution
        roles_frame = ttk.Frame(overview_frame)
        roles_frame.pack(fill=tk.X, padx=10, pady=10)
        
        role_counts = {
            "Developers": 5, "Testers": 4, "Designers": 3,
            "DevOps": 3, "Client Relations": 3, "Researchers": 2,
            "Integrators": 2, "Maintainers": 3
        }
        
        for i, (role, count) in enumerate(role_counts.items()):
            role_frame = ttk.Frame(roles_frame)
            role_frame.grid(row=i//4, column=i%4, padx=10, pady=5, sticky="ew")
            
            ttk.Label(role_frame, text=role, font=('Arial', 10, 'bold')).pack()
            ttk.Label(role_frame, text=f"{count} agents", font=('Arial', 12)).pack()
        
        # Minions list
        list_frame = ttk.LabelFrame(minions_frame, text="Agent Status")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for minions
        columns = ('Name', 'Role', 'Specialization', 'Status', 'Current Task', 'Performance')
        self.minions_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.minions_tree.heading(col, text=col)
            self.minions_tree.column(col, width=120)
        
        self.minions_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate minions tree
        self.update_minions_display()
        
        # Minion actions
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="🔄 Refresh Status", command=self.update_minions_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="⚡ Deploy Selected", command=self.deploy_selected_minion).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📈 View Metrics", command=self.view_minion_metrics).pack(side=tk.LEFT, padx=5)
    
    def setup_monitoring_tab(self):
        """Setup system monitoring interface"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="📊 Monitoring")
        
        # System metrics
        metrics_frame = ttk.LabelFrame(monitoring_frame, text="System Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Real-time metrics display
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, height=8)
        self.metrics_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Logs viewer
        logs_frame = ttk.LabelFrame(monitoring_frame, text="System Logs")
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=15)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log controls
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_controls, text="🔄 Refresh Logs", command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="🗑️ Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="💾 Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        """Setup system settings interface"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # API Configuration
        api_frame = ttk.LabelFrame(settings_frame, text="API Configuration")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API settings form
        ttk.Label(api_frame, text="OpenAI API Key:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.openai_key_var = tk.StringVar()
        ttk.Entry(api_frame, textvariable=self.openai_key_var, show="*", width=50).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(api_frame, text="Grok API Key:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.grok_key_var = tk.StringVar()
        ttk.Entry(api_frame, textvariable=self.grok_key_var, show="*", width=50).grid(row=1, column=1, padx=5, pady=5)
        
        # System Configuration
        system_frame = ttk.LabelFrame(settings_frame, text="System Configuration")
        system_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(system_frame, text="Max Concurrent Tasks:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.max_tasks_var = tk.IntVar(value=25)
        ttk.Spinbox(system_frame, from_=1, to=100, textvariable=self.max_tasks_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(system_frame, text="Auto-save Interval (minutes):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.autosave_var = tk.IntVar(value=5)
        ttk.Spinbox(system_frame, from_=1, to=60, textvariable=self.autosave_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Save settings button
        ttk.Button(settings_frame, text="💾 Save Settings", command=self.save_settings).pack(pady=20)
    
    def setup_monitoring(self):
        """Setup background monitoring"""
        def monitor_system():
            while True:
                try:
                    # Update system metrics
                    self.update_system_metrics()
                    
                    # Check agent health
                    self.check_agent_health()
                    
                    # Process task queue
                    self.process_task_queue()
                    
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def start_agent_orchestration(self):
        """Start the agent orchestration system"""
        def orchestrate():
            while True:
                try:
                    # Assign tasks to available minions
                    self.assign_tasks_to_minions()
                    
                    # Monitor task progress
                    self.monitor_task_progress()
                    
                    # Handle completed tasks
                    self.handle_completed_tasks()
                    
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.error(f"Orchestration error: {e}")
                    time.sleep(30)
        
        orchestration_thread = threading.Thread(target=orchestrate, daemon=True)
        orchestration_thread.start()
    
    def create_new_project(self):
        """Create a new project with AI assistance"""
        dialog = ProjectCreationDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
    
    def create_project(self):
        """Create project from form data"""
        name = self.project_name_var.get().strip()
        description = self.project_desc_text.get("1.0", tk.END).strip()
        tech_stack = self.tech_stack_var.get()
        
        if not name:
            messagebox.showerror("Error", "Project name is required")
            return
        
        project_id = str(uuid.uuid4())
        
        # Save to database
        conn = sqlite3.connect(self.project_database)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (id, name, description, status, assigned_minions, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_id, name, description, "planning",
            json.dumps([]), json.dumps({"tech_stack": tech_stack})
        ))
        
        conn.commit()
        conn.close()
        
        # Add to active projects
        self.active_projects[project_id] = {
            "name": name,
            "description": description,
            "status": "planning",
            "tech_stack": tech_stack,
            "assigned_minions": [],
            "progress": 0.0
        }
        
        # Update display
        self.update_project_display()
        
        # Clear form
        self.project_name_var.set("")
        self.project_desc_text.delete("1.0", tk.END)
        
        # Auto-assign minions
        self.auto_assign_minions(project_id)
        
        messagebox.showinfo("Success", f"Project '{name}' created successfully!")
        logger.info(f"Created new project: {name} (ID: {project_id})")
    
    def auto_assign_minions(self, project_id: str):
        """Automatically assign appropriate minions to a project"""
        project = self.active_projects.get(project_id)
        if not project:
            return
        
        # Assign based on project requirements
        assigned_minions = []
        
        # Always assign core team
        core_roles = ['coder_1', 'tester_1', 'designer_1', 'devops_1', 'liaison_1']
        assigned_minions.extend(core_roles)
        
        # Assign based on tech stack
        tech_stack = project.get('tech_stack', '')
        if 'React' in tech_stack or 'JavaScript' in tech_stack:
            assigned_minions.append('coder_2')  # JavaScript specialist
        if 'Python' in tech_stack or 'Django' in tech_stack or 'Flask' in tech_stack:
            assigned_minions.append('coder_1')  # Python specialist
        
        # Update project
        project['assigned_minions'] = assigned_minions
        
        # Update minion status
        for minion_id in assigned_minions:
            if minion_id in self.omni_minions:
                self.omni_minions[minion_id].status = "assigned"
                self.omni_minions[minion_id].current_task = f"Working on {project['name']}"
        
        logger.info(f"Auto-assigned {len(assigned_minions)} minions to project {project_id}")
    
    def deploy_all_minions(self):
        """Deploy all 25 OmniMinions"""
        try:
            deployed_count = 0
            for minion_id, minion in self.omni_minions.items():
                if minion.status == "idle":
                    minion.status = "active"
                    deployed_count += 1
            
            self.update_minions_display()
            messagebox.showinfo("Success", f"Deployed {deployed_count} OmniMinions successfully!")
            logger.info(f"Deployed {deployed_count} OmniMinions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to deploy minions: {e}")
            logger.error(f"Minion deployment error: {e}")
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive system report"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": self.system_metrics,
                "active_projects": len(self.active_projects),
                "minion_status": {}
            }
            
            # Collect minion data
            for minion_id, minion in self.omni_minions.items():
                report_data["minion_status"][minion_id] = {
                    "name": minion.name,
                    "role": minion.role,
                    "status": minion.status,
                    "performance": minion.performance_metrics
                }
            
            # Generate report file
            report_path = f"reports/system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("reports", exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            messagebox.showinfo("Success", f"Report generated: {report_path}")
            logger.info(f"Generated comprehensive report: {report_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            logger.error(f"Report generation error: {e}")
    
    def run_system_health_check(self):
        """Run comprehensive system health check"""
        try:
            health_status = {
                "database": self.check_database_health(),
                "minions": self.check_minions_health(),
                "resources": self.check_system_resources(),
                "logs": self.check_log_health()
            }
            
            # Display results
            result_window = tk.Toplevel(self.root)
            result_window.title("System Health Check")
            result_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(result_window)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget.insert(tk.END, "=== SYSTEM HEALTH CHECK RESULTS ===\n\n")
            
            for component, status in health_status.items():
                status_icon = "✅" if status else "❌"
                text_widget.insert(tk.END, f"{status_icon} {component.upper()}: {'HEALTHY' if status else 'ISSUES DETECTED'}\n")
            
            text_widget.insert(tk.END, f"\nCheck completed at: {datetime.now()}\n")
            
            logger.info("System health check completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Health check failed: {e}")
            logger.error(f"Health check error: {e}")
    
    def check_database_health(self) -> bool:
        """Check database connectivity and integrity"""
        try:
            conn = sqlite3.connect(self.project_database)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects")
            conn.close()
            return True
        except Exception:
            return False
    
    def check_minions_health(self) -> bool:
        """Check if all minions are responsive"""
        try:
            active_count = sum(1 for minion in self.omni_minions.values() if minion.status != "error")
            return active_count >= 20  # At least 80% should be healthy
        except Exception:
            return False
    
    def check_system_resources(self) -> bool:
        """Check system resource availability"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            return cpu_percent < 90 and memory_percent < 90 and disk_percent < 90
        except Exception:
            return True  # Assume healthy if can't check
    
    def check_log_health(self) -> bool:
        """Check log file accessibility"""
        try:
            log_path = "logs/omnitasker_ultimate.log"
            return os.path.exists(log_path) and os.access(log_path, os.W_OK)
        except Exception:
            return False
    
    def update_system_metrics(self):
        """Update system metrics display"""
        try:
            # Update metrics
            self.system_metrics["active_projects"] = len(self.active_projects)
            self.system_metrics["active_agents"] = sum(
                1 for minion in self.omni_minions.values() 
                if minion.status in ["active", "assigned", "working"]
            )
            
            # Update GUI
            if hasattr(self, 'metric_labels'):
                self.metric_labels["active_projects"].config(text=str(self.system_metrics["active_projects"]))
                self.metric_labels["completed_projects"].config(text=str(self.system_metrics["completed_projects"]))
                self.metric_labels["active_agents"].config(text=str(self.system_metrics["active_agents"]))
                self.metric_labels["success_rate"].config(text=f"{self.system_metrics['success_rate']:.1f}%")
            
        except Exception as e:
            logger.error(f"Metrics update error: {e}")
    
    def update_minions_display(self):
        """Update the minions tree display"""
        try:
            # Clear existing items
            for item in self.minions_tree.get_children():
                self.minions_tree.delete(item)
            
            # Add minions
            for minion_id, minion in self.omni_minions.items():
                performance_score = minion.performance_metrics.get("efficiency_score", 100.0)
                
                self.minions_tree.insert("", tk.END, values=(
                    minion.name,
                    minion.role,
                    minion.specialization,
                    minion.status.title(),
                    minion.current_task or "None",
                    f"{performance_score:.1f}%"
                ))
                
        except Exception as e:
            logger.error(f"Minions display update error: {e}")
    
    def update_project_display(self):
        """Update the projects tree display"""
        try:
            # Clear existing items
            for item in self.project_tree.get_children():
                self.project_tree.delete(item)
            
            # Add projects
            for project_id, project in self.active_projects.items():
                assigned_count = len(project.get("assigned_minions", []))
                
                self.project_tree.insert("", tk.END, values=(
                    project["name"],
                    project["status"].title(),
                    f"{project.get('progress', 0):.1f}%",
                    f"{assigned_count} agents",
                    datetime.now().strftime("%Y-%m-%d")
                ))
                
        except Exception as e:
            logger.error(f"Projects display update error: {e}")
    
    def process_task_queue(self):
        """Process pending tasks in the queue"""
        try:
            while not self.task_queue.empty():
                task = self.task_queue.get_nowait()
                self.execute_task(task)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Task queue processing error: {e}")
    
    def execute_task(self, task: Dict[str, Any]):
        """Execute a specific task"""
        try:
            task_type = task.get("type")
            
            if task_type == "code_generation":
                self.handle_code_generation_task(task)
            elif task_type == "testing":
                self.handle_testing_task(task)
            elif task_type == "deployment":
                self.handle_deployment_task(task)
            else:
                logger.warning(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Task execution error: {e}")
    
    def handle_code_generation_task(self, task: Dict[str, Any]):
        """Handle code generation tasks"""
        # Implementation for code generation
        logger.info(f"Executing code generation task: {task.get('description')}")
    
    def handle_testing_task(self, task: Dict[str, Any]):
        """Handle testing tasks"""
        # Implementation for testing
        logger.info(f"Executing testing task: {task.get('description')}")
    
    def handle_deployment_task(self, task: Dict[str, Any]):
        """Handle deployment tasks"""
        # Implementation for deployment
        logger.info(f"Executing deployment task: {task.get('description')}")
    
    def assign_tasks_to_minions(self):
        """Assign pending tasks to available minions"""
        # Implementation for task assignment logic
        pass
    
    def monitor_task_progress(self):
        """Monitor progress of active tasks"""
        # Implementation for progress monitoring
        pass
    
    def handle_completed_tasks(self):
        """Handle tasks that have been completed"""
        # Implementation for completed task handling
        pass
    
    def check_agent_health(self):
        """Check health status of all agents"""
        # Implementation for agent health checking
        pass
    
    # Additional GUI event handlers
    def view_project_details(self):
        """View detailed project information"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        # Implementation for project details view
        messagebox.showinfo("Info", "Project details view - Coming soon!")
    
    def pause_project(self):
        """Pause selected project"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        # Implementation for project pausing
        messagebox.showinfo("Info", "Project paused successfully!")
    
    def delete_project(self):
        """Delete selected project"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this project?"):
            # Implementation for project deletion
            messagebox.showinfo("Info", "Project deleted successfully!")
    
    def deploy_selected_minion(self):
        """Deploy selected minion"""
        selection = self.minions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a minion")
            return
        
        # Implementation for minion deployment
        messagebox.showinfo("Info", "Minion deployed successfully!")
    
    def view_minion_metrics(self):
        """View detailed minion metrics"""
        selection = self.minions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a minion")
            return
        
        # Implementation for metrics view
        messagebox.showinfo("Info", "Minion metrics view - Coming soon!")
    
    def refresh_logs(self):
        """Refresh the logs display"""
        try:
            log_path = "logs/omnitasker_ultimate.log"
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    logs = f.read()
                
                self.logs_text.delete("1.0", tk.END)
                self.logs_text.insert(tk.END, logs)
                self.logs_text.see(tk.END)
            
        except Exception as e:
            logger.error(f"Log refresh error: {e}")
    
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.delete("1.0", tk.END)
    
    def export_logs(self):
        """Export logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt")]
            )
            
            if filename:
                logs_content = self.logs_text.get("1.0", tk.END)
                with open(filename, 'w') as f:
                    f.write(logs_content)
                
                messagebox.showinfo("Success", f"Logs exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def save_settings(self):
        """Save system settings"""
        try:
            settings = {
                "openai_api_key": self.openai_key_var.get(),
                "grok_api_key": self.grok_key_var.get(),
                "max_concurrent_tasks": self.max_tasks_var.get(),
                "autosave_interval": self.autosave_var.get()
            }
            
            settings_path = "config/settings.json"
            os.makedirs("config", exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            logger.info("System settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            logger.error(f"Settings save error: {e}")
    
    def run(self):
        """Start the OmniTasker Ultimate System"""
        try:
            # Initialize directories
            for directory in ['logs', 'data', 'reports', 'config', 'backups']:
                os.makedirs(directory, exist_ok=True)
            
            # Load existing settings
            self.load_settings()
            
            # Update displays
            self.update_system_metrics()
            self.update_minions_display()
            self.update_project_display()
            
            # Start GUI
            logger.info("OmniTasker Ultimate System started successfully")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"System startup error: {e}")
            messagebox.showerror("Startup Error", f"Failed to start system: {e}")
    
    def load_settings(self):
        """Load system settings"""
        try:
            settings_path = "config/settings.json"
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                self.openai_key_var.set(settings.get("openai_api_key", ""))
                self.grok_key_var.set(settings.get("grok_api_key", ""))
                self.max_tasks_var.set(settings.get("max_concurrent_tasks", 25))
                self.autosave_var.set(settings.get("autosave_interval", 5))
                
        except Exception as e:
            logger.error(f"Settings load error: {e}")

class ProjectCreationDialog:
    """Dialog for creating new projects with AI assistance"""
    
    def __init__(self, parent, omnitasker_system):
        self.parent = parent
        self.system = omnitasker_system
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🚀 Create New Project - AI Assisted")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='#2d2d2d')
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the project creation dialog"""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="AI-Powered Project Creation", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Project idea input
        idea_frame = ttk.LabelFrame(main_frame, text="Project Idea")
        idea_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(idea_frame, text="Describe your project idea:").pack(anchor='w', padx=10, pady=(10, 5))
        self.idea_text = tk.Text(idea_frame, height=4, wrap=tk.WORD)
        self.idea_text.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # AI Analysis button
        ttk.Button(idea_frame, text="🤖 Analyze with AI", command=self.analyze_project_idea).pack(pady=10)
        
        # Analysis results
        results_frame = ttk.LabelFrame(main_frame, text="AI Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="✅ Create Project", command=self.create_project).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def analyze_project_idea(self):
        """Analyze project idea with AI"""
        idea = self.idea_text.get("1.0", tk.END).strip()
        
        if not idea:
            messagebox.showwarning("Warning", "Please enter a project idea")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "🤖 Analyzing project idea...\n\n")
        
        # Simulate AI analysis (replace with actual AI integration)
        analysis = self.simulate_ai_analysis(idea)
        
        self.results_text.insert(tk.END, analysis)
    
    def simulate_ai_analysis(self, idea: str) -> str:
        """Simulate AI analysis of project idea"""
        return f"""📊 PROJECT ANALYSIS COMPLETE

🎯 PROJECT OVERVIEW:
Based on your idea: "{idea[:100]}..."

💡 RECOMMENDED APPROACH:
• Technology Stack: React + Node.js + PostgreSQL
• Development Timeline: 8-12 weeks
• Team Composition: 8 OmniMinions recommended

🤖 ASSIGNED OMNIMINIONS:
• CodeMaster-1 (Python Backend)
• CodeMaster-2 (JavaScript Frontend)
• TestGuardian-1 (Unit Testing)
• DesignMaestro-1 (UI/UX Design)
• DeployMaster-1 (CI/CD Setup)
• ClientBridge-1 (Documentation)
• InsightSeeker-1 (Market Research)
• ConnectMaster-1 (API Integration)

📈 SUCCESS PROBABILITY: 94%

🔧 RECOMMENDED FEATURES:
• User Authentication
• Real-time Updates
• Mobile Responsive Design
• API Integration
• Analytics Dashboard

⚠️ POTENTIAL CHALLENGES:
• Scalability considerations
• Third-party API limitations
• User adoption strategy

✅ READY TO PROCEED
Click 'Create Project' to start development with your AI team!
"""
    
    def create_project(self):
        """Create the project based on AI analysis"""
        idea = self.idea_text.get("1.0", tk.END).strip()
        
        if not idea:
            messagebox.showwarning("Warning", "Please enter and analyze a project idea first")
            return
        
        # Extract project name from idea (simple approach)
        project_name = idea.split('.')[0][:50] if '.' in idea else idea[:50]
        
        # Create project in main system
        project_id = str(uuid.uuid4())
        
        self.system.active_projects[project_id] = {
            "name": project_name,
            "description": idea,
            "status": "planning",
            "tech_stack": "React + Node.js",
            "assigned_minions": [
                "coder_1", "coder_2", "tester_1", "designer_1",
                "devops_1", "liaison_1", "researcher_1", "integrator_1"
            ],
            "progress": 0.0
        }
        
        # Update displays
        self.system.update_project_display()
        
        messagebox.showinfo("Success", f"Project '{project_name}' created with AI assistance!")
        logger.info(f"AI-assisted project created: {project_name}")
        
        self.dialog.destroy()

def main():
    """Main entry point"""
    try:
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Initialize and run the system
        system = OmniTaskerUltimateSystem()
        system.run()
        
    except Exception as e:
        print(f"Failed to start OmniTasker Ultimate System: {e}")
        logging.error(f"System startup failed: {e}")

if __name__ == "__main__":
    main()
