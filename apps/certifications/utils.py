from django.contrib.staticfiles.storage import staticfiles_storage
from reportlab.pdfbase import pdfmetrics

def resize_font_for_text(canvas, text, max_width, min_font_size=10, max_font_size=120):
    """
    Réduit la taille de la police pour que le texte tienne dans une largeur maximale.

    :param canvas: L'objet canvas de ReportLab sur lequel dessiner le texte.
    :param text: Le texte à dessiner.
    :param max_width: La largeur maximale que le texte peut occuper.
    :param min_font_size: La taille minimale de la police (par défaut 10).
    :param max_font_size: La taille maximale de la police (par défaut 120).
    :return: La taille de la police utilisée.
    """
    # Commence avec la taille maximale
    font_size = max_font_size

    # Calcule la largeur du texte avec la taille de police initiale
    text_width = pdfmetrics.stringWidth(text, "AlexBrush", font_size)

    # Réduit la taille de la police tant que le texte dépasse la largeur maximale
    while text_width > max_width and font_size > min_font_size:
        font_size -= 1
        text_width = pdfmetrics.stringWidth(text, "AlexBrush", font_size)

    # Retourne la taille de la police utilisée
    return font_size


from typing import List, Tuple, Optional
from dataclasses import dataclass
from PIL import ImageFont, ImageDraw


@dataclass
class TextStyle:
    font: ImageFont.FreeTypeFont
    color: Tuple[int, int, int] = (0, 0, 0)
    is_bold: bool = False


@dataclass
class Word:
    text: str
    style: TextStyle
    width: int


class TextFormatter:
    def __init__(
            self,
            max_width: int,
            line_height: int,
            regular_font: ImageFont.FreeTypeFont,
            bold_font: ImageFont.FreeTypeFont
    ):
        self.max_width = max_width
        self.line_height = line_height
        self.regular_style = TextStyle(regular_font, is_bold=False)
        self.bold_style = TextStyle(bold_font, is_bold=True)

    def measure_text(self, text: str, font: ImageFont.FreeTypeFont) -> int:
        """Measure the width of text with a given font."""
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0]

    def parse_text_to_words(self, text: str) -> List[Word]:
        """Parse text with markdown-style bold markers (**) into individual words."""
        words = []
        segments = text.split('**')

        for i, segment in enumerate(segments):
            if not segment:
                continue

            style = self.bold_style if i % 2 else self.regular_style

            # Split segment into words while preserving spaces
            segment_words = segment.split()

            for word in segment_words:
                width = self.measure_text(word + " ", style.font)
                words.append(Word(word, style, width))

        return words

    def arrange_words_into_lines(self, words: List[Word]) -> List[List[Word]]:
        """Arrange words into lines respecting max_width."""
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            # If adding this word would exceed max_width, start a new line
            if current_width + word.width > self.max_width and current_line:
                lines.append(current_line)
                current_line = []
                current_width = 0

            current_line.append(word)
            current_width += word.width

        # Don't forget the last line
        if current_line:
            lines.append(current_line)

        return lines

    def render_text(
            self,
            draw: ImageDraw.ImageDraw,
            text: str,
            center_x: int,
            start_y: int
    ) -> int:
        """Render the text and return the final y position."""
        words = self.parse_text_to_words(text)
        lines = self.arrange_words_into_lines(words)
        current_y = start_y

        for line in lines:
            # Calculate line width for centering
            line_width = sum(word.width for word in line)
            current_x = center_x - (line_width / 2)

            # Render each word in the line
            for word in line:
                draw.text(
                    (current_x, current_y),
                    word.text + " ",
                    font=word.style.font,
                    fill=word.style.color
                )
                current_x += word.width

            current_y += self.line_height

        return current_y


def format_certificate_text(
        draw: ImageDraw.ImageDraw,
        text: str,
        center_x: int,
        start_y: int,
        max_width: int = 1900,
        line_height: int = 50,
        regular_font: Optional[ImageFont.FreeTypeFont] = None,
        bold_font: Optional[ImageFont.FreeTypeFont] = None
) -> int:
    """
    Format and render certificate text with bold sections that can span multiple lines.
    Returns the final y position after rendering.
    """
    formatter = TextFormatter(
        max_width=max_width,
        line_height=line_height,
        regular_font=regular_font or ImageFont.truetype(staticfiles_storage.path('fonts/Helvetica.ttf'), 36),
        bold_font=bold_font or ImageFont.truetype(staticfiles_storage.path('fonts/Helvetica-Bold.ttf'), 40)
    )

    return formatter.render_text(draw, text, center_x, start_y)


