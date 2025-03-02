#!/usr/bin/env python3
"""
Batch PDF Accessibility Validator

Checks multiple PDFs for accessibility features and generates reports.

Usage: python batch_validate.py input_dir output_dir
"""

import os
import sys
import argparse
import json
import csv
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import accessibility checker
try:
    from validate_accessibility import AccessibilityChecker
except ImportError:
    try:
        from accessibility_tools.validation.validate_accessibility import AccessibilityChecker
    except ImportError:
        logger.error("Error importing AccessibilityChecker. Make sure validate_accessibility.py is in the same directory.")
        sys.exit(1)

def process_pdf(pdf_path: str, detailed: bool = False) -> Dict[str, Any]:
    """
    Process a single PDF and return results
    
    Args:
        pdf_path: Path to PDF file
        detailed: Whether to include detailed information
        
    Returns:
        Dictionary with accessibility check results
    """
    try:
        logger.info(f"Processing: {pdf_path}")
        checker = AccessibilityChecker(pdf_path)
        results = checker.check(detailed=detailed)
        logger.info(f"Completed: {pdf_path} - Score: {results.get('summary', {}).get('accessibility_score', 0)}/100")
        return results
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "filename": os.path.basename(pdf_path),
            "path": pdf_path,
            "is_accessible": False,
            "issues": [f"Processing error: {str(e)}"],
            "error": str(e)
        }

def save_json_report(results: List[Dict[str, Any]], output_dir: str) -> str:
    """
    Save detailed results to JSON file
    
    Args:
        results: List of results for each PDF
        output_dir: Directory to save report
        
    Returns:
        Path to saved report
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"accessibility_report_{timestamp}.json")
    
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Saved detailed JSON report to: {json_path}")
    return json_path

def save_csv_report(results: List[Dict[str, Any]], output_dir: str) -> str:
    """
    Save summary results to CSV file
    
    Args:
        results: List of results for each PDF
        output_dir: Directory to save report
        
    Returns:
        Path to saved report
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_dir, f"accessibility_summary_{timestamp}.csv")
    
    with open(csv_path, 'w', newline='') as f:
        fieldnames = [
            'Filename', 'Accessible', 'Score', 'PDF/UA Compliant', 
            'Issues', 'Critical Issues', 'Tagged', 'Language', 
            'Has Title', 'Has Structure', 'Recommendation'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            summary = result.get('summary', {})
            features = result.get('features', {})
            compliance = result.get('compliance', {})
            
            writer.writerow({
                'Filename': result.get('filename', ''),
                'Accessible': 'Yes' if result.get('is_accessible', False) else 'No',
                'Score': summary.get('accessibility_score', 0),
                'PDF/UA Compliant': 'Yes' if compliance.get('has_pdf_ua_identifier', False) else 'No',
                'Issues': summary.get('issue_count', 0),
                'Critical Issues': summary.get('critical_issues', 0),
                'Tagged': 'Yes' if features.get('is_tagged', False) else 'No',
                'Language': features.get('language', 'Not specified'),
                'Has Title': 'Yes' if features.get('has_title', False) else 'No',
                'Has Structure': 'Yes' if features.get('has_structure', False) else 'No',
                'Recommendation': summary.get('recommendation', '')
            })
            
    logger.info(f"Saved CSV summary report to: {csv_path}")
    return csv_path

def generate_html_report(results: List[Dict[str, Any]], output_dir: str) -> str:
    """
    Generate HTML report with interactive features
    
    Args:
        results: List of results for each PDF
        output_dir: Directory to save report
        
    Returns:
        Path to saved report
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(output_dir, f"accessibility_report_{timestamp}.html")
    
    # Sort results by score
    sorted_results = sorted(
        results, 
        key=lambda x: x.get('summary', {}).get('accessibility_score', 0),
        reverse=True
    )
    
    # Calculate summary statistics
    total_pdfs = len(results)
    accessible_pdfs = sum(1 for r in results if r.get('is_accessible', False))
    pdf_ua_compliant = sum(1 for r in results if r.get('compliance', {}).get('has_pdf_ua_identifier', False))
    avg_score = sum(r.get('summary', {}).get('accessibility_score', 0) for r in results) / total_pdfs if total_pdfs else 0
    
    # Categories for chart
    score_categories = {
        'Excellent (90-100)': 0,
        'Good (70-89)': 0,
        'Fair (40-69)': 0,
        'Poor (0-39)': 0
    }
    
    for r in results:
        score = r.get('summary', {}).get('accessibility_score', 0)
        if score >= 90:
            score_categories['Excellent (90-100)'] += 1
        elif score >= 70:
            score_categories['Good (70-89)'] += 1
        elif score >= 40:
            score_categories['Fair (40-69)'] += 1
        else:
            score_categories['Poor (0-39)'] += 1
    
    # Generate HTML
    with open(html_path, 'w') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Accessibility Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary-box {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-box {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 200px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
        }}
        .chart-container {{
            display: flex;
            gap: 40px;
            margin-bottom: 30px;
        }}
        .chart {{
            flex: 1;
            min-height: 300px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .score {{
            font-weight: bold;
        }}
        .score-high {{
            color: #27ae60;
        }}
        .score-medium {{
            color: #f39c12;
        }}
        .score-low {{
            color: #e74c3c;
        }}
        .accessible-yes {{
            color: #27ae60;
            font-weight: bold;
        }}
        .accessible-no {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .hidden {{
            display: none;
        }}
        .issues-toggle {{
            cursor: pointer;
            color: #3498db;
            text-decoration: underline;
        }}
        .issues-list {{
            margin-top: 10px;
            padding-left: 20px;
            font-size: 0.85em;
        }}
        .search-box {{
            margin: 20px 0;
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .filter-buttons {{
            margin: 20px 0;
        }}
        .filter-button {{
            padding: 8px 15px;
            margin-right: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
        }}
        .filter-button.active {{
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }}
        @media print {{
            .no-print {{
                display: none;
            }}
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>PDF Accessibility Report</h1>
    <p>Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <h2>Summary</h2>
    <div class="summary-box">
        <div class="stat-box">
            <div class="stat-label">Total PDFs</div>
            <div class="stat-value">{total_pdfs}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Accessible PDFs</div>
            <div class="stat-value">{accessible_pdfs}</div>
            <div class="stat-label">{int(accessible_pdfs/total_pdfs*100) if total_pdfs else 0}% of total</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">PDF/UA Compliant</div>
            <div class="stat-value">{pdf_ua_compliant}</div>
            <div class="stat-label">{int(pdf_ua_compliant/total_pdfs*100) if total_pdfs else 0}% of total</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Average Score</div>
            <div class="stat-value">{int(avg_score)}</div>
            <div class="stat-label">out of 100</div>
        </div>
    </div>
    
    <div class="chart-container">
        <div class="chart">
            <canvas id="accessibilityChart"></canvas>
        </div>
        <div class="chart">
            <canvas id="scoreDistributionChart"></canvas>
        </div>
    </div>
    
    <h2>PDF Accessibility Details</h2>
    <div class="no-print">
        <input type="text" id="searchBox" class="search-box" placeholder="Search by filename...">
        
        <div class="filter-buttons">
            <button class="filter-button active" data-filter="all">All PDFs</button>
            <button class="filter-button" data-filter="accessible">Accessible</button>
            <button class="filter-button" data-filter="not-accessible">Not Accessible</button>
            <button class="filter-button" data-filter="pdf-ua">PDF/UA Compliant</button>
        </div>
    </div>
    
    <table id="resultsTable">
        <thead>
            <tr>
                <th>Filename</th>
                <th>Score</th>
                <th>Status</th>
                <th>PDF/UA</th>
                <th>Issues</th>
                <th>Tagged</th>
                <th>Language</th>
                <th>Title</th>
                <th>Recommendation</th>
            </tr>
        </thead>
        <tbody>
""")

        # Add table rows
        for result in sorted_results:
            filename = result.get('filename', '')
            is_accessible = result.get('is_accessible', False)
            score = result.get('summary', {}).get('accessibility_score', 0)
            issues = result.get('issues', [])
            features = result.get('features', {})
            compliance = result.get('compliance', {})
            
            # Determine score class
            score_class = 'score-low'
            if score >= 70:
                score_class = 'score-high'
            elif score >= 40:
                score_class = 'score-medium'
                
            # Create table row
            f.write(f"""
            <tr class="result-row" 
                data-accessible="{str(is_accessible).lower()}" 
                data-pdfua="{str(compliance.get('has_pdf_ua_identifier', False)).lower()}">
                <td>{filename}</td>
                <td class="score {score_class}">{score}/100</td>
                <td class="{'accessible-yes' if is_accessible else 'accessible-no'}">
                    {'Accessible' if is_accessible else 'Not Accessible'}
                </td>
                <td>{'Yes' if compliance.get('has_pdf_ua_identifier', False) else 'No'}</td>
                <td>
                    {len(issues)} 
                    {f'<span class="issues-toggle" onclick="toggleIssues(this)">Show</span><ul class="issues-list hidden">' if issues else ''}
                    {''.join(f'<li>{issue}</li>' for issue in issues)}
                    {'</ul>' if issues else ''}
                </td>
                <td>{'Yes' if features.get('is_tagged', False) else 'No'}</td>
                <td>{features.get('language', 'Not specified')}</td>
                <td>{'Yes' if features.get('has_title', False) else 'No'}</td>
                <td>{result.get('summary', {}).get('recommendation', '')}</td>
            </tr>
            """)
        
        # Complete HTML
        f.write("""
        </tbody>
    </table>
    
    <script>
        // Chart data
        document.addEventListener('DOMContentLoaded', function() {
            // Accessibility Chart
            const accessCtx = document.getElementById('accessibilityChart').getContext('2d');
            const accessChart = new Chart(accessCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Accessible', 'Not Accessible'],
                    datasets: [{
                        data: [""" + f"{accessible_pdfs}, {total_pdfs - accessible_pdfs}" + """],
                        backgroundColor: ['#27ae60', '#e74c3c']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Accessibility Status'
                        }
                    }
                }
            });
            
            // Score Distribution Chart
            const scoreCtx = document.getElementById('scoreDistributionChart').getContext('2d');
            const scoreChart = new Chart(scoreCtx, {
                type: 'bar',
                data: {
                    labels: [""" + ", ".join([f"'{cat}'" for cat in score_categories.keys()]) + """],
                    datasets: [{
                        label: 'Number of PDFs',
                        data: [""" + ", ".join([str(count) for count in score_categories.values()]) + """],
                        backgroundColor: ['#27ae60', '#2ecc71', '#f39c12', '#e74c3c']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Score Distribution'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of PDFs'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Score Range'
                            }
                        }
                    }
                }
            });
            
            // Search functionality
            const searchBox = document.getElementById('searchBox');
            searchBox.addEventListener('keyup', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = document.querySelectorAll('#resultsTable tbody tr');
                
                rows.forEach(row => {
                    const filename = row.cells[0].textContent.toLowerCase();
                    if(filename.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
            
            // Filter buttons
            const filterButtons = document.querySelectorAll('.filter-button');
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Remove active class from all buttons
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    
                    // Add active class to clicked button
                    this.classList.add('active');
                    
                    // Apply filter
                    const filter = this.getAttribute('data-filter');
                    const rows = document.querySelectorAll('#resultsTable tbody tr');
                    
                    rows.forEach(row => {
                        if(filter === 'all') {
                            row.style.display = '';
                        } else if(filter === 'accessible') {
                            row.style.display = row.getAttribute('data-accessible') === 'true' ? '' : 'none';
                        } else if(filter === 'not-accessible') {
                            row.style.display = row.getAttribute('data-accessible') === 'false' ? '' : 'none';
                        } else if(filter === 'pdf-ua') {
                            row.style.display = row.getAttribute('data-pdfua') === 'true' ? '' : 'none';
                        }
                    });
                });
            });
        });
        
        // Toggle issues list
        function toggleIssues(element) {
            const issuesList = element.nextElementSibling;
            if(issuesList.classList.contains('hidden')) {
                issuesList.classList.remove('hidden');
                element.textContent = 'Hide';
            } else {
                issuesList.classList.add('hidden');
                element.textContent = 'Show';
            }
        }
    </script>
</body>
</html>
""")
    
    logger.info(f"Generated HTML report: {html_path}")
    return html_path

def process_directory(input_dir: str, output_dir: str, detailed: bool = True, max_workers: int = 4) -> bool:
    """
    Process all PDFs in a directory
    
    Args:
        input_dir: Directory containing PDFs to process
        output_dir: Directory to save reports
        detailed: Whether to include detailed information
        max_workers: Maximum number of parallel workers
        
    Returns:
        True if successful
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # Validate directories
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"Input directory not found: {input_dir}")
        return False
        
    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDFs
    pdf_files = list(input_dir.glob('**/*.pdf'))
    if not pdf_files:
        logger.error(f"No PDF files found in {input_dir}")
        return False
        
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process PDFs in parallel
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all PDF processing tasks
        future_to_pdf = {
            executor.submit(process_pdf, str(pdf), detailed): pdf 
            for pdf in pdf_files
        }
        
        # Collect results as they complete
        for future in future_to_pdf:
            pdf = future_to_pdf[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {pdf}: {e}")
                results.append({
                    "filename": os.path.basename(str(pdf)),
                    "path": str(pdf),
                    "is_accessible": False,
                    "issues": [f"Processing error: {str(e)}"],
                    "error": str(e)
                })
    
    # Generate reports
    if results:
        save_json_report(results, str(output_dir))
        save_csv_report(results, str(output_dir))
        generate_html_report(results, str(output_dir))
        
        # Print summary
        accessible_count = sum(1 for r in results if r.get('is_accessible', False))
        logger.info(f"Processing complete: {len(results)} PDFs processed")
        logger.info(f"Accessible PDFs: {accessible_count}/{len(results)} ({int(accessible_count/len(results)*100 if results else 0)}%)")
        logger.info(f"Reports saved to: {output_dir}")
        return True
    else:
        logger.error("No results were generated")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Batch process PDFs for accessibility')
    parser.add_argument('input_dir', help='Directory containing PDF files to process')
    parser.add_argument('output_dir', help='Directory to save reports')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers (default: 4)')
    parser.add_argument('--simple', action='store_true', help='Generate simplified reports without detailed analysis')
    
    args = parser.parse_args()
    
    # Process PDFs
    start_time = datetime.datetime.now()
    success = process_directory(
        args.input_dir, 
        args.output_dir, 
        detailed=not args.simple,
        max_workers=args.workers
    )
    end_time = datetime.datetime.now()
    
    # Print execution time
    logger.info(f"Total execution time: {end_time - start_time}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())