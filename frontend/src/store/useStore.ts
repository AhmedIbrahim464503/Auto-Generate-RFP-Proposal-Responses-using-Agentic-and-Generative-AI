import { create } from "zustand";

interface Project {
  id: string;
  title: string;
  status: string;
}

interface AppState {
  currentProject: Project | null;
  gateApprovals: Record<string, boolean>;
  setProject: (project: Project) => void;
  approveGate: (gateId: string) => void;
  resetGates: () => void;
}

export const useStore = create<AppState>((set) => ({
  currentProject: null,
  gateApprovals: {
    gate1: false,
    gate2: false,
    gate3: false,
    gate4: false,
  },
  setProject: (project) => set({ currentProject: project }),
  approveGate: (gateId) =>
    set((state) => ({
      gateApprovals: {
        ...state.gateApprovals,
        [gateId]: true,
      },
    })),
  resetGates: () =>
    set({
      gateApprovals: {
        gate1: false,
        gate2: false,
        gate3: false,
        gate4: false,
      },
    }),
}));
