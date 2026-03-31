import os
import sys
# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.services.report import ReportService

analysis = {
    "prediction": "Fake",
    "confidence": 0.85,
    "headline": "This is a test fake headline for report verification.",
    "similarity": 0.12,
    "explanation": "Test explanation: The headline shows signs of fabrication and the visual context is unrelated.",
    "fact_checks": [
        {"title": "Test Fact Checker", "url": "https://example.com", "claim_reviewed": "Fake headline claim", "rating": "False"}
    ]
}

output_path = "test_report.pdf"
success = ReportService.generate_analysis_pdf(analysis, output_path)

if success:
    print(f"PDF successfully generated at {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
else:
    print("Failed to generate PDF")
