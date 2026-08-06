export function createCsvContent(headers, rows) {
  const sep = ';'
  const lines = [
    headers.join(sep),
    ...rows.map(row => row.map(v => {
      const s = String(v ?? '').replace(/"/g, '""')
      return s.includes(sep) || s.includes('"') || s.includes('\n') ? `"${s}"` : s
    }).join(sep))
  ]
  return '\uFEFF' + lines.join('\n')
}

export function exportCsv(headers, rows, filename = 'export.csv') {
  const blob = new Blob([createCsvContent(headers, rows)], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
