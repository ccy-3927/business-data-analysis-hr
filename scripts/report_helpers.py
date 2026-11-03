"""以课程原DOCX为母版生成论文；保留原样式、编号、封面及评分表。"""
from pathlib import Path
import json,copy,re,zipfile
import pandas as pd
from docx import Document
from docx.shared import Inches,Pt,RGBColor,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1];TABLE=ROOT/'outputs/tables';FIG=ROOT/'outputs/figures'

TITLE='IBM员工离职分析与可视化'
TEMPLATE=ROOT/'docs/template_reference.docx'
if not TEMPLATE.exists():TEMPLATE=next(ROOT.parent.glob('*模板.docx'))
d=Document(TEMPLATE);orig=list(d.paragraphs)
metrics=json.loads((TABLE/'metrics.json').read_text(encoding='utf-8'))
idx=pd.read_csv(TABLE/'figure_index.csv');figpaths={r['编号']:FIG/r['文件'] for _,r in idx.iterrows()}
body_text=[]
def font(r,size=10.5,name='宋体',bold=False):
    r.font.name=name;r.font.size=Pt(size);r.bold=bold;r.font.color.rgb=RGBColor(0,0,0)
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),name)
def replace(p,text,size=None,name=None):
    p.clear();r=p.add_run(text);font(r,size or 10.5,name or '宋体');return p
def para(anchor,text,kind='body',size=10.5):
    p=anchor.insert_paragraph_before();p.style=d.styles['Normal']
    p.paragraph_format.line_spacing=1.5;p.paragraph_format.space_after=Pt(3)
    p.paragraph_format.first_line_indent=Pt(21 if kind=='body' else 0)
    p.paragraph_format.widow_control=True
    if kind=='heading':p.paragraph_format.keep_with_next=True
    if kind=='code':
        p.paragraph_format.line_spacing=1.15
        p.paragraph_format.keep_together=True
    if 'https://' in text:p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    font(p.add_run(text),size)
    if kind=='body':body_text.append(text)
    return p
def image(anchor,num,caption):
    p=para(anchor,'',kind='figure');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(figpaths[f'fig{num:02d}']),width=Inches(5.65))
    cap=para(anchor,caption,kind='caption',size=10);cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_with_next=False
def table(anchor,headers,rows):
    t=d.add_table(rows=1,cols=len(headers));t.autofit=False
    widths=[2.0,4.3,8.1] if headers[0]=='图号' else [5.2,3.6,5.6]
    for col,width in zip(t.columns,widths):col.width=Cm(width)
    for c,v in zip(t.rows[0].cells,headers):c.text=str(v)
    for row in rows:
        for c,v in zip(t.add_row().cells,row):c.text=str(v)
    for i,row in enumerate(t.rows):
        for col_index,cell in enumerate(row.cells):
            cell.width=Cm(widths[col_index])
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcPr=cell._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');b.append(el)
            tcPr.append(b)
            if i==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EDEDED');tcPr.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing=1.15;p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4);p.paragraph_format.first_line_indent=Pt(0)
                ind=p._p.get_or_add_pPr().get_or_add_ind();ind.set(qn('w:firstLineChars'),'0');ind.set(qn('w:leftChars'),'0');ind.set(qn('w:rightChars'),'0')
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER if col_index==0 or headers[0]!='图号' else WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:font(r,9,bold=(i==0))
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in t.rows:
        cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
    anchor._p.addprevious(t._tbl)
    return t
def section(slot,paras,figures=[]):
    anchor=orig[slot]
    # 核心模型逐段配图：论证紧邻证据，避免先堆文字再堆图。
    interleaved={51:{0:[(11,'图11 岗位离职案例累计贡献')],1:[(15,'图15 员工分群特征画像'),(16,'图16 分群离职比例及95% Wilson区间')],2:[(17,'图17 独立测试集ROC曲线')],3:[(19,'图19 分类误报与漏报')]},58:{0:[(18,'图18 独立测试集精确率召回率曲线')],1:[(22,'图22 加班标签与离职标签的关联区间')]}}
    for i,text in enumerate(paras):
        para(anchor,text)
        if slot in interleaved:
            for n,cap in interleaved[slot].get(i,[]):image(anchor,n,cap)
    if slot not in interleaved:
        for n,cap in figures:image(anchor,n,cap)
    anchor._p.getparent().remove(anchor._p)

