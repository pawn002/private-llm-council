/**
 * Dialog for saving and loading encrypted deliberations.
 */

import { useState, useEffect } from 'react';
import { listDeliberations } from '../api/client';

interface SaveLoadDialogProps {
  mode: 'save' | 'load';
  isOpen: boolean;
  onClose: () => void;
  onSave?: (passphrase: string) => Promise<boolean>;
  onLoad?: (id: string, passphrase: string) => Promise<boolean>;
  onForget?: () => Promise<boolean>;
  deliberationId?: string;
}

export function SaveLoadDialog({
  mode,
  isOpen,
  onClose,
  onSave,
  onLoad,
  onForget,
  deliberationId,
}: SaveLoadDialogProps) {
  const [passphrase, setPassphrase] = useState('');
  const [confirmPassphrase, setConfirmPassphrase] = useState('');
  const [selectedId, setSelectedId] = useState('');
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && mode === 'load') {
      listDeliberations()
        .then(setSavedIds)
        .catch(() => setSavedIds([]));
    }
  }, [isOpen, mode]);

  useEffect(() => {
    if (!isOpen) {
      setPassphrase('');
      setConfirmPassphrase('');
      setError('');
    }
  }, [isOpen]);

  const handleSave = async () => {
    if (passphrase.length < 8) {
      setError('Passphrase must be at least 8 characters');
      return;
    }
    if (passphrase !== confirmPassphrase) {
      setError('Passphrases do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const success = await onSave?.(passphrase);
      if (success) {
        onClose();
      } else {
        setError('Failed to save deliberation');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async () => {
    if (!selectedId) {
      setError('Please select a deliberation');
      return;
    }
    if (!passphrase) {
      setError('Please enter the passphrase');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const success = await onLoad?.(selectedId, passphrase);
      if (success) {
        onClose();
      } else {
        setError('Failed to load deliberation - check passphrase');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  const handleForget = async () => {
    if (!confirm('This will securely delete the deliberation. This cannot be undone.')) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const success = await onForget?.();
      if (success) {
        onClose();
      } else {
        setError('Failed to forget deliberation');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to forget');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="bg-council-surface border border-council-border rounded-lg p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <span>{mode === 'save' ? '🔐' : '🔓'}</span>
          {mode === 'save' ? 'Encrypt & Save Deliberation' : 'Load Deliberation'}
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-300 text-sm">
            {error}
          </div>
        )}

        {mode === 'save' ? (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Your deliberation will be encrypted with AES-256-GCM. The passphrase
              is not stored - if you forget it, the data cannot be recovered.
            </p>

            {deliberationId && (
              <div className="text-sm text-gray-500">
                ID: <code className="text-council-accent">{deliberationId}</code>
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-1">Passphrase</label>
              <input
                type="password"
                value={passphrase}
                onChange={(e) => setPassphrase(e.target.value)}
                className="w-full px-3 py-2 bg-council-bg border border-council-border rounded text-white focus:border-council-accent focus:outline-none"
                placeholder="Minimum 8 characters"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Confirm Passphrase
              </label>
              <input
                type="password"
                value={confirmPassphrase}
                onChange={(e) => setConfirmPassphrase(e.target.value)}
                className="w-full px-3 py-2 bg-council-bg border border-council-border rounded text-white focus:border-council-accent focus:outline-none"
                placeholder="Re-enter passphrase"
              />
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Select a saved deliberation and enter the passphrase to decrypt it.
            </p>

            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Saved Deliberations
              </label>
              {savedIds.length === 0 ? (
                <p className="text-sm text-gray-500 italic">No saved deliberations</p>
              ) : (
                <select
                  value={selectedId}
                  onChange={(e) => setSelectedId(e.target.value)}
                  className="w-full px-3 py-2 bg-council-bg border border-council-border rounded text-white focus:border-council-accent focus:outline-none"
                >
                  <option value="">Select...</option>
                  {savedIds.map((id) => (
                    <option key={id} value={id}>
                      {id}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Passphrase</label>
              <input
                type="password"
                value={passphrase}
                onChange={(e) => setPassphrase(e.target.value)}
                className="w-full px-3 py-2 bg-council-bg border border-council-border rounded text-white focus:border-council-accent focus:outline-none"
                placeholder="Enter passphrase"
              />
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-between">
          <div>
            {mode === 'save' && onForget && (
              <button
                onClick={handleForget}
                disabled={loading}
                className="px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-900/30 rounded transition-colors"
              >
                Forget Forever
              </button>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-council-border rounded transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={mode === 'save' ? handleSave : handleLoad}
              disabled={loading}
              className="px-4 py-2 text-sm bg-council-accent text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : mode === 'save' ? 'Encrypt & Save' : 'Decrypt & Load'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
