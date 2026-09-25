import ExcelJS from 'exceljs'

// Palette reprise du template (thème navy type Excel).
const NAVY = 'FF1F4E79'
const NAVY_DARK = 'FF17395B'
const BAND = 'FFD9E2F3'
const BORDER_COLOR = 'FFB4C6E7'
const FONT_NAME = 'Arial'
const THIN_BORDER = {
  top: { style: 'thin', color: { argb: BORDER_COLOR } },
  left: { style: 'thin', color: { argb: BORDER_COLOR } },
  bottom: { style: 'thin', color: { argb: BORDER_COLOR } },
  right: { style: 'thin', color: { argb: BORDER_COLOR } },
}

// Normalise une cellule : nombres conservés, objets aplatis, null → ''.
export function normalizeCell(v) {
  if (v === null || v === undefined) return ''
  if (typeof v === 'object') {
    if (v instanceof Date) return v
    try { return JSON.stringify(v) } catch { return String(v) }
  }
  return v
}

export function todayStamp() {
  return new Date().toISOString().slice(0, 10)
}

export function todayFr() {
  return new Date().toLocaleDateString('fr-FR')
}

function safeSheetName(name) {
  const s = String(name || 'Export').replace(/[\\/?*[\]]/g, ' ').trim().slice(0, 31)
  return s || 'Export'
}

function styleSheet(ws, title, nCols, nRows) {
  // Titre fusionné + date d'export.
  ws.mergeCells(1, 1, 1, nCols)
  const titleCell = ws.getCell(1, 1)
  titleCell.value = title
  titleCell.font = { name: FONT_NAME, size: 14, bold: true, color: { argb: NAVY_DARK } }
  titleCell.alignment = { vertical: 'middle' }
  ws.getRow(1).height = 26
  ws.mergeCells(2, 1, 2, nCols)
  const dateCell = ws.getCell(2, 1)
  dateCell.value = `Exporté le ${todayFr()}`
  dateCell.font = { name: FONT_NAME, size: 10, italic: true, color: { argb: 'FF6B7280' } }

  // En-têtes (ligne 3) : fond navy, texte blanc gras, centrées.
  const headerRow = ws.getRow(3)
  headerRow.height = 22
  for (let c = 1; c <= nCols; c++) {
    const cell = headerRow.getCell(c)
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: NAVY } }
    cell.font = { name: FONT_NAME, bold: true, color: { argb: 'FFFFFFFF' }, size: 11 }
    cell.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true }
    cell.border = THIN_BORDER
  }

  // Corps : bandes bleu clair alternées + bordures fines.
  for (let r = 4; r < 4 + nRows; r++) {
    const row = ws.getRow(r)
    for (let c = 1; c <= nCols; c++) {
      const cell = row.getCell(c)
      cell.border = THIN_BORDER
      cell.font = { name: FONT_NAME, size: 11, color: { argb: 'FF1F2937' } }
      cell.alignment = {
        vertical: 'middle',
        horizontal: typeof cell.value === 'number' ? 'right' : 'left',
      }
      if ((r - 4) % 2 === 1) {
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: BAND } }
      }
    }
  }

  // Largeurs auto (min 12, max 42) + filtre + gel des volets.
  for (let c = 1; c <= nCols; c++) {
    let width = 12
    for (let r = 3; r < 4 + Math.min(nRows, 500); r++) {
      const v = ws.getCell(r, c).value
      const len = v == null ? 0 : String(v).length
      if (len + 2 > width) width = Math.min(42, len + 2)
    }
    ws.getColumn(c).width = width
  }
  ws.views = [{ state: 'frozen', ySplit: 3 }]
  if (nRows > 0) {
    ws.autoFilter = { from: { row: 3, column: 1 }, to: { row: 3 + nRows, column: nCols } }
  }
}

// Construit le classeur et renvoie son buffer (testable sans DOM).
// sheets : [{ name, headers, rows, title? }]
export async function buildWorkbookBuffer(sheets, docTitle = '2Saisons') {
  const wb = new ExcelJS.Workbook()
  wb.creator = '2Saisons'
  wb.created = new Date()
  const used = new Set()
  for (const sheet of (sheets || [])) {
    const headers = sheet.headers || []
    const rows = (sheet.rows || []).map(r => r.map(normalizeCell))
    const nCols = Math.max(headers.length, 1)
    let name = safeSheetName(sheet.name)
    let i = 2
    while (used.has(name)) name = (safeSheetName(sheet.name).slice(0, 28) + ' ' + i++).trim()
    used.add(name)
    const ws = wb.addWorksheet(name)
    ws.addRow(headers)
    for (const row of rows) ws.addRow(row)
    // Lignes insérées après titre (1) + date (2) : on décale tout de 2.
    ws.spliceRows(1, 0, [], [])
    styleSheet(ws, sheet.title || `${docTitle} — ${name}`, nCols, rows.length)
  }
  return wb.xlsx.writeBuffer()
}

function downloadBuffer(buffer, filename) {
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// Un seul tableau → un seul onglet.
export async function exportExcel(headers, rows, filename, sheetName = 'Export') {
  downloadBuffer(await buildWorkbookBuffer([{ name: sheetName, headers, rows }]), filename)
}

// Plusieurs tableaux → un onglet par tableau.
export async function exportWorkbook(sheets, filename) {
  downloadBuffer(await buildWorkbookBuffer(sheets), filename)
}
