"""
Audit report generation module for consensus engine.
Collects audit logs and generates summary reports.
"""

import logging
import os
from datetime import datetime

AUDIT_LOGGER_NAME = 'audit_logger'
AUDIT_LOG_FILE = 'audit.log'

def setup_audit_logger(log_file=AUDIT_LOG_FILE):
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def generate_audit_report(log_file=AUDIT_LOG_FILE):
    """
    Reads the audit log file and generates a summary report.
    Returns the report as a string.
    """
    if not os.path.exists(log_file):
        return "No audit log file found."

    report_lines = []
    with open(log_file, 'r') as f:
        lines = f.readlines()

    report_lines.append(f"Audit Report generated on {datetime.now().isoformat()}")
    report_lines.append(f"Total log entries: {len(lines)}")
    report_lines.append("")

    # Simple summary: count entries by type (INFO, WARNING, ERROR)
    counts = {'INFO': 0, 'WARNING': 0, 'ERROR': 0}
    for line in lines:
        if 'INFO' in line:
            counts['INFO'] += 1
        elif 'WARNING' in line:
            counts['WARNING'] += 1
        elif 'ERROR' in line:
            counts['ERROR'] += 1

    report_lines.append("Log entry counts by level:")
    for level, count in counts.items():
        report_lines.append(f"  {level}: {count}")

    report_lines.append("")
    report_lines.append("Recent log entries:")
    report_lines.extend(lines[-10:])  # last 10 entries

    return "\n".join(report_lines)
