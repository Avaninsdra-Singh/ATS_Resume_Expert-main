from fpdf import FPDF

def generate_pdf_report(resume_name, logic_score, logic_explain, ai_score, strengths, gaps):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="ATS Resume Expert - Evaluation Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Resume: {resume_name}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Logic-Based Score:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Score: {logic_score:.2f}/100")
    pdf.multi_cell(0, 10, f"Matched Skills: {', '.join(logic_explain['Matched Skills'])}")
    pdf.multi_cell(0, 10, f"Missing Skills: {', '.join(logic_explain['Missing Skills'])}")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="AI-Based Evaluation:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Score: {ai_score}/100")

    if strengths:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Strengths:", ln=True)
        pdf.set_font("Arial", '', 12)
        for s in strengths:
            pdf.multi_cell(0, 10, f"- {s}")
    
    if gaps:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Areas for Improvement:", ln=True)
        pdf.set_font("Arial", '', 12)
        for g in gaps:
            pdf.multi_cell(0, 10, f"- {g}")

    return pdf.output(dest='S').encode('latin1')
