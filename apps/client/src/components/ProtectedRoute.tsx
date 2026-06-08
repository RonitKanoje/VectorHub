import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import type { RootState } from "../redux/store";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({
  children,
}: ProtectedRouteProps) => {
  const { accessToken, isLoading } = useSelector(
    (state: RootState) => state.auth
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!accessToken) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;