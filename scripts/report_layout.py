"""Keep key analytical figures beside their discussion in the paper body."""
from copy import deepcopy
from docx.text.paragraph import Paragraph


def move_key_figures(document):
    targets = {
        13: ('K在2至6之间比较', '图13对照不同候选群数的轮廓系数，为选择K=2提供依据。'),
        20: ('选定模型的阈值以训练集折外F2', '图20展示精确率、召回率与F2随阈值变化的取舍，阈值选择需结合人工复核能力。'),
        21: ('置换重要性衡量', '图21展示特征置换后的AP下降及重复置换的波动，反映模型对各字段的依赖程度，不表示因果效应。'),
        25: ('群体编号固定于全样本分群', '图25展示大屏的筛选控件、关键指标、联动图表与岗位明细；交互功能可在配套HTML中操作。'),
    }
    for number, (anchor_text, explanation) in targets.items():
        caption = next((p for p in document.paragraphs if p.text.startswith(f'图{number:02d} ')), None)
        if caption is None:
            raise ValueError(f'Missing figure {number}')
        image = caption._p.getprevious()
        if image is None or not image.xpath('.//w:drawing'):
            raise ValueError(f'Missing image before caption {number}')
        anchor = next(p for p in document.paragraphs if anchor_text in p.text)
        # The text uses the adjacent body style; preserve the image and caption XML.
        lead = deepcopy(anchor._p)
        paragraph = Paragraph(lead, anchor._parent)
        paragraph.clear()
        run = paragraph.add_run(explanation)
        if anchor.runs and anchor.runs[0]._r.rPr is not None:
            run._r.insert(0, deepcopy(anchor.runs[0]._r.rPr))
        paragraph.paragraph_format.keep_with_next = True
        paragraph.paragraph_format.page_break_before = False
        anchor._p.addnext(lead)
        lead.addnext(image)
        image.addnext(caption._p)
        image_para = Paragraph(image, caption._parent)
        image_para.paragraph_format.keep_with_next = True
        image_para.paragraph_format.page_break_before = False
        caption.paragraph_format.keep_with_next = False
        caption.paragraph_format.keep_together = True
        caption.paragraph_format.page_break_before = False
    for p in list(document.paragraphs):
        if p.text.startswith('D 交互大屏运行截图'):
            p._p.getparent().remove(p._p)
        elif p.text.startswith('其余图表如下。正文已展示'):
            text = '其余图表如下。正文已展示图01、10、11、13、15—23及大屏截图图25。'
            p.runs[0].text = text
            for r in p.runs[1:]:
                r.text = ''
