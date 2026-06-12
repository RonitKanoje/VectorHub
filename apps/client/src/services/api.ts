import axios from "axios";
import type {
  AxiosError,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { store } from "../redux/store";
import { logout, setCredentials } from "../redux/features/authSlice";

interface RefreshResponse {
  accessToken: string;
}

type RetryRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

const api = axios.create({
  baseURL: "http://localhost:3000",
  withCredentials: true,
});

let refreshPromise: Promise<AxiosResponse<RefreshResponse>> | null = null; // AxiosResponse will be having RefreshResponse type 

// with the help of interceptors we can modify request and response so before every request run this code will execute 

// request interceptor
api.interceptors.request.use(
  // success handler
  (config) => {
    const token = store.getState().auth.accessToken;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  // error handler
  (error: AxiosError) => {
    return Promise.reject(error);
  },
);

// response interceptor
api.interceptors.response.use(
  // success
  (response) => response,

  // error
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryRequestConfig | undefined; //type assertion and taking out original request, casting it as RetryRequestConfig and it also contains _retry property
    const status = error.response?.status; // extract status 
    const url = originalRequest?.url || "";
    const method = originalRequest?.method?.toUpperCase() || "REQUEST"; // extracting the method of request

    if (status) {
      console.error(
        `${method} ${url} failed with ${status}`,
        error.response?.data,
      );
    }

    if (
      status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      url.includes("/api/auth/refresh-token")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true; // to avoid infinte loops

    try {
      if (!refreshPromise) {
        refreshPromise = api
          .post<RefreshResponse>("/api/auth/refresh-token", {})
          .finally(() => {
            refreshPromise = null;
          });
      }

      const response = await refreshPromise;
      const accessToken = response.data.accessToken;

      store.dispatch(setCredentials(accessToken));
      originalRequest.headers.Authorization = `Bearer ${accessToken}`;

      return api(originalRequest); // same request 
    } catch (refreshError) {
      store.dispatch(logout());
      return Promise.reject(refreshError); // creating a promise and passing the error forward 
    }
  },
);

export default api;
