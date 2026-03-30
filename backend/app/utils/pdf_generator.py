"""
PDF Report Generator
Generates PDF reports for analysis results
"""

import logging
from typing import Optional, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
import requests

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generates PDF reports for analysis"""
    
    @staticmethod
    def generate_report(
        headline: str,
        prediction: str,
        confidence: float,
        similarity: Optional[float],
        explanation: str,
        fact_checks: List[dict],
        image_url: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> BytesIO:
        """
        Generate PDF report for analysis
        Returns: BytesIO object containing PDF
        """
        try:
            # Create PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            
            # Container for PDF elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#374151'),
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            )
            
            # Title
            title = Paragraph("🧠 Fake News & Misinformation Detector Report", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.3*inch))
            
            # Report metadata
            report_date = created_at.strftime("%B %d, %Y at %H:%M:%S") if created_at else datetime.now().strftime("%B %d, %Y at %H:%M:%S")
            metadata = Paragraph(f"<b>Report Generated:</b> {report_date}", body_style)
            elements.append(metadata)
            elements.append(Spacer(1, 0.2*inch))
            
            # Headline section
            elements.append(Paragraph("<b>Headline:</b>", heading_style))
            headline_para = Paragraph(f'"{headline}"', body_style)
            elements.append(headline_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # Analysis results
            elements.append(Paragraph("<b>Analysis Results:</b>", heading_style))
            
            # Prediction color mapping
            prediction_colors = {
                "Fake": "#dc2626",
                "Real": "#16a34a",
                "Misleading": "#ea580c"
            }
            color = prediction_colors.get(prediction, "#6b7280")
            
            # Results table
            results_data = [
                ["Prediction", f"<font color='{color}'><b>{prediction}</b></font>"],
                ["Confidence", f"{confidence*100:.1f}%"],
            ]
            
            if similarity is not None:
                results_data.append(["Image-Text Similarity", f"{similarity*100:.1f}%"])
            
            results_table = Table(results_data, colWidths=[2*inch, 2*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(results_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Explanation
            elements.append(Paragraph("<b>Analysis Explanation:</b>", heading_style))
            explanation_para = Paragraph(explanation, body_style)
            elements.append(explanation_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Fact checks
            if fact_checks:
                elements.append(Paragraph("<b>Fact-Check References:</b>", heading_style))
                
                for i, fc in enumerate(fact_checks, 1):
                    fc_text = f"<b>{i}. {fc.get('title', 'Unknown')}</b><br/>"
                    fc_text += f"Rating: {fc.get('rating', 'N/A')}<br/>"
                    fc_text += f"Claim: {fc.get('claim_reviewed', 'N/A')[:100]}..."
                    elements.append(Paragraph(fc_text, body_style))
                    elements.append(Spacer(1, 0.1*inch))
            else:
                elements.append(Paragraph("No fact-check references found.", body_style))
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer_text = "This report was generated by the Fake News & Misinformation Detector system. " \
                         "Results are based on AI analysis and should be verified with additional sources."
            footer = Paragraph(footer_text, ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            ))
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
            
            logger.info("PDF report generated successfully")
            return pdf_buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    @staticmethod
    def generate_batch_report(analyses: List[dict]) -> BytesIO:
        """
        Generate batch PDF report for multiple analyses
        """
        try:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            # Title
            title = Paragraph("📊 Batch Analysis Report", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary
            summary_text = f"<b>Total Analyses:</b> {len(analyses)}<br/>"
            fake_count = sum(1 for a in analyses if a.get("prediction") == "Fake")
            real_count = sum(1 for a in analyses if a.get("prediction") == "Real")
            misleading_count = sum(1 for a in analyses if a.get("prediction") == "Misleading")
            
            summary_text += f"<b>Fake:</b> {fake_count} | <b>Real:</b> {real_count} | <b>Misleading:</b> {misleading_count}"
            elements.append(Paragraph(summary_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Add each analysis
            for i, analysis in enumerate(analyses, 1):
                if i > 1:
                    elements.append(PageBreak())
                
                elements.append(Paragraph(f"Analysis #{i}", styles['Heading2']))
                elements.append(Spacer(1, 0.2*inch))
                
                # Add analysis details
                details = f"<b>Headline:</b> {analysis.get('headline', 'N/A')[:100]}...<br/>"
                details += f"<b>Prediction:</b> {analysis.get('prediction', 'N/A')}<br/>"
                details += f"<b>Confidence:</b> {analysis.get('confidence', 0)*100:.1f}%"
                
                elements.append(Paragraph(details, styles['Normal']))
                elements.append(Spacer(1, 0.2*inch))
            
            doc.build(elements)
            pdf_buffer.seek(0)
            
            logger.info(f"Batch PDF report generated for {len(analyses)} analyses")
            return pdf_buffer
            
        except Exception as e:
            logger.error(f"Error generating batch PDF report: {e}")
            raise
