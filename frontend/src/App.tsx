import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterRecruiterPage } from "./pages/RegisterRecruiterPage";
import { RegisterStudentPage } from "./pages/RegisterStudentPage";

// Student Pages
import { MyApplications } from "./pages/student/MyApplications";
import { OpportunitiesExplore } from "./pages/student/OpportunitiesExplore";
import { StudentDashboard } from "./pages/student/StudentDashboard";
import { StudentProfilePage } from "./pages/student/StudentProfile";

// Recruiter Pages
import { CompanyProfilePage } from "./pages/recruiter/CompanyProfile";
import { ManageOpportunities } from "./pages/recruiter/ManageOpportunities";
import { RecruiterDashboard } from "./pages/recruiter/RecruiterDashboard";
import { ReviewApplications } from "./pages/recruiter/ReviewApplications";

// Admin Pages
import { AdminDashboard } from "./pages/admin/AdminDashboard";
import { AllApplications } from "./pages/admin/AllApplications";
import { AllOpportunities } from "./pages/admin/AllOpportunities";
import { CompanyDirectory } from "./pages/admin/CompanyDirectory";
import { UserManagement } from "./pages/admin/UserManagement";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register/student" element={<RegisterStudentPage />} />
        <Route path="/register/recruiter" element={<RegisterRecruiterPage />} />

        {/* Protected Student Routes */}
        <Route
          path="/student"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/opportunities"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <OpportunitiesExplore />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/applications"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <MyApplications />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/profile"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <StudentProfilePage />
            </ProtectedRoute>
          }
        />

        {/* Protected Recruiter Routes */}
        <Route
          path="/recruiter"
          element={
            <ProtectedRoute allowedRoles={["recruiter"]}>
              <RecruiterDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recruiter/opportunities"
          element={
            <ProtectedRoute allowedRoles={["recruiter"]}>
              <ManageOpportunities />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recruiter/applications"
          element={
            <ProtectedRoute allowedRoles={["recruiter"]}>
              <ReviewApplications />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recruiter/company"
          element={
            <ProtectedRoute allowedRoles={["recruiter"]}>
              <CompanyProfilePage />
            </ProtectedRoute>
          }
        />

        {/* Protected Admin Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <UserManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/companies"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <CompanyDirectory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/opportunities"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AllOpportunities />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/applications"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AllApplications />
            </ProtectedRoute>
          }
        />

        {/* Catch-All */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
