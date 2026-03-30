"""
Report Service
Generates PDF reports for analysis results
"""

import os
import logging
from datetime import datetime
from fpdf import FPDF
from app.schemas.analysis import AnalysisResponse

logger = logging.getLogger(__name__)

class ReportGenerator(FPDF):
    def header(self):
        # Logo or Title
        self.set_font('Arial', 'B', 20)
        self.set_text_color(40, 48, 68)
        self.cell(0, 10, 'Fake News Detector - Analysis Report', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'C')

class ReportService:
    """Handles PDF report generation"""

    @staticmethod
    def generate_analysis_pdf(analysis: dict, output_path: str):
        """
        Generate a PDF report for a given analysis
        """
        try:
            pdf = ReportGenerator()
            pdf.add_page()
            
            # Prediction Summary Section
            prediction = analysis.get("prediction", "Unknown")
            confidence = analysis.get("confidence", 0) * 100
            
            # Map colors based on prediction
            if prediction == "Fake":
                pdf.set_fill_color(255, 235, 238) # Light Red
                pdf.set_text_color(183, 28, 28) # Dark Red
            elif prediction == "Real":
                pdf.set_fill_color(232, 245, 233) # Light Green
                pdf.set_text_color(27, 94, 32) # Dark Green
            else:
                pdf.set_fill_color(255, 243, 224) # Light Orange
                pdf.set_text_color(230, 81, 0) # Dark Orange

            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 15, f' {prediction.upper()} - {confidence:.1f}% Confidence', 1, 1, 'L', fill=True)
            pdf.ln(5)

            # Headline Section
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Headline Analysis:', 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 8, analysis.get("headline", ""), 0, 'L')
            pdf.ln(5)

            # Similarity Section
            if "similarity" in analysis and analysis["similarity"] is not None:
                sim = analysis["similarity"] * 100
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Visual Context Similarity:', 0, 1, 'L')
                pdf.set_font('Arial', '', 11)
                pdf.cell(0, 8, f'Score: {sim:.1f}%', 0, 1, 'L')
                pdf.ln(5)

            # Explanation Section
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Detailed Explanation:', 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 8, analysis.get("explanation", "No explanation provided."), 0, 'L')
            pdf.ln(5)

            # Fact Checks Section
            fact_checks = analysis.get("fact_checks", [])
            if fact_checks:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'External Fact-Check References:', 0, 1, 'L')
                pdf.ln(2)
                
                for i, fc in enumerate(fact_checks, 1):
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(0, 6, f'{i}. {fc.get("title", "Reference")}', 0, 1, 'L')
                    pdf.set_font('Arial', 'I', 9)
                    pdf.set_text_color(0, 0, 255)
                    pdf.cell(0, 6, f'Link: {fc.get("url", "N/A")}', 0, 1, 'L')
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('Arial', '', 9)
                    pdf.multi_cell(0, 6, f'Rating: {fc.get("rating", "N/A")} | Claim: {fc.get("claim_reviewed", "N/A")}', 0, 'L')
                    pdf.ln(2)

            # Save the file
            pdf.output(output_path)
            return True

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False
