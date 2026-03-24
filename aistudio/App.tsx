import React, { useState } from 'react';
import { 
  Plus, 
  Search, 
  FileText,
  Users,
  Calendar,
  Settings,
  LogOut,
  ChevronRight,
  Filter,
  ArrowUpRight,
  LayoutDashboard,
  MoreHorizontal,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { motion } from 'motion/react';

// --- Types ---
interface CasePaper {
  id: string;
  patient: string;
  date: string;
  practitioner: string;
  status: 'DRAFT' | 'FINAL' | 'PENDING';
  priority: 'NORMAL' | 'HIGH';
}

// --- Mock Data ---
const MOCK_CASES: CasePaper[] = [
  { id: 'HC-001', patient: 'Lydia Vance', date: '2026.03.24', practitioner: 'Dr. Abhay', status: 'DRAFT', priority: 'HIGH' },
  { id: 'HC-002', patient: 'Marcus Thorne', date: '2026.03.23', practitioner: 'Dr. Abhay', status: 'FINAL', priority: 'NORMAL' },
  { id: 'HC-003', patient: 'Elena Rossi', date: '2026.03.22', practitioner: 'Dr. Abhay', status: 'PENDING', priority: 'NORMAL' },
  { id: 'HC-004', patient: 'Julian Gray', date: '2026.03.21', practitioner: 'Dr. Abhay', status: 'DRAFT', priority: 'HIGH' },
  { id: 'HC-005', patient: 'Sarah Miller', date: '2026.03.20', practitioner: 'Dr. Abhay', status: 'FINAL', priority: 'NORMAL' },
  { id: 'HC-006', patient: 'Thomas Kent', date: '2026.03.19', practitioner: 'Dr. Abhay', status: 'DRAFT', priority: 'NORMAL' },
  { id: 'HC-007', patient: 'Isabella Chen', date: '2026.03.18', practitioner: 'Dr. Abhay', status: 'FINAL', priority: 'NORMAL' },
];

// --- Components ---

const NavIcon: React.FC<{ icon: any, active?: boolean }> = ({ icon: Icon, active = false }) => (
  <div className={`w-14 h-14 flex items-center justify-center cursor-pointer transition-all border-b border-ink ${active ? 'bg-ink text-paper' : 'hover:bg-accent hover:text-paper'}`}>
    <Icon size={22} strokeWidth={1.5} />
  </div>
);

const StatCard: React.FC<{ icon: any, label: string, value: string, subtext: string, trend?: string }> = ({ icon: Icon, label, value, subtext, trend }) => (
  <div className="p-5 border border-ink flex flex-col justify-between h-36 bg-paper hover:bg-ink/5 transition-colors">
    <div className="flex justify-between items-start">
      <span className="mono text-[10px] uppercase tracking-widest font-bold opacity-60">{label}</span>
      <Icon size={16} className="opacity-40" />
    </div>
    <div>
      <div className="flex items-baseline gap-2">
        <div className="serif text-4xl font-medium">{value}</div>
        {trend && <span className="mono text-[9px] text-accent font-bold">{trend}</span>}
      </div>
      <div className="mono text-[9px] uppercase mt-1 opacity-50">{subtext}</div>
    </div>
  </div>
);

const CaseRow: React.FC<{ caseData: CasePaper }> = ({ caseData }) => (
  <motion.div 
    initial={{ opacity: 0, y: 2 }}
    animate={{ opacity: 1, y: 0 }}
    className="group grid grid-cols-[80px_1.8fr_1fr_1fr_120px_60px] border-b border-ink hover:bg-accent/5 transition-all cursor-pointer"
  >
    <div className="p-3 border-r border-ink mono text-[10px] flex items-center opacity-50">{caseData.id}</div>
    <div className="p-3 border-r border-ink flex flex-col justify-center">
      <span className="serif text-lg font-semibold tracking-tight group-hover:text-accent transition-colors">{caseData.patient}</span>
      <span className="mono text-[8px] opacity-40 uppercase">Patient_Record_Verified</span>
    </div>
    <div className="p-3 border-r border-ink mono text-[10px] flex items-center">{caseData.date}</div>
    <div className="p-3 border-r border-ink flex items-center text-[11px] opacity-70 italic">{caseData.practitioner}</div>
    <div className="p-3 border-r border-ink flex items-center gap-2">
      <span className={`mono text-[9px] px-2 py-0.5 border ${
        caseData.status === 'FINAL' ? 'bg-accent text-paper border-accent' : 
        caseData.status === 'PENDING' ? 'bg-ink text-paper border-ink' : 'border-ink opacity-60'
      }`}>
        {caseData.status}
      </span>
      {caseData.priority === 'HIGH' && (
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
          <span className="mono text-[8px] text-red-600 font-bold">URGENT</span>
        </div>
      )}
    </div>
    <div className="p-3 flex items-center justify-center">
      <MoreHorizontal size={14} className="opacity-20 group-hover:opacity-100 transition-all" />
    </div>
  </motion.div>
);

export default function App() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="flex h-screen w-full bg-paper selection:bg-accent selection:text-paper text-ink">
      {/* Sidebar - Rail (Kept as requested) */}
      <aside className="w-14 flex flex-col border-r border-ink bg-paper z-50">
        <div className="w-14 h-14 flex items-center justify-center border-b border-ink bg-accent">
          <FileText size={24} className="text-paper" />
        </div>
        <NavIcon icon={LayoutDashboard} />
        <NavIcon icon={FileText} active />
        <NavIcon icon={Users} />
        <NavIcon icon={Calendar} />
        <div className="mt-auto">
          <NavIcon icon={Settings} />
          <NavIcon icon={LogOut} />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header Bar */}
        <header className="h-14 border-b border-ink flex items-center justify-between px-6 bg-paper">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-ink flex items-center justify-center">
              <Plus size={16} className="text-paper" />
            </div>
            <div>
              <h1 className="serif text-xl font-bold tracking-tight leading-none">HomeoCase Dashboard</h1>
              <span className="mono text-[8px] opacity-40 uppercase tracking-[0.2em]">Medical_Records_Management_System</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-4 border-r border-ink pr-6 mr-6">
              <div className="text-right">
                <div className="mono text-[9px] opacity-40 uppercase">Last Sync</div>
                <div className="mono text-[10px] font-bold">04:26:29 UTC</div>
              </div>
              <div className="text-right">
                <div className="mono text-[9px] opacity-40 uppercase">Database</div>
                <div className="mono text-[10px] font-bold text-accent">CONNECTED</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex flex-col items-end">
                <span className="mono text-[10px] font-bold">DR. ABHAY</span>
                <span className="mono text-[8px] opacity-40 uppercase">Chief Practitioner</span>
              </div>
              <div className="w-10 h-10 border border-ink flex items-center justify-center serif text-lg font-bold bg-ink text-paper">
                AB
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-y-auto bg-[#F0F0EF]">
          <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
            
            {/* Top Section: Stats & Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
              <StatCard 
                icon={FileText} 
                label="Total Archives" 
                value="1,204" 
                subtext="Cumulative Records" 
                trend="+2.4%"
              />
              <StatCard 
                icon={Clock} 
                label="Active Drafts" 
                value="08" 
                subtext="Pending Finalization" 
                trend="STABLE"
              />
              <StatCard 
                icon={CheckCircle2} 
                label="Finalized" 
                value="1,196" 
                subtext="Verified Reports" 
                trend="+12"
              />
              <div className="p-5 border border-ink flex flex-col justify-between h-36 bg-accent text-paper group cursor-pointer hover:bg-ink transition-all shadow-[4px_4px_0px_0px_rgba(10,10,10,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]">
                <div className="flex justify-between items-start">
                  <span className="mono text-[10px] uppercase tracking-widest font-bold">Primary Action</span>
                  <Plus size={18} />
                </div>
                <div>
                  <h2 className="serif text-2xl font-bold italic leading-tight">Create New<br/>Case Paper</h2>
                  <p className="mono text-[8px] uppercase mt-2 opacity-70 tracking-widest">Initialize Clinical Protocol</p>
                </div>
              </div>
            </div>

            {/* Middle Section: Search & Filters */}
            <div className="flex flex-col md:flex-row gap-4 items-stretch">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 opacity-30" size={16} />
                <input 
                  type="text" 
                  placeholder="SEARCH_BY_PATIENT_NAME_OR_REF_ID..."
                  className="w-full bg-paper border border-ink py-3 pl-12 pr-4 text-[11px] mono focus:outline-none focus:ring-1 focus:ring-accent transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <button className="px-6 border border-ink bg-paper mono text-[10px] uppercase font-bold flex items-center gap-2 hover:bg-ink hover:text-paper transition-all">
                <Filter size={14} />
                Advanced_Filters
              </button>
            </div>

            {/* Main Data Grid */}
            <div className="border border-ink bg-paper shadow-sm">
              <div className="grid grid-cols-[80px_1.8fr_1fr_1fr_120px_60px] border-b border-ink bg-ink text-paper sticky top-0 z-10">
                <div className="p-3 border-r border-paper/10 mono text-[9px] uppercase tracking-widest font-bold">Ref_ID</div>
                <div className="p-3 border-r border-paper/10 mono text-[9px] uppercase tracking-widest font-bold">Patient_Identity</div>
                <div className="p-3 border-r border-paper/10 mono text-[9px] uppercase tracking-widest font-bold">Archive_Date</div>
                <div className="p-3 border-r border-paper/10 mono text-[9px] uppercase tracking-widest font-bold">Practitioner</div>
                <div className="p-3 border-r border-paper/10 mono text-[9px] uppercase tracking-widest font-bold">Status_Level</div>
                <div className="p-3"></div>
              </div>
              
              <div className="flex flex-col min-h-[400px]">
                {MOCK_CASES.map((c) => (
                  <CaseRow key={c.id} caseData={c} />
                ))}
                {/* Fill empty space with subtle grid lines */}
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="grid grid-cols-[80px_1.8fr_1fr_1fr_120px_60px] border-b border-ink h-14 opacity-[0.03]" />
                ))}
              </div>
              
              {/* Table Footer / Pagination */}
              <div className="h-10 flex items-center justify-between px-4 bg-ink/5 border-t border-ink">
                <div className="mono text-[9px] opacity-50 font-bold uppercase tracking-tighter">Total_Records: 1,204 // Page 1 of 172</div>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <button className="mono text-[9px] uppercase font-bold opacity-30 cursor-not-allowed">Prev</button>
                    <span className="mono text-[9px] font-bold px-2 py-0.5 border border-ink bg-ink text-paper">01</span>
                    <button className="mono text-[9px] uppercase font-bold hover:text-accent transition-colors">Next</button>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Section: Activity & Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 p-5 border border-ink bg-paper space-y-4">
                <div className="flex justify-between items-center border-b border-ink pb-2">
                  <h3 className="serif text-lg font-bold italic">Recent System Activity</h3>
                  <span className="mono text-[8px] opacity-40 uppercase tracking-widest">Live_Feed</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
                  {[
                    { text: "Case HC-002 finalized by Dr. Abhay", time: "2h ago", type: "SUCCESS" },
                    { text: "New draft created for Lydia Vance", time: "4h ago", type: "INFO" },
                    { text: "System backup completed successfully", time: "12h ago", type: "SYSTEM" },
                    { text: "Patient record HC-005 updated", time: "1d ago", type: "INFO" }
                  ].map((item, i) => (
                    <div key={i} className="flex justify-between items-center text-[10px] border-b border-ink/5 pb-1">
                      <div className="flex items-center gap-2">
                        <div className={`w-1 h-1 rounded-full ${item.type === 'SUCCESS' ? 'bg-accent' : 'bg-ink'}`} />
                        <span className="opacity-70 font-medium">{item.text}</span>
                      </div>
                      <span className="mono opacity-40 text-[9px]">{item.time}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="p-5 border border-ink bg-red-50/30 space-y-4">
                <div className="flex items-center justify-between border-b border-red-200 pb-2">
                  <div className="flex items-center gap-2 text-red-700">
                    <AlertCircle size={16} />
                    <h3 className="serif text-lg font-bold italic">Clinical Alerts</h3>
                  </div>
                  <span className="mono text-[8px] text-red-600 font-bold uppercase tracking-widest">Priority_High</span>
                </div>
                <div className="space-y-2">
                  <div className="p-3 border border-red-200 bg-white flex justify-between items-center group cursor-pointer hover:bg-red-50 transition-colors">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-red-800">PENDING_FINALIZATION</span>
                      <span className="text-[9px] opacity-60">4 Case Papers overdue ({'>'} 48h)</span>
                    </div>
                    <ArrowUpRight size={14} className="text-red-400 group-hover:text-red-700" />
                  </div>
                  <div className="p-3 border border-red-100 bg-white/50 flex justify-between items-center opacity-60">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold">SYSTEM_MAINTENANCE</span>
                      <span className="text-[9px]">Scheduled for 2026.03.26</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Status Footer */}
        <footer className="h-10 border-t border-ink flex items-center justify-between px-6 bg-paper z-20">
          <div className="mono text-[8px] uppercase tracking-[0.4em] opacity-40 font-bold">
            HomeoCase // Clinical_Documentation_v2.4.0 // Secure_Environment
          </div>
          <div className="flex items-center gap-4 mono text-[8px] uppercase font-bold opacity-40">
            <span className="flex items-center gap-1"><div className="w-1 h-1 rounded-full bg-accent" /> Encrypted</span>
            <span>{new Date().toLocaleDateString()} // {new Date().toLocaleTimeString()}</span>
          </div>
        </footer>
      </main>
    </div>
  );
}
