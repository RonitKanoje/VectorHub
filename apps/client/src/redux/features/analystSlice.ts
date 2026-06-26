import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type {
  AnalystMessage,
  AnalystDataset,
  AnalystVisualization,
} from "../../types";

interface AnalystState {
  messages: AnalystMessage[];
  isSending: boolean;
  uploadedDatasets: AnalystDataset[];
  activeDatasetId: string | null;
}

const initialState: AnalystState = {
  messages: [],
  isSending: false,
  uploadedDatasets: [],
  activeDatasetId: null,
};

const analystSlice = createSlice({
  name: "analyst",
  initialState,
  reducers: {
    addUserMessage(state, action: PayloadAction<string>) {
      state.messages.push({ id: crypto.randomUUID(), role: "user", content: action.payload });
      state.messages.push({ id: crypto.randomUUID(), role: "assistant", content: "", pending: true });
    },
    appendChunk(state, action: PayloadAction<string>) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant") {
        last.content += action.payload;
        last.pending = false;
      }
    },
    appendVisualization(state, action: PayloadAction<AnalystVisualization>) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant") {
        if (!last.visualizations) last.visualizations = [];
        last.visualizations.push(action.payload);
        last.pending = false;
      }
    },
    finalizeResponse(state) {
      const last = state.messages[state.messages.length - 1];
      if (last) last.pending = false;
    },
    setError(state, action: PayloadAction<string>) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.pending) {
        last.content = action.payload;
        last.pending = false;
      }
    },
    setIsSending(state, action: PayloadAction<boolean>) {
      state.isSending = action.payload;
    },
    addDataset(state, action: PayloadAction<AnalystDataset>) {
      state.uploadedDatasets.unshift(action.payload);
      state.activeDatasetId = action.payload.id;
    },
    setActiveDataset(state, action: PayloadAction<string>) {
      state.activeDatasetId = action.payload;
      // Reset conversation when switching datasets
      state.messages = [];
    },
    clearMessages(state) {
      state.messages = [];
    },
    setMessages(state, action: PayloadAction<AnalystMessage[]>) {
      state.messages = action.payload;
    },
  },
});

export const {
  addUserMessage,
  appendChunk,
  appendVisualization,
  finalizeResponse,
  setError,
  setIsSending,
  addDataset,
  setActiveDataset,
  clearMessages,
  setMessages,
} = analystSlice.actions;

export default analystSlice.reducer;
