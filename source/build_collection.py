import sys,pathlib,json,re,math,html,hashlib,shutil,datetime,collections,argparse
ROOT=pathlib.Path(__file__).resolve().parent
if (ROOT/'pydeps').exists():sys.path.insert(0,str(ROOT/'pydeps'))
import chess
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color,white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core_lessons import CHAPTERS
from themes import THEMES

DEFAULT_OUT=ROOT.parent/'outputs'/'chess keys'
PAGE_W,PAGE_H=595.276,841.89
M=42;WIDTH=PAGE_W-2*M
INK=HexColor('#19352f');TEXT=HexColor('#243a37');MUTED=HexColor('#526b65');TEAL=HexColor('#1d7564');GOLD=HexColor('#b17a22');PALE=HexColor('#eef4f0');LINE=HexColor('#ccd9d1')
FONT=pathlib.Path('C:/Windows/Fonts/seguisym.ttf')
if not FONT.exists():raise RuntimeError('Pass a chess-symbol font for non-Windows rebuilds; see source README.')
pdfmetrics.registerFont(TTFont('ChessSymbols',str(FONT)))
SYMBOLS={'K':'\u2654','Q':'\u2655','R':'\u2656','B':'\u2657','N':'\u2658','P':'\u2659','k':'\u265a','q':'\u265b','r':'\u265c','b':'\u265d','n':'\u265e','p':'\u265f'}
VALUES={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9,chess.KING:0}
LAYOUT=[]
def esc(t):return html.escape(str(t))
def slug(t):return re.sub('[^a-z0-9]+','-',t.lower()).strip('-')[:100]
def color_name(c):return 'White' if c else 'Black'
def piece_name(p):return chess.piece_name(p.piece_type)
def sq(s):return chess.square_name(s)
def material(b,c):return sum(VALUES[p.piece_type] for p in b.piece_map().values() if p.color==c)
def phrase_list(items):
    if not items:return 'none'
    if len(items)==1:return items[0]
    return ', '.join(items[:-1])+' and '+items[-1]
def paragraph(c,text,x,y,w=WIDTH,size=11,leading=None,bold=False,color=TEXT):
    s=ParagraphStyle('p',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=leading or size*1.36,textColor=color,spaceAfter=0,allowWidows=0,allowOrphans=0)
    p=Paragraph(text,s);pw,ph=p.wrap(w,PAGE_H)
    p.drawOn(c,x,y-ph)
    return y-ph
def label(c,text,x,y):
    c.setFont('Helvetica-Bold',8.2);c.setFillColor(TEAL);c.drawString(x,y,text.upper())
    return y-12
def divider(c,y):
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,y,PAGE_W-M,y)
def header(c,n,chapter,title,kind):
    c.setFillColor(INK);c.rect(0,PAGE_H-13,PAGE_W,13,fill=1,stroke=0)
    c.setFont('Helvetica-Bold',10);c.drawString(M,PAGE_H-42,'CHESS KEYS')
    c.setFillColor(MUTED);c.setFont('Helvetica',8.5);c.drawRightString(PAGE_W-M,PAGE_H-41,f'KEY {n:04d} / 3000  |  {kind}')
    y=paragraph(c,esc(title),M,PAGE_H-62,size=23,leading=25,bold=True,color=INK)
    y=paragraph(c,esc(chapter),M,y-9,size=9.4,color=MUTED)
    divider(c,y-13)
    return y-31
def footer(c,n,source=None):
    divider(c,43)
    c.setFont('Helvetica',7.4);c.setFillColor(MUTED)
    c.drawString(M,30,'CHESS KEYS  |  Read. Calculate. Explain. Apply.')
    c.drawRightString(PAGE_W-M,30,f'{n:04d}  |  1 / 1')
    if source:
        c.setFont('Helvetica',7.3);c.drawString(M,52,source)
        c.linkURL(source,(M,50,PAGE_W-M,60),relative=0,thickness=0)
def new_canvas(path,title):
    c=canvas.Canvas(str(path),pagesize=(PAGE_W,PAGE_H),pageCompression=1,invariant=1)
    c.setTitle(title);c.setAuthor('Chess Keys');c.setSubject('A one-page chess lesson with a worked example and checkpoint')
    return c
def core_pdf(path,n,chapter,r):
    c=new_canvas(path,r['title']);y=header(c,n,chapter,r['title'],'CONCEPT')
    y=label(c,'The idea',M,y)
    y=paragraph(c,esc(r['principle']),M,y,size=12.1,leading=17.4)-26
    y=label(c,'Worked example',M,y)
    y=paragraph(c,esc(r['example']),M,y,size=12,leading=17.3)-28
    y=label(c,'Try it before reading on',M,y)
    y=paragraph(c,esc(r['task']),M,y,size=12,leading=17.3,bold=True)-24
    y=label(c,'Answer and reasoning',M,y)
    y=paragraph(c,esc(r['answer']),M,y,size=11.8,leading=16.8)-26
    boxheight=66
    c.setFillColor(PALE);c.roundRect(M,y-boxheight,WIDTH,boxheight,7,fill=1,stroke=0)
    label(c,'Take this into your next game',M+14,y-17)
    paragraph(c,esc(r['takeaway']),M+14,y-30,w=WIDTH-28,size=11.2,leading=15,bold=True,color=INK)
    y-=boxheight
    assert y>78,('core overflow',n,y)
    footer(c,n);c.showPage();c.save();LAYOUT.append({'id':n,'bottom':round(y,2),'kind':'concept'})

def draw_board(c,b,x,y,size,last):
    cell=size/8
    for rank in range(8):
        for file in range(8):
            s=chess.square(file,rank);xx=x+file*cell;yy=y+rank*cell
            c.setFillColor(HexColor('#f0eee4') if (file+rank)%2 else HexColor('#85aaa0'))
            c.rect(xx,yy,cell,cell,fill=1,stroke=0)
            if s in (last.from_square,last.to_square):
                c.setStrokeColor(GOLD);c.setLineWidth(1.3);c.rect(xx+1,yy+1,cell-2,cell-2,fill=0,stroke=1)
            p=b.piece_at(s)
            if p:
                c.setFillColor(HexColor('#0e1a17'));c.setFont('ChessSymbols',cell*.9)
                c.drawCentredString(xx+cell/2,yy+cell*.13,SYMBOLS[p.symbol()])
    c.setStrokeColor(INK);c.setLineWidth(.6);c.rect(x,y,size,size,fill=0,stroke=1)
    c.setFont('Helvetica',7.7);c.setFillColor(MUTED)
    for i in range(8):
        c.drawCentredString(x+(i+.5)*cell,y-11,chess.FILE_NAMES[i])
        c.drawRightString(x-6,y+(i+.42)*cell,str(i+1))

def numbered_san(b,m):return f'{b.fullmove_number}'+('.' if b.turn else '...')+b.san(m)
def material_summary(b):return f'White {material(b,chess.WHITE)} / Black {material(b,chess.BLACK)}'
def mover_annotation(b,m):
    mover=b.piece_at(m.from_square);who=color_name(b.turn);san=b.san(m);name=piece_name(mover);dst=sq(m.to_square)
    capture=b.piece_at(m.to_square)
    if b.is_en_passant(m):capture=chess.Piece(chess.PAWN,not b.turn)
    before=b.copy();b.push(m)
    parts=[]
    if b.is_checkmate():
        checkers=[piece_name(b.piece_at(s))+' on '+sq(s) for s in b.checkers()]
        parts.append(f"Mate: {phrase_list(checkers)} {'gives' if len(checkers)==1 else 'give'} check; {color_name(b.turn)} has no legal reply.")
    elif b.is_check():
        replies=b.legal_moves.count()
        parts.append(f"Check restricts {color_name(b.turn)} to {replies} legal {'reply' if replies==1 else 'replies'} here.")
    elif capture:
        parts.append(f"The {name} captures the {piece_name(capture)} on {dst}.")
    elif before.is_castling(m):
        parts.append('Castling moves the king and rook together, changing king safety and rook activity.')
    else:
        parts.append(f"The {name} moves from {sq(m.from_square)} to {dst}.")
    if m.promotion:parts.append('The pawn becomes a '+chess.piece_name(m.promotion)+'.')
    if not b.is_checkmate():
        moving_piece=b.piece_at(m.to_square)
        victims=[]
        if moving_piece:
            for s in b.attacks(m.to_square):
                p=b.piece_at(s)
                if p and p.color!=moving_piece.color and p.piece_type>=chess.KNIGHT:
                    victims.append((VALUES[p.piece_type]+(100 if p.piece_type==chess.KING else 0),piece_name(p)+' on '+sq(s)))
        victims.sort(reverse=True)
        if len(victims)>=2:
            parts.append('From '+dst+' it attacks '+phrase_list([x[1] for x in victims[:3]])+'.')
        else:
            discovered=[]
            for s,p in b.piece_map().items():
                if p.color==mover.color and p.piece_type in [chess.BISHOP,chess.ROOK,chess.QUEEN] and s!=m.to_square:
                    for t in b.attacks(s):
                        target=b.piece_at(t)
                        if target and target.color!=p.color and target.piece_type>=chess.KNIGHT and t not in before.attacks(s):
                            discovered.append(f'the {piece_name(p)} on {sq(s)} attacks the {piece_name(target)} on {sq(t)}')
            if discovered:parts.append('The changed line means '+discovered[0]+'.')
            elif capture and b.is_check():parts.append(f'The move also takes the {piece_name(capture)} on {dst}.')
    return ' '.join(parts)

def make_case(r):
    b=chess.Board(r['FEN']);setup=chess.Move.from_uci(r['Moves'].split()[0]);previous=numbered_san(b,setup);b.push(setup)
    initial=b.copy();solver=b.turn;moves=[chess.Move.from_uci(x) for x in r['Moves'].split()[1:]]
    first=moves[0];p=b.piece_at(first.from_square)
    title=f"{THEMES[r['chapter_theme']]['title']}: {color_name(solver)}, move {b.fullmove_number}"
    line=b.variation_san(moves);steps=[]
    for i,m in enumerate(moves):
        san=numbered_san(b,m)
        if i%2==0:
            note=mover_annotation(b,m);steps.append({'san':san,'note':note,'reply':None})
        else:
            b.push(m);steps[-1]['reply']=san
    final=b.copy();balance0=material(initial,solver)-material(initial,not solver);balance1=material(final,solver)-material(final,not solver);delta=balance1-balance0
    pins=[piece_name(pp)+' on '+sq(s) for s,pp in initial.piece_map().items() if pp.color!=solver and pp.piece_type!=chess.KING and initial.is_pinned(pp.color,s)]
    loose=[piece_name(pp)+' on '+sq(s) for s,pp in initial.piece_map().items() if pp.color!=solver and pp.piece_type in [chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN] and not initial.attackers(pp.color,s)]
    king=sq(initial.king(not solver))
    clue=f'The defending king is on {king}.'
    if pins:clue+=' Absolute pin: '+phrase_list(pins[:2])+'.'
    elif loose:clue+=' Geometrically undefended: '+phrase_list(loose[:2])+'. Check for tactical protection.'
    else:clue+=' Look for a defender that can be displaced or overloaded.'
    if final.is_checkmate():
        result=f"The line ends in checkmate against the king on {sq(final.king(final.turn))}. Material gain is unnecessary once no legal defense exists."
        checkers=[piece_name(final.piece_at(s))+' on '+sq(s) for s in final.checkers()]
        question='Which piece delivers the final check, and why can the defender not continue?'
        answer=phrase_list(checkers).capitalize()+'. The king is in check and the position has zero legal replies.'
    else:
        result=f"At the end, nominal material is {material_summary(final)} (P=1, N/B=3, R=5, Q=9). Over this line, {color_name(solver)}'s balance changes by {delta:+d}. Activity and king safety still affect the evaluation."
        question=f"Using P=1, N/B=3, R=5, Q=9, how much does {color_name(solver)}'s material balance change over the complete line?"
        answer=f"{delta:+d}: the balance goes from {balance0:+d} to {balance1:+d}. Count promotions and every recapture, not just the first gain."
    return dict(title=title,initial=initial,final=final,solver=solver,setup=setup,previous=previous,line=line,steps=steps,clue=clue,result=result,question=question,answer=answer,fen=initial.fen())

def practice_pdf(path,n,chapter,r,case):
    t=THEMES[r['chapter_theme']];c=new_canvas(path,case['title']);y=header(c,n,chapter,case['title'],'POSITION LESSON')
    top=y-15;size=218;board_bottom=top-size
    c.setFont('Helvetica-Bold',10.2);c.setFillColor(INK);c.drawString(M,top+10,color_name(case['solver'])+' to move')
    draw_board(c,case['initial'],M,board_bottom,size,case['setup'])
    paragraph(c,'Previous move: '+esc(case['previous'])+'. Gold borders mark its start and finish.',M,board_bottom-20,w=size,size=8.7,leading=11.6,color=MUTED)
    x=M+244;w=WIDTH-244
    yy=label(c,'What this position teaches',x,top+10)
    yy=paragraph(c,esc(t['principle']),x,yy,w,size=10.4,leading=14)-13
    yy=label(c,'How to look',x,yy)
    yy=paragraph(c,esc(t['method']),x,yy,w,size=10.2,leading=13.7)-12
    yy=paragraph(c,esc(case['clue']),x,yy,w,size=9.5,leading=12.6,color=MUTED)
    y=min(board_bottom-53,yy-15)
    y=label(c,'Worked continuation - cover this section first',M,y)
    y=paragraph(c,esc(case['line']),M,y,size=11.1,leading=14.2,bold=True,color=INK)-9
    # Every source line is explained in complete solver turns.
    for step in case['steps']:
        text='<b>'+esc(step['san'])+'</b> '+esc(step['note'])
        if step['reply']:text+=' Recorded reply: <b>'+esc(step['reply'])+'</b>.'
        y=paragraph(c,text,M,y,size=9.7,leading=12.6)-5
    y=paragraph(c,esc(case['result']),M,y-2,size=9.6,leading=12.7)-12
    y=label(c,'Checkpoint',M,y)
    y=paragraph(c,esc(case['question'])+' <b>Answer:</b> '+esc(case['answer']),M,y,size=9.5,leading=12.5)-12
    y=label(c,'Carry the idea into your games',M,y)
    y=paragraph(c,esc(t['caution']),M,y,size=9.6,leading=12.7)
    if y<72:raise ValueError(('practice overflow',n,round(y),len(case['steps']),r['PuzzleId']))
    source='https://lichess.org/training/'+r['PuzzleId']
    footer(c,n,source);c.showPage();c.save();LAYOUT.append({'id':n,'bottom':round(y,2),'kind':'position'})

def html_index(entries,chapters,out):
    data=json.dumps(entries,ensure_ascii=True).replace('<','\\u003c')
    template='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chess Keys - 3,000 lessons</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f5f3eb;color:#19352f;font:17px/1.55 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:48px 24px}header{border-bottom:1px solid #a5bab0;padding-bottom:26px}.eyebrow{letter-spacing:.18em;font-size:12px;font-weight:750;text-transform:uppercase}h1{font-size:clamp(42px,8vw,80px);letter-spacing:-.05em;line-height:1;margin:18px 0}p{max-width:770px}.controls{display:flex;gap:12px;flex-wrap:wrap;margin:26px 0 12px}input,select{font:inherit;padding:12px;border:1px solid #9fb6ab;border-radius:6px;background:white}input{flex:2;min-width:230px}select{flex:1;min-width:220px}#count{color:#526b65;font-size:14px;margin:12px 0}article{display:grid;grid-template-columns:74px 1fr auto;gap:16px;align-items:center;padding:19px 8px;border-top:1px solid #ced9d0}a{color:#176952;text-decoration-thickness:1px;text-underline-offset:4px}h2{font-size:18px;margin:0}small{color:#526b65}.badge{font-size:12px;border:1px solid #b4c7bc;border-radius:20px;padding:4px 10px}button{font:inherit;padding:10px 20px;background:#19352f;color:white;border:0;border-radius:5px;cursor:pointer;margin-top:18px}nav{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}footer{margin-top:40px;font-size:13px;color:#526b65}@media(max-width:650px){article{grid-template-columns:46px 1fr}.badge{display:none}main{padding:30px 18px}}
    </style><main><header><div class="eyebrow">Read. Calculate. Explain. Apply.</div><h1>Chess Keys</h1><p><strong>3,000 one-page lessons.</strong> Start with 120 focused concept pages, then study 2,880 distinct positions with diagrams, worked continuations, and checkpoints. Every folder contains 80 PDFs or fewer.</p><nav><a href="https://github.com/1d42c4/chess-keys">Repository &amp; downloads</a><a href="README.md">Course guide</a><a href="SOURCES.md">Sources and methods</a><a href="QUALITY.md">Validation report</a></nav></header><div class="controls"><input id="search" type="search" aria-label="Search lessons" placeholder="Search: opening, math, pin, opposition..."><select id="chapter" aria-label="Select a chapter"><option value="">All 42 chapters</option></select></div><p id="count" role="status"></p><section id="lessons" aria-label="Lessons"></section><button id="more">Show 100 more</button><footer>Works offline. Links open individual PDFs. Source puzzle ratings are dated training estimates, not a measurement of your playing strength.</footer></main><script>
    if(location.protocol!=='file:'){for(const a of document.querySelectorAll('nav a')){const href=a.getAttribute('href');if(href&&href.endsWith('.md'))a.href='https://github.com/1d42c4/chess-keys/blob/main/'+href;}}const data=__DATA__;const search=document.querySelector('#search'),chapter=document.querySelector('#chapter'),list=document.querySelector('#lessons'),more=document.querySelector('#more');let limit=100;for(const name of [...new Set(data.map(x=>x.chapter))]){const o=document.createElement('option');o.value=name;o.textContent=name;chapter.append(o)}function render(){const q=search.value.toLowerCase().trim();const rows=data.filter(x=>(!chapter.value||x.chapter===chapter.value)&&(!q||(x.title+' '+x.chapter+' '+x.tags+' '+x.id).toLowerCase().includes(q)));document.querySelector('#count').textContent=rows.length+(rows.length===1?' lesson found':' lessons found') • showing '+Math.min(limit,rows.length);list.replaceChildren();for(const r of rows.slice(0,limit)){const a=document.createElement('article'),num=document.createElement('small'),div=document.createElement('div'),h=document.createElement('h2'),link=document.createElement('a'),sub=document.createElement('small'),badge=document.createElement('span');num.textContent=String(r.id).padStart(4,'0');link.href=r.path;link.textContent=r.title;h.append(link);sub.textContent=r.chapter+(r.rating?' • source puzzle rating '+r.rating:'');div.append(h,sub);badge.className='badge';badge.textContent=r.kind;a.append(num,div,badge);list.append(a)}more.hidden=rows.length<=limit}search.addEventListener('input',()=>{limit=100;render()});chapter.addEventListener('change',()=>{limit=100;render()});more.addEventListener('click',()=>{limit+=100;render()});render();</script></html>'''
    (out/'index.html').write_text(template.replace('__DATA__',data),encoding='utf-8')

def supporting_files(entries,chapterinfo,out,puzzles):
    table='\n'.join(f"| [{name.replace('-', ' ').title()}]({name}/README.md) | {count} | {lo:04d}-{hi:04d} |" for name,count,lo,hi in chapterinfo)
    (out/'README.md').write_text('''# Chess Keys

**3,000 meaningful one-page chess lessons, organized in 42 chapters.**

**[Read and search all 3,000 lessons online](https://1d42c4.github.io/chess-keys/).** To study offline, download the repository, extract it, and open **[index.html](index.html)**. The chapter links below also open individual PDFs on GitHub. Each concept chapter contains 20 PDFs; each practice chapter contains 80. No PDF folder has more than 99 files.

## Start here

- [Chess math: count the whole exchange](02-chess-math/0021-chess-math-count-the-whole-exchange.pdf)
- [When to learn chess openings](03-opening-decisions/0041-when-to-learn-chess-openings.pdf)
- [Improve your worst piece](04-positional-judgment/0061-improve-your-worst-piece.pdf)
- [Activate the king safely](05-endgame-technique/0081-activate-the-king-safely.pdf)
- [Build a complete move habit](01-foundations/0020-build-a-complete-move-habit.pdf)

## How to study

Read one concept page and explain its worked example in your own words. For a position lesson, set up the diagram (White is always at the bottom), cover the continuation, and write a complete line. Compare your answer with the explanation, then answer the checkpoint. Record the resource you missed and revisit the position after a delay. Try one relevant habit in your next slow game.

The 120 concept lessons teach principles, concrete examples, questions, and answers. The 2,880 practice lessons use distinct positions and include a diagram, a theme-specific method, a legal annotated continuation, a position-specific checkpoint, and a link to the source. Practice positions are sorted by source puzzle rating within each chapter. These ratings are approximate puzzle difficulty estimates, not player ratings.

These are short lessons, not claims that 3,000 unrelated chess principles exist. Motifs recur deliberately in different positions. Some lines show one representative defense; other replies can require separate calculation. The explanations identify exact moves and board relationships without pretending to provide exhaustive engine analysis.

## Chapters

| Chapter | PDFs | Lesson numbers |
|---|---:|---|
'''+table+'''

## Files and checks

- [Sources and methods](SOURCES.md): provenance, interpretation of diagrams, and scope of checks.
- [Quality report](QUALITY.md): counts, legal-move checks, engine review, rendering, and layout bounds.
- `catalog.json`: machine-readable lesson index; `SHA256SUMS.txt`: file integrity checks.
- `source/`: original prose, selected public-domain position data, and the PDF builder.

No account or internet connection is required to read downloaded PDFs. Lichess source links require an internet connection.
''',encoding='utf-8')
    (out/'SOURCES.md').write_text('''# Sources and methods

The prose concept lessons and thematic teaching notes were written for Chess Keys with AI assistance. They are educational summaries and practical examples, not copied pages from chess books. This collection has automated chess and document checks, plus sampled visual review; it has not received a full human chess-editor review of every page.

## Practice data

The 2,880 practice positions and recorded solution lines come from the [Lichess open puzzle database](https://database.lichess.org/#puzzles), whose database exports are dedicated to the public domain under [CC0](https://creativecommons.org/publicdomain/zero/1.0/). The database page identified the source snapshot as 2026-09-10 when retrieved for this build on 2026-09-29 UTC. Each practice PDF links to its specific puzzle; `source/puzzles.json` retains puzzle ID, original FEN, source move sequence, rating, themes, and game URL.

The first move in a Lichess puzzle row is the opponent's setup move. This build applies it before drawing the diagram. The solution begins with the second source move. White is always at the bottom of the diagrams, even when Black moves next. Gold square borders identify the setup move. No position is duplicated in the practice set, including positions with different move counters.

Selection uses source puzzle ratings 650-2400, popularity at least 80, at least 100 recorded plays, and source sequences of at most ten plies including setup. Each of 36 theme chapters contains 80 unique positions, ordered by source rating. One position can have several themes; it is assigned to exactly one chapter.

## Chess checks and interpretation

All starting boards are checked for structural validity with python-chess. Every setup and solution move is replayed and checked for legality. All source lines tagged mate are required to finish in actual checkmate. Material checkpoints are computed from the board using P=1, N/B=3, R=5, Q=9; these are teaching approximations rather than a complete evaluation.

Stockfish 19 performed a 30,000-node MultiPV 2 comparison at each exercise's initial position, with an additional 30,000-node source-move search when needed. A large apparent disagreement triggered a deeper 3,000,000-node MultiPV 3 review. The one flagged case was resolved: the source move forces mate. This is an automated sanity check, not exhaustive proof of every defensive branch. The full audit is retained in `source/engine-audit.json`.

The displayed continuation is a recorded solution branch. A statement such as 'three legal replies' is a legal-move count, not a claim that all three are equally strong. Geometric attacks or undefended pieces may have tactical qualifications; the prose explicitly asks the reader to check them. Theoretical endgame guidance is conditional on the described arrangement rather than a universal promise of a win.

## References and tools

- [FIDE Laws of Chess](https://handbook.fide.com/chapter/E012023): reference for standard-chess rules, not a substitute for local tournament regulations.
- [Lichess database documentation](https://database.lichess.org/#puzzles): data license, schema, and setup-move convention.
- [python-chess](https://python-chess.readthedocs.io/): board validity, move legality, SAN, and mate detection.
- [Stockfish](https://stockfishchess.org/): engine review. Engine binaries are not included in this repository.
- ReportLab generated the PDFs; Poppler and PyMuPDF were used for rendering and inspection. Chess glyphs are embedded from the system's Segoe UI Symbol font; the font file itself is not distributed.

No separate reuse license has been assigned to the original instructional text or build code. The Lichess records retain their CC0 status. Third-party software and fonts retain their own licenses; their packages are not redistributed here.
''',encoding='utf-8')
    (out/'THIRD_PARTY_NOTICES.md').write_text('''# Third-party notices

The selected Lichess puzzle database records are CC0, as stated at https://database.lichess.org/ . See https://creativecommons.org/publicdomain/zero/1.0/legalcode for the dedication.

Third-party tools and fonts retain their own terms. No engine binaries, package installations, or standalone font files are included. Segoe UI Symbol glyphs are embedded in the PDFs. No separate reuse license is specified for the original instructional text or build code.
''',encoding='utf-8')
    (out/'catalog.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
    for name,count,lo,hi in chapterinfo:
        subset=[e for e in entries if e['folder']==name]
        txt='# '+name.replace('-',' ').title()+'\n\n'+str(count)+' one-page lessons. [Back to the course](../README.md).\n\n'
        txt+='\n'.join(f"- [{e['id']:04d} - {e['title']}]({pathlib.Path(e['path']).name})" for e in subset)+'\n'
        (out/name/'README.md').write_text(txt,encoding='utf-8')
    source=out/'source';source.mkdir(exist_ok=True)
    for name in ['core_lessons.py','themes.py','build_collection.py','puzzles.json','engine-audit.json']:
        shutil.copy2(ROOT/name,source/name)
    (source/'requirements.txt').write_text('reportlab>=4,<5\npython-chess==1.999\npypdf\nPyMuPDF\n',encoding='utf-8')
    (source/'README.md').write_text('''# Rebuilding

Install ReportLab and python-chess in your Python environment, then run `python build_collection.py --output <new-output-directory>` from this directory. The builder reads the retained data and does not need network access. On Windows it uses `C:/Windows/Fonts/seguisym.ttf` for chess glyphs; adapt `FONT` to an installed font containing U+2654-U+265F on other systems, respecting that font's embedding license. Engine binaries and package installations are not part of the repository.

`core_lessons.py` contains 120 original concept lessons. `themes.py` contains 36 original theme explanations. `puzzles.json` contains the 2,880 selected CC0 records. `engine-audit.json` records the automated root-position checks. The builder annotates legal board changes and computes checkpoints, rather than inserting arbitrary move strings into prose.

Rebuilding generates the course, indexes, and sources. Run your own validation afterward before replacing a published collection. The delivered `QUALITY.md` describes the checks made for the published edition.
''',encoding='utf-8')
    (out/'.nojekyll').write_text('',encoding='utf-8')
    html_index(entries,chapterinfo,out)

def build(output,samples=False):
    out=pathlib.Path(output);out.mkdir(parents=True,exist_ok=True);entries=[];chapterinfo=[];n=0
    for folder,lessons in CHAPTERS:
        d=out/folder;d.mkdir(exist_ok=True);chapter=folder[3:].replace('-',' ').title();lo=n+1
        for r in lessons:
            n+=1;path=d/f"{n:04d}-{slug(r['title'])}.pdf"
            if not samples or n in [1,21,41,61,81,101]:core_pdf(path,n,chapter,r)
            entries.append(dict(id=n,title=r['title'],folder=folder,chapter=chapter,kind='Concept',path=path.relative_to(out).as_posix(),tags=chapter.lower(),rating=None))
        chapterinfo.append((folder,len(lessons),lo,n))
    puzzles=json.loads((ROOT/'puzzles.json').read_text(encoding='utf-8'))
    for idx,(theme,t) in enumerate(THEMES.items(),7):
        rows=[r for r in puzzles if r['chapter_theme']==theme];assert len(rows)==80
        folder=f'{idx:02d}-{slug(t["title"])}';d=out/folder;d.mkdir(exist_ok=True);lo=n+1
        for j,r in enumerate(rows):
            n+=1;case=make_case(r);path=d/f"{n:04d}-{slug(case['title'])}-{r['PuzzleId']}.pdf"
            if not samples or j in [0,79]:practice_pdf(path,n,t['title'],r,case)
            entries.append(dict(id=n,title=case['title'],folder=folder,chapter=t['title'],kind='Position',path=path.relative_to(out).as_posix(),tags=r['Themes'],rating=int(r['Rating']),puzzle_id=r['PuzzleId'],fen=case['fen'],solution_san=case['line']))
        chapterinfo.append((folder,len(rows),lo,n));print(f'Completed {n}/3000 - {t["title"]}',flush=True)
    assert n==3000
    if not samples:supporting_files(entries,chapterinfo,out,puzzles)
    (ROOT/('sample-layout.json' if samples else 'layout.json')).write_text(json.dumps(LAYOUT,indent=2))
    print('Generated',len(LAYOUT),'PDFs in',out,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(DEFAULT_OUT));p.add_argument('--samples',action='store_true');a=p.parse_args();build(a.output,a.samples)
