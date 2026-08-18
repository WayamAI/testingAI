import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { EmptyState } from "./components/common/EmptyState";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AppLayout />}>
            {/* Full route table added across Tasks 15-18. Placeholder
                landing route keeps AppLayout reachable and non-empty until
                those routes land. */}
            <Route
              path="/dashboard"
              element={
                <EmptyState
                  title="Dashboard coming soon"
                  description="This page will be populated in a later task."
                />
              }
            />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
