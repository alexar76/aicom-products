import { useEffect, useState } from 'react';
import { fetchSpend, fetchAllowance, fetchWallet, SpendData } from '../../api/operator';
import SpendSummary from './SpendSummary';

interface DashboardProps {
  onNavigateAnalytics: () => void;
}

export default function Dashboard({ onNavigateAnalytics }: DashboardProps) {
  const [spend, setSpend] = useState<SpendData | null>(null);
  const [allowance, setAllowance] = useState<any>(null);
  const [wallet, setWallet] = useState<any>(null);

  useEffect(() => {
    fetchSpend().then(setSpend).catch(console.error);
    fetchAllowance().then(setAllowance).catch(console.error);
    fetchWallet().then(setWallet).catch(console.error);
  }, []);

  if (!spend) return <div>Loading...</div>;

  return (
    <div>
      <h2>Operator Dashboard</h2>
      <SpendSummary spend={spend} allowance={allowance} wallet={wallet} />
      <button className="btn" onClick={onNavigateAnalytics}>Analytics Workspace</button>
    </div>
  );
}
