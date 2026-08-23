import { useState, useMemo } from 'react';

/**
 * Connector capability page: four tabs, progressive disclosure and a detail
 * panel, driven entirely by the capability graph passed in as `data`.
 * Generated pages stay tiny; all presentation logic lives here.
 */
export const CapabilityPage = ({ data }) => {
  const d = data || {};
  const [tab, setTab] = useState('overview');
  const [sel, setSel] = useState(null);
  const [q, setQ] = useState('');
  const [outcome, setOutcome] = useState('');
  const [status, setStatus] = useState('');
  const [limit, setLimit] = useState(8);

  const monitor = d.monitor || [];
  const audits = d.audits || [];
  const autos = d.autos || [];

  const outcomes = useMemo(() => {
    const s = new Set();
    monitor.forEach((m) => s.add(m.o));
    audits.forEach((a) => s.add(a.o));
    return [...s].sort();
  }, [monitor, audits]);

  const rows = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (tab === 'monitor') {
      return monitor.filter(
        (m) =>
          (!t || (m.n + ' ' + (m.d || '')).toLowerCase().includes(t)) &&
          (!outcome || m.o === outcome)
      );
    }
    if (tab === 'audit') {
      return audits.filter(
        (a) =>
          (!t || (a.n + ' ' + (a.why || '')).toLowerCase().includes(t)) &&
          (!outcome || a.o === outcome) &&
          (!status || a.s === status)
      );
    }
    if (tab === 'automate') {
      return autos.filter((w) => !t || (w.n + ' ' + (w.d || '')).toLowerCase().includes(t));
    }
    return [];
  }, [tab, q, outcome, status, monitor, audits, autos]);

  const pill = (text, kind) => {
    const tone =
      kind === 'good'
        ? { color: '#1f9e54', borderColor: '#1f9e54', background: '#ecf8f110' }
        : kind === 'warn'
        ? { color: '#c07a17', borderColor: '#c07a17', background: '#fdf6e910' }
        : kind === 'bad'
        ? { color: '#c53527', borderColor: '#c53527', background: '#fdf0ee10' }
        : kind === 'brand'
        ? { color: '#5529d6', borderColor: '#5529d6' }
        : { color: 'inherit', borderColor: 'currentColor', opacity: 0.65 };
    return (
      <span
        key={text}
        style={{
          fontSize: '10.5px',
          fontFamily: 'ui-monospace, monospace',
          border: '1px solid',
          borderRadius: '999px',
          padding: '2px 8px',
          whiteSpace: 'nowrap',
          ...tone,
        }}
      >
        {text}
      </span>
    );
  };

  const sevKind = (s) => (s === 'critical' ? 'bad' : s === 'high' ? 'warn' : 'muted');
  const fixKind = (s) => (s === 'Prepared fix' ? 'good' : s === 'Candidate remediation' ? 'warn' : 'muted');

  const card = (item, kind) => {
    const title = item.n;
    const badges =
      kind === 'monitor'
        ? [pill(item.o, 'brand'), pill(item.a === 'Watch only' || item.a === 'Merchant rule' ? item.a : `Alert ${item.a}`, 'muted')]
        : kind === 'audit'
        ? [pill(item.sev, sevKind(item.sev)), pill(item.s, fixKind(item.s))]
        : [pill(item.role, 'brand'), pill(item.ready, 'good')];
    const body = kind === 'monitor' ? (item.nc ? 'Description pending editorial review; the signal is live.' : item.d) : kind === 'audit' ? item.why : item.d;
    return (
      <button
        key={title}
        onClick={() => setSel({ kind, item })}
        style={{
          display: 'block',
          width: '100%',
          textAlign: 'left',
          border: '1px solid rgba(128,128,128,.28)',
          borderRadius: '10px',
          padding: '12px 14px',
          marginBottom: '8px',
          background: 'transparent',
          cursor: 'pointer',
          font: 'inherit',
          color: 'inherit',
        }}
      >
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <strong style={{ fontSize: '14px' }}>{title}</strong>
          <span style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>{badges}</span>
        </div>
        {body ? <div style={{ fontSize: '12.5px', opacity: 0.72, marginTop: '4px' }}>{body}</div> : null}
      </button>
    );
  };

  const tabBtn = (id, label) => (
    <button
      key={id}
      onClick={() => {
        setTab(id);
        setLimit(8);
        setQ('');
      }}
      style={{
        border: 0,
        background: 'none',
        font: 'inherit',
        fontWeight: 600,
        fontSize: '14px',
        padding: '9px 14px',
        cursor: 'pointer',
        color: tab === id ? '#5529d6' : 'inherit',
        opacity: tab === id ? 1 : 0.65,
        borderBottom: tab === id ? '2px solid #5529d6' : '2px solid transparent',
      }}
    >
      {label}
    </button>
  );

  const inputStyle = {
    border: '1px solid rgba(128,128,128,.3)',
    borderRadius: '999px',
    padding: '7px 13px',
    font: 'inherit',
    fontSize: '13px',
    background: 'transparent',
    color: 'inherit',
  };

  return (
    <div style={{ position: 'relative' }}>
      {/* capability counts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(120px,1fr))', gap: '10px', margin: '18px 0' }}>
        {(d.stats || []).map(([v, l]) => (
          <div key={l} style={{ border: '1px solid rgba(128,128,128,.28)', borderRadius: '10px', padding: '11px 13px' }}>
            <div style={{ fontSize: v.length > 6 ? '15px' : '21px', fontWeight: 700, letterSpacing: '-.02em', color: v.length > 6 ? '#5529d6' : 'inherit' }}>{v}</div>
            <div style={{ fontSize: '11px', opacity: 0.66 }}>{l}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid rgba(128,128,128,.25)', marginBottom: '16px', flexWrap: 'wrap' }}>
        {tabBtn('overview', 'Overview')}
        {tabBtn('monitor', `Monitor (${monitor.length})`)}
        {tabBtn('audit', `Audit (${audits.length})`)}
        {tabBtn('automate', 'Automate')}
      </div>

      {tab === 'overview' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: '10px' }}>
            {outcomes.map((o) => (
              <div key={o} style={{ border: '1px solid rgba(128,128,128,.28)', borderLeft: '3px solid #5529d6', borderRadius: '10px', padding: '11px 14px' }}>
                <strong style={{ fontSize: '13.5px' }}>{o}</strong>
              </div>
            ))}
          </div>
          <p style={{ fontSize: '13px', opacity: 0.75, marginTop: '16px' }}>
            Every capability follows the same controlled sequence: connect, monitor, detect, recommend,
            approve, execute, verify. Nothing changes a connected system without the approval step.
          </p>
        </div>
      )}

      {tab !== 'overview' && (
        <div>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
            <input
              style={{ ...inputStyle, flex: 1, minWidth: '170px' }}
              placeholder={`Search ${tab === 'monitor' ? 'signals' : tab === 'audit' ? 'checks' : 'workflows'}...`}
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setLimit(8);
              }}
            />
            {tab !== 'automate' && (
              <select style={inputStyle} value={outcome} onChange={(e) => { setOutcome(e.target.value); setLimit(8); }}>
                <option value="">All outcomes</option>
                {outcomes.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            )}
            {tab === 'audit' && (
              <select style={inputStyle} value={status} onChange={(e) => { setStatus(e.target.value); setLimit(8); }}>
                <option value="">All fix statuses</option>
                <option>Prepared fix</option>
                <option>Candidate remediation</option>
                <option>Report only</option>
              </select>
            )}
          </div>

          {rows.length === 0 && tab === 'automate' && (
            <div style={{ border: '1px dashed #5529d6', borderRadius: '10px', padding: '15px' }}>
              <strong style={{ fontSize: '14px' }}>Ready to build your first {d.name} workflow</strong>
              <p style={{ fontSize: '12.5px', opacity: 0.75, margin: '6px 0 0' }}>
                Vortex IQ is integrated with {d.reads} read and {d.writes} write operations on {d.name}.
                Pick a trigger, add them as steps, and every step that changes data pauses for approval.
              </p>
            </div>
          )}
          {rows.length === 0 && tab !== 'automate' && (
            <div style={{ opacity: 0.6, fontSize: '13px' }}>Nothing matches this search or filter.</div>
          )}

          {rows.slice(0, limit).map((r) => card(r, tab))}

          {rows.length > limit && (
            <button
              onClick={() => setLimit(rows.length)}
              style={{ ...inputStyle, display: 'block', margin: '10px auto 0', cursor: 'pointer' }}
            >
              View all {rows.length}
            </button>
          )}
        </div>
      )}

      {/* detail panel */}
      {sel && (
        <>
          <div
            onClick={() => setSel(null)}
            style={{ position: 'fixed', inset: 0, background: 'rgba(10,6,26,.45)', zIndex: 40 }}
          />
          <aside
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              width: 'min(430px, 94vw)',
              height: '100vh',
              overflowY: 'auto',
              background: 'var(--background, #fff)',
              backgroundColor: 'light-dark(#fff, #0c061f)',
              borderLeft: '1px solid rgba(128,128,128,.3)',
              padding: '20px 22px',
              zIndex: 50,
            }}
          >
            <button
              onClick={() => setSel(null)}
              style={{ float: 'right', border: '1px solid rgba(128,128,128,.3)', background: 'transparent', color: 'inherit', borderRadius: '999px', width: '30px', height: '30px', cursor: 'pointer' }}
            >
              ×
            </button>
            <DetailBody sel={sel} d={d} pill={pill} sevKind={sevKind} fixKind={fixKind} />
          </aside>
        </>
      )}
    </div>
  );
};

const Label = ({ children }) => (
  <div style={{ fontFamily: 'ui-monospace, monospace', fontSize: '10px', letterSpacing: '.1em', textTransform: 'uppercase', color: '#5529d6', margin: '16px 0 3px' }}>
    {children}
  </div>
);

const DetailBody = ({ sel, d, pill, sevKind, fixKind }) => {
  const { kind, item } = sel;
  const P = ({ children }) => <p style={{ fontSize: '13px', opacity: 0.8, margin: 0 }}>{children}</p>;
  return (
    <div>
      <Label>{kind === 'monitor' ? 'Performance signal' : kind === 'audit' ? 'Automated check' : 'Workflow template'}</Label>
      <h3 style={{ margin: '2px 0 8px', fontSize: '17px' }}>{item.n}</h3>
      <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
        {kind === 'monitor' && [pill(item.o, 'brand'), pill(item.a, 'muted')]}
        {kind === 'audit' && [pill(item.sev, sevKind(item.sev)), pill(item.s, fixKind(item.s))]}
        {kind === 'automate' && [pill(item.role, 'brand'), pill(item.ready, 'good')]}
      </div>

      <Label>What it does and why it matters</Label>
      <P>{kind === 'monitor' ? (item.nc ? `Live signal on ${d.name}; its description is queued for editorial review.` : item.d) : kind === 'audit' ? item.why : item.d}</P>

      {kind === 'audit' && (
        <>
          <Label>Fix status and controls</Label>
          <P>
            {item.s === 'Prepared fix'
              ? 'A prepared, approval-gated fix exists: the proposed change, affected records, risk, reversibility and verification are shown before execution.'
              : item.s === 'Candidate remediation'
              ? 'A likely corrective operation exists, but its mapping and recovery are not yet complete, so execution is not offered. Evidence and recommended manual steps are provided.'
              : 'Vortex IQ detects and explains this; resolution is manual, with evidence and recommended steps.'}
          </P>
          <Label>Reference</Label>
          <P>
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: '11px' }}>{(item.codes || []).join(', ')}</span>
          </P>
        </>
      )}

      {kind === 'monitor' && (
        <>
          <Label>Alert behaviour</Label>
          <P>
            {item.a === 'Watch only'
              ? 'Watch only today. Add a merchant threshold or baseline watcher to alert on movement.'
              : item.a === 'Merchant rule'
              ? 'Alerts use a merchant-configured rule rather than a universal default.'
              : `Default alert band ${item.a}, adjustable per merchant.`}
          </P>
        </>
      )}

      {kind === 'automate' && (
        <>
          {item.also && item.also.length > 0 && (
            <>
              <Label>Also available on</Label>
              <P>{item.also.join(', ')}</P>
            </>
          )}
          {item.tested && item.tested.length > 0 && (
            <>
              <Label>Tested alongside</Label>
              <P>{item.tested.join(', ')}</P>
            </>
          )}
          <Label>Approval and delivery</Label>
          <P>
            Runs on a schedule or trigger. Any step that changes data pauses for approval per the merchant
            policy, and results deliver to the configured destination with a run receipt.
          </P>
        </>
      )}
    </div>
  );
};

export default CapabilityPage;
