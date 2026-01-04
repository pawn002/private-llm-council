/**
 * Member identity constants for consistent styling across components.
 */

export const MEMBER_COLORS: Record<string, string> = {
  phi: 'border-blue',
  psi: 'border-purple',
  omega: 'border-amber',
  sigma: 'border-green',
  delta: 'border-red',
};

export const MEMBER_ICONS: Record<string, string> = {
  phi: 'Φ',
  psi: 'Ψ',
  omega: 'Ω',
  sigma: 'Σ',
  delta: 'Δ',
};

export const getMemberColor = (memberId: string): string =>
  MEMBER_COLORS[memberId] || 'border-gray';

export const getMemberIcon = (memberId: string): string =>
  MEMBER_ICONS[memberId] || memberId[0]?.toUpperCase() || '?';
