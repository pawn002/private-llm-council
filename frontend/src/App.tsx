/**
 * The Sovereign Council - Main Application
 *
 * A privacy-first local LLM council for deliberative AI assistance.
 */

import { usePrivacy } from './hooks/usePrivacy';
import { ConsentBanner, Council } from './components';

function App() {
  const { status, loading, showConsentBanner, dismissConsent } = usePrivacy();

  return (
    <div className="min-h-screen bg-council-bg">
      {/* Privacy consent banner - shows every session */}
      {showConsentBanner && (
        <ConsentBanner
          status={status}
          loading={loading}
          onDismiss={dismissConsent}
        />
      )}

      {/* Main content - offset if banner is showing */}
      <main
        className={`transition-all ${
          showConsentBanner ? 'pt-32' : 'pt-8'
        } pb-8 px-4`}
      >
        <div className="max-w-4xl mx-auto">
          <Council />
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-council-surface/80 backdrop-blur border-t border-council-border py-2">
        <div className="max-w-4xl mx-auto px-4 flex items-center justify-between text-xs text-gray-500">
          <span>The Sovereign Council v0.1.0</span>
          <span className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500" />
            {status?.mode.mode || 'Loading...'}
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
