import { SpendData } from '../../api/operator';

interface SpendSummaryProps {
  spend: SpendData;
  allowance: any;
  wallet: any;
}

export default function SpendSummary({ spend, allowance, wallet }: SpendSummaryProps) {
  return (
    <div className="card">
      <h3>Spend & Allowance</h3>
      <p>Total Spend: ${spend.total_spend_usd.toFixed(2)}</p>
      <p>Daily Spend: ${spend.daily_spend_usd.toFixed(2)} / ${spend.budget_usd.toFixed(2)}</p>
      <p>Invokes: {spend.invokes_total} ({spend.invokes_24h} in 24h)</p>
      <p>Allowance: {allowance ? `${allowance.used}/${allowance.max}` : 'Unknown'}</p>
      <p>Wallet: {wallet?.wallet_enabled ? `${wallet.address_truncated} (${wallet.chain})` : 'Free allowance mode'}</p>
    </div>
  );
}
