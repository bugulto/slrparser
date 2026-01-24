from flask import Blueprint, request, send_file, jsonify
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
import base64
import tempfile
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import uuid
import json
from datetime import datetime

# Create blueprint for PDF routes
pdf_bp = Blueprint('pdf', __name__)

def create_styles():
    """Create custom styles for the PDF"""
    styles = getSampleStyleSheet()
    
    # helper to add or update styles
    def add_or_get_style(name, parent_name, **kwargs):
        if name in styles:
            # Update existing style or just return it
            # For simplicity, we'll just use the existing one if it's there
            return styles[name]
        
        new_style = ParagraphStyle(name=name, parent=styles[parent_name], **kwargs)
        styles.add(new_style)
        return new_style

    # Title style
    add_or_get_style(
        'CustomTitle',
        'Title',
        fontSize=24,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Main heading style
    add_or_get_style(
        'MainHeading',
        'Heading1',
        fontSize=18,
        textColor=colors.HexColor('#4A5568'),
        spaceBefore=20,
        spaceAfter=10,
        leftIndent=0
    )
    
    # Subheading style
    add_or_get_style(
        'SubHeading',
        'Heading2',
        fontSize=14,
        textColor=colors.HexColor('#2D3748'),
        spaceBefore=15,
        spaceAfter=8,
        backColor=colors.HexColor('#EDF2F7'),
        leftIndent=10
    )
    
    # Code style - Use a more unique name to avoid conflict with built-in 'Code'
    add_or_get_style(
        'CustomCode',
        'Code',
        fontSize=10,
        fontName='Courier',
        textColor=colors.HexColor('#2D3748'),
        backColor=colors.HexColor('#F7FAFC'),
        leftIndent=20,
        borderPadding=5,
        borderWidth=1,
        borderColor=colors.HexColor('#E2E8F0')
    )
    
    # Normal style with better spacing
    add_or_get_style(
        'NormalSpaced',
        'Normal',
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    # Success style
    add_or_get_style(
        'Success',
        'Normal',
        fontSize=11,
        textColor=colors.HexColor('#276749'),
        backColor=colors.HexColor('#C6F6D5'),
        spaceAfter=8
    )
    
    # Error style
    add_or_get_style(
        'Error',
        'Normal',
        fontSize=11,
        textColor=colors.HexColor('#9B2C2C'),
        backColor=colors.HexColor('#FED7D7'),
        spaceAfter=8
    )
    
    return styles

def generate_comprehensive_slr_pdf(parser_data):
    """
    Generate a comprehensive PDF with all SLR parsing steps.
    Optimized for better structure, minimal white spaces, and accurate content.
    """
    # Generate unique filename
    file_name = f"slr_parser_report_{uuid.uuid4().hex[:8]}.pdf"
    file_path = os.path.join(tempfile.gettempdir(), file_name)
    
    # Create document
    doc = SimpleDocTemplate(
        file_path, 
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    styles = create_styles()
    story = []
    
    # ---------- COVER PAGE ----------
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("<b>SLR PARSER DESIGN REPORT</b>", styles['CustomTitle']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("<center>Comprehensive Technical Analysis of Formal Grammar and SLR(1) Parsing States</center>", styles['NormalSpaced']))
    story.append(Spacer(1, 0.5*inch))
    
    # Create a summary box on cover
    summary_info = [
        ["Report Type", "SLR(1) Parsing Full Workflow"],
        ["Generated Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ["Grammar Status", "SLR(1) Compliant" if parser_data.get('is_slr1') else "Contains Conflicts"]
    ]
    summary_table = Table(summary_info, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F7FAFC')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*inch))
    
    # ---------- STEP 1. GRAMMAR INPUT & VERIFICATION ----------
    story.append(Paragraph("<b>Step 1: Grammar Input & Verification</b>", styles['MainHeading']))
    
    # Grammar Synthesis Table
    story.append(Paragraph("<b>Grammar Synthesis:</b>", styles['SubHeading']))
    synth_data = [
        ["Non-Terminals", ", ".join(parser_data.get('non_terminals', []))],
        ["Terminals", ", ".join(parser_data.get('terminals', []))],
        ["Start Symbol", parser_data.get('start_symbol', 'N/A')]
    ]
    synth_table = Table(synth_data, colWidths=[1.5*inch, 4.5*inch])
    synth_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EDF2F7')),
    ]))
    story.append(synth_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Original Grammar Rules:</b>", styles['SubHeading']))
    if 'grammar' in parser_data:
        grammar = parser_data['grammar']
        for nt, productions in grammar.items():
            for prod in productions:
                story.append(Paragraph(f"<b>{nt}</b> → {prod}", styles['CustomCode']))
    
    # ---------- STEP 2. AUGMENTED GRAMMAR ----------
    story.append(Paragraph("<b>Step 2: Augmented Grammar</b>", styles['MainHeading']))
    story.append(Paragraph("The grammar is augmented with a new start symbol (S') to define the initial state of the parser.", styles['NormalSpaced']))
    
    if 'augmented_grammar' in parser_data:
        aug_grammar = parser_data['augmented_grammar']
        for nt, productions in aug_grammar.items():
            for prod in productions:
                story.append(Paragraph(f"<b>{nt}</b> → {prod}", styles['CustomCode']))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Numbered Productions (Canonical Order):</b>", styles['SubHeading']))
    if 'productions' in parser_data:
        productions = parser_data['productions']
        table_data = [["ID", "Production Rule"]]
        for i, (lhs, rhs) in enumerate(productions):
            rhs_str = rhs if rhs else "ε"
            table_data.append([str(i), f"{lhs} → {rhs_str}"])
        
        table = Table(table_data, colWidths=[0.6*inch, 4.4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CBD5E0')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(table)
    
    # ---------- STEP 3. FIRST & FOLLOW SETS ----------
    story.append(Paragraph("<b>Step 3: FIRST & FOLLOW Sets</b>", styles['MainHeading']))
    
    set_data = [["Non-Terminal", "FIRST Set", "FOLLOW Set"]]
    if 'first_sets' in parser_data and 'follow_sets' in parser_data:
        all_nts = sorted(parser_data['first_sets'].keys())
        for nt in all_nts:
            first_set = parser_data['first_sets'].get(nt, [])
            follow_set = parser_data['follow_sets'].get(nt, [])
            set_data.append([
                nt, 
                "{ " + ", ".join(sorted(first_set)) + " }",
                "{ " + ", ".join(sorted(follow_set)) + " }"
            ])
        
        set_table = Table(set_data, colWidths=[1.2*inch, 2.4*inch, 2.4*inch])
        set_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(set_table)
    
    story.append(PageBreak())
    
    # ---------- STEP 4. DFA BUILDER ----------
    story.append(Paragraph("<b>Step 4: DFA Builder</b>", styles['MainHeading']))
    
    # DFA Diagram
    if parser_data.get('dfa_diagram'):
        story.append(Paragraph("<b>4.1 DFA Canonical Collection Visual:</b>", styles['SubHeading']))
        try:
            img_data = base64.b64decode(parser_data['dfa_diagram'])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                tmp_img.write(img_data)
                tmp_img_path = tmp_img.name
            story.append(Image(tmp_img_path, width=6.5*inch, height=4.5*inch, kind='proportional'))
            story.append(Spacer(1, 0.1*inch))
        except:
            pass

    # DFA States
    story.append(Paragraph("<b>4.2 LR(0) Item Sets (States):</b>", styles['SubHeading']))
    if 'states' in parser_data:
        states = parser_data['states']
        state_chunks = [states[i:i+2] for i in range(0, len(states), 2)]
        for chunk in state_chunks:
            row_cells = []
            for state in chunk:
                state_html = f"<b>State {state['name']}{' (Start)' if state.get('is_start') else ''}:</b><br/>"
                for item in state.get('items', []):
                    state_html += f"&nbsp;&nbsp;{item}<br/>"
                row_cells.append(Paragraph(state_html, styles['CustomCode']))
            if len(row_cells) < 2: row_cells.append(Paragraph("", styles['Normal']))
            story.append(Table([row_cells], colWidths=[3.2*inch, 3.2*inch], style=[('VALIGN', (0,0), (-1,-1), 'TOP')]))

    # ---------- STEP 5. SLR PARSING TABLE ----------
    story.append(Paragraph("<b>Step 5: SLR Parsing Table</b>", styles['MainHeading']))
    
    if 'parsing_table' in parser_data:
        pt = parser_data['parsing_table']
        action_table = pt.get('ACTION', {})
        goto_table = pt.get('GOTO', {})
        
        terms = set()
        for s in action_table.values(): terms.update(s.keys())
        terms = sorted(list(terms))
        if '$' in terms: terms.remove('$'); terms.append('$')
            
        nonterms = set()
        for s in goto_table.values(): nonterms.update(s.keys())
        nonterms = sorted(list(nonterms))
        
        header1 = ["State"] + ["ACTION"] * len(terms) + ["GOTO"] * len(nonterms)
        header2 = [""] + terms + nonterms
        full_table_data = [header2]
        
        all_state_ids = sorted([int(k) for k in action_table.keys()])
        for sid in all_state_ids:
            sid_str = str(sid)
            row = [f"I{sid}"]
            row += [action_table.get(sid_str, {}).get(t, "") for t in terms]
            row += [goto_table.get(sid_str, {}).get(nt, "") for nt in nonterms]
            full_table_data.append(row)
            
        n_cols = len(terms) + len(nonterms) + 1
        col_w = 6.4 / n_cols
        parsing_table = Table(full_table_data, colWidths=[0.6*inch] + [col_w*inch] * (n_cols-1))
        
        p_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1,-1), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]
        
        for r_idx, row in enumerate(full_table_data[1:], 1):
            for c_idx, cell in enumerate(row):
                if not cell: continue
                if cell.startswith('s'): p_style.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.darkblue))
                elif cell.startswith('r'): p_style.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.darkred))
                elif cell == 'acc': p_style.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.lightgreen))
        
        parsing_table.setStyle(TableStyle(p_style))
        story.append(parsing_table)

    # Conflict Analysis
    if parser_data.get('conflicts'):
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Warning: {len(parser_data['conflicts'])} conflicts found!</b>", styles['Error']))
        for conflict in parser_data['conflicts']:
            story.append(Paragraph(f"• {conflict}", styles['Error']))

    # ---------- STEP 6. INPUT STRING PARSER ----------
    if 'parsing_result' in parser_data:
        story.append(PageBreak())
        story.append(Paragraph("<b>Step 6: Input String Parser</b>", styles['MainHeading']))
        story.append(Paragraph(f"<b>Test Input:</b> {parser_data.get('input_string', 'Empty')}", styles['NormalSpaced']))
        
        res = parser_data['parsing_result']
        status_box = styles['Success'] if res.get('success') else styles['Error']
        story.append(Paragraph(f"<b>Parsing Result:</b> {res.get('message', 'N/A')}", status_box))
        
        if res.get('steps'):
            trace_data = [["Step", "Stack Content", "Input Buffer", "Action Taken"]]
            for s in res['steps']:
                trace_data.append([str(s['step']), s['stack'], s['input'], s['action']])
            
            trace_table = Table(trace_data, colWidths=[0.5*inch, 2.3*inch, 1.4*inch, 2.3*inch])
            trace_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F7FAFC')),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
            ]))
            story.append(trace_table)

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<center><b>--- Technical Analysis Complete ---</b></center>", styles['NormalSpaced']))
    
    doc.build(story)
    return file_path

@pdf_bp.route('/export-pdf', methods=['POST'])
def export_pdf():
    """Generate comprehensive SLR parser PDF"""
    try:
        data = request.json
        
        # This function should be called from slr_service.py
        # We need to reconstruct the parser data from the grammar
        from slr_service import SLRParser
        
        parser = SLRParser()
        grammar_text = data.get('grammar', '')
        
        if not grammar_text:
            return jsonify({'success': False, 'error': 'No grammar provided'})
        
        # Parse grammar
        grammar = parser.parse_grammar(grammar_text)
        
        # Augment grammar
        augmented_grammar = parser.augment_grammar()
        
        # Compute FIRST and FOLLOW
        first_sets = parser.compute_first_sets()
        follow_sets = parser.compute_follow_sets()
        
        # Build DFA
        states, transitions = parser.build_dfa()
        
        # Format states for PDF
        formatted_states = []
        for i, state in enumerate(states):
            items = []
            for item in state:
                lhs, rhs, dot_pos = item
                rhs_str = rhs if rhs else 'ε'
                symbols = parser._split_production(rhs_str)
                item_str = f"{lhs} → " + ' '.join(symbols[:dot_pos]) + ' • ' + ' '.join(symbols[dot_pos:])
                items.append(item_str)
            formatted_states.append({
                'name': f'I{i}',
                'is_start': i == 0,
                'items': items
            })
        
        # Format transitions for PDF
        formatted_transitions = []
        for (state_idx, symbol), next_state_idx in transitions.items():
            formatted_transitions.append({
                'from': f'I{state_idx}',
                'symbol': symbol,
                'to': f'I{next_state_idx}'
            })
        
        # Build parsing table
        parsing_table, conflicts = parser.build_parsing_table()
        
        # Check if grammar is SLR(1)
        is_slr1 = len(conflicts) == 0
        
        # Prepare parser data for PDF generation
        parser_data = {
            'grammar': grammar,
            'augmented_grammar': augmented_grammar,
            'productions': parser.productions,
            'first_sets': first_sets,
            'follow_sets': follow_sets,
            'states': formatted_states,
            'transitions': formatted_transitions,
            'parsing_table': parsing_table,
            'conflicts': conflicts,
            'is_slr1': is_slr1,
            'start_symbol': parser.start_symbol
        }
        
        # Generate PDF
        pdf_path = generate_comprehensive_slr_pdf(parser_data)
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name='SLR_Parser_Report.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Also keep the original simple function for backward compatibility
def generate_pdf(grammar, start_symbol, first, follow):
    """Simple PDF generator for FIRST/FOLLOW sets only"""
    file_name = f"grammar_notes_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join("/tmp", file_name)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    story = []

    # ---------- TITLE ----------
    story.append(Paragraph("<b>Compiler Design Notes</b>", styles["Title"]))
    story.append(Paragraph(
        "Grammar, FIRST and FOLLOW (Auto-generated)",
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    # ---------- INPUT GRAMMAR ----------
    story.append(Paragraph("<b>1. Input Grammar</b>", styles["Heading2"]))
    for nt, productions in grammar.items():
        for p in productions:
            story.append(Paragraph(f"{nt} → {p}", styles["Normal"]))

    story.append(Spacer(1, 12))

    # ---------- GRAMMAR INFO ----------
    story.append(Paragraph("<b>2. Grammar Definition</b>", styles["Heading2"]))
    story.append(Paragraph("Type: Context-Free Grammar (CFG)", styles["Normal"]))
    story.append(Paragraph(f"Start Symbol: {start_symbol}", styles["Normal"]))

    non_terminals = ", ".join(grammar.keys())
    story.append(Paragraph(f"Non-terminals: {{ {non_terminals} }}", styles["Normal"]))

    story.append(Spacer(1, 12))

    # ---------- FIRST ----------
    story.append(Paragraph("<b>3. FIRST Set</b>", styles["Heading2"]))
    story.append(Paragraph(
        "FIRST(X) is the set of terminals that begin strings derivable from X.",
        styles["Normal"]
    ))

    for nt, values in first.items():
        story.append(
            Paragraph(f"FIRST({nt}) = {{ {', '.join(values)} }}", styles["Normal"])
        )

    story.append(Spacer(1, 12))

    # ---------- FOLLOW ----------
    story.append(Paragraph("<b>4. FOLLOW Set</b>", styles["Heading2"]))
    story.append(Paragraph(
        "FOLLOW(A) is the set of terminals that can appear immediately to the right of A.",
        styles["Normal"]
    ))

    for nt, values in follow.items():
        story.append(
            Paragraph(f"FOLLOW({nt}) = {{ {', '.join(values)} }}", styles["Normal"])
        )

    story.append(Spacer(1, 12))

    # ---------- SUMMARY TABLE ----------
    story.append(Paragraph("<b>5. FIRST & FOLLOW Summary</b>", styles["Heading2"]))

    table_data = [["Non-Terminal", "FIRST", "FOLLOW"]]
    for nt in grammar.keys():
        table_data.append([
            nt,
            ", ".join(first.get(nt, [])),
            ", ".join(follow.get(nt, []))
        ])

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
    ]))

    story.append(table)

    story.append(Spacer(1, 12))

    # ---------- EXAM NOTES ----------
    story.append(Paragraph("<b>6. Exam Notes</b>", styles["Heading2"]))
    story.append(Paragraph(
        "- FIRST helps in predicting derivations<br/>"
        "- FOLLOW defines valid symbols after a non-terminal<br/>"
        "- Used in LL(1) and SLR parsing",
        styles["Normal"]
    ))

    doc.build(story)
    return file_path