"""Fill Apart's submission template (.docx) with report/mondegreen-submission.md.

    python scripts/build_docx.py TEMPLATE.docx report/mondegreen-submission.md OUT.docx

Keeps the template's header block, fonts, heading styles, page setup and list
definitions; replaces the guidance text with the report. Supports the small
Markdown subset the report uses: ## / ### headings, paragraphs, "- " bullets,
"1. " numbered lists, pipe tables, **bold**, *italic*, and two directives:
@abstract (next paragraph goes in the template's abstract box), @figure PATH,
@caption TEXT.
"""

import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

FONT = '<w:rFonts w:ascii="Old Standard TT" w:cs="Old Standard TT" w:eastAsia="Old Standard TT" w:hAnsi="Old Standard TT"/>'
TEXT_W = 9360  # DXA, 6.5 in at 1 in margins
EMU_PER_IN = 914400


def runs(text, size=None, base_italic=False):
    """Inline **bold** and *italic* into w:r elements."""
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part:
            continue
        bold = part.startswith("**")
        italic = base_italic or (part.startswith("*") and not bold)
        body = part[2:-2] if bold else part[1:-1] if part.startswith("*") else part
        rpr = FONT + ("<w:b w:val=\"1\"/><w:bCs w:val=\"1\"/>" if bold else "") + \
            ("<w:i w:val=\"1\"/><w:iCs w:val=\"1\"/>" if italic else "") + \
            (f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "")
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(body)}</w:t></w:r>')
    return "".join(out)


def para(text, *, jc=None, after=120, size=None, italic=False, keep_next=False, num=None):
    ppr = ""
    if num:
        ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr><w:ind w:left="720" w:hanging="360"/>'
    ppr += f'<w:spacing w:after="{after}" w:line="264" w:lineRule="auto"/>'
    if keep_next:
        ppr += "<w:keepNext/>"
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    return f"<w:p><w:pPr>{ppr}<w:rPr>{FONT}</w:rPr></w:pPr>{runs(text, size, italic)}</w:p>"


def heading(text, level):
    style, size, spacing = (("Heading2", 28, '<w:spacing w:after="80" w:before="240" w:line="360" w:lineRule="auto"/>')
                            if level == 2 else
                            ("Heading3", 24, '<w:spacing w:after="60" w:before="160" w:lineRule="auto"/>'))
    rpr = f'{FONT}<w:b w:val="1"/><w:bCs w:val="1"/><w:color w:val="000000"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    return (f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{spacing}<w:keepNext/><w:rPr>{rpr}</w:rPr></w:pPr>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def table(rows):
    ncol = len(rows[0])
    first = 3000 if ncol > 2 else 4680
    rest = (TEXT_W - first) // (ncol - 1)
    widths = [first] + [rest] * (ncol - 1)
    widths[-1] += TEXT_W - sum(widths)
    border = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="808080"/>'
    borders = "".join(border.format(s) for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    xml = [f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:jc w:val="center"/>'
           f'<w:tblBorders>{borders}</w:tblBorders><w:tblLayout w:type="fixed"/>'
           f'<w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
           f'<w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>']
    xml += [f'<w:gridCol w:w="{w}"/>' for w in widths]
    xml.append("</w:tblGrid>")
    for r, row in enumerate(rows):
        xml.append('<w:tr><w:trPr><w:cantSplit/>' + ('<w:tblHeader/>' if r == 0 else '') + '</w:trPr>')
        for c, cell in enumerate(row):
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="EFEDE8"/>' if r == 0 else ""
            text = f"**{cell}**" if r == 0 and cell else cell
            xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[c]}" w:type="dxa"/>{shade}</w:tcPr>'
                       + para(text, after=0, size=18, jc=None if c == 0 else "center") + "</w:tc>")
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def figure(rid, path, pic_id):
    w_px, h_px = png_size(path)
    cx = int(6.3 * EMU_PER_IN)
    cy = int(cx * h_px / w_px)
    return (f'<w:p><w:pPr><w:spacing w:before="120" w:after="60"/><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{pic_id}" name="Figure {pic_id}"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{pic_id}" name="fig{pic_id}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
            '</wp:inline></w:drawing></w:r></w:p>')


def top_level_items(body):
    """Top-level w:p and w:tbl elements of the body, respecting nested tables."""
    items, depth, start = [], 0, None
    for m in re.finditer(r"<(/?)w:(tbl|p)(?=[\s>/])[^>]*?(/?)>", body):
        closing, selfclosing = m.group(1) == "/", m.group(3) == "/"
        if selfclosing:
            if depth == 0:
                items.append(m.group(0))
            continue
        if not closing:
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                items.append(body[start:m.end()])
    return items


def parse(md):
    meta = dict(re.findall(r"^(\w+): (.+)$", md.split("---")[1], re.M))
    body = md.split("---", 2)[2]
    blocks, buf = [], []
    for line in body.splitlines() + [""]:
        if line.strip() == "":
            if buf:
                blocks.append(buf)
                buf = []
        else:
            buf.append(line)
    return {k: v.strip().strip('"') for k, v in meta.items()}, blocks


def build(template, md_path, out_path):
    root = Path(md_path).resolve().parents[1]
    meta, blocks = parse(Path(md_path).read_text(encoding="utf-8"))
    zin = zipfile.ZipFile(template)
    files = {n: zin.read(n) for n in zin.namelist() if not n.endswith("/")}
    doc = files["word/document.xml"].decode("utf-8")
    head, body = doc.split("<w:body>", 1)
    sect = body[body.rindex("<w:sectPr>"):body.rindex("</w:body>")]
    items = top_level_items(body)

    # header block: title and author
    hdr = items[1].replace(">PROJECT TITLE<", f">{escape(meta['title'])}<")
    # replace the nested author grid with one centred author line
    a0 = hdr.index("Author name 1")
    t0 = hdr.rindex("<w:tbl>", 0, a0)
    t1 = hdr.index("</w:tbl>", hdr.index("Author name 6")) + len("</w:tbl>")
    author_xml = (para(f"**{meta['author']}**", jc="center", after=0)
                  + para(meta["affiliation"], jc="center", after=120))
    hdr = hdr[:t0] + author_xml + hdr[t1:]
    assert "PROJECT TITLE" not in hdr and "Author name" not in hdr

    # numbering: one fresh, restarting list per numbered block; bullets reuse numId 3
    numbering = files["word/numbering.xml"].decode("utf-8")
    next_num = [100]

    def new_decimal_list():
        n = next_num[0]
        next_num[0] += 1
        nonlocal numbering
        numbering = numbering.replace("</w:numbering>",
            f'<w:num w:numId="{n}"><w:abstractNumId w:val="5"/>'
            f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num></w:numbering>')
        return n

    rels = files["word/_rels/document.xml.rels"].decode("utf-8")
    out, abstract_xml, pending_abstract, pic = [], None, False, 0
    for blk in blocks:
        first = blk[0]
        if first.startswith("@abstract"):
            pending_abstract = True
            rest = blk[1:]
            if rest:
                abstract_xml = para(" ".join(rest), jc="both", after=0)
                pending_abstract = False
            continue
        if pending_abstract:
            abstract_xml = para(" ".join(blk), jc="both", after=0)
            pending_abstract = False
            continue
        if first.startswith("### "):
            out.append(heading(first[4:], 3))
            blk = blk[1:]
            if not blk:
                continue
            first = blk[0]
        elif first.startswith("## "):
            out.append(heading(first[3:], 2))
            blk = blk[1:]
            if not blk:
                continue
            first = blk[0]
        if first.startswith("@figure"):
            pic += 1
            path = root / first.split(" ", 1)[1].strip()
            rid = f"rIdFig{pic}"
            files[f"word/media/fig{pic}.png"] = path.read_bytes()
            rels = rels.replace("</Relationships>",
                f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig{pic}.png"/></Relationships>')
            out.append(figure(rid, path, pic))
            for line in blk[1:]:
                if line.startswith("@caption"):
                    out.append(para(line[9:], jc="both", size=18, italic=True, after=200))
        elif first.startswith("@caption"):
            out.append(para(first[9:], jc="both", size=18, italic=True, after=80, keep_next=True))
            if len(blk) > 1 and blk[1].startswith("|"):
                rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in blk[1:]
                        if not re.match(r"^\|[-| :]+\|$", l.strip())]
                out.append(table(rows))
                out.append(para("", after=120))
        elif first.startswith("|"):
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in blk
                    if not re.match(r"^\|[-| :]+\|$", l.strip())]
            out.append(table(rows))
            out.append(para("", after=120))
        elif first.startswith("- "):
            for line in blk:
                out.append(para(line[2:], num=3, after=60))
            out[-1] = out[-1].replace('w:after="60"', 'w:after="120"', 1)
        elif re.match(r"^\d+\. ", first):
            n = new_decimal_list()
            for line in blk:
                out.append(para(re.sub(r"^\d+\. ", "", line), num=n, after=60))
            out[-1] = out[-1].replace('w:after="60"', 'w:after="120"', 1)
        else:
            out.append(para(" ".join(blk), jc="both"))

    assert abstract_xml, "no @abstract block"
    # the abstract box is a table nested inside the header table
    a0 = hdr.index("Summarize your project")
    t0 = hdr.rindex("<w:tbl>", 0, a0)
    t1 = hdr.index("</w:tbl>", a0) + len("</w:tbl>")
    abs_tbl = hdr[t0:t1]
    cell_start = abs_tbl.index("<w:p ")
    cell_end = abs_tbl.rindex("</w:p>") + len("</w:p>")
    hdr = hdr[:t0] + abs_tbl[:cell_start] + abstract_xml + abs_tbl[cell_end:] + hdr[t1:]
    assert "Summarize your project" not in hdr

    # items: 0 empty paragraph, 1 header table, 2 empty paragraph, 3 "How to use" box (dropped)
    new_body = "".join([items[0], hdr, items[2]] + out) + sect
    doc = head + "<w:body>" + new_body + "</w:body></w:document>"
    if 'xmlns:wp=' not in head or 'xmlns:r=' not in head:
        raise SystemExit("template lacks drawing namespaces")
    files["word/document.xml"] = doc.encode("utf-8")
    files["word/numbering.xml"] = numbering.encode("utf-8")
    files["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    ct = files["[Content_Types].xml"].decode("utf-8")
    if 'Extension="png"' not in ct:
        ct = ct.replace("<Default ", '<Default ContentType="image/png" Extension="png"/><Default ', 1)
    files["[Content_Types].xml"] = ct.encode("utf-8")

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        for name, data in files.items():
            z.writestr(name, data)
    print("wrote", out_path, "|", len(out), "blocks,", pic, "figures")


if __name__ == "__main__":
    build(*sys.argv[1:4])
