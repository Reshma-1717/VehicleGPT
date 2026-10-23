import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewPage } from './pages/OverviewPage';
import { AssistantPage } from './pages/AssistantPage';
import { TelemetryPage } from './pages/TelemetryPage';
import { EventsPage } from './pages/EventsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SystemStatusPage } from './pages/SystemStatusPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';
import { ShieldCheck, Info } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [initialAssistantQuery, setInitialAssistantQuery] = useState<string | undefined>(undefined);
  const [simulationActive, setSimulationActive] = useState<boolean>(true);

  useEffect(() => {
    // Check initial simulation state
    api.getSystemStatus()
      .then((st) => setSimulationActive(st.simulation_active))
      .catch((err) => console.error(err));
  }, []);

  const handleNavigateToAssistant = (query?: string) => {
    if (query) {
      setInitialAssistantQuery(query);
    }
    setActiveTab('assistant');
  };

  const renderActiveScreen = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <OverviewPage
            onNavigateToAssistant={handleNavigateToAssistant}
            onNavigateToEvents={() => setActiveTab('events')}
          />
        );
      case 'assistant':
        return (
          <AssistantPage
            initialQuery={initialAssistantQuery}
            onClearInitialQuery={() => setInitialAssistantQuery(undefined)}
          />
        );
      case 'telemetry':
        return <TelemetryPage />;
      case 'events':
        return <EventsPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'system':
        return <SystemStatusPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return (
          <OverviewPage
            onNavigateToAssistant={handleNavigateToAssistant}
            onNavigateToEvents={() => setActiveTab('events')}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        simulationActive={simulationActive}
        offlineMode={true}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {renderActiveScreen()}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/90 py-3 px-4 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Info className="h-3.5 w-3.5 text-blue-400" />
            <span>
              <strong>VehicleGPT Edge Intelligence Prototype</strong> • TATA TELIPORT Case Study 5 • Simulated Environment
            </span>
          </div>

          <div className="flex items-center gap-3 font-mono text-[11px] text-slate-400">
            <span>RAM: ~2GB Profile</span>
            <span>•</span>
            <span>ARM64 Offline Mode</span>
            <span>•</span>
            <span>Latency Target: &lt;2000ms</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
