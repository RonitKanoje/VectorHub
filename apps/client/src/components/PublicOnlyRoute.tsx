import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import type { RootState } from "../redux/store";

interface PublicOnlyRouteProps {
  children: React.ReactNode;
}

const PublicOnlyRoute = ({ children }: PublicOnlyRouteProps) => {
  const { accessToken, isLoading } = useSelector(
    (state: RootState) => state.auth,
  );

  if (isLoading) {
    return null;
  }

  if (accessToken) {
    return <Navigate to="/chat" replace />;
  }

  return children;
};

export default PublicOnlyRoute;
