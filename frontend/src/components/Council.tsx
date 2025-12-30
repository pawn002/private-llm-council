/**
 * Main Council interface component.
 */

import { useState } from 'react';
import type { DeliberationPhase } from '../types';
import { useDeliberation } from '../hooks/useDeliberation';
import { DeliberationView } from './DeliberationView';
import { SaveLoadDialog } from './SaveLoadDialog';

const phaseMessages: Record<DeliberationPhase, string> = {
  idle: '',
  gathering: 'Gathering perspectives from council members...',
  reviewing: 'Council members reviewing each other...',
  synthesizing: 'Chairman synthesizing perspectives...',
  analyzing: 'Analyzing disagreements and minority positions...',
  complete: 'Deliberation complete',
  error: 'An error occurred',
};

const phaseIcons: Record<DeliberationPhase, string> = {
  idle: '',
  gathering: '🎭',
  reviewing: '👁️',
  synthesizing: '⚖️',
  analyzing: '🔍',
  complete: '✅',
  error: '❌',
};

export function Council() {
  const {
    phase,
    statusMessage,
    deliberation,
    error,
    isLoading,
    ask,
    save,
    load,
    forget,
    reset,
  } = useDeliberation();

  const [question, setQuestion] = useState('');
  const [dialogMode, setDialogMode] = useState<'save' | 'load' | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      ask(question.trim());
      setQuestion('');
    }
  };

  // Idle state - show question input
  if (phase === 'idle') {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">The Sovereign Council</h1>
          <p className="text-gray-400">
            A privacy-first council of local LLMs ready to deliberate
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="question" className="sr-only">
              Your question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What question would you like the council to deliberate?"
              rows={4}
              className="w-full px-4 py-3 bg-council-surface border border-council-border rounded-lg text-white placeholder-gray-500 focus:border-council-accent focus:outline-none resize-none"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={!question.trim()}
              className="flex-1 py-3 bg-council-accent text-white font-medium rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Convene the Council
            </button>
            <button
              type="button"
              onClick={() => setDialogMode('load')}
              className="px-4 py-3 bg-council-surface border border-council-border text-gray-300 rounded-lg hover:bg-council-border transition-colors"
            >
              Load Saved
            </button>
          </div>
        </form>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>All processing happens locally on your machine.</p>
          <p>Your questions never leave your device.</p>
        </div>

        <SaveLoadDialog
          mode="load"
          isOpen={dialogMode === 'load'}
          onClose={() => setDialogMode(null)}
          onLoad={load}
        />
      </div>
    );
  }

  // Loading state - show progress
  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-council-surface rounded-lg p-8 border border-council-border">
          <div className="text-4xl mb-4 animate-pulse">{phaseIcons[phase]}</div>
          <h2 className="text-xl font-semibold text-white mb-2">
            {phaseMessages[phase]}
          </h2>
          <p className="text-gray-400">{statusMessage}</p>

          <div className="mt-6 flex justify-center">
            <div className="flex gap-1">
              {['gathering', 'reviewing', 'synthesizing', 'analyzing'].map((p) => (
                <div
                  key={p}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    phase === p
                      ? 'bg-council-accent animate-pulse'
                      : ['gathering', 'reviewing', 'synthesizing', 'analyzing'].indexOf(
                          phase
                        ) >
                        ['gathering', 'reviewing', 'synthesizing', 'analyzing'].indexOf(
                          p
                        )
                      ? 'bg-green-500'
                      : 'bg-council-border'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (phase === 'error') {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-council-surface rounded-lg p-8 border border-red-900">
          <div className="text-4xl mb-4">❌</div>
          <h2 className="text-xl font-semibold text-red-400 mb-2">
            Deliberation Failed
          </h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={reset}
            className="px-4 py-2 bg-council-accent text-white rounded hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Complete state - show deliberation
  if (phase === 'complete' && deliberation) {
    return (
      <>
        <DeliberationView
          deliberation={deliberation}
          onSave={() => setDialogMode('save')}
          onNewQuestion={reset}
        />

        <SaveLoadDialog
          mode="save"
          isOpen={dialogMode === 'save'}
          onClose={() => setDialogMode(null)}
          onSave={save}
          onForget={forget}
          deliberationId={deliberation.id}
        />
      </>
    );
  }

  return null;
}
