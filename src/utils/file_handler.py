import PyPDF2


def read_pdf_file(file):
    if file is None:
        return ""

    if hasattr(file, "seek"):
        file.seek(0)

    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text