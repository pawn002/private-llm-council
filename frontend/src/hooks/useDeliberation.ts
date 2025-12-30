/**
 * Hook for managing deliberation state.
 *
 * Handles the deliberation lifecycle: asking questions, tracking phases,
 * and managing the resulting deliberation.
 */

import { useState, useCallback } from 'react';
import type { Deliberation, DeliberationPhase, DeliberationState } from '../types';
import {
  startDeliberation,
  deliberate,
  saveDeliberation,
  loadDeliberation,
  forgetDeliberation,
} from '../api/client';

export function useDeliberation() {
  const [state, setState] = useState<DeliberationState>({
    phase: 'idle',
    statusMessage: '',
    deliberation: null,
    error: null,
  });

  const setPhase = (phase: DeliberationPhase, message = '') => {
    setState((prev) => ({ ...prev, phase, statusMessage: message }));
  };

  const setError = (error: string) => {
    setState((prev) => ({
      ...prev,
      phase: 'error',
      error,
      statusMessage: '',
    }));
  };

  const ask = useCallback(async (question: string) => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setState({
      phase: 'gathering',
      statusMessage: 'Gathering perspectives from council members...',
      deliberation: null,
      error: null,
    });

    try {
      // Try streaming first, fall back to regular request
      const deliberation = await startDeliberation(question, (message) => {
        // Update phase based on status message
        if (message.toLowerCase().includes('gathering')) {
          setPhase('gathering', message);
        } else if (message.toLowerCase().includes('review')) {
          setPhase('reviewing', message);
        } else if (message.toLowerCase().includes('synthesi')) {
          setPhase('synthesizing', message);
        } else if (message.toLowerCase().includes('analy')) {
          setPhase('analyzing', message);
        } else {
          setState((prev) => ({ ...prev, statusMessage: message }));
        }
      });

      setState({
        phase: 'complete',
        statusMessage: 'Deliberation complete',
        deliberation,
        error: null,
      });
    } catch (err) {
      // Try non-streaming fallback
      try {
        const deliberation = await deliberate(question);
        setState({
          phase: 'complete',
          statusMessage: 'Deliberation complete',
          deliberation,
          error: null,
        });
      } catch (fallbackErr) {
        setError(
          fallbackErr instanceof Error ? fallbackErr.message : 'Deliberation failed'
        );
      }
    }
  }, []);

  const save = useCallback(
    async (passphrase: string): Promise<boolean> => {
      if (!state.deliberation) {
        setError('No deliberation to save');
        return false;
      }

      try {
        await saveDeliberation(state.deliberation.id, passphrase);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save deliberation');
        return false;
      }
    },
    [state.deliberation]
  );

  const load = useCallback(async (id: string, passphrase: string): Promise<boolean> => {
    setState({
      phase: 'gathering',
      statusMessage: 'Decrypting deliberation...',
      deliberation: null,
      error: null,
    });

    try {
      const deliberation = await loadDeliberation(id, passphrase);
      setState({
        phase: 'complete',
        statusMessage: 'Deliberation loaded',
        deliberation,
        error: null,
      });
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load deliberation');
      return false;
    }
  }, []);

  const forget = useCallback(
    async (): Promise<boolean> => {
      if (!state.deliberation) {
        setError('No deliberation to forget');
        return false;
      }

      try {
        await forgetDeliberation(state.deliberation.id);
        setState({
          phase: 'idle',
          statusMessage: '',
          deliberation: null,
          error: null,
        });
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to forget deliberation');
        return false;
      }
    },
    [state.deliberation]
  );

  const reset = useCallback(() => {
    setState({
      phase: 'idle',
      statusMessage: '',
      deliberation: null,
      error: null,
    });
  }, []);

  return {
    ...state,
    ask,
    save,
    load,
    forget,
    reset,
    isLoading: ['gathering', 'reviewing', 'synthesizing', 'analyzing'].includes(
      state.phase
    ),
  };
}
