# app/services/document_processor.py

import logging
from typing import Optional, Union
from io import BytesIO
from abc import ABC, abstractmethod
import os
from app.utils.timing import log_timing

# Import necessary modules
from PIL import Image, UnidentifiedImageError
import pytesseract
import pyheif
import pdfplumber
from docx import Document

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BaseDocumentProcessor(ABC):
    def __init__(self, file: Union[BytesIO, 'File'], filename: str):
        self.file = file
        self.filename = filename

    @abstractmethod
    def extract_text(self) -> Optional[str]:
        pass

class ImageProcessor(BaseDocumentProcessor):
    def extract_text(self) -> Optional[str]:
        try:
            image = Image.open(self.file)
            text = pytesseract.image_to_string(image)
            return text.strip() or None
        except UnidentifiedImageError as e:
            logger.error(f"Unable to open image file: {self.filename}. Error: {e}")
        except Exception as e:
            logger.error(f"Error processing image file: {self.filename}. Error: {e}")
        return None

class HEICProcessor(BaseDocumentProcessor):
    def extract_text(self) -> Optional[str]:
        try:
            heif_file = pyheif.read(self.file.read())
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            text = pytesseract.image_to_string(image)
            return text.strip() or None
        except Exception as e:
            logger.error(f"Unable to process HEIC file: {self.filename}. Error: {e}")
        return None

class PDFProcessor(BaseDocumentProcessor):
    def extract_text(self) -> Optional[str]:
        text = ""
        try:
            with pdfplumber.open(self.file) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        logger.warning(f"No text extracted from page {page_number} of PDF: {self.filename}")
            return text.strip() or None
        except Exception as e:
            logger.error(f"Error processing PDF file: {self.filename}. Error: {e}")
        return None

class DOCXProcessor(BaseDocumentProcessor):
    def extract_text(self) -> Optional[str]:
        text = ""
        try:
            doc = Document(self.file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip() or None
        except Exception as e:
            logger.error(f"Error processing DOCX file: {self.filename}. Error: {e}")
        return None

def get_processor(file: Union[BytesIO, 'File'], filename: str) -> Optional[BaseDocumentProcessor]:
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension in {".png", ".jpg", ".jpeg"}:
        logger.info(f"Processing image file: {filename}")
        return ImageProcessor(file, filename)
    elif file_extension == ".heic":
        logger.info(f"Processing HEIC file: {filename}")
        return HEICProcessor(file, filename)
    elif file_extension == ".pdf":
        logger.info(f"Processing PDF file: {filename}")
        return PDFProcessor(file, filename)
    elif file_extension == ".docx":
        logger.info(f"Processing DOCX file: {filename}")
        return DOCXProcessor(file, filename)
    else:
        logger.warning(f"Unsupported file type: {file_extension}")
        return None

@log_timing("OCR Text Extraction")
def extract_text_from_file(file: Union[BytesIO, 'File'], filename: str) -> Optional[str]:
    processor = get_processor(file, filename)
    if not processor:
        logger.error(f"No processor available for file: {filename}")
        return None

    text = processor.extract_text()
    if not text:
        logger.warning(f"No text extracted from file: {filename}")
        return None

    return text
