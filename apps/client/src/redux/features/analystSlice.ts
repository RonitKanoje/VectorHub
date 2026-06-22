import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export interface AnalystMessage {
  role: "user" | "assistant" | "system";
  content: string;
  pending?: boolean;
  mediaAttachment?: { type: string; name: string };
}

export interface UploadedDataset {
  id: string;
  name: string;
  thread_id: string;
  uploadedAt: string;
}

interface AnalystState {
  messages: AnalystMessage[];
  isSending: boolean;
  uploadedDatasets: UploadedDataset[];
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
      state.messages.push({ role: "user", content: action.payload });
      state.messages.push({ role: "assistant", content: "", pending: true });
    },
    appendChunk(state, action: PayloadAction<string>) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant") {
        last.content += action.payload;
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
    addDataset(state, action: PayloadAction<UploadedDataset>) {
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
  },
});

export const {
  addUserMessage,
  appendChunk,
  finalizeResponse,
  setError,
  setIsSending,
  addDataset,
  setActiveDataset,
  clearMessages,
} = analystSlice.actions;

export default analystSlice.reducer;
