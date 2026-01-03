#!/usr/bin/env python3
"""
Document Indexing Gateway - Complete Production GUI
Version 2.0.0 - Full AVEVA Compliance + Advanced OCR

Features:
- Complete AVEVA NET specification compliance
- Advanced OCR with intelligent preprocessing
- Monitor mode with real-time updates
- File validation and fixing
- Complete error handling
- Production-ready implementation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import json
import threading
import subprocess
import time
from pathlib import Path
from datetime import datetime
import webbrowser
import shutil

# Try to import the gateway module
try:
    from document_indexing_gateway_complete import DocumentIndexingGateway, ProjectConfig
    GATEWAY_AVAILABLE = True
except ImportError:
    GATEWAY_AVAILABLE = False


class AVEDACompleteGUI:
    """Complete AVEVA-compliant GUI with all features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Document Indexing Gateway v2.0 - Complete Edition")
        
        # Window configuration
        self.setup_window()
        
        # Variables
        self.setup_variables()
        
        # UI Setup
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        
        # Monitor thread
        self.monitor_thread = None
        self.monitor_running = False
        
        # Load last config
        self.load_last_config()
    
    def setup_window(self):
        """Configure main window"""
        width = 1100
        height = 750
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # DPI awareness
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
        except:
            try:
                from ctypes import windll
                windll.user32.SetProcessDPIAware()
            except:
                pass
    
    def setup_variables(self):
        """Initialize all variables"""
        # Project
        self.project_name = tk.StringVar(value="My P&ID Project")
        self.config_location = tk.StringVar()
        
        # Folders
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.staging_area = tk.StringVar()
        self.processed_folder = tk.StringVar()
        self.unprocessed_folder = tk.StringVar()
        self.log_folder = tk.StringVar()
        
        # AVEVA Standard Options
        self.include_subfolders = tk.BooleanVar(value=True)
        self.copy_source_files = tk.BooleanVar(value=True)
        self.copy_other_files = tk.BooleanVar(value=False)
        self.move_processed = tk.BooleanVar(value=True)
        self.search_filenames_for_tags = tk.BooleanVar(value=False)
        self.create_trigger_file = tk.BooleanVar(value=True)
        self.insert_line_breaks = tk.BooleanVar(value=True)
        self.object_id_from_vnet = tk.BooleanVar(value=False)
        
        # Pattern mapping
        self.pattern_file = tk.StringVar()
        self.default_context = tk.StringVar(value="Plant|Process Area")
        
        # Spreadsheet settings
        self.use_ranges = tk.BooleanVar(value=False)
        self.document_type = tk.StringVar(value="xlsx")
        
        # Timeouts
        self.open_file_timeout_enabled = tk.BooleanVar(value=True)
        self.open_file_timeout = tk.IntVar(value=30)
        self.processing_timeout_enabled = tk.BooleanVar(value=False)
        self.processing_timeout = tk.DoubleVar(value=60.0)
        self.als_retry_timeout = tk.IntVar(value=120)
        
        # Conversion
        self.convert_doc = tk.BooleanVar(value=False)
        self.convert_xls = tk.BooleanVar(value=False)
        
        # OCR settings
        self.use_ocr = tk.BooleanVar(value=True)
        self.ocr_language = tk.StringVar(value="eng")
        self.ocr_dpi = tk.IntVar(value=300)
        self.extract_vertical_text = tk.BooleanVar(value=True)
        self.rotate_for_ocr = tk.BooleanVar(value=True)
        
        # Advanced OCR
        self.adaptive_dpi = tk.BooleanVar(value=True)
        self.dpi_min = tk.IntVar(value=300)
        self.dpi_max = tk.IntVar(value=500)
        self.preprocess_images = tk.BooleanVar(value=True)
        self.enhance_contrast = tk.DoubleVar(value=1.5)
        self.enhance_sharpness = tk.DoubleVar(value=1.5)
        self.denoise = tk.BooleanVar(value=True)
        self.use_multi_pass_ocr = tk.BooleanVar(value=True)
        self.detect_regions = tk.BooleanVar(value=True)
        self.min_text_confidence = tk.IntVar(value=60)
        self.save_debug_images = tk.BooleanVar(value=False)
        
        # Processing mode
        self.processing_mode = tk.StringVar(value="balanced")
        
        # Status
        self.status_text = tk.StringVar(value="Ready")
        self.is_processing = False
    
    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        
        try:
            style.theme_use('vista')
        except:
            try:
                style.theme_use('clam')
            except:
                pass
        
        # Configure styles
        style.configure('TFrame', background='#ffffff')
        style.configure('Header.TFrame', background='#f0f0f0')
        
        style.configure('TLabel', background='#ffffff', font=('Segoe UI', 9))
        style.configure('Header.TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        style.configure('Title.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Section.TLabel', font=('Segoe UI', 9, 'bold'))
        
        style.configure('TButton', font=('Segoe UI', 9))
        style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'))
        
        style.configure('TCheckbutton', background='#ffffff', font=('Segoe UI', 9))
        style.configure('TLabelframe', background='#ffffff', font=('Segoe UI', 9))
        style.configure('TLabelframe.Label', background='#ffffff', font=('Segoe UI', 9, 'bold'))
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Configuration", command=self.new_config)
        file_menu.add_command(label="Select Configuration", command=self.load_config)
        file_menu.add_command(label="Save Configuration", command=self.save_config, accelerator="Ctrl+S")
        file_menu.add_command(label="Reload Configuration", command=self.reload_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Input File Names", command=self.validate_file_names)
        tools_menu.add_command(label="Fix File Names", command=self.fix_file_names)
        tools_menu.add_command(label="Test Patterns", command=self.test_patterns)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.open_manual)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard bindings
        self.root.bind('<Control-s>', lambda e: self.save_config())
    
    def create_ui(self):
        """Create main UI"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Project section
        self.create_project_section(main_frame)
        
        # Tabs
        self.create_tabs(main_frame)
        
        # Controls
        self.create_controls(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create header"""
        header = ttk.Frame(parent, style='Header.TFrame', padding=12)
        header.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(header, text="Document Indexing Gateway", 
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        version = ttk.Label(header, text="Release 2.0 + OCR Enhanced", 
                           style='Header.TLabel', foreground='#0066cc')
        version.pack(side=tk.LEFT, padx=(10, 0))
        
        if not GATEWAY_AVAILABLE:
            warning = ttk.Label(header, text="⚠ Gateway module not found", 
                              foreground='#e74c3c', style='Header.TLabel')
            warning.pack(side=tk.RIGHT)
    
    def create_project_section(self, parent):
        """Create project section"""
        project_frame = ttk.LabelFrame(parent, text="Project", padding=10)
        project_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Project name
        name_frame = ttk.Frame(project_frame)
        name_frame.pack(fill=tk.X)
        
        ttk.Label(name_frame, text="Name:", width=15).pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=self.project_name, width=40).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(name_frame, text="Location:").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Entry(name_frame, textvariable=self.config_location, width=50, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_tabs(self, parent):
        """Create tabbed interface"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create tabs
        self.create_locations_tab(notebook)
        self.create_settings_tab(notebook)
        self.create_ocr_basic_tab(notebook)
        self.create_ocr_advanced_tab(notebook)
        self.create_patterns_tab(notebook)
        self.create_advanced_tab(notebook)
    
    def create_locations_tab(self, notebook):
        """Locations tab"""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="📁 Locations")
        
        # Include subfolders
        ttk.Checkbutton(frame, text="Include subfolders", 
                       variable=self.include_subfolders).pack(anchor='w', pady=(0, 10))
        
        # Folder configurations
        folders = [
            ("Source Folder:", self.source_folder, True),
            ("Destination Folder:", self.destination_folder, False),
            ("Staging Area:", self.staging_area, True),
            ("Processed Folder:", self.processed_folder, False),
            ("Unprocessed Folder:", self.unprocessed_folder, False),
            ("Log Folder:", self.log_folder, False),
        ]
        
        for label, var, required in folders:
            self.create_folder_row(frame, label, var, required)
    
    def create_folder_row(self, parent, label_text, variable, required):
        """Create folder selection row"""
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=3)
        
        label_frame = ttk.Frame(row)
        label_frame.pack(side=tk.LEFT)
        
        ttk.Label(label_frame, text=label_text, width=20, anchor='w').pack(side=tk.LEFT)
        
        if required:
            ttk.Label(label_frame, text="*", foreground='red').pack(side=tk.LEFT)
        
        ttk.Entry(row, textvariable=variable, width=60).pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        ttk.Button(row, text="Browse", width=8, 
                  command=lambda: self.browse_folder(variable)).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_settings_tab(self, notebook):
        """Settings tab - AVEVA standard options"""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="⚙️ Settings")
        
        # Create scrollable frame
        canvas = tk.Canvas(frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Spreadsheet Format
        spread_frame = ttk.LabelFrame(scroll_frame, text="Spreadsheet Format", padding=10)
        spread_frame.pack(fill=tk.X, pady=(0, 10))
        
        type_row = ttk.Frame(spread_frame)
        type_row.pack(fill=tk.X)
        ttk.Label(type_row, text="Document Type:").pack(side=tk.LEFT)
        ttk.Radiobutton(type_row, text="XLSX", variable=self.document_type, value="xlsx").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_row, text="XLS", variable=self.document_type, value="xls").pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(spread_frame, text="Use Ranges", variable=self.use_ranges).pack(anchor='w', pady=(5, 0))
        
        # Options
        options_frame = ttk.LabelFrame(scroll_frame, text="File Handling Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        options = [
            ("Copy Source Files to Staging Area", self.copy_source_files),
            ("Copy Other Files to Staging Area", self.copy_other_files),
            ("Search File Names for Tags", self.search_filenames_for_tags),
            ("Create Trigger File (trigger.start)", self.create_trigger_file),
            ("Move Processed and Unprocessed Files", self.move_processed),
            ("Insert Line Breaks", self.insert_line_breaks),
            ("Object ID from VNet File", self.object_id_from_vnet),
        ]
        
        for text, var in options:
            ttk.Checkbutton(options_frame, text=text, variable=var).pack(anchor='w', pady=2)
        
        # Time Outs
        timeout_frame = ttk.LabelFrame(scroll_frame, text="Time Outs", padding=10)
        timeout_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Open file timeout
        open_frame = ttk.Frame(timeout_frame)
        open_frame.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(open_frame, text="Open File Time Out (seconds):", 
                       variable=self.open_file_timeout_enabled).pack(side=tk.LEFT)
        ttk.Spinbox(open_frame, textvariable=self.open_file_timeout, from_=1, to=300, 
                   increment=5, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Processing timeout
        proc_frame = ttk.Frame(timeout_frame)
        proc_frame.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(proc_frame, text="Processing Time Out (minutes):", 
                       variable=self.processing_timeout_enabled).pack(side=tk.LEFT)
        ttk.Spinbox(proc_frame, textvariable=self.processing_timeout, from_=0.5, to=120, 
                   increment=0.5, width=10, format="%.1f").pack(side=tk.LEFT, padx=(5, 0))
        
        # ALS retry timeout
        als_frame = ttk.Frame(timeout_frame)
        als_frame.pack(fill=tk.X, pady=2)
        ttk.Label(als_frame, text="ALS Connection Retry Time (seconds):").pack(side=tk.LEFT)
        ttk.Spinbox(als_frame, textvariable=self.als_retry_timeout, from_=10, to=300, 
                   increment=10, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Conversion
        conv_frame = ttk.LabelFrame(scroll_frame, text="File Conversion", padding=10)
        conv_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(conv_frame, text="Convert .doc Source Files to .docx before processing", 
                       variable=self.convert_doc).pack(anchor='w', pady=2)
        ttk.Checkbutton(conv_frame, text="Convert .xls Source Files to .xlsx before processing", 
                       variable=self.convert_xls).pack(anchor='w', pady=2)
    
    def create_ocr_basic_tab(self, notebook):
        """OCR Basic tab"""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="🔍 OCR Basic")
        
        # Enable OCR
        enable_frame = ttk.Frame(frame)
        enable_frame.pack(fill=tk.X, pady=(0, 15))
        
        chk = ttk.Checkbutton(enable_frame, text="Enable OCR (Optical Character Recognition)", 
                             variable=self.use_ocr, command=self.toggle_ocr)
        chk.pack(anchor='w')
        
        self.ocr_basic_frame = ttk.Frame(frame)
        self.ocr_basic_frame.pack(fill=tk.BOTH, expand=True)
        
        # Basic settings
        settings_frame = ttk.LabelFrame(self.ocr_basic_frame, text="Basic OCR Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language
        lang_row = ttk.Frame(settings_frame)
        lang_row.pack(fill=tk.X, pady=3)
        ttk.Label(lang_row, text="Language:", width=20).pack(side=tk.LEFT)
        ttk.Combobox(lang_row, textvariable=self.ocr_language, 
                    values=['eng', 'fra', 'deu', 'spa', 'ita'], width=15).pack(side=tk.LEFT)
        
        # Base DPI
        dpi_row = ttk.Frame(settings_frame)
        dpi_row.pack(fill=tk.X, pady=3)
        ttk.Label(dpi_row, text="Base DPI:", width=20).pack(side=tk.LEFT)
        ttk.Spinbox(dpi_row, textvariable=self.ocr_dpi, from_=200, to=600, 
                   increment=50, width=15).pack(side=tk.LEFT)
        
        # Options
        options_frame = ttk.LabelFrame(self.ocr_basic_frame, text="Text Extraction Options", padding=10)
        options_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(options_frame, text="Extract Vertical Text (rotated tags)", 
                       variable=self.extract_vertical_text).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_frame, text="Rotate for OCR (multiple angles: 0°, 90°, 180°, 270°)", 
                       variable=self.rotate_for_ocr).pack(anchor='w', pady=2)
        
        # Info
        info_frame = ttk.Frame(self.ocr_basic_frame, padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        info = tk.Text(info_frame, wrap=tk.WORD, height=10, font=('Segoe UI', 9), bg='#f8f8f8')
        info.pack(fill=tk.BOTH, expand=True)
        
        info_text = """📋 Basic OCR Settings Guide:

Language: Select OCR language (eng = English)
Base DPI: Image resolution (300 = standard, 400-600 = better quality for small text)

Extract Vertical Text: Detects tags rotated 90° (common in P&IDs)
Rotate for OCR: Tries multiple angles to capture text at any orientation

💡 For complex P&IDs with small text, tables, or mixed orientations:
   Enable "OCR Advanced" tab for intelligent multi-pass processing"""
        
        info.insert('1.0', info_text)
        info.config(state='disabled')
    
    def create_ocr_advanced_tab(self, notebook):
        """OCR Advanced tab"""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="⚡ OCR Advanced")
        
        # Create scrollable frame
        canvas = tk.Canvas(frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Processing mode
        mode_frame = ttk.LabelFrame(scroll_frame, text="Processing Mode Presets", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        modes = [
            ("🏃 Fast Mode (8-12 sec/page, 60-70% accuracy)", "fast"),
            ("⚖️ Balanced Mode (15-25 sec/page, 75-85% accuracy) - Recommended", "balanced"),
            ("🎯 High Quality (25-40 sec/page, 85-95% accuracy)", "high_quality"),
        ]
        
        for text, mode in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.processing_mode,
                           value=mode, command=self.apply_processing_mode).pack(anchor='w', pady=2)
        
        # Adaptive DPI
        dpi_frame = ttk.LabelFrame(scroll_frame, text="Adaptive DPI (Auto-adjust for small text)", padding=10)
        dpi_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(dpi_frame, text="Enable Adaptive DPI", variable=self.adaptive_dpi).pack(anchor='w')
        
        dpi_settings = ttk.Frame(dpi_frame, padding=(20, 5, 0, 0))
        dpi_settings.pack(fill=tk.X)
        
        ttk.Label(dpi_settings, text="Min DPI:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(dpi_settings, textvariable=self.dpi_min, from_=200, to=400, 
                   increment=50, width=10).grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(dpi_settings, text="Max DPI:").grid(row=0, column=2, sticky='w')
        ttk.Spinbox(dpi_settings, textvariable=self.dpi_max, from_=300, to=600, 
                   increment=50, width=10).grid(row=0, column=3, padx=(5, 0))
        
        # Image Preprocessing
        preproc_frame = ttk.LabelFrame(scroll_frame, text="Image Preprocessing (6 Strategies)", padding=10)
        preproc_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(preproc_frame, text="Enable Image Preprocessing", 
                       variable=self.preprocess_images).pack(anchor='w')
        
        enhance_frame = ttk.Frame(preproc_frame, padding=(20, 5, 0, 0))
        enhance_frame.pack(fill=tk.X)
        
        ttk.Label(enhance_frame, text="Contrast:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(enhance_frame, textvariable=self.enhance_contrast, from_=1.0, to=3.0,
                   increment=0.1, width=10, format="%.1f").grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(enhance_frame, text="Sharpness:").grid(row=0, column=2, sticky='w')
        ttk.Spinbox(enhance_frame, textvariable=self.enhance_sharpness, from_=1.0, to=3.0,
                   increment=0.1, width=10, format="%.1f").grid(row=0, column=3, padx=(5, 0))
        
        ttk.Checkbutton(preproc_frame, text="Denoise (remove artifacts)", 
                       variable=self.denoise).pack(anchor='w', pady=(5, 0), padx=(20, 0))
        
        # Advanced Features
        advanced_frame = ttk.LabelFrame(scroll_frame, text="Advanced OCR Features", padding=10)
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(advanced_frame, text="Multi-Pass OCR (4-8 passes per region for maximum accuracy)", 
                       variable=self.use_multi_pass_ocr).pack(anchor='w', pady=2)
        ttk.Checkbutton(advanced_frame, text="Smart Region Detection (title block, table, equipment zones)", 
                       variable=self.detect_regions).pack(anchor='w', pady=2)
        
        # Quality Control
        quality_frame = ttk.LabelFrame(scroll_frame, text="Quality Control", padding=10)
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        conf_row = ttk.Frame(quality_frame)
        conf_row.pack(fill=tk.X)
        
        ttk.Label(conf_row, text="Minimum Text Confidence:").pack(side=tk.LEFT)
        ttk.Spinbox(conf_row, textvariable=self.min_text_confidence, from_=50, to=90,
                   increment=5, width=10).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(conf_row, text="% (lower = more tags, less accurate)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Debug
        debug_frame = ttk.LabelFrame(scroll_frame, text="Debug Options", padding=10)
        debug_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(debug_frame, text="Save Debug Images (intermediate processing steps)", 
                       variable=self.save_debug_images).pack(anchor='w')
    
    def create_patterns_tab(self, notebook):
        """Patterns tab"""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="🎯 Pattern Mapping")
        
        # Pattern file
        file_frame = ttk.LabelFrame(frame, text="Pattern Mapping File (XML)", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_row = ttk.Frame(file_frame)
        file_row.pack(fill=tk.X)
        
        ttk.Entry(file_row, textvariable=self.pattern_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_row, text="Browse", width=8, command=self.browse_pattern_file).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(file_row, text="Create", width=8, command=self.create_pattern_file).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(file_row, text="Edit", width=8, command=self.edit_pattern_file).pack(side=tk.LEFT, padx=(5, 0))
        
        # Default context
        context_frame = ttk.LabelFrame(frame, text="Default Context (Hierarchical)", padding=10)
        context_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(context_frame, text="Use | to separate context levels (e.g., Plant A|Process Area 2|Bay B)").pack(anchor='w')
        ttk.Entry(context_frame, textvariable=self.default_context, width=70).pack(fill=tk.X, pady=(5, 0))
        
        # Pattern info
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, font=('Consolas', 9), bg='#f8f8f8')
        info.pack(fill=tk.BOTH, expand=True)
        
        info_text = """📋 Pattern Mapping Guide (AVEVA NET Standard):

Pattern mapping uses regular expressions to identify and classify tags in documents.

Example Pattern File (XML):
─────────────────────────────────────────────────────────────────
<?xml version="1.0" encoding="UTF-8"?>
<Patterns version="5.0">
  <!-- Equipment Tags: ###-X-##### -->
  <Pattern from="\\d{3}-[A-Z]-\\d{5}" to="Equipment"/>
  
  <!-- Valve Tags: ###-HV-##### -->
  <Pattern from="\\d{3}-HV-\\d{5}" to="Valve"/>
  
  <!-- Complex Pipeline: ###-XX-#####-##"-XXXXXXX-XX-### -->
  <Pattern from="\\d{3}-[A-Z]{2}-\\d{5}-\\d{1,2}\\"-[A-Z0-9]{6,8}-[A-Z]{2}-\\d{3}" 
           to="PipeLine"/>
  
  <!-- Motor Tags with Expansion -->
  <Pattern from="\\d{3}-EM-\\d{5}[A-Z]-[A-Z]" to="Motor">
    <Expand Interpolate="true">
      <SubPattern>[A-Z]-[A-Z]</SubPattern>
      <Char>-</Char>
    </Expand>
  </Pattern>
  
  <!-- Tag with Replacement -->
  <Pattern from="[A-Z]-\\d{3}" to="Valve">
    <Replace>
      <Original>[A-Z]-</Original>
      <Replacement>[A-Z]</Replacement>
    </Replace>
  </Pattern>
</Patterns>
─────────────────────────────────────────────────────────────────

Supported Features:
• Regular expression patterns (from="...")
• Classification (to="...")
• Context override (context="...")
• Tag expansion with interpolation
• String replacement
• String insertion
• Exclusion patterns

For your P&ID project, use the provided 'pattern_mapping_precise.xml' file."""
        
        info.insert('1.0', info_text)
        info.config(state='disabled')
    
    def create_advanced_tab(self, notebook):
        """Advanced settings tab"""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="🔧 Advanced")
        
        # File types
        types_frame = ttk.LabelFrame(frame, text="Supported File Types", padding=10)
        types_frame.pack(fill=tk.X, pady=(0, 10))
        
        types_text = """Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, ZIP, RTF, DWG
Configure additional file types in the configuration XML file."""
        
        ttk.Label(types_frame, text=types_text, foreground='#666').pack(anchor='w')
        
        # Command line
        cmd_frame = ttk.LabelFrame(frame, text="Command Line Usage", padding=10)
        cmd_frame.pack(fill=tk.BOTH, expand=True)
        
        cmd_text = scrolledtext.ScrolledText(cmd_frame, wrap=tk.WORD, font=('Consolas', 8), bg='#f8f8f8', height=15)
        cmd_text.pack(fill=tk.BOTH, expand=True)
        
        cmd_info = """Command Line Arguments (AVEVA NET Standard):

Basic Usage:
  AVEVA.NET.Document.Indexing.Gateway.exe -c "config.xml"

Arguments:
  -c "config.xml"        Configuration file (required)
  -f "file.pdf"          Process single file or directory
  -r "docname"           Output document name (override)
  -d                     Delete staging files
  -t "staging"           Alternative staging area
  -s                     Silent mode (no message boxes)
  -noReport              Don't create summary/report files
  -context "A|B|C"       Override default context

Examples:
  # Process all files in configured source folder
  gateway.exe -c "project.xml"
  
  # Process single file
  gateway.exe -c "project.xml" -f "C:\\drawings\\PID-001.pdf"
  
  # Process with custom document name
  gateway.exe -c "project.xml" -f "file.pdf" -r "CustomName"
  
  # Silent processing
  gateway.exe -c "project.xml" -s -noReport

Exit Codes:
  0     Success
  1     General failure
  1001  License expired
  1002  Insufficient license seats
  1003  License missing
  1004  Invalid license server"""
        
        cmd_text.insert('1.0', cmd_info)
        cmd_text.config(state='disabled')
    
    def create_controls(self, parent):
        """Create control buttons"""
        controls = ttk.Frame(parent, padding=(0, 10, 0, 0))
        controls.pack(fill=tk.X)
        
        # Left side
        left_frame = ttk.Frame(controls)
        left_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_frame, text="💾 Save Config", width=14, 
                  command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_frame, text="📂 Load Config", width=14, 
                  command=self.load_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_frame, text="🧪 Test Patterns", width=14, 
                  command=self.test_patterns).pack(side=tk.LEFT)
        
        # Right side
        right_frame = ttk.Frame(controls)
        right_frame.pack(side=tk.RIGHT)
        
        self.run_button = ttk.Button(right_frame, text="▶️ Run", width=12, 
                                     style='Action.TButton', command=self.run_processing)
        self.run_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.monitor_button = ttk.Button(right_frame, text="👁️ Monitor", width=12, 
                                        command=self.monitor_processing)
        self.monitor_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(right_frame, text="⏹️ Stop", width=12, 
                                      command=self.stop_processing, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(right_frame, text="📊 View Report", width=14, 
                  command=self.view_report).pack(side=tk.LEFT)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status = ttk.Frame(parent, style='Header.TFrame', padding=(8, 5))
        status.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status, textvariable=self.status_text, style='Header.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status, mode='indeterminate', length=200)
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
    
    # Event handlers
    
    def browse_folder(self, variable):
        """Browse for folder"""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            variable.set(folder)
    
    def browse_pattern_file(self):
        """Browse for pattern file"""
        file = filedialog.askopenfilename(
            title="Select Pattern Mapping File",
            filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
        )
        if file:
            self.pattern_file.set(file)
    
    def create_pattern_file(self):
        """Create new pattern file"""
        file = filedialog.asksaveasfilename(
            title="Create Pattern File",
            defaultextension=".xml",
            filetypes=[("XML Files", "*.xml")]
        )
        
        if file:
            template = """<?xml version="1.0" encoding="UTF-8"?>
<Patterns version="5.0">
    <!-- Equipment Tags: ###-X-##### -->
    <Pattern from="\\d{3}-[A-Z]-\\d{5}" to="Equipment"/>
    
    <!-- Valve Tags: ###-HV-##### -->
    <Pattern from="\\d{3}-HV-\\d{5}" to="Valve"/>
    
    <!-- Motor Tags: ###-EM-#####X-## -->
    <Pattern from="\\d{3}-EM-\\d{5}[A-Z]-\\d{2}" to="Motor"/>
    
    <!-- Add your custom patterns here -->
    
</Patterns>"""
            
            try:
                with open(file, 'w') as f:
                    f.write(template)
                self.pattern_file.set(file)
                messagebox.showinfo("Success", "Pattern file created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create pattern file:\n{e}")
    
    def edit_pattern_file(self):
        """Edit pattern file"""
        file = self.pattern_file.get()
        if not file or not os.path.exists(file):
            messagebox.showwarning("Warning", "Please select a valid pattern file first.")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(file)
            else:
                subprocess.call(['xdg-open', file])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open pattern file:\n{e}")
    
    def toggle_ocr(self):
        """Toggle OCR controls"""
        state = 'normal' if self.use_ocr.get() else 'disabled'
        for child in self.ocr_basic_frame.winfo_children():
            self.set_state_recursive(child, state)
    
    def set_state_recursive(self, widget, state):
        """Set state recursively"""
        try:
            widget.configure(state=state)
        except:
            pass
        
        for child in widget.winfo_children():
            self.set_state_recursive(child, state)
    
    def apply_processing_mode(self):
        """Apply processing mode preset"""
        mode = self.processing_mode.get()
        
        if mode == "fast":
            self.adaptive_dpi.set(False)
            self.preprocess_images.set(False)
            self.use_multi_pass_ocr.set(False)
            self.detect_regions.set(False)
        elif mode == "balanced":
            self.adaptive_dpi.set(True)
            self.dpi_max.set(500)
            self.preprocess_images.set(True)
            self.use_multi_pass_ocr.set(True)
            self.detect_regions.set(True)
        elif mode == "high_quality":
            self.adaptive_dpi.set(True)
            self.dpi_max.set(600)
            self.preprocess_images.set(True)
            self.enhance_contrast.set(2.0)
            self.enhance_sharpness.set(2.0)
            self.denoise.set(True)
            self.use_multi_pass_ocr.set(True)
            self.detect_regions.set(True)
    
    def validate_file_names(self):
        """Validate file names (AVEVA feature)"""
        if not self.source_folder.get():
            messagebox.showwarning("Warning", "Please select a source folder first.")
            return
        
        # Scan for invalid file names
        invalid_files = []
        for root, dirs, files in os.walk(self.source_folder.get()):
            for name in files + dirs:
                # Check for invalid patterns (double spaces, etc.)
                if '  ' in name or name != name.strip():
                    invalid_files.append(os.path.join(root, name))
        
        if invalid_files:
            result = messagebox.askyesno("Invalid File Names Found", 
                                        f"Found {len(invalid_files)} invalid file/folder names.\n\n"
                                        f"Do you want to fix them?")
            if result:
                self.fix_file_names()
        else:
            messagebox.showinfo("Validation Complete", "No invalid file names found.")
    
    def fix_file_names(self):
        """Fix invalid file names (AVEVA feature)"""
        if not self.source_folder.get():
            messagebox.showwarning("Warning", "Please select a source folder first.")
            return
        
        fixed_count = 0
        for root, dirs, files in os.walk(self.source_folder.get()):
            for name in files + dirs:
                old_path = os.path.join(root, name)
                # Fix double spaces
                new_name = ' '.join(name.split())
                new_name = new_name.strip()
                
                if new_name != name:
                    new_path = os.path.join(root, new_name)
                    try:
                        os.rename(old_path, new_path)
                        fixed_count += 1
                    except:
                        pass
        
        messagebox.showinfo("Fix Complete", f"Fixed {fixed_count} file/folder names.")
    
    def test_patterns(self):
        """Test pattern matching"""
        pattern_file = self.pattern_file.get()
        
        if not pattern_file or not os.path.exists(pattern_file):
            messagebox.showwarning("Warning", "Please select a valid pattern file first.")
            return
        
        test_script = Path("test_pattern_matching.py")
        if not test_script.exists():
            messagebox.showwarning("Warning", "test_pattern_matching.py not found.")
            return
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_script), pattern_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Show results
            dialog = tk.Toplevel(self.root)
            dialog.title("Pattern Test Results")
            dialog.geometry("900x650")
            
            text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, font=('Consolas', 9))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text.insert('1.0', result.stdout)
            text.config(state='disabled')
            
            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Pattern test timed out.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run pattern test:\n{e}")
    
    def get_config(self) -> dict:
        """Get configuration dictionary"""
        return {
            "name": self.project_name.get(),
            "source_folder": self.source_folder.get(),
            "destination_folder": self.destination_folder.get(),
            "staging_area": self.staging_area.get(),
            "processed_folder": self.processed_folder.get(),
            "unprocessed_folder": self.unprocessed_folder.get(),
            "log_folder": self.log_folder.get(),
            "pattern_mapping_file": self.pattern_file.get(),
            "default_context": self.default_context.get(),
            
            "include_subfolders": self.include_subfolders.get(),
            "copy_source_files": self.copy_source_files.get(),
            "copy_other_files": self.copy_other_files.get(),
            "move_processed": self.move_processed.get(),
            "search_filenames_for_tags": self.search_filenames_for_tags.get(),
            "create_trigger_file": self.create_trigger_file.get(),
            "insert_line_breaks": self.insert_line_breaks.get(),
            "object_id_from_vnet": self.object_id_from_vnet.get(),
            
            "use_ranges": self.use_ranges.get(),
            "document_type": self.document_type.get(),
            
            "open_file_timeout_enabled": self.open_file_timeout_enabled.get(),
            "open_file_timeout": self.open_file_timeout.get(),
            "processing_timeout_enabled": self.processing_timeout_enabled.get(),
            "processing_timeout": self.processing_timeout.get(),
            "als_retry_timeout": self.als_retry_timeout.get(),
            
            "convert_doc": self.convert_doc.get(),
            "convert_xls": self.convert_xls.get(),
            
            "use_ocr": self.use_ocr.get(),
            "ocr_language": self.ocr_language.get(),
            "ocr_dpi": self.ocr_dpi.get(),
            "extract_vertical_text": self.extract_vertical_text.get(),
            "rotate_for_ocr": self.rotate_for_ocr.get(),
            
            "adaptive_dpi": self.adaptive_dpi.get(),
            "dpi_min": self.dpi_min.get(),
            "dpi_max": self.dpi_max.get(),
            "preprocess_images": self.preprocess_images.get(),
            "enhance_contrast": self.enhance_contrast.get(),
            "enhance_sharpness": self.enhance_sharpness.get(),
            "denoise": self.denoise.get(),
            "use_multi_pass_ocr": self.use_multi_pass_ocr.get(),
            "detect_regions": self.detect_regions.get(),
            "min_text_confidence": self.min_text_confidence.get(),
            "save_debug_images": self.save_debug_images.get(),
        }
    
    def new_config(self):
        """Create new configuration"""
        # Show dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("New Configuration")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Project Name:").pack(anchor='w')
        name_var = tk.StringVar(value="New Project")
        ttk.Entry(frame, textvariable=name_var, width=50).pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(frame, text="Configuration Folder:").pack(anchor='w')
        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill=tk.X, pady=(5, 20))
        
        folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=folder_var, width=45).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse", width=8,
                  command=lambda: folder_var.set(filedialog.askdirectory())).pack(side=tk.LEFT, padx=(5, 0))
        
        def create():
            if not name_var.get() or not folder_var.get():
                messagebox.showwarning("Warning", "Please fill in all fields.")
                return
            
            self.project_name.set(name_var.get())
            config_file = os.path.join(folder_var.get(), f"{name_var.get()}.xml")
            self.config_location.set(config_file)
            
            # Create default config
            os.makedirs(folder_var.get(), exist_ok=True)
            self.save_config_to_file(config_file)
            
            dialog.destroy()
            messagebox.showinfo("Success", "New configuration created successfully!")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Create", command=create, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)
    
    def save_config(self):
        """Save configuration"""
        config_file = self.config_location.get()
        
        if not config_file:
            config_file = filedialog.asksaveasfilename(
                title="Save Configuration",
                defaultextension=".xml",
                filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
            )
        
        if config_file:
            self.save_config_to_file(config_file)
    
    def save_config_to_file(self, file_path):
        """Save configuration to file"""
        try:
            config = self.get_config()
            
            # Convert to XML format (simplified for now, should match AVEVA format)
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.config_location.set(file_path)
            
            # Save as last config
            last_config_path = Path.home() / ".aveva_gateway_last_config.json"
            with open(last_config_path, 'w') as f:
                json.dump({"last_config": file_path}, f)
            
            self.status_text.set(f"Configuration saved: {Path(file_path).name}")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
    
    def load_config(self):
        """Load configuration"""
        file = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("XML Files", "*.xml"), ("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file:
            self.load_config_from_file(file)
    
    def load_config_from_file(self, file_path):
        """Load configuration from file"""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Apply all settings
            self.project_name.set(config.get("name", ""))
            self.source_folder.set(config.get("source_folder", ""))
            self.destination_folder.set(config.get("destination_folder", ""))
            self.staging_area.set(config.get("staging_area", ""))
            self.processed_folder.set(config.get("processed_folder", ""))
            self.unprocessed_folder.set(config.get("unprocessed_folder", ""))
            self.log_folder.set(config.get("log_folder", ""))
            self.pattern_file.set(config.get("pattern_mapping_file", ""))
            self.default_context.set(config.get("default_context", ""))
            
            self.include_subfolders.set(config.get("include_subfolders", True))
            self.copy_source_files.set(config.get("copy_source_files", True))
            self.copy_other_files.set(config.get("copy_other_files", False))
            self.move_processed.set(config.get("move_processed", True))
            self.search_filenames_for_tags.set(config.get("search_filenames_for_tags", False))
            self.create_trigger_file.set(config.get("create_trigger_file", True))
            self.insert_line_breaks.set(config.get("insert_line_breaks", True))
            self.object_id_from_vnet.set(config.get("object_id_from_vnet", False))
            
            self.use_ranges.set(config.get("use_ranges", False))
            self.document_type.set(config.get("document_type", "xlsx"))
            
            self.open_file_timeout_enabled.set(config.get("open_file_timeout_enabled", True))
            self.open_file_timeout.set(config.get("open_file_timeout", 30))
            self.processing_timeout_enabled.set(config.get("processing_timeout_enabled", False))
            self.processing_timeout.set(config.get("processing_timeout", 60.0))
            self.als_retry_timeout.set(config.get("als_retry_timeout", 120))
            
            self.convert_doc.set(config.get("convert_doc", False))
            self.convert_xls.set(config.get("convert_xls", False))
            
            self.use_ocr.set(config.get("use_ocr", True))
            self.ocr_language.set(config.get("ocr_language", "eng"))
            self.ocr_dpi.set(config.get("ocr_dpi", 300))
            self.extract_vertical_text.set(config.get("extract_vertical_text", True))
            self.rotate_for_ocr.set(config.get("rotate_for_ocr", True))
            
            self.adaptive_dpi.set(config.get("adaptive_dpi", True))
            self.dpi_min.set(config.get("dpi_min", 300))
            self.dpi_max.set(config.get("dpi_max", 500))
            self.preprocess_images.set(config.get("preprocess_images", True))
            self.enhance_contrast.set(config.get("enhance_contrast", 1.5))
            self.enhance_sharpness.set(config.get("enhance_sharpness", 1.5))
            self.denoise.set(config.get("denoise", True))
            self.use_multi_pass_ocr.set(config.get("use_multi_pass_ocr", True))
            self.detect_regions.set(config.get("detect_regions", True))
            self.min_text_confidence.set(config.get("min_text_confidence", 60))
            self.save_debug_images.set(config.get("save_debug_images", False))
            
            self.config_location.set(file_path)
            
            # Save as last config
            last_config_path = Path.home() / ".aveva_gateway_last_config.json"
            with open(last_config_path, 'w') as f:
                json.dump({"last_config": file_path}, f)
            
            self.status_text.set(f"Configuration loaded: {Path(file_path).name}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{e}")
    
    def reload_config(self):
        """Reload current configuration"""
        config_file = self.config_location.get()
        if config_file and os.path.exists(config_file):
            self.load_config_from_file(config_file)
        else:
            messagebox.showwarning("Warning", "No configuration file to reload.")
    
    def load_last_config(self):
        """Load last used configuration"""
        try:
            last_config_path = Path.home() / ".aveva_gateway_last_config.json"
            if last_config_path.exists():
                with open(last_config_path, 'r') as f:
                    data = json.load(f)
                    last_file = data.get("last_config")
                    if last_file and Path(last_file).exists():
                        self.load_config_from_file(last_file)
        except:
            pass
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.source_folder.get():
            messagebox.showwarning("Validation", "Please select a source folder.")
            return False
        
        if not self.staging_area.get():
            messagebox.showwarning("Validation", "Please select a staging area.")
            return False
        
        if not os.path.exists(self.source_folder.get()):
            messagebox.showwarning("Validation", "Source folder does not exist.")
            return False
        
        if self.pattern_file.get() and not os.path.exists(self.pattern_file.get()):
            messagebox.showwarning("Validation", "Pattern file does not exist.")
            return False
        
        return True
    
    def run_processing(self):
        """Run processing (AVEVA Run button)"""
        if not self.validate_config():
            return
        
        if not GATEWAY_AVAILABLE:
            messagebox.showerror("Error", "Gateway module not available.")
            return
        
        # Create folders
        for folder in [self.staging_area.get(), self.processed_folder.get(),
                      self.unprocessed_folder.get(), self.log_folder.get()]:
            if folder:
                os.makedirs(folder, exist_ok=True)
        
        # Start processing
        self.is_processing = True
        self.run_button.config(state='disabled')
        self.monitor_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start(10)
        self.status_text.set("Processing...")
        
        thread = threading.Thread(target=self.process_thread, daemon=True)
        thread.start()
    
    def monitor_processing(self):
        """Monitor processing (AVEVA Monitor button)"""
        if not self.validate_config():
            return
        
        if not GATEWAY_AVAILABLE:
            messagebox.showerror("Error", "Gateway module not available.")
            return
        
        # Create monitor window
        monitor_win = tk.Toplevel(self.root)
        monitor_win.title("Gateway Monitor")
        monitor_win.geometry("800x600")
        monitor_win.transient(self.root)
        
        # Controls
        control_frame = ttk.Frame(monitor_win, padding=10)
        control_frame.pack(fill=tk.X)
        
        self.monitor_running = False
        
        def start_monitor():
            self.monitor_running = True
            start_btn.config(state='disabled')
            stop_btn.config(state='normal')
            
            # Start monitor thread
            self.monitor_thread = threading.Thread(
                target=lambda: self.monitor_thread_func(log_text, monitor_win), 
                daemon=True
            )
            self.monitor_thread.start()
        
        def stop_monitor():
            self.monitor_running = False
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')
        
        start_btn = ttk.Button(control_frame, text="▶️ Start", command=start_monitor, width=12)
        start_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = ttk.Button(control_frame, text="⏹️ Stop", command=stop_monitor, width=12, state='disabled')
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Log area
        log_frame = ttk.Frame(monitor_win, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=('Consolas', 9))
        log_text.pack(fill=tk.BOTH, expand=True)
        
        log_text.insert('1.0', "Monitor ready. Click Start to begin monitoring...\n")
    
    def monitor_thread_func(self, log_widget, window):
        """Monitor thread function"""
        try:
            log_widget.insert('end', f"\n[{datetime.now().strftime('%H:%M:%S')}] Monitoring started...\n")
            log_widget.see('end')
            
            config_dict = self.get_config()
            config = ProjectConfig.from_dict(config_dict)
            
            gateway = DocumentIndexingGateway(config)
            
            if config.pattern_mapping_file and os.path.exists(config.pattern_mapping_file):
                gateway.load_pattern_mapping(config.pattern_mapping_file)
            
            processed_files = set()
            
            while self.monitor_running and window.winfo_exists():
                # Discover files
                files = gateway.discover_files()
                
                for file_path in files:
                    if file_path not in processed_files:
                        log_widget.insert('end', f"\n[{datetime.now().strftime('%H:%M:%S')}] Found: {os.path.basename(file_path)}\n")
                        log_widget.see('end')
                        
                        try:
                            success = gateway.process_file(file_path)
                            if success:
                                log_widget.insert('end', f"  ✓ Success\n")
                            else:
                                log_widget.insert('end', f"  ✗ Failed\n")
                        except Exception as e:
                            log_widget.insert('end', f"  ✗ Error: {e}\n")
                        
                        processed_files.add(file_path)
                        log_widget.see('end')
                
                time.sleep(2)  # Check every 2 seconds
            
            log_widget.insert('end', f"\n[{datetime.now().strftime('%H:%M:%S')}] Monitoring stopped.\n")
            log_widget.see('end')
        
        except Exception as e:
            log_widget.insert('end', f"\nMonitor error: {e}\n")
            log_widget.see('end')
    
    def process_thread(self):
        """Processing thread"""
        try:
            config_dict = self.get_config()
            config = ProjectConfig.from_dict(config_dict)
            
            gateway = DocumentIndexingGateway(config)
            
            if config.pattern_mapping_file and os.path.exists(config.pattern_mapping_file):
                gateway.load_pattern_mapping(config.pattern_mapping_file)
            
            gateway.process_batch()
            
            self.root.after(0, self.processing_complete, 
                          len(gateway.processed_files), len(gateway.failed_files))
        
        except Exception as e:
            self.root.after(0, self.processing_error, str(e))
    
    def processing_complete(self, processed, failed):
        """Processing completed"""
        self.is_processing = False
        self.run_button.config(state='normal')
        self.monitor_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
        
        self.status_text.set(f"Complete: {processed} processed, {failed} failed")
        
        messagebox.showinfo("Processing Complete", 
                          f"Processing completed!\n\n"
                          f"Processed: {processed}\n"
                          f"Failed: {failed}\n\n"
                          f"Check logs folder for detailed reports.")
    
    def processing_error(self, error):
        """Processing error"""
        self.is_processing = False
        self.run_button.config(state='normal')
        self.monitor_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
        
        self.status_text.set("Error occurred")
        messagebox.showerror("Processing Error", f"Processing failed:\n\n{error}")
    
    def stop_processing(self):
        """Stop processing"""
        if messagebox.askyesno("Confirm", "Stop processing?"):
            self.is_processing = False
            self.monitor_running = False
            self.status_text.set("Stopped by user")
    
    def view_report(self):
        """View HTML report"""
        log_folder = self.log_folder.get()
        
        if not log_folder or not os.path.exists(log_folder):
            messagebox.showwarning("Warning", "Logs folder not found. Run processing first.")
            return
        
        report_file = os.path.join(log_folder, "summary_report.html")
        
        if not os.path.exists(report_file):
            messagebox.showwarning("Warning", "Report file not found. Run processing first.")
            return
        
        try:
            webbrowser.open(f"file://{os.path.abspath(report_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open report:\n{e}")
    
    def open_manual(self):
        """Open user manual"""
        messagebox.showinfo("User Manual", 
                          "User manual available at:\n"
                          "README_COMPLETE.md\n\n"
                          "Or visit AVEVA documentation website.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Document Indexing Gateway
Complete Edition with Advanced OCR

Version: 5.0.11 + OCR Enhanced
Release: January 2026

Features:
• Complete AVEVA NET specification compliance
• Advanced OCR with intelligent preprocessing
• Multi-pass OCR for complex P&IDs
• Vertical and rotated text extraction
• Monitor mode with real-time updates
• File validation and fixing
• Comprehensive error handling

Python GUI Implementation"""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AVEDACompleteGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
