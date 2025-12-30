/**
 * Card displaying a council member's perspective.
 */

import type { Perspective } from '../types';

interface PerspectiveCardProps {
  perspective: Perspective;
  isExpanded?: boolean;
  onToggle?: () => void;
}

const memberColors: Record<string, string> = {
  phi: 'border-blue-500',
  psi: 'border-purple-500',
  omega: 'border-amber-500',
  sigma: 'border-green-500',
  delta: 'border-red-500',
};

const memberIcons: Record<string, string> = {
  phi: 'Φ',
  psi: 'Ψ',
  omega: 'Ω',
  sigma: 'Σ',
  delta: 'Δ',
};

export function PerspectiveCard({
  perspective,
  isExpanded = false,
  onToggle,
}: PerspectiveCardProps) {
  const borderColor = memberColors[perspective.member_id] || 'border-gray-500';
  const icon = memberIcons[perspective.member_id] || perspective.member_id[0].toUpperCase();

  return (
    <div
      className={`bg-council-surface border-l-4 ${borderColor} rounded-r-lg overflow-hidden`}
    >
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-council-border/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl font-serif text-gray-300">{icon}</span>
          <div className="text-left">
            <h3 className="font-semibold text-white capitalize">
              {perspective.member_id}
            </h3>
            <p className="text-xs text-gray-400">
              {perspective.character} · {perspective.model}
            </p>
          </div>
        </div>
        <span className="text-gray-400">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4">
          <div className="prose-council text-sm text-gray-300 whitespace-pre-wrap">
            {perspective.content}
          </div>
          <div className="mt-2 text-xs text-gray-500">
            {new Date(perspective.timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
}
