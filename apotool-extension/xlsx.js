/**
 * 外部ライブラリ無しで有効な .xlsx（Excelブック）を生成する最小実装。
 *
 * - ZIP は「無圧縮(stored)」でパックし、CRC32 を正しく付与する
 * - セル文字列は inlineStr（<is><t>）で埋め込むので UTF-8（日本語）がそのまま通る
 * - 太字ヘッダー用に最小の styles.xml（s="1" が太字）を同梱
 *
 * 使い方:
 *   const bytes = window.__apoXlsx.build("月次レポート", rows);
 *   // rows: 2次元配列。セルは 文字列 / 数値 / { v, bold:true } / null
 *   const blob = new Blob([bytes], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
 */
(function () {
  "use strict";

  const enc = new TextEncoder();

  // ---- CRC32 ----------------------------------------------------------
  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) {
        c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      }
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(bytes) {
    let c = 0xffffffff;
    for (let i = 0; i < bytes.length; i++) {
      c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
    }
    return (c ^ 0xffffffff) >>> 0;
  }

  // ---- ZIP（stored / 無圧縮）------------------------------------------
  function zip(files) {
    // files: [{ name:string, data:Uint8Array }]
    const chunks = [];
    const central = [];
    let offset = 0;

    for (const f of files) {
      const nameBytes = enc.encode(f.name);
      const data = f.data;
      const crc = crc32(data);

      const lh = new Uint8Array(30 + nameBytes.length);
      const dv = new DataView(lh.buffer);
      dv.setUint32(0, 0x04034b50, true); // local file header signature
      dv.setUint16(4, 20, true); // version needed
      dv.setUint16(6, 0, true); // flags
      dv.setUint16(8, 0, true); // method: 0 = stored
      dv.setUint16(10, 0, true); // mod time
      dv.setUint16(12, 0x21, true); // mod date = 1980-01-01
      dv.setUint32(14, crc, true);
      dv.setUint32(18, data.length, true); // compressed size
      dv.setUint32(22, data.length, true); // uncompressed size
      dv.setUint16(26, nameBytes.length, true);
      dv.setUint16(28, 0, true); // extra length
      lh.set(nameBytes, 30);

      chunks.push(lh, data);

      const cd = new Uint8Array(46 + nameBytes.length);
      const cdv = new DataView(cd.buffer);
      cdv.setUint32(0, 0x02014b50, true); // central dir signature
      cdv.setUint16(4, 20, true); // version made by
      cdv.setUint16(6, 20, true); // version needed
      cdv.setUint16(8, 0, true); // flags
      cdv.setUint16(10, 0, true); // method
      cdv.setUint16(12, 0, true); // time
      cdv.setUint16(14, 0x21, true); // date
      cdv.setUint32(16, crc, true);
      cdv.setUint32(20, data.length, true);
      cdv.setUint32(24, data.length, true);
      cdv.setUint16(28, nameBytes.length, true);
      cdv.setUint16(30, 0, true); // extra
      cdv.setUint16(32, 0, true); // comment
      cdv.setUint16(34, 0, true); // disk number start
      cdv.setUint16(36, 0, true); // internal attrs
      cdv.setUint32(38, 0, true); // external attrs
      cdv.setUint32(42, offset, true); // local header offset
      cd.set(nameBytes, 46);
      central.push(cd);

      offset += lh.length + data.length;
    }

    const cdStart = offset;
    let cdSize = 0;
    for (const c of central) {
      chunks.push(c);
      cdSize += c.length;
    }

    const eocd = new Uint8Array(22);
    const edv = new DataView(eocd.buffer);
    edv.setUint32(0, 0x06054b50, true); // EOCD signature
    edv.setUint16(4, 0, true); // disk number
    edv.setUint16(6, 0, true); // disk with central dir
    edv.setUint16(8, central.length, true); // entries this disk
    edv.setUint16(10, central.length, true); // total entries
    edv.setUint32(12, cdSize, true); // central dir size
    edv.setUint32(16, cdStart, true); // central dir offset
    edv.setUint16(20, 0, true); // comment length
    chunks.push(eocd);

    let total = 0;
    for (const c of chunks) total += c.length;
    const out = new Uint8Array(total);
    let p = 0;
    for (const c of chunks) {
      out.set(c, p);
      p += c.length;
    }
    return out;
  }

  // ---- OOXML パーツ ---------------------------------------------------
  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function colName(n) {
    // 0-based 列番号 -> A, B, ..., Z, AA...
    let s = "";
    n++;
    while (n > 0) {
      const m = (n - 1) % 26;
      s = String.fromCharCode(65 + m) + s;
      n = Math.floor((n - 1) / 26);
    }
    return s;
  }

  function cellXml(rowNum, colIdx, cell) {
    const ref = colName(colIdx) + rowNum;
    let v = cell;
    let bold = false;
    if (cell && typeof cell === "object") {
      v = cell.v;
      bold = !!cell.bold;
    }
    const s = bold ? ' s="1"' : "";
    if (v === null || v === undefined || v === "") {
      return `<c r="${ref}"${s}/>`;
    }
    if (typeof v === "number" && isFinite(v)) {
      return `<c r="${ref}"${s}><v>${v}</v></c>`;
    }
    return `<c r="${ref}"${s} t="inlineStr"><is><t xml:space="preserve">${esc(v)}</t></is></c>`;
  }

  const CONTENT_TYPES =
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
    '<Default Extension="xml" ContentType="application/xml"/>' +
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' +
    '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' +
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' +
    "</Types>";

  const RELS =
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>' +
    "</Relationships>";

  const WB_RELS =
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>' +
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' +
    "</Relationships>";

  const STYLES =
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' +
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>' +
    '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>' +
    '<borders count="1"><border/></borders>' +
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>' +
    '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>' +
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>' +
    "</styleSheet>";

  function workbookXml(sheetName) {
    return (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
      '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">' +
      "<sheets>" +
      `<sheet name="${esc(sheetName).slice(0, 31)}" sheetId="1" r:id="rId1"/>` +
      "</sheets>" +
      "</workbook>"
    );
  }

  function sheetXml(rows) {
    let sd = "";
    rows.forEach((row, i) => {
      const r = i + 1;
      let cells = "";
      (row || []).forEach((cell, ci) => {
        cells += cellXml(r, ci, cell);
      });
      sd += `<row r="${r}">${cells}</row>`;
    });
    return (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' +
      '<cols><col min="1" max="1" width="46" customWidth="1"/><col min="2" max="2" width="18" customWidth="1"/></cols>' +
      `<sheetData>${sd}</sheetData>` +
      "</worksheet>"
    );
  }

  function build(sheetName, rows) {
    const files = [
      { name: "[Content_Types].xml", data: enc.encode(CONTENT_TYPES) },
      { name: "_rels/.rels", data: enc.encode(RELS) },
      { name: "xl/workbook.xml", data: enc.encode(workbookXml(sheetName || "Sheet1")) },
      { name: "xl/_rels/workbook.xml.rels", data: enc.encode(WB_RELS) },
      { name: "xl/styles.xml", data: enc.encode(STYLES) },
      { name: "xl/worksheets/sheet1.xml", data: enc.encode(sheetXml(rows || [])) },
    ];
    return zip(files);
  }

  window.__apoXlsx = { build };
})();
