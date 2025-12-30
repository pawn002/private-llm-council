/**
 * Main view for displaying a completed deliberation.
 */

import { useState } from 'react';
import type { Deliberation } from '../types';
import { PerspectiveCard } from './PerspectiveCard';
import { SynthesisPanel } from './SynthesisPanel';

interface DeliberationViewProps {
  deliberation: Deliberation;
  onSave: () => void;
  onNewQuestion: () => void;
}

export function DeliberationView({
  deliberation,
  onSave,
  onNewQuestion,
}: DeliberationViewProps) {
  const [expandedPerspective, setExpandedPerspective] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'synthesis' | 'perspectives'>('synthesis');

  return (
    <div className="space-y-6">
      {/* Question Header */}
      <div className="bg-council-surface rounded-lg p-6 border border-council-border">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Question</p>
            <h1 className="text-xl text-white font-medium">{deliberation.question}</h1>
            <p className="text-xs text-gray-500 mt-2">
              {deliberation.perspectives.length} perspectives ·{' '}
              {deliberation.disagreements.length} disagreements ·{' '}
              {new Date(deliberation.timestamp).toLocaleString()}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={onSave}
              className="px-3 py-1.5 text-sm bg-council-border hover:bg-gray-600 rounded transition-colors flex items-center gap-1"
            >
              <span>🔐</span> Save
            </button>
            <button
              onClick={onNewQuestion}
              className="px-3 py-1.5 text-sm bg-council-accent hover:bg-blue-600 text-white rounded transition-colors"
            >
              New Question
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-council-border">
        <button
          onClick={() => setActiveTab('synthesis')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'synthesis'
              ? 'text-council-accent border-b-2 border-council-accent'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Synthesis
        </button>
        <button
          onClick={() => setActiveTab('perspectives')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'perspectives'
              ? 'text-council-accent border-b-2 border-council-accent'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Perspectives ({deliberation.perspectives.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'synthesis' ? (
        <SynthesisPanel
          synthesis={deliberation.synthesis}
          disagreements={deliberation.disagreements}
          minorityReports={deliberation.minority_reports}
        />
      ) : (
        <div className="space-y-3">
          {deliberation.perspectives.map((perspective) => (
            <PerspectiveCard
              key={perspective.member_id}
              perspective={perspective}
              isExpanded={expandedPerspective === perspective.member_id}
              onToggle={() =>
                setExpandedPerspective(
                  expandedPerspective === perspective.member_id
                    ? null
                    : perspective.member_id
                )
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
