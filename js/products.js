// Toolbench catalog — one entry per genuinely-useful tool. The loop appends here
// as it ships each app. Rules: every tool must be genuinely useful and
// defensible (no brainrot); monetization is only 'free', 'buy', 'rent', or
// 'sell' — never ads; a tool is only listed once its live URL serves real code.
//
// status:  'live' (deployed + verified) | 'building' (in progress, not listed)
// category: short, human label used for grouping on the hub.

export const TOOLS = [
  {
    name: 'AccessProof',
    tagline: 'Check if your online store breaks EU accessibility law — before a lawyer does.',
    what: 'Scans a page for the real WCAG 2.1 AA failures the EU Accessibility Act requires you to fix, in plain English, 100% in your browser. Flags the “accessibility widgets” that don’t actually make you compliant.',
    category: 'Compliance',
    emoji: '♿',
    liveUrl: 'https://emin-dev.github.io/accessproof/',
    repoUrl: 'https://github.com/Emin-dev/accessproof',
    status: 'live',
    monetization: 'free',
    price: 'Free scan',
  },
];
