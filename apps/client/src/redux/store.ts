import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./features/authSlice";
import themeReducer from "./features/themeSlice";
import analystReducer from "./features/analystSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    theme: themeReducer,
    analyst: analystReducer,
  },
});


// For type safety 
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
