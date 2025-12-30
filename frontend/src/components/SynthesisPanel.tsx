/**
 * Panel displaying the chairman's synthesis.
 */

import type { Synthesis, Disagreement, MinorityReport } from '../types';

interface SynthesisPanelProps {
  synthesis: Synthesis;
  disagreements: Disagreement[];
  minorityReports: MinorityReport[];
}

function ConfidenceMeter({ value, label }: { value: number; label: string }) {
  const percentage = Math.round(value * 100);
  const color =
    value >= 0.7 ? 'bg-green-500' : value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 w-24">{label}</span>
      <div className="flex-1 h-2 bg-council-border rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-gray-300 w-12 text-right">{percentage}%</span>
    </div>
  );
}

function SeverityBadge({ severity }: { severity?: string }) {
  const colors: Record<string, string> = {
    minor: 'bg-blue-900 text-blue-300',
    moderate: 'bg-yellow-900 text-yellow-300',
    fundamental: 'bg-red-900 text-red-300',
  };

  const color = colors[severity || 'moderate'] || colors.moderate;

  return (
    <span className={`px-2 py-0.5 text-xs rounded ${color}`}>
      {severity || 'moderate'}
    </span>
  );
}

export function SynthesisPanel({
  synthesis,
  disagreements,
  minorityReports,
}: SynthesisPanelProps) {
  return (
    <div className="space-y-6">
      {/* Main Synthesis */}
      <div className="bg-council-surface rounded-lg p-6 border border-council-border">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">⚖️</span>
          <h2 className="text-xl font-semibold text-white">Council Synthesis</h2>
        </div>

        <div className="prose-council text-gray-300 whitespace-pre-wrap">
          {synthesis.content}
        </div>

        {/* Confidence Score */}
        {synthesis.confidence && (
          <div className="mt-6 pt-4 border-t border-council-border">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">
              Confidence Assessment
            </h3>
            <div className="space-y-2">
              <ConfidenceMeter
                value={synthesis.confidence.overall}
                label="Overall"
              />
              <ConfidenceMeter
                value={synthesis.confidence.consensus_strength}
                label="Consensus"
              />
              <ConfidenceMeter
                value={synthesis.confidence.dissent_strength}
                label="Dissent"
              />
            </div>
            <p className="mt-2 text-xs text-gray-500 italic">
              {synthesis.confidence.reasoning}
            </p>
          </div>
        )}
      </div>

      {/* Consensus Points */}
      {synthesis.consensus_points.length > 0 && (
        <div className="bg-council-surface rounded-lg p-4 border border-green-900">
          <h3 className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
            <span>✓</span> Points of Agreement
          </h3>
          <ul className="space-y-1">
            {synthesis.consensus_points.map((point, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-green-500">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Divisions */}
      {synthesis.divisions.length > 0 && (
        <div className="bg-council-surface rounded-lg p-4 border border-yellow-900">
          <h3 className="text-sm font-semibold text-yellow-400 mb-2 flex items-center gap-2">
            <span>⚡</span> Areas of Division
          </h3>
          <ul className="space-y-1">
            {synthesis.divisions.map((division, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-yellow-500">•</span>
                {division}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Unique Insights */}
      {synthesis.unique_insights.length > 0 && (
        <div className="bg-council-surface rounded-lg p-4 border border-purple-900">
          <h3 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
            <span>💡</span> Unique Insights
          </h3>
          <ul className="space-y-1">
            {synthesis.unique_insights.map((insight, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-purple-500">•</span>
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Disagreements */}
      {disagreements.length > 0 && (
        <div className="bg-council-surface rounded-lg p-4 border border-council-border">
          <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
            <span>🔍</span> Detailed Disagreements
          </h3>
          <div className="space-y-4">
            {disagreements.map((d, i) => (
              <div key={i} className="border-l-2 border-council-border pl-3">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-white">{d.topic}</h4>
                  <SeverityBadge severity={d.severity} />
                </div>
                <p className="text-sm text-gray-400 mb-2">{d.description}</p>
                <div className="space-y-1">
                  {Object.entries(d.positions).map(([member, position]) => (
                    <div key={member} className="text-sm">
                      <span className="text-council-accent capitalize">{member}:</span>{' '}
                      <span className="text-gray-300">{position}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Minority Reports */}
      {minorityReports.length > 0 && (
        <div className="bg-council-surface rounded-lg p-4 border border-red-900">
          <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
            <span>📋</span> Minority Reports
          </h3>
          <div className="space-y-4">
            {minorityReports.map((report, i) => (
              <div key={i} className="border-l-2 border-red-800 pl-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg font-serif text-red-400 capitalize">
                    {report.member_id}
                  </span>
                </div>
                <p className="text-sm text-white font-medium">{report.position}</p>
                <p className="text-sm text-gray-400 mt-1">{report.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
