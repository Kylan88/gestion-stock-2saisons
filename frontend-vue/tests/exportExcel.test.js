import { describe, expect, it } from 'vitest'
import ExcelJS from 'exceljs'
import { buildWorkbookBuffer, normalizeCell } from '../src/utils/exportExcel'

describe('normalizeCell', () => {
  it('keeps numbers, flattens objects, empties null', () => {
    expect(normalizeCell(null)).toBe('')
    expect(normalizeCell(undefined)).toBe('')
    expect(normalizeCell(12.5)).toBe(12.5)
    expect(normalizeCell('Mangue')).toBe('Mangue')
    expect(normalizeCell({ a: 1 })).toBe('{"a":1}')
  })
})

describe('buildWorkbookBuffer', () => {
  it('creates one styled sheet per table with headers and rows', async () => {
    const buffer = await buildWorkbookBuffer([
      { name: 'Lots', headers: ['Code', 'Poids'], rows: [['LOT-1', 10], ['LOT-2', null]] },
      { name: 'Fournisseurs', headers: ['Nom'], rows: [['Coop']] },
    ])
    const wb = new ExcelJS.Workbook()
    await wb.xlsx.load(buffer)
    expect(wb.worksheets.map(w => w.name)).toEqual(['Lots', 'Fournisseurs'])

    const ws = wb.getWorksheet('Lots')
    // Titre + date + mise en forme de l'en-tête.
    expect(ws.getCell(1, 1).value).toBe('2Saisons — Lots')
    expect(ws.getCell(3, 1).value).toBe('Code')
    expect(ws.getCell(3, 1).fill).toMatchObject({
      type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E79' },
    })
    expect(ws.getCell(3, 1).font).toMatchObject({ bold: true })
    // Données : nombres conservés, null → ''.
    expect(ws.getCell(4, 1).value).toBe('LOT-1')
    expect(ws.getCell(4, 2).value).toBe(10)
    expect(ws.getCell(5, 2).value).toBe('')
    // Bande alternée sur la 2e ligne de données.
    expect(ws.getCell(5, 1).fill).toMatchObject({ fgColor: { argb: 'FFD9E2F3' } })
  })
})
