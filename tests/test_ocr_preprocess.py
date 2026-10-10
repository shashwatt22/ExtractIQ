from PIL import Image, ImageDraw
from backend.app.pipeline.ingest import _prepare_ocr_image


def test_ocr_preprocess_upscales_tiny_receipts_and_grayscales():
    image = Image.new("RGB", (300, 450), "white")
    ImageDraw.Draw(image).text((15, 15), "TOTAL 123.45", fill="black")
    result = _prepare_ocr_image(image)
    assert result.mode == "L"
    assert min(result.size) >= 900
    assert result.size[0] > image.size[0]


def test_ocr_preprocess_handles_blank_pages():
    image = Image.new("RGB", (600, 900), "white")
    result = _prepare_ocr_image(image)
    assert result.mode == "L"
    assert result.size[0] >= image.size[0]
