import * as XLSX from 'xlsx';
import type { Company } from '../types';

function formatScore(score?: number): string {
  if (score == null) return '';
  const normalized = score <= 1 ? score * 100 : score;
  return `${Math.round(normalized)}%`;
}

function qualityLabel(score?: number): string {
  if (score == null) return 'Unknown';
  if (score < 55) return 'Low';
  if (score < 75) return 'Medium';
  return 'High';
}

function upsellLabel(website?: string, score?: number, issues?: string[]): string {
  const hasIssues = Array.isArray(issues) && issues.length >= 2;
  const shouldUpsell = !website || (score ?? 100) < 55 || hasIssues;
  return shouldUpsell ? 'Yes' : 'No';
}

/**
 * Downloads the given companies as an Excel file matching the current list view.
 */
export function downloadCompaniesAsXlsx(
  companies: Company[],
  viewMode: 'all' | 'top',
  searchQuery?: string
): void {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const safeSearch = (searchQuery || '').trim().replace(/[^\w\-]+/g, '_').slice(0, 40);
  const suffix = safeSearch ? `-${safeSearch}` : '';
  const filename = `companies-${viewMode}${suffix}-${stamp}.xlsx`;

  const rows = companies.map((c) => ({
    Name: c.name,
    Type: c.business_type ?? '',
    Location: c.location ?? '',
    Email: c.email ?? '',
    Website: c.website ?? '',
    Phone: c.phone ?? '',
    'Lead score': formatScore(c.analysis_score),
    'Website quality': qualityLabel(c.website_quality_score),
    'Upsell opportunity': upsellLabel(c.website, c.website_quality_score, c.website_quality_issues),
    Status: c.status,
    'Created at': c.created_at,
  }));

  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Companies');
  XLSX.writeFile(wb, filename);
}
