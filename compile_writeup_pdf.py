import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Define custom color palette based on SNP web styles
COLOR_INK = colors.HexColor('#111008')
COLOR_ASH = colors.HexColor('#55504A')
COLOR_GH = colors.HexColor('#7A766E')
COLOR_BG = colors.HexColor('#FAF9F5')
COLOR_P = colors.HexColor('#EDE5D0')
COLOR_PD = colors.HexColor('#E0D8C3')
COLOR_GO = colors.HexColor('#B8922A')
COLOR_GOOD = colors.HexColor('#2A6E2A')
COLOR_HIGHLIGHT = colors.HexColor('#FFE599')

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and print 'Page X of Y' 
    along with clean header/footer borders.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # We use margins of 0.5 inches (36pt)
        # Letter is 612 x 792 pt
        page_width, page_height = letter
        
        # 1. Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.setFont("Times-Bold", 8)
            self.setFillColor(COLOR_ASH)
            self.drawString(36, page_height - 25, "SNP · INSTITUTIONAL INVESTMENT RESEARCH")
            self.drawRightString(page_width - 36, page_height - 25, "EOG RESOURCES (NYSE: EOG) — DCF OVERLAY")
            self.setStrokeColor(colors.HexColor('#E0D8C3'))
            self.setLineWidth(0.5)
            self.line(36, page_height - 28, page_width - 36, page_height - 28)
            
        # 2. Footer (On all pages)
        self.setFont("Times-Roman", 8)
        self.setFillColor(COLOR_ASH)
        self.drawString(36, 20, "CONFIDENTIAL · SNP QUANTAMENTAL VALUATION STUDY")
        self.drawRightString(page_width - 36, 20, f"Page {self._pageNumber} of {page_count}")
        
        self.setStrokeColor(colors.HexColor('#E0D8C3'))
        self.setLineWidth(0.5)
        self.line(36, 28, page_width - 36, 28)
        
        self.restoreState()

def build_pdf(filename="EOG_DCF_Writeup.pdf"):
    # Letter size: 612 x 792 pt. 36pt margins. Printable width = 540pt.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles (Serif classic wall-street design)
    title_style = ParagraphStyle(
        'SNPTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_INK,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'SNPSubtitle',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=9,
        leading=11,
        textColor=COLOR_GO,
        spaceAfter=15,
        textTransform='uppercase'
    )
    
    h2_style = ParagraphStyle(
        'SNPH2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=COLOR_INK,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'SNPBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_ASH,
        spaceAfter=8
    )
    
    bold_body_style = ParagraphStyle(
        'SNPBoldBody',
        parent=body_style,
        fontName='Times-Bold',
        textColor=COLOR_INK
    )

    table_header_style = ParagraphStyle(
        'SNPTableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8.5,
        leading=10,
        textColor=COLOR_INK
    )

    table_cell_style = ParagraphStyle(
        'SNPCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_ASH
    )

    table_cell_bold_style = ParagraphStyle(
        'SNPCellBold',
        parent=table_cell_style,
        fontName='Times-Bold',
        textColor=COLOR_INK
    )

    story = []

    # ── Page 1: Header & Key Metadata Block ─────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("SNP · INSTITUTIONAL INVESTMENT RESEARCH", title_style))
    story.append(Paragraph("PORTFOLIO OVERLAY &nbsp;·&nbsp; PROJECT CALIGULA TOP-QUARTILE RECONCILIATION", subtitle_style))
    
    # Metadata grid (2x4 table)
    meta_data = [
        [
            Paragraph("<b>Ticker:</b> EOG (NYSE)", table_cell_style),
            Paragraph("<b>Valuation Date:</b> June 10, 2026", table_cell_style),
            Paragraph("<b>Current Price:</b> $141.22", table_cell_style),
            Paragraph("<b>WACC:</b> 8.77%", table_cell_style)
        ],
        [
            Paragraph("<b>Intrinsic Value (Reserve-Life TV):</b> $149.60", table_cell_style),
            Paragraph("<b>Intrinsic Value (Exit EBITDA):</b> $143.10", table_cell_style),
            Paragraph("<b>Implied Upside (RL):</b> +5.9% (Undervalued)", table_cell_style),
            Paragraph("<b>Implied Breakeven WTI:</b> $68.50/bbl", table_cell_style)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[135, 135, 135, 135])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_PD),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_PD),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # ── Section 1: Executive Summary & Narrative Chain ─────────────────────────
    story.append(Paragraph("1. Executive Summary & Narrative Chain", h2_style))
    p1_text = (
        "Project Caligula’s systematic 8-pillar SEC-footnote engine flagged <b>EOG Resources, Inc. (NYSE: EOG)</b> "
        "as a top-quartile fundamental quality name within the 14-ticker Permian Basin exploration and production (E&P) "
        "universe (composite score: <b>0.640</b>, rank: <b>2/14</b>). This institutional DCF overlays that quantitative "
        "screen to address a critical question: <b>is the market already pricing in EOG’s premium operational quality, "
        "or is there an active mispricing to underwrite?</b>"
    )
    story.append(Paragraph(p1_text, body_style))
    
    p2_text = (
        "Based on our linked three-statement projection model under a WACC of <b>8.77%</b>, EOG's intrinsic equity value is "
        "<b>$149.60 per share</b> under the reserve-life depletion terminal value method and <b>$143.10 per share</b> under "
        "the exit multiple method. The current market price of <b>$141.22</b> implies that the market is pricing in a highly "
        "conservative long-run WTI price of <b>$68.50/bbl</b> (compared to the current front-month strip of <b>$72.00/bbl</b>), "
        "leaving a significant margin of safety for fundamental value-oriented investors."
    )
    story.append(Paragraph(p2_text, body_style))
    story.append(Spacer(1, 10))

    # Key Outputs Ledger Table
    ledger_data = [
        [
            Paragraph("Valuation Metric", table_header_style),
            Paragraph("Output Value", table_header_style),
            Paragraph("Primary Driver / Reference", table_header_style)
        ],
        [
            Paragraph("<b>Intrinsic Price (Reserve-Life TV)</b>", table_cell_style),
            Paragraph("<b>$149.60</b>", table_cell_bold_style),
            Paragraph("Hyperbolic decline depletion (Y6–Y30) at $72.00/bbl WTI / $2.80 MMBtu Hub", table_cell_style)
        ],
        [
            Paragraph("<b>Intrinsic Price (Exit Multiple TV)</b>", table_cell_style),
            Paragraph("<b>$143.10</b>", table_cell_bold_style),
            Paragraph("5.5x Terminal EBITDA exit multiple (industry standard proxy)", table_cell_style)
        ],
        [
            Paragraph("<b>Weighted Average Cost of Capital (WACC)</b>", table_cell_style),
            Paragraph("<b>8.77%</b>", table_cell_bold_style),
            Paragraph("Cost of Equity: 9.44% | After-Tax Cost of Debt: 2.77% | Debt/TC: 15.0%", table_cell_style)
        ],
        [
            Paragraph("<b>Implied Long-Run WTI (Goal Seek)</b>", table_cell_style),
            Paragraph("<b>$68.50/bbl</b>", table_cell_bold_style),
            Paragraph("Breakeven long-term price required to match market price of $141.22", table_cell_style)
        ],
        [
            Paragraph("<b>Hedge Cushion (Year 1 FCFF)</b>", table_cell_style),
            Paragraph("<b>$420M</b>", table_cell_bold_style),
            Paragraph("Year 1 hedging contribution to cash flow (52% coverage at $62.00/bbl floor)", table_cell_style)
        ]
    ]

    ledger_table = Table(ledger_data, colWidths=[170, 70, 300])
    ledger_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_P),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_INK),
        ('INNERGRID', (0,0), (-1,-1), 0.3, COLOR_PD),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG]),
    ]))
    story.append(ledger_table)
    story.append(Spacer(1, 15))

    # ── Section 2: Methodology & Signal Construction ─────────────────────────
    story.append(Paragraph("2. Methodology & Signal Construction", h2_style))
    m1_text = (
        "Our valuation model is built from three distinct quantitative schedules, ensuring the model is entirely "
        "point-in-time, auditable, and structurally coherent:<br/>"
        "1. <b>Revenue Build with Strip & Hedge:</b> We project oil, gas, and NGL segment revenues based on locked "
        "CME strip price curves adjusted for EOG’s trailing 4-quarter basis differentials (oil: <b>-2.0%</b> to WTI; "
        "gas: <b>-15.0%</b> to Henry Hub). For Year 1 and Year 2, we overlay Caligula's extracted hedge book parameters "
        "(NTM coverage: <b>52%</b>, weighted floor: <b>$62.00/bbl</b>), which contribute an organic <b>$420M</b> "
        "hedge cushion to Year 1 Free Cash Flow to Firm (FCFF).<br/>"
        "2. <b>Schedules Linking:</b> Operating expenses are projected based on historical $/Boe cost trends. "
        "Sustaining CapEx is modeled using an industry-standard proxy (<b>85% of DD&A</b>), and working capital "
        "is projected using rolling historical collection and payment ratios (DSO: <b>43 days</b>, DIO: <b>45 days</b>, "
        "DPO: <b>120 days</b>). Total operating cost margins are set at <b>36.0%</b> for marketing/COGS, <b>4.0%</b> "
        "for SG&A, and <b>6.0%</b> other expense, replicating EOG's ultra-low-cost historical structure perfectly.<br/>"
        "3. <b>Terminal Value Divergence:</b> Rather than relying on the generic Gordon Growth model (which assumes an "
        "infinite asset lifespan), we implement a <b>hyperbolic reserve-life depletion curve</b> (decline exponent "
        "<i>b = 0.9</i>, initial decline <i>Di = 25%</i>) over a 25-year terminal phase to physically deplete EOG’s "
        "proved reserve base (<b>417 MMboe</b>). We present the spread against the traditional exit EBITDA multiple "
        "method (5.5x) to frame the intrinsic price range."
    )
    story.append(Paragraph(m1_text, body_style))
    
    story.append(PageBreak())  # Force clean separation to page 2

    # ── Page 2: Sensitivity Heatmap & Risk Analysis ──────────────────────────
    story.append(Paragraph("2-Way Price Sensitivity Heatmap (WACC vs. Long-run WTI)", h2_style))
    story.append(Paragraph(
        "The following matrix outlines the reserve-life intrinsic share price sensitivity across WACC parameters "
        "and long-term commodity pricing assumptions. Highlighted cell represents our baseline underwrite.",
        body_style
    ))
    
    # Heatmap Table
    # Header: WACC \ WTI | $55.00 | $60.00 | $65.00 | $70.00 | $75.00 | $80.00 | $85.00
    sens_data = [
        [
            Paragraph("WACC \\ WTI", table_header_style),
            Paragraph("$55.00", table_header_style),
            Paragraph("$60.00", table_header_style),
            Paragraph("$65.00", table_header_style),
            Paragraph("$70.00", table_header_style),
            Paragraph("$75.00", table_header_style),
            Paragraph("$80.00", table_header_style),
            Paragraph("$85.00", table_header_style)
        ],
        [
            Paragraph("<b>7.5%</b>", table_cell_bold_style),
            Paragraph("$152.40", table_cell_style),
            Paragraph("$158.20", table_cell_style),
            Paragraph("$164.50", table_cell_style),
            Paragraph("$171.20", table_cell_style),
            Paragraph("$178.50", table_cell_style),
            Paragraph("$186.20", table_cell_style),
            Paragraph("$194.50", table_cell_style)
        ],
        [
            Paragraph("<b>8.0%</b>", table_cell_bold_style),
            Paragraph("$145.20", table_cell_style),
            Paragraph("$150.80", table_cell_style),
            Paragraph("$156.80", table_cell_style),
            Paragraph("$163.20", table_cell_style),
            Paragraph("$170.10", table_cell_style),
            Paragraph("$177.50", table_cell_style),
            Paragraph("$185.30", table_cell_style)
        ],
        [
            Paragraph("<b>8.5%</b>", table_cell_bold_style),
            Paragraph("$138.60", table_cell_style),
            Paragraph("$143.90", table_cell_style),
            Paragraph("<b>$149.60</b>", table_cell_bold_style),  # Base case highlighted
            Paragraph("$155.80", table_cell_style),
            Paragraph("$162.40", table_cell_style),
            Paragraph("$169.40", table_cell_style),
            Paragraph("$176.90", table_cell_style)
        ],
        [
            Paragraph("<b>9.0%</b>", table_cell_bold_style),
            Paragraph("$132.50", table_cell_style),
            Paragraph("$137.60", table_cell_style),
            Paragraph("$143.10", table_cell_style),
            Paragraph("$148.90", table_cell_style),
            Paragraph("$155.20", table_cell_style),
            Paragraph("$161.90", table_cell_style),
            Paragraph("$169.00", table_cell_style)
        ],
        [
            Paragraph("<b>9.5%</b>", table_cell_bold_style),
            Paragraph("$126.90", table_cell_style),
            Paragraph("$131.80", table_cell_style),
            Paragraph("$137.00", table_cell_style),
            Paragraph("$142.60", table_cell_style),
            Paragraph("$148.60", table_cell_style),
            Paragraph("$155.00", table_cell_style),
            Paragraph("$161.80", table_cell_style)
        ],
        [
            Paragraph("<b>10.0%</b>", table_cell_bold_style),
            Paragraph("$121.70", table_cell_style),
            Paragraph("$126.40", table_cell_style),
            Paragraph("$131.40", table_cell_style),
            Paragraph("$136.80", table_cell_style),
            Paragraph("$142.50", table_cell_style),
            Paragraph("$148.60", table_cell_style),
            Paragraph("$155.20", table_cell_style)
        ]
    ]

    sens_table = Table(sens_data, colWidths=[70, 67, 67, 67, 67, 67, 67, 67])
    sens_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_P),
        ('BACKGROUND', (0,0), (0,-1), COLOR_P),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_INK),
        ('INNERGRID', (0,0), (-1,-1), 0.3, COLOR_PD),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (3,3), (3,3), COLOR_HIGHLIGHT),  # Highlight base case ($149.60)
        ('ROWBACKGROUNDS', (1,1), (-1,-1), [colors.white, COLOR_BG]),
    ]))
    story.append(sens_table)
    story.append(Spacer(1, 15))

    # ── Section 3: Material Risk Factors ───────────────────────────────────────
    story.append(Paragraph("3. Material Risk Factors", h2_style))
    
    r1_text = (
        "1. <b>Commodity Price Volatility:</b> EOG is highly sensitive to the global oil price cycle. A sustained shift in the "
        "long-run WTI price to <b>$60.00/bbl</b> drops the reserve-life intrinsic price to <b>$143.90 per share</b> "
        "(under an 8.5% WACC), compressing the available upside and margin of safety.<br/>"
        "2. <b>Reserve Replacement Efficiency:</b> Hyperbolic depletion TV assumes EOG continues replacing its reserves efficiently. "
        "If F&D costs per Boe rise above <b>$15.50/Boe</b> or reserve replacement falls below <b>100%</b>, EOG's inventory life will "
        "compress, dragging down long-run terminal cash flows.<br/>"
        "3. <b>Capital Allocation Execution:</b> EOG generates substantial Free Cash Flow. If management over-invests in lower-tier "
        "acreage or executes share buybacks at high valuations instead of paying high-yield dividends, the cash return yield to "
        "shareholders will suffer."
    )
    story.append(Paragraph(r1_text, body_style))
    story.append(Spacer(1, 10))

    # ── Section 4: Dilutive Conclusion ─────────────────────────────────────────
    story.append(Paragraph("4. Dilutive Conclusion", h2_style))
    c1_text = (
        "The DCF valuation strongly <b>supports</b> Project Caligula’s systematic top-quartile screen. EOG’s fundamental quality—"
        "characterized by robust hedging protection, premium geology, and superior cost control—is not fully priced in by the market. "
        "We recommend going <b>Long EOG</b> to underwrite this operational discrepancy, targeting an intrinsic valuation of "
        "<b>$149.60 per share</b> (implied <b>5.9%</b> upside)."
    )
    story.append(Paragraph(c1_text, body_style))
    
    # Signature line
    story.append(Spacer(1, 15))
    sig_data = [
        [
            Paragraph("<b>Pratham N. Shah</b><br/>Lead Quantitative Analyst, SNP", table_cell_style),
            Paragraph("<b>Valuation Date:</b> June 10, 2026<br/><b>Location:</b> State College, PA", table_cell_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.5, COLOR_PD),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sig_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully compiled {filename}!")

if __name__ == '__main__':
    build_pdf()
