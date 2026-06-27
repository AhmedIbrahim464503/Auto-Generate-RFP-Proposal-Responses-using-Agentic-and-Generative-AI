import { describe, it, expect } from 'vitest';
import { useUIStore, useWorkflowStore, useProposalStore } from '../store/workflowStore';

describe('Frontend Zustand Stores state actions', () => {
  it('should initialize with default states', () => {
    expect(useUIStore.getState().activeTab).toBe('command_center');
    expect(useUIStore.getState().isSidebarOpen).toBe(true);
    expect(useWorkflowStore.getState().activeExecutionId).toBeNull();
    expect(useProposalStore.getState().activeProposalId).toBeNull();
  });

  it('should update active tab on setActiveTab call', () => {
    useUIStore.getState().setActiveTab('workflow');
    expect(useUIStore.getState().activeTab).toBe('workflow');
  });

  it('should toggle sidebar on toggleSidebar call', () => {
    const initial = useUIStore.getState().isSidebarOpen;
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().isSidebarOpen).toBe(!initial);
  });

  it('should register active proposal ID and chapter nodes', () => {
    useProposalStore.getState().setActiveProposalId('proposal_123');
    useProposalStore.getState().setSelectedChapterId('chapter_abc');
    expect(useProposalStore.getState().activeProposalId).toBe('proposal_123');
    expect(useProposalStore.getState().selectedChapterId).toBe('chapter_abc');
  });
});
