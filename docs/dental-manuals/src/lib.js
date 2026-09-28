const fs = require("fs");
const path = require("path");
const d = require("docx");
const {
  Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, ImageRun, VerticalAlign, Header, Footer, PageNumber, LevelFormat, TableLayoutType,
} = d;

const FONT = "BIZ UDPゴシック";
const C = {
  navy: "1F4E79", navyLight: "E8EEF5", blue: "2E75B6", gray: "595959", grayLight: "F2F2F2",
  line: "BFC9D4", amber: "C55A11", amberBg: "FFF4E5", green: "2E7D32", greenBg: "E8F5E9",
  red: "C00000", redBg: "FDECEA", mute: "808080",
};
const PAGE_W = 11906, MARGIN = 1020, CONTENT = PAGE_W - MARGIN * 2; // 9866
const IMG_DIR = path.join(__dirname, "img");

// ---------- text ----------
// rich("通常 **太字** 通常") -> TextRun[]
function rich(s, o = {}) {
  return String(s).split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((t) =>
    t.startsWith("**") ? new TextRun({ ...o, text: t.slice(2, -2), bold: true, color: o.boldColor || o.color })
                       : new TextRun({ text: t, ...o }));
}
const P = (s, o = {}) => new Paragraph({ children: rich(s, o.run || {}), spacing: { after: 60 }, ...o.para });

// ---------- headings ----------
function chapter(num, title, newPage = false) {
  return new Paragraph({
    pageBreakBefore: newPage,
    spacing: { before: 240, after: 140 },
    shading: { type: ShadingType.CLEAR, fill: C.navy, color: "auto" },
    keepNext: true,
    children: [
      new TextRun({ text: ` ${num} `, bold: true, color: "FFFFFF", size: 28 }),
      new TextRun({ text: `  ${title}`, bold: true, color: "FFFFFF", size: 26 }),
    ],
  });
}
function section(num, title, tag) {
  const kids = [
    new TextRun({ text: `${num}　`, bold: true, color: C.blue, size: 23 }),
    new TextRun({ text: title, bold: true, color: C.navy, size: 23 }),
  ];
  if (tag) kids.push(new TextRun({ text: `　${tag}`, color: C.amber, size: 18, bold: true }));
  return new Paragraph({
    spacing: { before: 280, after: 100 }, keepNext: true,
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.blue, space: 2 } },
    children: kids,
  });
}
// small colored label like 【補綴物側】
function label(text, color = C.navy) {
  return new Paragraph({
    spacing: { before: 100, after: 40 }, keepNext: true,
    children: [new TextRun({ text: `■ ${text}`, bold: true, color, size: 19 })],
  });
}
// one-line key point at the top of a procedure
function point(text) {
  return new Paragraph({
    spacing: { after: 80 },
    shading: { type: ShadingType.CLEAR, fill: C.navyLight, color: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color: C.blue, space: 6 } },
    indent: { left: 120 },
    children: [new TextRun({ text: "ポイント　", bold: true, color: C.blue, size: 19 }), ...rich(text, { size: 19 })],
  });
}
function caution(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    shading: { type: ShadingType.CLEAR, fill: C.amberBg, color: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color: C.amber, space: 6 } },
    indent: { left: 120 },
    children: [new TextRun({ text: "注意　", bold: true, color: C.amber, size: 19 }), ...rich(text, { size: 19 })],
  });
}
function note(text) {
  return new Paragraph({
    spacing: { after: 40 }, indent: { left: 240, hanging: 240 },
    children: [new TextRun({ text: "※ ", color: C.mute, size: 17 }), ...rich(text, { color: C.gray, size: 17 })],
  });
}

// ---------- numbered steps (each call restarts at 1) ----------
let stepInstance = 0;
function steps(items) {
  stepInstance++;
  return items.map((s) => {
    const [main, sub] = Array.isArray(s) ? s : [s];
    const out = [new Paragraph({
      numbering: { reference: "steps", level: 0, instance: stepInstance },
      spacing: { after: sub ? 0 : 40 }, children: rich(main),
    })];
    if (sub) out.push(new Paragraph({ indent: { left: 420 }, spacing: { after: 40 },
      children: rich(sub, { color: C.gray, size: 17 }) }));
    return out;
  }).flat();
}
function bullets(items) {
  return items.map((s) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 30 }, children: rich(s) }));
}

// ---------- images ----------
function img(name, w = 72) {
  const h = Math.round(w * 4 / 3);
  return new ImageRun({ type: "jpg", data: fs.readFileSync(path.join(IMG_DIR, name + ".jpg")),
    transformation: { width: w, height: h }, altText: { title: name, description: name, name } });
}
function photoBlock(name, caption, w = 72) {
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 0 }, children: [img(name, w)] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
      children: [new TextRun({ text: caption, size: 15, color: C.gray })] }),
  ];
}

// ---------- tables ----------
const thin = { style: BorderStyle.SINGLE, size: 4, color: C.line };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const gridBorders = { top: thin, bottom: thin, left: thin, right: thin };
const noBorders = { top: none, bottom: none, left: none, right: none };

function cell(content, width, o = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map((c) =>
    c instanceof Paragraph || c instanceof Table ? c
      : new Paragraph({ alignment: o.align, spacing: { after: 0, line: 264, lineRule: d.LineRuleType.AUTO },
          children: rich(c, { size: o.size || 18, color: o.color, bold: o.bold }) }));
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, children: paras,
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    verticalAlign: o.valign || VerticalAlign.CENTER, rowSpan: o.rowSpan, columnSpan: o.columnSpan,
    margins: { top: 70, bottom: 70, left: 100, right: 100 }, borders: o.borders || gridBorders,
  });
}
// rows: array of arrays of (string | {t, fill, color, bold, align, rowSpan})
function table(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) =>
    cell(h, widths[i], { fill: C.navy, color: "FFFFFF", bold: true, size: 18, align: AlignmentType.CENTER })) });
  const body = rows.map((r, ri) => {
    // rows shorter than the header are continuation rows of a leading rowSpan cell
    let col = widths.length - r.length;
    return new TableRow({ cantSplit: true, children: r.map((c) => {
      const spec = typeof c === "object" && !(c instanceof Paragraph) && !Array.isArray(c) ? c : { t: c };
      const w = widths[col]; col++;
      const zebra = o.zebra !== false && ri % 2 === 1 ? "FAFBFC" : undefined;
      return cell(spec.t, w, { fill: spec.fill || zebra, color: spec.color, bold: spec.bold, align: spec.align,
        rowSpan: spec.rowSpan, size: spec.size, valign: spec.valign });
    }) });
  });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [head, ...body] });
}

// Procedure block: main text on the left, product photos stacked on the right
function withPhotos(mainChildren, photos) {
  if (!photos || !photos.length) return mainChildren;
  const PW = 1900, MW = CONTENT - PW;
  return [new Table({
    width: { size: CONTENT, type: WidthType.DXA }, columnWidths: [MW, PW], layout: TableLayoutType.FIXED,
    borders: { ...noBorders, insideHorizontal: none, insideVertical: none },
    rows: [new TableRow({ cantSplit: true, children: [
      new TableCell({ width: { size: MW, type: WidthType.DXA }, children: mainChildren, borders: noBorders,
        margins: { top: 0, bottom: 0, left: 0, right: 200 } }),
      new TableCell({ width: { size: PW, type: WidthType.DXA }, borders: noBorders,
        shading: { type: ShadingType.CLEAR, fill: C.grayLight, color: "auto" }, verticalAlign: VerticalAlign.TOP,
        margins: { top: 60, bottom: 60, left: 60, right: 60 },
        children: [
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 },
            children: [new TextRun({ text: "使う材料", size: 15, bold: true, color: C.navy })] }),
          ...photos.map(([n, cap]) => photoBlock(n, cap)).flat(),
        ] }),
    ] })],
  }), new Paragraph({ spacing: { after: 60 }, children: [] })];
}

// flow boxes: A → B → C
function flow(items, fill = C.navyLight) {
  const n = items.length, arrowW = 400;
  const boxW = Math.floor((CONTENT - arrowW * (n - 1)) / n);
  const widths = []; items.forEach((_, i) => { widths.push(boxW); if (i < n - 1) widths.push(arrowW); });
  const sum = widths.reduce((a, b) => a + b, 0);
  const cells = [];
  items.forEach(([t, sub], i) => {
    cells.push(new TableCell({ width: { size: boxW, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      shading: { type: ShadingType.CLEAR, fill, color: "auto" }, borders: gridBorders,
      margins: { top: 80, bottom: 80, left: 80, right: 80 },
      children: [
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: t, bold: true, color: C.navy, size: 19 })] }),
        ...(sub ? [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: rich(sub, { size: 16, color: C.gray }) })] : []),
      ] }));
    if (i < n - 1) cells.push(new TableCell({ width: { size: arrowW, type: WidthType.DXA }, borders: noBorders, verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "▶", color: C.blue, size: 20 })] })] }));
  });
  return [new Table({ width: { size: sum, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ children: cells })] }), new Paragraph({ spacing: { after: 80 }, children: [] })];
}

function titleBlock(title, sub) {
  return [
    new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: title, bold: true, size: 40, color: C.navy })] }),
    new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: C.navy, space: 4 } },
      children: [new TextRun({ text: sub, size: 19, color: C.gray })] }),
  ];
}

function makeDoc(docTitle, children) {
  return new d.Document({
    creator: "博多ステラ歯科・矯正歯科クリニック", title: docTitle,
    styles: {
      default: { document: { run: { font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT, cs: FONT }, size: 19 },
        paragraph: { spacing: { line: 290, lineRule: d.LineRuleType.AUTO, after: 60 } } } },
    },
    numbering: { config: [
      { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 420, hanging: 320 } }, run: { bold: true, color: C.blue } } }] },
      { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 420, hanging: 280 } }, run: { color: C.blue, size: 14 } } }] },
    ] },
    sections: [{
      properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 1000, bottom: 1000, left: MARGIN, right: MARGIN, header: 500, footer: 500 } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: `${docTitle}｜博多ステラ歯科・矯正歯科クリニック`, size: 15, color: C.mute })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], size: 16, color: C.mute })] })] }) },
      children,
    }],
  });
}

async function save(doc, file) {
  fs.writeFileSync(file, await d.Packer.toBuffer(doc));
  console.log("wrote", file);
}

const spacer = (after = 120) => new Paragraph({ spacing: { after }, children: [] });

module.exports = { d, C, CONTENT, rich, P, chapter, section, label, point, caution, note, steps, bullets, img, photoBlock,
  cell, table, withPhotos, flow, titleBlock, makeDoc, save, spacer, gridBorders, noBorders };
