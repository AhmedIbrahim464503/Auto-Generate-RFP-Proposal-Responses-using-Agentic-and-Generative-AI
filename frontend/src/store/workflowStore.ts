import { create } from "zustand";

interface UIState {
  activeTab: string;
  isSidebarOpen: boolean;
  setActiveTab: (tab: string) => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeTab: "command_center",
  isSidebarOpen: true,
  setActiveTab: (tab) => set({ activeTab: tab }),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));

interface WorkflowState {
  activeExecutionId: string | null;
  playbackSpeed: number;
  setActiveExecutionId: (id: string | null) => void;
  setPlaybackSpeed: (speed: number) => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  activeExecutionId: null,
  playbackSpeed: 1.0,
  setActiveExecutionId: (id) => set({ activeExecutionId: id }),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),
}));

interface ProposalState {
  activeProposalId: string | null;
  selectedChapterId: string | null;
  setActiveProposalId: (id: string | null) => void;
  setSelectedChapterId: (id: string | null) => void;
}

export const useProposalStore = create<ProposalState>((set) => ({
  activeProposalId: null,
  selectedChapterId: null,
  setActiveProposalId: (id) => set({ activeProposalId: id }),
  setSelectedChapterId: (id) => set({ selectedChapterId: id }),
}));

interface ReviewState {
  selectedFindingCategory: string | null;
  setSelectedFindingCategory: (category: string | null) => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  selectedFindingCategory: null,
  setSelectedFindingCategory: (category) => set({ selectedFindingCategory: category }),
}));

interface AIState {
  selectedAgentId: string | null;
  setSelectedAgentId: (id: string | null) => void;
}

export const useAIStore = create<AIState>((set) => ({
  selectedAgentId: null,
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),
}));
