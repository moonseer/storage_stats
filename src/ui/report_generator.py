#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Report Generator for creating savable reports from scan results
"""

import os
import logging
import csv
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject

from src.utils.helpers import human_readable_size, format_timestamp

logger = logging.getLogger("StorageStats.ReportGenerator")

class ReportGenerator(QObject):
    """Generate reports from scan results in various formats"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def generate_report(self, scan_results, analyzer, format_type="html", parent_widget=None):
        """
        Generate a report of the scan results
        
        Args:
            scan_results (dict): Scan results data
            analyzer (DataAnalyzer): Analyzer object with processed results
            format_type (str): "html", "csv", "text", or "json"
            parent_widget (QWidget): Parent widget for file dialogs
            
        Returns:
            bool: True if report was generated successfully, False otherwise
        """
        if not scan_results:
            logger.warning("No scan results to generate report from")
            return False
        
        # Get file path from user
        file_extension = self._get_file_extension(format_type)
        file_path = self._get_save_path(format_type, file_extension, parent_widget)
        
        if not file_path:
            return False
        
        # Generate report based on format
        try:
            if format_type == "html":
                return self._generate_html_report(file_path, scan_results, analyzer)
            elif format_type == "csv":
                return self._generate_csv_report(file_path, scan_results, analyzer)
            elif format_type == "text":
                return self._generate_text_report(file_path, scan_results, analyzer)
            elif format_type == "json":
                return self._generate_json_report(file_path, scan_results, analyzer)
            else:
                logger.error(f"Unsupported report format: {format_type}")
                return False
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            return False
    
    def _get_file_extension(self, format_type):
        """Get the file extension for the given format type"""
        extensions = {
            "html": "html",
            "csv": "csv",
            "text": "txt",
            "json": "json"
        }
        return extensions.get(format_type, "txt")
    
    def _get_save_path(self, format_type, extension, parent_widget):
        """Show a file dialog to get the save path"""
        formats = {
            "html": "HTML Files (*.html)",
            "csv": "CSV Files (*.csv)",
            "text": "Text Files (*.txt)",
            "json": "JSON Files (*.json)"
        }
        
        title = f"Save {format_type.upper()} Report"
        file_filter = formats.get(format_type, "All Files (*)")
        
        default_name = f"storage_stats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            title,
            os.path.join(os.path.expanduser("~"), default_name),
            file_filter
        )
        
        return file_path
    
    def _generate_html_report(self, file_path, scan_results, analyzer):
        """Generate an HTML report"""
        # Get data for the report
        root_path = scan_results.get('root_info', {}).path
        scan_time = scan_results.get('scan_time', 0)
        total_size = scan_results.get('total_size', 0)
        total_files = scan_results.get('total_files', 0)
        total_dirs = scan_results.get('total_dirs', 0)
        
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get largest files and directories
        largest_files = analyzer.get_largest_files(limit=20)
        largest_dirs = analyzer.get_largest_dirs(limit=20)
        
        # Get duplicate files
        duplicate_groups = analyzer.get_duplicate_files()
        
        # Get file type distribution
        file_types = analyzer.get_file_type_distribution()
        
        # Create pie chart for file types (top 10)
        plt.figure(figsize=(8, 6))
        
        # Sort file types by size and get top 10
        sorted_types = sorted(file_types.items(), key=lambda x: x[1]['size'], reverse=True)[:10]
        labels = [t[0] for t in sorted_types]
        sizes = [t[1]['size'] for t in sorted_types]
        
        # Create the pie chart
        plt.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Storage by File Type (Top 10)')
        plt.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))
        
        # Save chart to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Encode the image as base64 for HTML embedding
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        # Start building the HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Storage Stats Report - {root_path}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .summary {{ display: flex; flex-wrap: wrap; margin-bottom: 20px; }}
                .summary-card {{ flex: 1; margin: 10px; padding: 15px; border-radius: 5px; background-color: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 200px; }}
                .summary-card h3 {{ margin-top: 0; }}
                .chart {{ max-width: 100%; height: auto; margin: 20px 0; }}
                .footer {{ margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>Storage Stats Report</h1>
            <p>Generated on: {timestamp}</p>
            
            <h2>Scan Information</h2>
            <p><strong>Path:</strong> {root_path}</p>
            <p><strong>Scan Duration:</strong> {scan_time:.2f} seconds</p>
            
            <h2>Summary</h2>
            <div class="summary">
                <div class="summary-card">
                    <h3>Total Size</h3>
                    <p>{human_readable_size(total_size)}</p>
                </div>
                <div class="summary-card">
                    <h3>Total Files</h3>
                    <p>{total_files:,}</p>
                </div>
                <div class="summary-card">
                    <h3>Total Directories</h3>
                    <p>{total_dirs:,}</p>
                </div>
                <div class="summary-card">
                    <h3>Average File Size</h3>
                    <p>{human_readable_size(total_size / total_files if total_files > 0 else 0)}</p>
                </div>
            </div>
            
            <h2>File Type Distribution</h2>
            <div class="chart">
                <img src="data:image/png;base64,{img_str}" alt="File Type Distribution Chart" width="600">
            </div>
            
            <table>
                <tr>
                    <th>Type</th>
                    <th>Count</th>
                    <th>Size</th>
                    <th>Percentage</th>
                </tr>
        """
        
        # Add file type rows
        for file_type, data in sorted_types:
            html_content += f"""
                <tr>
                    <td>{file_type}</td>
                    <td>{data['count']:,}</td>
                    <td>{human_readable_size(data['size'])}</td>
                    <td>{data['size'] / total_size * 100:.1f}%</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Largest Files</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Path</th>
                    <th>Size</th>
                    <th>Last Modified</th>
                </tr>
        """
        
        # Add largest files rows
        for file_info in largest_files:
            html_content += f"""
                <tr>
                    <td>{os.path.basename(file_info['path'])}</td>
                    <td>{file_info['path']}</td>
                    <td>{human_readable_size(file_info['size'])}</td>
                    <td>{format_timestamp(file_info['last_modified'])}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Largest Directories</h2>
            <table>
                <tr>
                    <th>Path</th>
                    <th>Size</th>
                    <th>Files</th>
                </tr>
        """
        
        # Add largest directories rows
        for dir_info in largest_dirs:
            html_content += f"""
                <tr>
                    <td>{dir_info['path']}</td>
                    <td>{human_readable_size(dir_info['size'])}</td>
                    <td>{dir_info.get('file_count', 'N/A')}</td>
                </tr>
            """
        
        html_content += """
            </table>
        """
        
        # Add duplicate files section if any
        if duplicate_groups:
            total_wasted = sum(group['wasted_space'] for group in duplicate_groups.values())
            
            html_content += f"""
                <h2>Duplicate Files</h2>
                <p>Found {len(duplicate_groups)} duplicate groups wasting {human_readable_size(total_wasted)}</p>
                
                <table>
                    <tr>
                        <th>Group</th>
                        <th>Files</th>
                        <th>Size per File</th>
                        <th>Wasted Space</th>
                    </tr>
            """
            
            # Add duplicate groups
            for i, (hash_value, group) in enumerate(
                sorted(duplicate_groups.items(), key=lambda x: x[1]['wasted_space'], reverse=True)[:15]
            ):
                html_content += f"""
                    <tr>
                        <td>Group {i+1}</td>
                        <td>{group['count']}</td>
                        <td>{human_readable_size(group['size'])}</td>
                        <td>{human_readable_size(group['wasted_space'])}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            """
        
        # Close the HTML
        html_content += """
            <div class="footer">
                <p>Generated by Storage Stats Disk Space Analyzer</p>
            </div>
        </body>
        </html>
        """
        
        # Write the HTML to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to {file_path}")
        return True
    
    def _generate_csv_report(self, file_path, scan_results, analyzer):
        """Generate a CSV report"""
        # We'll generate separate CSV files for different sections
        base_path, extension = os.path.splitext(file_path)
        
        # Generate summary CSV
        summary_path = f"{base_path}_summary{extension}"
        with open(summary_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Property', 'Value'])
            writer.writerow(['Path', scan_results.get('root_info', {}).path])
            writer.writerow(['Scan Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(['Scan Duration (s)', scan_results.get('scan_time', 0)])
            writer.writerow(['Total Size', scan_results.get('total_size', 0)])
            writer.writerow(['Total Size (Human)', human_readable_size(scan_results.get('total_size', 0))])
            writer.writerow(['Total Files', scan_results.get('total_files', 0)])
            writer.writerow(['Total Directories', scan_results.get('total_dirs', 0)])
        
        # Generate largest files CSV
        largest_files = analyzer.get_largest_files(limit=100)
        if largest_files:
            largest_files_path = f"{base_path}_largest_files{extension}"
            with open(largest_files_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Path', 'Size', 'Size (Human)', 'Last Modified'])
                for file_info in largest_files:
                    writer.writerow([
                        os.path.basename(file_info['path']),
                        file_info['path'],
                        file_info['size'],
                        human_readable_size(file_info['size']),
                        format_timestamp(file_info['last_modified'])
                    ])
        
        # Generate largest directories CSV
        largest_dirs = analyzer.get_largest_dirs(limit=100)
        if largest_dirs:
            largest_dirs_path = f"{base_path}_largest_dirs{extension}"
            with open(largest_dirs_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Path', 'Size', 'Size (Human)', 'Files Count'])
                for dir_info in largest_dirs:
                    writer.writerow([
                        dir_info['path'],
                        dir_info['size'],
                        human_readable_size(dir_info['size']),
                        dir_info.get('file_count', 'N/A')
                    ])
        
        # Generate file types CSV
        file_types = analyzer.get_file_type_distribution()
        if file_types:
            types_path = f"{base_path}_file_types{extension}"
            with open(types_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Type', 'Count', 'Size', 'Size (Human)', 'Percentage'])
                total_size = scan_results.get('total_size', 0)
                for file_type, data in sorted(file_types.items(), key=lambda x: x[1]['size'], reverse=True):
                    writer.writerow([
                        file_type,
                        data['count'],
                        data['size'],
                        human_readable_size(data['size']),
                        f"{data['size'] / total_size * 100:.1f}%" if total_size > 0 else '0%'
                    ])
        
        # Generate duplicate files CSV
        duplicate_groups = analyzer.get_duplicate_files()
        if duplicate_groups:
            dupes_path = f"{base_path}_duplicates{extension}"
            with open(dupes_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Group', 'Count', 'Size per File', 'Size (Human)', 'Wasted Space', 'Wasted Space (Human)'])
                for i, (hash_value, group) in enumerate(sorted(duplicate_groups.items(), key=lambda x: x[1]['wasted_space'], reverse=True)):
                    writer.writerow([
                        f"Group {i+1}",
                        group['count'],
                        group['size'],
                        human_readable_size(group['size']),
                        group['wasted_space'],
                        human_readable_size(group['wasted_space'])
                    ])
            
            # Generate detailed duplicate files list
            dupes_detail_path = f"{base_path}_duplicates_detail{extension}"
            with open(dupes_detail_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Group', 'Path', 'Size', 'Last Modified'])
                for i, (hash_value, group) in enumerate(sorted(duplicate_groups.items(), key=lambda x: x[1]['wasted_space'], reverse=True)):
                    for file_info in group['files']:
                        writer.writerow([
                            f"Group {i+1}",
                            file_info['path'],
                            human_readable_size(group['size']),
                            format_timestamp(file_info['last_modified'])
                        ])
        
        logger.info(f"CSV reports saved to {base_path}*{extension}")
        return True
    
    def _generate_text_report(self, file_path, scan_results, analyzer):
        """Generate a plain text report"""
        # Get data for the report
        root_path = scan_results.get('root_info', {}).path
        scan_time = scan_results.get('scan_time', 0)
        total_size = scan_results.get('total_size', 0)
        total_files = scan_results.get('total_files', 0)
        total_dirs = scan_results.get('total_dirs', 0)
        
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Start building the text content
        text_content = f"""
STORAGE STATS REPORT
===========================================
Generated: {timestamp}

SCAN INFORMATION
-------------------------------------------
Path: {root_path}
Scan Duration: {scan_time:.2f} seconds

SUMMARY
-------------------------------------------
Total Size: {human_readable_size(total_size)}
Total Files: {total_files:,}
Total Directories: {total_dirs:,}
Average File Size: {human_readable_size(total_size / total_files if total_files > 0 else 0)}

FILE TYPE DISTRIBUTION
-------------------------------------------
"""
        
        # Add file type distribution
        file_types = analyzer.get_file_type_distribution()
        for file_type, data in sorted(file_types.items(), key=lambda x: x[1]['size'], reverse=True)[:20]:
            text_content += f"{file_type:<15} {data['count']:<10,} {human_readable_size(data['size']):<10} {data['size'] / total_size * 100:.1f}%\n"
        
        text_content += """
LARGEST FILES
-------------------------------------------
"""
        
        # Add largest files
        largest_files = analyzer.get_largest_files(limit=20)
        for i, file_info in enumerate(largest_files):
            text_content += f"{i+1:<3} {os.path.basename(file_info['path'])[:30]:<30} {human_readable_size(file_info['size']):<10} {file_info['path']}\n"
        
        text_content += """
LARGEST DIRECTORIES
-------------------------------------------
"""
        
        # Add largest directories
        largest_dirs = analyzer.get_largest_dirs(limit=20)
        for i, dir_info in enumerate(largest_dirs):
            text_content += f"{i+1:<3} {human_readable_size(dir_info['size']):<10} {dir_info['path']}\n"
        
        # Add duplicate files section if any
        duplicate_groups = analyzer.get_duplicate_files()
        if duplicate_groups:
            total_wasted = sum(group['wasted_space'] for group in duplicate_groups.values())
            
            text_content += f"""
DUPLICATE FILES
-------------------------------------------
Found {len(duplicate_groups)} duplicate groups wasting {human_readable_size(total_wasted)}

"""
            
            # Add top 15 duplicate groups
            for i, (hash_value, group) in enumerate(
                sorted(duplicate_groups.items(), key=lambda x: x[1]['wasted_space'], reverse=True)[:15]
            ):
                text_content += f"Group {i+1}: {group['count']} files, {human_readable_size(group['size'])} each, wasting {human_readable_size(group['wasted_space'])}\n"
                # List up to 5 sample files in each group
                for j, file_info in enumerate(group['files'][:5]):
                    text_content += f"  - {file_info['path']}\n"
                if len(group['files']) > 5:
                    text_content += f"  - ... and {len(group['files']) - 5} more\n"
                text_content += "\n"
        
        # Close the text report
        text_content += """
===========================================
Generated by Storage Stats Disk Space Analyzer
"""
        
        # Write the text to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        logger.info(f"Text report saved to {file_path}")
        return True
    
    def _generate_json_report(self, file_path, scan_results, analyzer):
        """Generate a JSON report with full scan data"""
        # Create a report dictionary with all relevant data
        report = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "app_name": "Storage Stats Disk Space Analyzer",
                "version": "1.0.0"
            },
            "scan_info": {
                "path": scan_results.get('root_info', {}).path,
                "scan_time": scan_results.get('scan_time', 0),
                "total_size": scan_results.get('total_size', 0),
                "total_size_human": human_readable_size(scan_results.get('total_size', 0)),
                "total_files": scan_results.get('total_files', 0),
                "total_dirs": scan_results.get('total_dirs', 0)
            },
            "file_types": analyzer.get_file_type_distribution(),
            "largest_files": analyzer.get_largest_files(limit=100),
            "largest_dirs": analyzer.get_largest_dirs(limit=100),
            "duplicate_files": analyzer.get_duplicate_files(),
            "recommendations": analyzer.get_recommendations()
        }
        
        # Convert datetime objects to strings
        def json_serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)
        
        # Write the JSON to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, default=json_serialize, indent=2)
        
        logger.info(f"JSON report saved to {file_path}")
        return True 