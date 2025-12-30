/**
 * Privacy consent banner.
 *
 * Per requirements: always shown but dismissable per session.
 * Displays privacy mode and network status.
 */

import type { PrivacyStatus } from '../types';

interface ConsentBannerProps {
  status: PrivacyStatus | null;
  loading: boolean;
  onDismiss: () => void;
}

export function ConsentBanner({ status, loading, onDismiss }: ConsentBannerProps) {
  const getModeColor = () => {
    if (!status) return 'border-gray-600';
    switch (status.mode.mode) {
      case 'SOVEREIGN':
        return 'border-green-500';
      case 'SANCTUARY':
        return 'border-blue-500';
      case 'CITADEL':
        return 'border-yellow-500';
      default:
        return 'border-gray-600';
    }
  };

  const getModeIcon = () => {
    if (!status) return '?';
    switch (status.mode.mode) {
      case 'SOVEREIGN':
        return '🏰';
      case 'SANCTUARY':
        return '🛡️';
      case 'CITADEL':
        return '🐳';
      default:
        return '?';
    }
  };

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 bg-council-surface border-b-2 ${getModeColor()} transition-colors`}
    >
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-2xl">{getModeIcon()}</span>
            <div>
              <h2 className="font-semibold text-white">
                The Sovereign Council - Privacy First
              </h2>
              {loading ? (
                <p className="text-sm text-gray-400">Checking privacy status...</p>
              ) : status ? (
                <div className="text-sm">
                  <span className="text-gray-300">
                    Mode: <span className="text-council-accent">{status.mode.mode}</span>
                  </span>
                  <span className="text-gray-500 mx-2">|</span>
                  <span className="text-gray-300">
                    Network:{' '}
                    <span
                      className={
                        status.network_status.local_only
                          ? 'text-green-400'
                          : 'text-yellow-400'
                      }
                    >
                      {status.network_status.local_only
                        ? 'Local Only'
                        : 'External Detected'}
                    </span>
                  </span>
                  <span className="text-gray-500 mx-2">|</span>
                  <span className="text-gray-300">
                    Ollama:{' '}
                    <span
                      className={
                        status.network_status.ollama_reachable
                          ? 'text-green-400'
                          : 'text-red-400'
                      }
                    >
                      {status.network_status.ollama_reachable
                        ? 'Connected'
                        : 'Unavailable'}
                    </span>
                  </span>
                </div>
              ) : (
                <p className="text-sm text-red-400">
                  Unable to verify privacy status
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {status?.warnings && status.warnings.length > 0 && (
              <div className="text-yellow-400 text-sm">
                {status.warnings.length} warning(s)
              </div>
            )}
            <button
              onClick={onDismiss}
              className="px-3 py-1 text-sm bg-council-border hover:bg-gray-600 rounded transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>

        {status?.warnings && status.warnings.length > 0 && (
          <div className="mt-2 pt-2 border-t border-council-border">
            <ul className="text-sm text-yellow-400 space-y-1">
              {status.warnings.map((warning, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span>⚠</span>
                  {warning}
                </li>
              ))}
            </ul>
          </div>
        )}

        <p className="mt-2 text-xs text-gray-500">
          All processing happens locally. Your questions and deliberations never
          leave your machine. This banner will reappear each session.
        </p>
      </div>
    </div>
  );
}
