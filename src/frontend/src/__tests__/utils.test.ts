import { severityColor, severityBg, formatTimestamp, formatDate } from '@/lib/utils';

describe('Frontend Utility Functions', () => {
  it('returns correct text color classes for severity levels', () => {
    expect(severityColor('CRITICAL')).toBe('text-red-500');
    expect(severityColor('HIGH')).toBe('text-orange-500');
    expect(severityColor('MEDIUM')).toBe('text-yellow-500');
    expect(severityColor('LOW')).toBe('text-green-500');
    expect(severityColor('UNKNOWN')).toBe('text-slate-400');
  });

  it('returns correct background and border classes for severity levels', () => {
    expect(severityBg('CRITICAL')).toContain('bg-red-500/10');
    expect(severityBg('HIGH')).toContain('bg-orange-500/10');
    expect(severityBg('MEDIUM')).toContain('bg-yellow-500/10');
    expect(severityBg('LOW')).toContain('bg-green-500/10');
  });

  it('formats timestamp and date properly', () => {
    const ts = '2024-03-15T10:01:23Z';
    expect(formatTimestamp(ts)).toBeTruthy();
    expect(formatDate(ts)).toBeTruthy();
  });
});
