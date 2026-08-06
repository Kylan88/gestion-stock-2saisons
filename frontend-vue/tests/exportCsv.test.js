import { describe, expect, it } from 'vitest'
import { createCsvContent } from '../src/utils/exportCsv'

describe('createCsvContent', () => {
  it('uses a UTF-8 BOM and protects semicolons, quotes and line breaks', () => {
    const result = createCsvContent(
      ['Nom', 'Note'],
      [['Mangue', 'Qualité "A"; prête'], ['Banane', 'Ligne 1\nLigne 2']],
    )

    expect(result).toBe('\uFEFFNom;Note\nMangue;"Qualité ""A""; prête"\nBanane;"Ligne 1\nLigne 2"')
  })
})
