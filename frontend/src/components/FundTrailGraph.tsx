import { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  MarkerType,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { ShieldAlert, Landmark } from "lucide-react";

function AccountNode({ data }: { data: any }) {
  const accent = data.riskLevel === "high" ? "#FF3B5C" : data.riskLevel === "medium" ? "#FFB020" : "#00FF9D";
  const isSeed = data.isSeed;
  return (
    <div
      className="relative rounded-lg border bg-ink-900 px-3 py-2 shadow-panel transition-transform hover:scale-105"
      style={{
        borderColor: isSeed ? "#00E5FF" : `${accent}66`,
        boxShadow: isSeed ? "0 0 18px rgba(0,229,255,0.35)" : `0 0 12px ${accent}22`,
        minWidth: 150,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: accent, width: 7, height: 7 }} />
      <div className="flex items-center gap-2">
        <div
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full"
          style={{ background: `${accent}1a`, border: `1px solid ${accent}55` }}
        >
          {isSeed ? <Landmark className="h-3.5 w-3.5" style={{ color: "#00E5FF" }} /> : <ShieldAlert className="h-3.5 w-3.5" style={{ color: accent }} />}
        </div>
        <div className="min-w-0">
          <div className="max-w-[130px] truncate font-mono text-[10.5px] font-semibold" style={{ color: isSeed ? "#00E5FF" : "#E2E8F0" }}>
            {data.label}
          </div>
          <div className="font-mono text-[9px] text-slate-500">
            ↑₹{data.received.toLocaleString("en-IN")} ↓₹{data.sent.toLocaleString("en-IN")}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} style={{ background: accent, width: 7, height: 7 }} />
    </div>
  );
}

const nodeTypes = { account: AccountNode };

export function FundTrailGraph({ nodes, edges, clusters }: { nodes: any[]; edges: any[]; clusters: any[] }) {
  const flowNodes: Node[] = useMemo(() => {
    const clusterAccounts = new Set<string>();
    (clusters ?? []).forEach((c: any) => (c.accounts ?? []).forEach((a: string) => clusterAccounts.add(a)));

    const positions: Record<string, { x: number; y: number }> = {};
    nodes.forEach((n, i) => {
      const col = i % 4;
      const row = Math.floor(i / 4);
      positions[n.id] = { x: col * 220 + (row % 2) * 40, y: row * 130 };
    });

    return nodes.map((n) => ({
      id: n.id,
      type: "account",
      position: positions[n.id] ?? { x: 0, y: 0 },
      data: {
        label: n.label,
        received: n.received,
        sent: n.sent,
        isSeed: n.is_seed,
        riskLevel: clusterAccounts.has(n.id) ? "high" : n.risk_level,
      },
    }));
  }, [nodes, clusters]);

  const flowEdges: Edge[] = useMemo(
    () =>
      edges.map((e, i) => ({
        id: e.id ?? `e-${i}`,
        source: e.source,
        target: e.target,
        label: e.label,
        animated: true,
        style: { stroke: "#00E5FF", strokeWidth: 1.6, opacity: 0.75 },
        labelStyle: { fill: "#94A3B8", fontSize: 9, fontFamily: "JetBrains Mono" },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#00E5FF", width: 14, height: 14 },
      })),
    [edges]
  );

  return (
    <ReactFlow
      nodes={flowNodes}
      edges={flowEdges}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.25 }}
      minZoom={0.3}
      maxZoom={2}
      proOptions={{ hideAttribution: true }}
    >
      <Background color="rgba(0,229,255,0.07)" gap={28} size={1} />
      <Controls showInteractive={false} style={{ background: "#0D1326", border: "1px solid rgba(0,229,255,0.2)", borderRadius: 8, color: "#00E5FF" }} />
    </ReactFlow>
  );
}