import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

interface AuthState {
  accessToken: string | null;
  isLoading: boolean;
}

const initialState: AuthState = {
  accessToken: null,
  isLoading: true,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setCredentials: (state, action: PayloadAction<string>) => {
      state.accessToken = action.payload;
      state.isLoading = false;
    },

    finishLoading: (state) => {
      state.isLoading = false;
    },

    logout: (state) => {
      state.accessToken = null;
      state.isLoading = false;
    },
  },
});

export const { setCredentials, finishLoading, logout } = authSlice.actions;

export default authSlice.reducer;
